import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from transformers import pipeline

# Configuración inicial
SOURCES = [
    "https://www.argentina.gob.ar/transparencia",  # Portal público de transparencia
    "https://www.lanacion.com.ar/politica/"  # Ejemplo de medio (verifica términos)
]
OUTPUT_DIR = "docs"  # Carpeta para GitHub Pages
SENTIMENT_ANALYZER = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def scrape_news(url):
    """Extrae titulares y resúmenes de una página pública."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        articles = []
        for item in soup.find_all("h3")[:5]:  # Limitamos a 5 titulares
            title = item.get_text().strip()
            summary = item.find_next("p")
            summary_text = summary.get_text().strip() if summary else "Sin resumen disponible."
            articles.append({"title": title, "summary": summary_text})
        return articles
    except Exception as e:
        print(f"Error al scrapear {url}: {e}")
        return []

def analyze_content(text):
    """Genera un comentario crítico y reflexivo con IA."""
    sentiment = SENTIMENT_ANALYZER(text)[0]
    label = sentiment["label"]
    
    if label == "NEGATIVE":
        comment = (
            f"Esto es indignante: {text[:100]}... ¿Cómo es posible que sigamos tolerando esta opacidad? "
            "Es hora de exigir respuestas claras y que los corruptos rindan cuentas."
        )
    else:
        comment = (
            f"Una luz de esperanza: {text[:100]}... Pero, ¿es suficiente? Reflexionemos: ¿qué falta para que "
            "esto realmente cambie la vida de nuestra provincia?"
        )
    return comment

def generate_note(articles):
    """Genera una nota en markdown para GitHub Pages."""
    date = datetime.now().strftime("%Y-%m-%d")
    note_content = f"# Diario Crítico - {date}\n\n"
    note_content += "## Reflexiones del Día\n\n"
    
    for article in articles:
        title = article["title"]
        summary = article["summary"]
        comment = analyze_content(summary)
        note_content += f"### {title}\n\n"
        note_content += f"**Resumen**: {summary}\n\n"
        note_content += f"**Reflexión**: {comment}\n\n"
    
    note_content += (
        "\n---\n"
        "Este diario es para vos, para que no te calles. ¡Comparte y despertemos juntos!\n"
        "Apoyanos en Cafecito: [Dona aquí](https://cafecito.app/diariocritico)"
    )
    return note_content

def save_note(content):
    """Guarda la nota en la carpeta docs para GitHub Pages."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    date = datetime.now().strftime("%Y%m%d")
    file_path = os.path.join(OUTPUT_DIR, f"nota_{date}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Nota guardada en: {file_path}")

def main():
    """Función principal."""
    all_articles = []
    for url in SOURCES:
        articles = scrape_news(url)
        all_articles.extend(articles)
    
    if all_articles:
        note_content = generate_note(all_articles)
        save_note(note_content)
    else:
        print("No se encontraron artículos para procesar.")

if __name__ == "__main__":
    main()