# OCR-MAD Portable

![Windows](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

OCR-MAD es una aplicación portátil para Windows que convierte documentos PDF e imágenes (JPG, PNG, TIFF, BMP) a PDF con texto seleccionable utilizando reconocimiento óptico de caracteres (OCR).

## 🌟 Características

- **Totalmente portable**: No requiere instalación ni permisos de administrador
- **Interfaz gráfica intuitiva**: Fácil de usar para cualquier usuario
- **Soporte múltiples formatos**: PDF, JPG/JPEG, PNG, TIFF, BMP
- **Idiomas soportados**: Español e Inglés
- **Procesamiento en segundo plano**: No bloquea la interfaz durante el OCR
- **Barra de progreso**: Muestra el estado del procesamiento en tiempo real
- **Logging detallado**: Registra todos los errores para diagnóstico
- **Sin dependencias externas**: Incluye todas las bibliotecas necesarias en el ejecutable

## 📦 Requisitos del Sistema

- Windows 10/11 (64-bit)
- 500 MB de espacio en disco
- 2 GB de RAM recomendados para documentos grandes

## 🚀 Cómo Usar

1. **Descargar el ejecutable**: Obtén la última versión desde [Releases](https://github.com/martdumo/OCR-MAD/releases)
2. **Extraer la carpeta**: Descomprime el archivo ZIP en cualquier ubicación
3. **Ejecutar la aplicación**: Haz doble clic en `OCR-MAD.exe`
4. **Seleccionar archivo**: Elige un PDF o imagen para procesar
5. **Convertir**: Haz clic en "CONVERTIR AHORA"
6. **Obtener resultado**: El archivo PDF con OCR se guardará en la misma carpeta

## 🛠️ Para Desarrolladores

### Instalación de dependencias
```bash
pip install -r requirements.txt
profile
Qwen3-Max
4:45 pm
Pensamiento y búsqueda completados
· 81,920 tokens presupuesto




📁 requirements.txt
txt


1
2
3
pymupdf==1.26.6
Pillow==12.0.0
pytesseract==0.3.13
📄 README.md
markdown


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
# OCR-MAD Portable

![Windows](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.13+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

OCR-MAD es una aplicación portátil para Windows que convierte documentos PDF e imágenes (JPG, PNG, TIFF, BMP) a PDF con texto seleccionable utilizando reconocimiento óptico de caracteres (OCR).

## 🌟 Características

- **Totalmente portable**: No requiere instalación ni permisos de administrador
- **Interfaz gráfica intuitiva**: Fácil de usar para cualquier usuario
- **Soporte múltiples formatos**: PDF, JPG/JPEG, PNG, TIFF, BMP
- **Idiomas soportados**: Español e Inglés
- **Procesamiento en segundo plano**: No bloquea la interfaz durante el OCR
- **Barra de progreso**: Muestra el estado del procesamiento en tiempo real
- **Logging detallado**: Registra todos los errores para diagnóstico
- **Sin dependencias externas**: Incluye todas las bibliotecas necesarias en el ejecutable

## 📦 Requisitos del Sistema

- Windows 10/11 (64-bit)
- 500 MB de espacio en disco
- 2 GB de RAM recomendados para documentos grandes

## 🚀 Cómo Usar

1. **Descargar el ejecutable**: Obtén la última versión desde [Releases](https://github.com/tu-usuario/OCR-MAD/releases)
2. **Extraer la carpeta**: Descomprime el archivo ZIP en cualquier ubicación
3. **Ejecutar la aplicación**: Haz doble clic en `OCR-MAD.exe`
4. **Seleccionar archivo**: Elige un PDF o imagen para procesar
5. **Convertir**: Haz clic en "CONVERTIR AHORA"
6. **Obtener resultado**: El archivo PDF con OCR se guardará en la misma carpeta

## 🛠️ Para Desarrolladores

### Instalación de dependencias
```bash
pip install -r requirements.txt


Estructura de carpetas requerida


OCR-MAD/
├── tesseract/
│   ├── tesseract.exe
│   └── tessdata/
│       ├── spa.traineddata
│       └── eng.traineddata
├── OCR_MAD.py
├── requirements.txt
└── README.md

Compilación a ejecutable portable
pyinstaller --onefile --windowed --clean `
--add-binary "tesseract/tesseract.exe;tesseract" `
--add-binary "tesseract/tessdata/spa.traineddata;tesseract/tessdata" `
--add-binary "tesseract/tessdata/eng.traineddata;tesseract/tessdata" `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\Lib\site-packages\pymupdf\*.dll;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\Lib\site-packages\PIL\_imaging.cp313-win_amd64.pyd;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\Lib\site-packages\PIL\_imagingtk.cp313-win_amd64.pyd;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\Lib\site-packages\PIL\_imagingmath.cp313-win_amd64.pyd;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\Lib\site-packages\PIL\_imagingmorph.cp313-win_amd64.pyd;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\vcruntime140.dll;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\vcruntime140_1.dll;." `
--add-binary "$env:LOCALAPPDATA\Programs\Python\Python313\python313.dll;." `
--hidden-import pymupdf `
--hidden-import PIL `
--hidden-import pytesseract `
--hidden-import tkinter `
OCR_MAD.py


📥 Descarga de Tesseract
Para que la aplicación funcione, necesitas los siguientes archivos de Tesseract:

tesseract.exe: Descargar desde UB-Mannheim
Archivos de idioma:
spa.traineddata
eng.traineddata
🐛 Solución de Problemas
Problemas comunes y soluciones:
No se encuentran archivos de idioma
Verifica que los archivos
spa.traineddata
y
eng.traineddata
estén en la carpeta
tesseract/tessdata
Error de DLL faltante
Asegúrate de haber copiado todas las DLLs necesarias durante la compilación
La aplicación no se cierra
Usa el botón de cerrar ventana estándar de Windows
Botones no visibles
Verifica que estás ejecutando la versión compilada con todas las dependencias

Archivo de log
Si la aplicación falla, consulta el archivo ocr_mad_debug.log en tu escritorio para ver los detalles del error.

🤝 Contribuir
¡Las contribuciones son bienvenidas! Por favor abre un issue o pull request para:

Correcciones de errores
Mejoras en la interfaz de usuario
Soporte para nuevos formatos de archivo
Optimización de rendimiento
📄 Licencia
Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

🙏 Agradecimientos
PyMuPDF - Procesamiento de PDF
Pillow - Manipulación de imágenes
Tesseract OCR - Motor de reconocimiento de texto
PyInstaller - Creación de ejecutables portables


## ¡Feliz reconocimiento de texto! 🚀