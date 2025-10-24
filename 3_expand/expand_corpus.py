# expand_corpus.py
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

def download_georgian_texts():
    """Скачивание дополнительных грузинских текстов"""
    urls = [
        "https://www.ambebi.ge",
        "https://netgazeti.ge", 
        "https://on.ge",
        "https://www.radiotavisupleba.ge"
    ]
    
    corpus_dir = Path("1.Collect a text corpus/corpus")
    corpus_dir.mkdir(parents=True, exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        try:
            print(f"Скачивание {i}/{len(urls)}: {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем текст
            text = soup.get_text()
            # Фильтруем только грузинский текст
            georgian_text = ' '.join([word for word in text.split() 
                                    if any('\u10A0' <= char <= '\u10FF' for char in word)])
            
            if georgian_text:
                with open(corpus_dir / f"web_{i}.txt", 'w', encoding='utf-8') as f:
                    f.write(georgian_text)
                print(f"Сохранено: web_{i}.txt")
            
            time.sleep(2)  # Пауза между запросами
            
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

if __name__ == "__main__":
    download_georgian_texts()