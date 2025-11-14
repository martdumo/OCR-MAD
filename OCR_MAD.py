import os
import sys
import io
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import platform
import traceback
import logging
import tempfile
import subprocess

# === CONFIGURACIÓN DE LOGGING MEJORADA ===
def setup_logging():
    """Configura logging compatible con Windows y modo --onefile"""
    try:
        # Determinar dónde guardar el log
        if getattr(sys, 'frozen', False):
            # Modo --onefile: guardar en el escritorio
            log_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            # Modo desarrollo: guardar en la carpeta del script
            log_dir = os.path.dirname(os.path.abspath(__file__))
        
        log_file = os.path.join(log_dir, "ocr_mad_debug.log")
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ],
            encoding='utf-8'
        )
        logging.info(f"Log creado en: {log_file}")
        return log_file
    except Exception as e:
        print(f"Error configurando logging: {e}")
        return None

DEBUG_LOG = setup_logging()
logging.info("=== INICIANDO OCR-MAD ===")
logging.info(f"Ruta base: {os.path.dirname(os.path.abspath(__file__))}")

# === IMPORTAR LIBRERÍAS ===
try:
    import pymupdf as fitz
    logging.info("PyMuPDF importado correctamente")
except ImportError as e:
    logging.error(f"Error importando PyMuPDF: {e}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error crítico", "No se pudo cargar PyMuPDF. Reinstala la aplicación.")
    sys.exit(1)

try:
    from PIL import Image, ImageEnhance, ImageFilter
    logging.info("PIL importado correctamente")
except ImportError as e:
    logging.error(f"Error importando PIL: {e}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error crítico", "No se pudo cargar PIL. Reinstala la aplicación.")
    sys.exit(1)

try:
    import pytesseract
    logging.info("pytesseract importado correctamente")
except ImportError as e:
    logging.error(f"Error importando pytesseract: {e}")
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error crítico", "No se pudo cargar pytesseract. Reinstala la aplicación.")
    sys.exit(1)

# === FUNCIÓN PARA DETECTAR RUTA BASE MEJORADA ===
def get_base_dir():
    """Obtiene la ruta base correctamente para --onefile y desarrollo"""
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        else:
            return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
logging.info(f"BASE_DIR detectado: {BASE_DIR}")

