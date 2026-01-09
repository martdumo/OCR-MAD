# OCR-MAD Portable

Una herramienta simple y portable para Windows que le mete OCR a tus PDFs e imágenes  
y te devuelve todo bonito con texto seleccionable (¡por fin!).

![Vista principal de OCR-MAD](/2026-01-09%2011_10_37-.png)

Funciona con: PDF, JPG, PNG, TIFF, BMP  
Idiomas: Español e Inglés

## Lo bueno que tiene (o eso intento)

- 100% portable → lo tirás en cualquier carpeta y anda
- No pide instalación ni permisos de administrador
- Interfaz sencilla (no te vas a perder)
- Procesa en segundo plano → no se congela la ventana
- Te muestra una barra de progreso para que sepas que no se colgó
- Guarda un logcito cuando algo sale mal (ocr_mad_debug.log en el escritorio)
- Todo incluido → no tenés que instalar nada más

## ¿Qué necesitás para que ande?

- Windows 10 o 11 (64 bits)
- Unos 500 MB libres
- Ideal 2 GB de RAM si vas a meterle PDFs muy gordos

## Cómo usarlo (paso a paso tranqui)

1. Bajate el último ZIP desde [Releases](https://github.com/martdumo/OCR-MAD/releases)
2. Descomprimilo donde quieras (escritorio, descargas, donde sea)
3. Hacé doble clic en `OCR-MAD.exe`
4. Arrastrá o elegí el archivo que querés procesar
5. Dale al botón grande que dice **CONVERTIR AHORA**
6. Esperá un ratito... y listo, el PDF con texto seleccionable aparece en la misma carpeta

## Cosas que pueden salir mal (y cómo arreglarlas)

- **No encuentra los idiomas** → chequeá que estén spa.traineddata y eng.traineddata dentro de la carpeta tesseract/tessdata
- **Faltan DLLs y se queja** → probablemente algo falló al compilar, intentá con la versión que está en releases
- **La ventana no se cierra** → usá la × de windows de siempre
- **Algo falla y no sabés por qué** → mirá el archivo ocr_mad_debug.log en tu escritorio

## Para los que quieren meter mano (o sea... yo mismo)

Estructura que usa:
```
OCR-MAD/
├── tesseract/
│   ├── tesseract.exe
│   └── tessdata/
│       ├── spa.traineddata
│       └── eng.traineddata
├── OCR_MAD.py
└── requirements.txt
```

Dependencias (muy pocas):

pymupdf==1.26.6
Pillow==12.0.0
pytesseract==0.3.13


Y si querés compilar tu propio .exe (con PyInstaller):
Es un comando larguísimo y feo, mejor usar el de releases jajaja
Pero si insistís, está en la versión anterior de este readme 😅
Licencia
MIT – hacé lo que quieras, pero dejá el crédito si te parece copado
¡Espero que les sirva y no tengan que pelear mucho con el OCR! 🫡
Cualquier cosa, tiren un issue (soy lento respondiendo pero eventualmente contesto)
Proyecto en Python • La carpeta tesseract contiene instaladores/binarios del motor OCR Tesseract y no forma parte del código principal del proyecto
