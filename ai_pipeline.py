import os
from scripts.extract_pdf import extract_text_from_pdf, summarize_long_text
from scripts.tts import Narrador
import re

def procesar_pdf_con_ia(input_pdf_path, output_dir="output"):
    output_texto = os.path.join(output_dir, "texto.txt")
    output_audio = os.path.join(output_dir, "narracion.wav")
    os.makedirs(output_dir, exist_ok=True)
    print("[INFO] Extrayendo texto del PDF...")
    texto = extract_text_from_pdf(input_pdf_path)
    if not texto.strip():
        raise ValueError("No se pudo extraer texto del PDF o está vacío")
    print("\n[INFO] Guardando texto...")
    with open(output_texto, "w", encoding="utf-8") as f:
        f.write(texto)
    print("\n[INFO] Generando narración de audio...")
    if not texto.strip():
        raise ValueError("El texto está vacío, no se puede generar audio.")
    narrador = Narrador()
    ruta_audio = narrador.narrar_texto(output_texto, output_audio)
    print(f"[INFO] Narración guardada en: {ruta_audio}")
    print("\nProceso completado exitosamente.")
    return {
        "texto": texto,
        "audio_path": output_audio
    }