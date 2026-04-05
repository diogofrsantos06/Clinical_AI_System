import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_clinical_text(text):
    """
    Limpa o texto extraído para otimizar o processamento da LLM.
    """
    # 1. Substitui múltiplos espaços por um único espaço
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 2. Substitui múltiplas quebras de linha por apenas duas (preserva parágrafos)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # 3. Remove espaços no início e fim de cada linha
    text = "\n".join([line.strip() for line in text.split('\n')])

    text = re.sub(r'([^a-zA-Z0-9\s])\1+', r'\1', text)    
    
    return text.strip()


def extract_full_pdf_text(pdf_path, debug=True):
    """
    Extrai o texto integral do PDF, aplica OCR se necessário e limpa o conteúdo.
    """
    full_text = ""

    try:
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            width, height = page.rect.width, page.rect.height
            # Mantemos o crop mas podes ajustar se necessário
            interest_area = fitz.Rect(0, height * 0.01, width, height * 0.99)
            
            page_text = page.get_text("text", clip=interest_area, sort=True)

            # Se não houver texto, dispara OCR
            if not page_text.strip():
                if debug: print(f"Página {page_num+1}: Iniciando OCR...")
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_text = pytesseract.image_to_string(img, lang='por')
            
            if page_text:
                full_text += page_text + "\n"

        doc.close()

        # APLICAR LIMPEZA
        full_text = clean_clinical_text(full_text)

        if debug:
            print("\n" + "="*20 + " TEXTO INTEGRAL LIMPO " + "="*20)
            print(full_text)
            print("="*60 + "\n")

    except Exception as e:
        print(f"Erro na extração: {e}")

    return full_text

'''
if __name__ == "__main__":
    caminho_teste = "C:\\Users\\Utilizador\\Desktop\\01.pdf" 
    texto_final, texto_inicial = extract_full_pdf_text(caminho_teste)
    print(f"Processamento concluído. Tamanho inicial: {len(texto_inicial)} Tamanho do texto: {len(texto_final)} caracteres.")
'''