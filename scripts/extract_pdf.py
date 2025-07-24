from pdfminer.pdfpage import PDFPage
from pdfminer.high_level import extract_text
import re
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

model_id = "mrm8488/bert2bert_shared-spanish-finetuned-summarization"
model = AutoModelForSeq2SeqLM.from_pretrained(
    model_id,
    device_map=None,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=False
)
print(f"Modelo cargado en dispositivo: {next(model.parameters()).device}")
tokenizer = AutoTokenizer.from_pretrained(model_id)
summarizer = pipeline(
    "summarization",
    model=model,
    tokenizer=tokenizer,
    device=-1
)
def extract_text_from_pdf(pdf_path):
    full_text = ""
    with open(pdf_path, "rb") as f:
        total_pages = sum(1 for _ in PDFPage.get_pages(f))
        f.seek(0)
        for i in range(total_pages):
            text = extract_text(f, page_numbers=[i])
            print(f"Página {i + 1} - longitud: {len(text)}")
            full_text += text
    print(f"Texto total extraído (len={len(full_text)}):\n{full_text[:500]}")
    return full_text
def summarize_long_text(texto, max_tokens_per_chunk=512):
    tokens = summarizer.tokenizer(texto, return_tensors="pt", truncation=False)["input_ids"][0]
    num_tokens = len(tokens)
    print(f"[DEBUG] Total de tokens: {num_tokens}")
    chunks = [tokens[i:i + max_tokens_per_chunk] for i in range(0, num_tokens, max_tokens_per_chunk)]
    resumenes = []
    for i, chunk in enumerate(chunks):
        if len(chunk) == 0:
            print(f"Chunk {i + 1} está vacío. Se salta.")
            continue
        input_text = summarizer.tokenizer.decode(chunk, skip_special_tokens=True).strip()
        input_text = limpiar_texto(input_text)
        if not input_text:
            print(f"Chunk {i + 1} vacío tras limpiar. Se omite.")
            continue        
        print(f"[DEBUG] Texto limpio para resumen del bloque {i + 1}:\n{input_text[:500]}")
        try:
            resumen = summarizer(
                input_text,
                max_length=150,
                min_length=50,
                truncation=True,
                do_sample=False
            )[0]['summary_text']
            print(f"[DEBUG] Resumen bloque {i + 1}:\n{resumen}")
            resumenes.append(resumen)
        except Exception as e:
            print(f"Error al resumir bloque {i + 1}: {e}")

    resumen_final = " ".join(resumenes)
    print(f"\nResumen completo generado ({len(resumenes)} partes):\n{resumen_final[:500]}...\n")
    return resumen_final
def limpiar_texto(texto):
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[■�●•]+', '', texto)
    return texto.strip()