# === CONFIGURACIÓN DE TESSERACT PORTABLE MEJORADA ===
def setup_tesseract():
    """Configura Tesseract OCR para funcionar correctamente en modo portátil y --onefile"""
    try:
        # Determinar la ruta base correcta
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        logging.info(f"Ruta base para Tesseract: {base_path}")
        
        # Buscar tesseract.exe en múltiples ubicaciones
        possible_paths = [
            os.path.join(base_path, "tesseract", "tesseract.exe"),
            os.path.join(base_path, "tesseract.exe"),
            os.path.join(os.path.dirname(sys.executable), "tesseract", "tesseract.exe"),
            "tesseract.exe"  # Buscar en PATH como último recurso
        ]
        
        tesseract_exe = None
        for path in possible_paths:
            if os.path.exists(path):
                tesseract_exe = path
                logging.info(f"Tesseract encontrado en: {path}")
                break
        
        if not tesseract_exe:
            error_msg = "ERROR:No se encontró tesseract.exe en las rutas esperadas:\n" + "\n".join(possible_paths)
            logging.error(error_msg)
            return False, None, error_msg
        
        # Determinar la ruta de tessdata correctamente
        # ¡¡¡CRÍTICO!!! tessdata debe estar DENTRO de la carpeta tesseract
        tessdata_dir = None
        
        # Opción 1: tessdata dentro de la carpeta tesseract
        tessdata_option1 = os.path.join(os.path.dirname(tesseract_exe), "tessdata")
        if os.path.exists(tessdata_option1):
            tessdata_dir = tessdata_option1
            logging.info(f"tessdata encontrado en: {tessdata_dir} (dentro de carpeta tesseract)")
        
        # Opción 2: tessdata en la misma carpeta que el ejecutable
        if not tessdata_dir:
            tessdata_option2 = os.path.join(base_path, "tesseract", "tessdata")
            if os.path.exists(tessdata_option2):
                tessdata_dir = tessdata_option2
                logging.info(f"tessdata encontrado en: {tessdata_dir} (ruta alternativa)")
        
        # Opción 3: tessdata en la carpeta temporal para modo --onefile
        if not tessdata_dir and getattr(sys, 'frozen', False):
            # Crear una carpeta temporal para tessdata
            temp_tessdata = os.path.join(tempfile.gettempdir(), "ocr_mad_tessdata")
            if not os.path.exists(temp_tessdata):
                os.makedirs(temp_tessdata, exist_ok=True)
            
            # Copiar los archivos de idioma si existen
            source_tessdata = os.path.join(os.path.dirname(tesseract_exe), "tessdata")
            if os.path.exists(source_tessdata):
                import shutil
                try:
                    shutil.copytree(source_tessdata, temp_tessdata, dirs_exist_ok=True)
                    tessdata_dir = temp_tessdata
                    logging.info(f"tessdata copiado a carpeta temporal: {tessdata_dir}")
                except Exception as e:
                    logging.error(f"Error copiando tessdata a temporal: {e}")
        
        if not tessdata_dir or not os.path.exists(tessdata_dir):
            error_msg = f"ERROR:No se encontró la carpeta tessdata en ninguna ubicación esperada"
            logging.error(error_msg)
            return False, None, error_msg
        
        # Verificar archivos de idioma esenciales
        required_files = ["spa.traineddata", "eng.traineddata"]
        missing_files = []
        for lang_file in required_files:
            lang_path = os.path.join(tessdata_dir, lang_file)
            if not os.path.exists(lang_path):
                missing_files.append(lang_file)
        
        if missing_files:
            error_msg = f"ERROR:Faltan archivos de idioma en tessdata: {', '.join(missing_files)}"
            logging.error(error_msg)
            return False, None, error_msg
        
        # Configurar Tesseract y variables de entorno
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        os.environ["TESSDATA_PREFIX"] = tessdata_dir
        
        # Verificar que Tesseract funciona correctamente
        try:
            version = subprocess.check_output([tesseract_exe, '--version'], stderr=subprocess.STDOUT, text=True)
            logging.info(f"Tesseract versión: {version.strip()}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error verificando Tesseract: {e.output}")
            error_msg = f"ERROR:Error al verificar Tesseract: {e.output}"
            return False, None, error_msg
        
        logging.info(f" Tesseract configurado correctamente:")
        logging.info(f"   tesseract_cmd: {tesseract_exe}")
        logging.info(f"   TESSDATA_PREFIX: {tessdata_dir}")
        
        return True, tesseract_exe, None
    
    except Exception as e:
        error_msg = f"ERROR:Error crítico configurando Tesseract: {traceback.format_exc()}"
        logging.error(error_msg)
        return False, None, error_msg

