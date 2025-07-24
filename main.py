import requests
from config import API_ENDPOINT, TARGET_URLS, LOCAL_PDF_PATH
from auth import get_auth_header
from ai_pipeline import procesar_pdf_con_ia

def get_pdf_url_from_wp():
    urls_str = ",".join(TARGET_URLS)
    full_url = f"{API_ENDPOINT}?urls={urls_str}"
    print(f"Solicitando contenido a: {full_url}")
    headers = get_auth_header()
    response = requests.get(full_url, headers=headers)
    if response.status_code != 200:
        print("Error al obtener el PDF:", response.text)
        return None
    data = response.json()
    return data.get("pdf_url")

def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(LOCAL_PDF_PATH, 'wb') as f:
            f.write(response.content)
        print(f"PDF descargado correctamente en: {LOCAL_PDF_PATH}")
        return True
    else:
        print("Error al descargar el PDF:", response.status_code)
        return False

def main():
    pdf_url = get_pdf_url_from_wp()
    if pdf_url:
        print(f"URL del PDF recibido: {pdf_url}")
        if download_pdf(pdf_url):
            print("Listo para procesar el PDF con IA.")
            procesamiento = procesar_pdf_con_ia(LOCAL_PDF_PATH)            
            print("Texto procesamiento:", procesamiento["texto"])
            print("Audio procesamiento en:", procesamiento["audio_path"])
            #print("Video final en:", procesamiento["video_path"])
        else:
            print("Fallo al descargar el PDF.")
    else:
        print("No se pudo obtener la URL del PDF.")

if __name__ == "__main__":
    main()
