from TTS.api import TTS
import torch
import soundfile as sf
import numpy as np
import os 
import numbers

import collections
from TTS.utils.radam import RAdam

torch.serialization.add_safe_globals([RAdam, collections.defaultdict, dict])

class Narrador:
    def __init__(self, modelo="tts_models/es/mai/tacotron2-DDC", speaker=None, progress_bar=True, sample_rate=22050, usar_gpu=False):
        print(f"[INFO] Inicializando modelo TTS: {modelo} | GPU: {usar_gpu}")
        try:
            self.tts = TTS(model_name=modelo, progress_bar=progress_bar, gpu=usar_gpu)
            print(f"Voces disponibles: {self.tts.speakers}")  # <-- mover esta línea acá
            self.modelo_multilingue = "multi" in modelo or "your_tts" in modelo
            self.modelo_multispeaker = bool(self.tts.speakers)
            self.speaker = speaker or (self.tts.speakers[0] if self.modelo_multispeaker else None)

            print("[IDIOMAS]:", self.tts.languages)
            print("[VOCES]:", self.tts.speakers)
            print("[INFO] Modelo TTS cargado correctamente.")
            if self.modelo_multispeaker:
                print(f"[INFO] Voces disponibles: {self.tts.speakers}")
                print(f"[INFO] Voz seleccionada: {self.speaker}")

        except Exception as e:
            msg = f"[ERROR] Error al cargar el modelo TTS: {e}"
            print(msg)
            raise RuntimeError(msg)

        self.errores = []
        self.sample_rate = sample_rate
        self.device = "cuda" if usar_gpu and torch.cuda.is_available() else "cpu"   

    def narrar_texto(self, ruta_texto, ruta_guardado=None):
        print(f"[DEBUG] Ruta de texto a sintetizar: '{ruta_texto}'")
        with open(ruta_texto, "r", encoding="utf-8") as f:
            contenido = f.read()
        frases = contenido.split(".")  # o mejor usa una librería de segmentación de oraciones
        
        frases_filtradas = unir_frases_cortas(frases, min_len=5)  # evitar frases muy cortas
        
        audio_total = []
        for idx, frase in enumerate(frases_filtradas):
            frase = frase.strip()
            if not frase:
                continue
            try:
                print(f"[DEBUG] Sintetizando frase {idx+1}/{len(frases_filtradas)}: {frase}")
                if self.modelo_multispeaker and self.speaker:
                    audio_raw = self.tts.tts(text=frase, speaker=self.speaker)
                else:
                    audio_raw = self.tts.tts(text=frase)

                # Procesar audio_raw como antes (convertir a np.array)
                # Aquí asumo que es lista de floats
                if isinstance(audio_raw, list):
                    audio = np.array(audio_raw, dtype=np.float32)
                else:
                    raise TypeError(f"Tipo de audio no soportado: {type(audio_raw)}")

                audio_total.append(audio)
            except Exception as e:
                print(f"[ERROR] Error sintetizando frase '{frase}': {e}")
                continue

        if not audio_total:
            print("[ERROR] No se generó audio para ninguna frase.")
            return None

        audio_final = np.concatenate(audio_total)
        max_val = np.max(np.abs(audio_final))
        if max_val > 0:
            audio_final = audio_final / max_val
        else:
            print("[WARNING] Audio final con valor máximo cero o negativo.")

        if ruta_guardado:
            sf.write(ruta_guardado, audio_final, self.sample_rate)
            print(f"[INFO] Audio guardado en: {ruta_guardado}")

        return audio_final

def unir_frases_cortas(frases, min_len=10):
    frases_limpias = []
    buffer = ""
    for frase in frases:
        if len(frase.split()) < min_len:
            buffer += " " + frase
        else:
            if buffer:
                frases_limpias.append(buffer.strip())
                buffer = ""
            frases_limpias.append(frase)
    if buffer:
        frases_limpias.append(buffer.strip())
    return frases_limpias