# === PREPROCESAMIENTO DE IMÁGENES MEJORADO ===
def preprocess_image(img: Image.Image) -> Image.Image:
    """Preprocesa la imagen para mejorar el reconocimiento OCR"""
    try:
        logging.debug("Iniciando preprocesamiento de imagen")
        # Convertir a escala de grises
        img = img.convert("L")
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        # Aumentar nitidez
        img = img.filter(ImageFilter.SHARPEN)
        # Umbral adaptativo
        img = img.point(lambda x: 0 if x < 140 else 255, '1')
        logging.debug("Preprocesamiento completado")
        return img
    except Exception as e:
        logging.error(f"Error en preprocesamiento: {traceback.format_exc()}")
        return img


    """Realiza OCR en una imagen y genera un PDF con texto seleccionable"""
    try:
        logging.info(f"Iniciando OCR para imagen: {input_image}")
        logging.info(f"Archivo de salida: {output_pdf}")
        
        if progress_callback:
            progress_callback(1, 1, "Procesando imagen")
        
        # Abrir y preprocesar imagen
        img = Image.open(input_image)
        img = preprocess_image(img)
        
        # Configurar rutas temporales seguras
        temp_prefix = "tess_image_"
        temp_dir = tempfile.gettempdir()
        
        # Realizar OCR
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(
            img,
            lang="spa+eng",
            config="--oem 1 --psm 3 -c preserve_interword_spaces=1",
            extension="pdf",
            temp_dir=temp_dir,
            output_file_prefix=temp_prefix
        )
        
        # Guardar PDF
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        
        file_size = os.path.getsize(output_pdf) / 1024 / 1024
        logging.info(f"Archivo guardado: {output_pdf} ({file_size:.2f} MB)")
        
        return True
        
    except Exception as e:
        logging.error(f"Error crítico en ocr_image: {traceback.format_exc()}")
        raise


# === OCR PARA PDF - CORREGIDO DEFINITIVO ===
def ocr_pdf(input_pdf: str, output_pdf: str, progress_callback=None):
    """Realiza OCR en un archivo PDF y genera un PDF con texto seleccionable"""
    try:
        logging.info(f"Iniciando OCR para PDF: {input_pdf}")
        logging.info(f"Archivo de salida: {output_pdf}")
        
        # Abrir documento
        doc = fitz.open(input_pdf)
        out_doc = fitz.open()
        total_pages = len(doc)
        logging.info(f"Total de páginas: {total_pages}")
        
        # Procesar cada página
        for n, page in enumerate(doc, start=1):
            if progress_callback:
                progress_callback(n, total_pages, f"Página {n}/{total_pages}")
            
            try:
                logging.debug(f"Procesando página {n}")
                # Renderizar página a imagen de alta resolución
                mat = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                img = preprocess_image(img)
                
                # Usar una carpeta temporal específica para este proceso
                temp_dir = tempfile.mkdtemp(prefix="ocr_mad_")
                temp_img_path = os.path.join(temp_dir, f"page_{n}_input.png")
                temp_output_base = os.path.join(temp_dir, f"page_{n}_output")
                
                # Guardar imagen temporal
                img.save(temp_img_path)
                logging.debug(f"Imagen temporal guardada en: {temp_img_path}")
                
                # Configurar comando Tesseract con sintaxis CORRECTA para Tesseract 5.5.0
                tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
                tessdata_dir = os.environ.get("TESSDATA_PREFIX", "")
                
                # ¡¡¡SINTAXIS CORRECTA PARA TESSERACT 5.5.0!!!
                cmd = [
                    tesseract_cmd,
                    temp_img_path,
                    temp_output_base,  # Base name sin extensión
                    '-l', 'spa+eng',
                    '--oem', '1',
                    '--psm', '3',
                    '-c', 'preserve_interword_spaces=1',
                    '-c', 'tessedit_create_pdf=1'  # ¡¡¡ESTA ES LA FORMA CORRECTA DE GENERAR PDF!!!
                ]
                
                if tessdata_dir:
                    cmd.extend(['--tessdata-dir', tessdata_dir])
                
                logging.debug(f"Ejecutando comando CORRECTO v2: {' '.join(cmd)}")
                
                # Ejecutar Tesseract directamente
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                # Mostrar salida de Tesseract para diagnóstico
                if result.stdout.strip():
                    logging.debug(f"Tesseract stdout: {result.stdout}")
                if result.stderr.strip():
                    logging.debug(f"Tesseract stderr: {result.stderr}")
                
                if result.returncode != 0:
                    logging.error(f"Error Tesseract (página {n}): {result.stderr}")
                    logging.error(f"Código de retorno: {result.returncode}")
                    # Intentar con configuración más simple
                    logging.warning("Intentando con configuración más simple...")
                    simpler_cmd = [
                        tesseract_cmd,
                        temp_img_path,
                        temp_output_base,
                        '-l', 'spa+eng',
                        '--oem', '1',
                        '--psm', '3',
                        '-c', 'tessedit_create_pdf=1'
                    ]
                    if tessdata_dir:
                        simpler_cmd.extend(['--tessdata-dir', tessdata_dir])
                    
                    simpler_result = subprocess.run(
                        simpler_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if simpler_result.returncode != 0:
                        logging.error(f"Error Tesseract simple (página {n}): {simpler_result.stderr}")
                        raise Exception(f"Tesseract falló en página {n}")
                
                # El archivo PDF se genera con el mismo nombre base + .pdf
                temp_pdf_path = f"{temp_output_base}.pdf"
                
                # Verificar que el archivo PDF se creó
                if not os.path.exists(temp_pdf_path):
                    # Intentar con la extensión .PDF (a veces Windows es sensible a mayúsculas/minúsculas)
                    alt_path = temp_pdf_path.replace('.pdf', '.PDF')
                    if os.path.exists(alt_path):
                        temp_pdf_path = alt_path
                    else:
                        logging.error(f"Archivo PDF no encontrado: {temp_pdf_path}")
                        logging.error(f"Contenido de carpeta temporal:")
                        for file in os.listdir(temp_dir):
                            logging.error(f"  - {file}")
                        # Mostrar el comando exacto que falló
                        logging.error(f"Comando ejecutado: {' '.join(cmd)}")
                        raise FileNotFoundError(f"No se encontró archivo PDF para página {n}")
                
                logging.debug(f"PDF generado: {temp_pdf_path} ({os.path.getsize(temp_pdf_path)} bytes)")
                
                # Leer el PDF generado
                with open(temp_pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                
                # Convertir a PDF y añadir al documento final
                ocr_page = fitz.open("pdf", pdf_bytes)
                out_doc.insert_pdf(ocr_page)
                ocr_page.close()
                logging.debug(f"Página {n} procesada correctamente")
                
                # Limpiar archivos temporales
                try:
                    os.unlink(temp_img_path)
                    os.unlink(temp_pdf_path)
                    os.rmdir(temp_dir)
                except Exception as e:
                    logging.warning(f"No se pudieron limpiar archivos temporales: {e}")
                
            except Exception as e:
                logging.error(f"Error en página {n}: {traceback.format_exc()}")
                continue
        
        # Guardar documento final solo si hay páginas
        if out_doc.page_count == 0:
            error_msg = "No se pudo procesar ninguna página. Verifica que el PDF tenga contenido visible y que Tesseract esté funcionando correctamente."
            logging.error(error_msg)
            out_doc.close()
            raise ValueError(error_msg)
        
        logging.info("Guardando documento final")
        out_doc.save(output_pdf)
        file_size = os.path.getsize(output_pdf) / 1024 / 1024
        logging.info(f"Archivo guardado: {output_pdf} ({file_size:.2f} MB)")
        
        # Cerrar documentos
        out_doc.close()
        doc.close()
        
        return True
        
    except Exception as e:
        logging.error(f"Error crítico en ocr_pdf: {traceback.format_exc()}")
        raise

# === OCR PARA IMÁGENES - CORREGIDO DEFINITIVO ===
def ocr_image(input_image: str, output_pdf: str, progress_callback=None):
    """Realiza OCR en una imagen y genera un PDF con texto seleccionable"""
    try:
        logging.info(f"Iniciando OCR para imagen: {input_image}")
        logging.info(f"Archivo de salida: {output_pdf}")
        
        if progress_callback:
            progress_callback(1, 1, "Procesando imagen")
        
        # Abrir y preprocesar imagen
        img = Image.open(input_image)
        img = preprocess_image(img)
        
        # Usar carpeta temporal específica
        temp_dir = tempfile.mkdtemp(prefix="ocr_mad_img_")
        temp_img_path = os.path.join(temp_dir, "input.png")
        temp_output_base = os.path.join(temp_dir, "output")
        
        # Guardar imagen temporal
        img.save(temp_img_path)
        
        # Configurar comando Tesseract con sintaxis CORRECTA
        tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
        tessdata_dir = os.environ.get("TESSDATA_PREFIX", "")
        
        # ¡¡¡SINTAXIS CORRECTA PARA TESSERACT 5.5.0!!!
        cmd = [
            tesseract_cmd,
            temp_img_path,
            temp_output_base,  # Base name sin extensión
            '-l', 'spa+eng',
            '--oem', '1',
            '--psm', '3',
            '-c', 'preserve_interword_spaces=1',
            '-c', 'tessedit_create_pdf=1'  # ¡¡¡ESTA ES LA FORMA CORRECTA DE GENERAR PDF!!!
        ]
        
        if tessdata_dir:
            cmd.extend(['--tessdata-dir', tessdata_dir])
        
        logging.debug(f"Ejecutando comando imagen CORRECTO v2: {' '.join(cmd)}")
        
        # Ejecutar Tesseract directamente
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        # Mostrar salida para diagnóstico
        if result.stdout.strip():
            logging.debug(f"Tesseract imagen stdout: {result.stdout}")
        if result.stderr.strip():
            logging.debug(f"Tesseract imagen stderr: {result.stderr}")
        
        if result.returncode != 0:
            logging.error(f"Error Tesseract imagen: {result.stderr}")
            # Intentar con configuración más simple
            simpler_cmd = [
                tesseract_cmd,
                temp_img_path,
                temp_output_base,
                '-l', 'spa+eng',
                '--oem', '1',
                '--psm', '3',
                '-c', 'tessedit_create_pdf=1'
            ]
            if tessdata_dir:
                simpler_cmd.extend(['--tessdata-dir', tessdata_dir])
            
            simpler_result = subprocess.run(
                simpler_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if simpler_result.returncode != 0:
                logging.error(f"Error Tesseract simple imagen: {simpler_result.stderr}")
                raise Exception("Tesseract falló al procesar la imagen")
        
        # El archivo PDF se genera con el mismo nombre base + .pdf
        temp_pdf_path = f"{temp_output_base}.pdf"
        
        # Verificar que el archivo PDF se creó
        if not os.path.exists(temp_pdf_path):
            alt_path = temp_pdf_path.replace('.pdf', '.PDF')
            if os.path.exists(alt_path):
                temp_pdf_path = alt_path
            else:
                logging.error(f"Archivo PDF no encontrado: {temp_pdf_path}")
                logging.error(f"Contenido de carpeta temporal:")
                for file in os.listdir(temp_dir):
                    logging.error(f"  - {file}")
                raise FileNotFoundError("No se encontró archivo PDF generado")
        
        logging.debug(f"PDF generado: {temp_pdf_path} ({os.path.getsize(temp_pdf_path)} bytes)")
        
        # Guardar PDF final
        with open(temp_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        with open(output_pdf, "wb") as f:
            f.write(pdf_bytes)
        
        # Limpiar archivos temporales
        try:
            os.unlink(temp_img_path)
            os.unlink(temp_pdf_path)
            os.rmdir(temp_dir)
        except Exception as e:
            logging.warning(f"No se pudieron limpiar archivos temporales de imagen: {e}")
        
        file_size = os.path.getsize(output_pdf) / 1024 / 1024
        logging.info(f"Archivo guardado: {output_pdf} ({file_size:.2f} MB)")
        
        return True
        
    except Exception as e:
        logging.error(f"Error crítico en ocr_image: {traceback.format_exc()}")
        raise



# === INTERFAZ MEJORADA ===
class OCRApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR-MAD Portable")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Centrar ventana
        self.root.eval('tk::PlaceWindow . center')
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(main_frame, text="OCR-MAD Portable", font=('Arial', 18, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10
        )
        
        ttk.Label(main_frame, text="Reconocimiento de texto para PDF e imágenes", font=('Arial', 10)).grid(
            row=1, column=0, columnspan=2, pady=5
        )
        
        # Botón seleccionar archivo
        self.select_btn = ttk.Button(
            main_frame, 
            text="📁 Seleccionar archivo", 
            command=self.select_file,
            width=25
        )
        self.select_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Label de archivo seleccionado
        self.file_label = ttk.Label(main_frame, text="Ningún archivo seleccionado", wraplength=400)
        self.file_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            main_frame, 
            orient=tk.HORIZONTAL, 
            length=400, 
            mode='determinate'
        )
        self.progress.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Label de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para procesar")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Botón de conversión PRINCIPAL
        self.convert_btn = ttk.Button(
            main_frame, 
            text="CONVERTIR AHORA", 
            command=self.start_ocr,
            state=tk.DISABLED,
            width=25,
            style='Accent.TButton'
        )
        self.convert_btn.grid(row=6, column=0, columnspan=2, pady=15)
        
        # Botón para ver log
        self.log_btn = ttk.Button(
            main_frame,
            text="📋 Ver Log de Errores",
            command=self.show_log,
            width=20
        )
        self.log_btn.grid(row=7, column=0, columnspan=2, pady=5)
        
        self.selected_file = None
        self.output_file = None
        
        # Configurar estilos
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        
        # Verificar dependencias al iniciar
        self.check_dependencies()
    
    def check_dependencies(self):
        """Verifica que todas las dependencias estén disponibles"""
        logging.info("Verificando dependencias...")
        success, _, error_msg = setup_tesseract()
        
        if not success:
            logging.error(f"Error de dependencias: {error_msg}")
            messagebox.showerror("OCR-MAD - Error", error_msg)
            self.select_btn.config(state=tk.DISABLED)
            self.convert_btn.config(state=tk.DISABLED)
            return False
        
        try:
            # Verificación adicional de PyMuPDF
            test_doc = fitz.open()
            test_doc.close()
            logging.info("PyMuPDF verificado correctamente")
        except Exception as e:
            error_msg = f"No se pudo verificar PyMuPDF: {str(e)}"
            logging.error(error_msg)
            messagebox.showerror("OCR-MAD - Error", error_msg)
            self.select_btn.config(state=tk.DISABLED)
            self.convert_btn.config(state=tk.DISABLED)
            return False
        
        logging.info(" Todas las dependencias verificadas correctamente")
        self.status_var.set(" Listo para procesar archivos")
        self.status_label.config(foreground='#27ae60')
        return True
    
    def select_file(self):
        """Selecciona un archivo para procesar"""
        file_path = filedialog.askopenfilename(
            title="Selecciona un PDF o una imagen",
            filetypes=[
                ("Archivos soportados", "*.pdf;*.png;*.jpg;*.jpeg;*.tiff;*.bmp"),
                ("PDF", "*.pdf"),
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.tiff;*.bmp")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"📄 {os.path.basename(file_path)}")
            self.convert_btn.config(state=tk.NORMAL)
            
            # Preparar ruta de salida
            base_name = os.path.splitext(file_path)[0]
            self.output_file = f"{base_name}_OCR.pdf"
            logging.info(f"Archivo seleccionado: {file_path}")
            logging.info(f"Archivo de salida: {self.output_file}")
    
    def update_progress(self, current, total, message):
        """Actualiza la barra de progreso y el estado"""
        progress = (current / total) * 100
        self.progress['value'] = progress
        self.status_var.set(f"{message} ({progress:.1f}%)")
        self.root.update()
    
    def start_ocr(self):
        """Inicia el proceso de OCR en un hilo separado"""
        if not self.selected_file:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo primero")
            return
        
        # Deshabilitar botones durante el procesamiento
        self.select_btn.config(state=tk.DISABLED)
        self.convert_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_var.set("Iniciando procesamiento...")
        self.status_label.config(foreground='#2980b9')
        self.root.update()
        
        # Ejecutar en hilo separado
        threading.Thread(target=self.process_file, daemon=True).start()
    
    def process_file(self):
        """Procesa el archivo seleccionado"""
        try:
            logging.info("Iniciando proceso de OCR en hilo separado")
            success = False
            
            if self.selected_file.lower().endswith(".pdf"):
                logging.info("Procesando como PDF")
                success = ocr_pdf(
                    self.selected_file, 
                    self.output_file, 
                    progress_callback=self.update_progress
                )
            else:
                logging.info("Procesando como imagen")
                success = ocr_image(
                    self.selected_file, 
                    self.output_file, 
                    progress_callback=self.update_progress
                )
            
            if success and os.path.exists(self.output_file):
                logging.info(" Proceso completado exitosamente")
                self.root.after(0, lambda: self.show_success())
            else:
                error_msg = "El archivo de salida no se generó correctamente"
                logging.error(f"ERROR:{error_msg}")
                self.root.after(0, lambda: self.show_error(error_msg))
                
        except Exception as e:
            error_msg = f"Error durante el procesamiento:\n{traceback.format_exc()}"
            logging.error(f"ERROR:Error crítico: {error_msg}")
            self.root.after(0, lambda: self.show_error(error_msg))
        finally:
            self.root.after(0, self.reset_ui)
    
    def show_success(self):
        """Muestra mensaje de éxito"""
        message = (
            " OCR completado exitosamente!\n\n"
            f"Archivo generado:\n{self.output_file}\n\n"
            f"Tamaño: {os.path.getsize(self.output_file) / 1024 / 1024:.2f} MB\n\n"
            "¿Quieres abrir la carpeta contenedora?"
        )
        
        if messagebox.askyesno("OCR-MAD - Éxito", message):
            folder_path = os.path.dirname(os.path.abspath(self.output_file))
            if platform.system() == "Windows":
                os.startfile(folder_path)
    
    def show_error(self, error_message):
        """Muestra mensaje de error detallado"""
        messagebox.showerror("OCR-MAD - Error", 
                            f"ERROR:Error durante el procesamiento:\n\n{error_message}\n\n"
                            f"Consulta el archivo de log para más detalles:\n{DEBUG_LOG}")
    
    def show_log(self):
        """Muestra el archivo de log"""
        log_path = os.path.abspath(DEBUG_LOG)
        if platform.system() == "Windows":
            os.startfile(log_path)
    
    def reset_ui(self):
        """Restaura la interfaz después de procesar"""
        self.select_btn.config(state=tk.NORMAL)
        if self.selected_file:
            self.convert_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        self.status_label.config(foreground='#27ae60')

# === FUNCIÓN PRINCIPAL ===
def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    
    # Establecer tema moderno
    style = ttk.Style()
    if "winnative" in style.theme_names():
        style.theme_use("winnative")
    
    # Crear aplicación
    app = OCRApplication(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    
    root.mainloop()

def on_closing(root):
    """Maneja el cierre de la aplicación"""
    if messagebox.askokcancel("Salir", "¿Seguro que quieres salir de OCR-MAD?"):
        root.destroy()
        logging.info("=== APLICACIÓN CERRADA ===")

if __name__ == "__main__":
    # Verificar que se está ejecutando en Windows
    if platform.system() != "Windows":
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Advertencia de compatibilidad",
            "Esta versión portable está diseñada para Windows.\n"
            f"Sistema detectado: {platform.system()}"
        )
        root.destroy()
        sys.exit(1)
    
    # Verificar dependencias críticas antes de iniciar
    try:
        import pymupdf
        import PIL
        import pytesseract
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error de dependencias",
            "Faltan dependencias críticas. Por favor reinstala la aplicación completa."
        )
        sys.exit(1)
    
    main()