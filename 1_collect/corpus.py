import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse
import re
from collections import deque
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextCorpusCollector:
    def __init__(self, output_dir="corpus", max_pages=100, delay=1):
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.delay = delay  # Задержка между запросами
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Создаем директорию для корпуса
        os.makedirs(output_dir, exist_ok=True)
    
    def is_georgian_text(self, text):
        """Проверяет, содержит ли текст грузинские символы"""
        georgian_chars = re.findall(r'[\u10A0-\u10FF]+', text)
        return len(georgian_chars) > 0
    
    def clean_text(self, text):
        """Очищает и нормализует текст"""
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Удаляем специальные символы, но сохраняем грузинские буквы и базовую пунктуацию
        text = re.sub(r'[^\u10A0-\u10FF\s\.\,\!\?\:\;\(\)\"\'\-\–\—]', '', text)
        return text.strip()
    
    def extract_text_from_html(self, html_content):
        """Извлекает чистый текст из HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Удаляем ненужные элементы
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Ищем основной контент
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article|post', re.I))
        
        if main_content:
            text_elements = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        else:
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        text_parts = []
        for element in text_elements:
            text = element.get_text().strip()
            if text and len(text) > 20:  # Минимальная длина текстового блока
                cleaned_text = self.clean_text(text)
                if cleaned_text and self.is_georgian_text(cleaned_text):
                    text_parts.append(cleaned_text)
        
        return '\n'.join(text_parts)
    
    def get_domain_links(self, html_content, base_url):
        """Извлекает все ссылки с того же домена"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            
            # Берем только ссылки с того же домена и игнорируем файлы
            if (parsed_url.netloc == base_domain and 
                not parsed_url.path.endswith(('.pdf', '.doc', '.docx', '.jpg', '.png', '.zip'))):
                links.append(full_url)
        
        return links
    
    def download_page(self, url):
        """Скачивает и обрабатывает одну страницу"""
        try:
            logger.info(f"Обрабатывается: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Проверяем, что это HTML страница
            if 'text/html' not in response.headers.get('content-type', ''):
                return None
            
            text_content = self.extract_text_from_html(response.content)
            
            if text_content and len(text_content) > 100:  # Минимальный размер текста
                return text_content
            else:
                logger.warning(f"Страница {url} содержит слишком мало текста")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка при загрузке {url}: {e}")
            return None
    
    def save_text(self, text, url, counter):
        """Сохраняет текст в файл"""
        filename = f"text_{counter:04d}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"URL: {url}\n")
            f.write(f"Собрано: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
            f.write(text)
            f.write("\n" + "=" * 50 + "\n")
        
        logger.info(f"Сохранен файл: {filename}")
        return filepath
    
    def collect_from_url(self, start_url):
        """Основная функция сбора корпуса с одного сайта"""
        queue = deque([start_url])
        collected_count = 0
        file_counter = 1
        
        while queue and collected_count < self.max_pages:
            url = queue.popleft()
            
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            
            # Скачиваем и обрабатываем страницу
            text_content = self.download_page(url)
            
            if text_content:
                # Сохраняем текст
                self.save_text(text_content, url, file_counter)
                collected_count += 1
                file_counter += 1
                
                # Если нужно больше страниц, получаем ссылки
                if collected_count < self.max_pages:
                    try:
                        response = self.session.get(url, timeout=10)
                        links = self.get_domain_links(response.content, url)
                        
                        # Добавляем новые ссылки в очередь
                        for link in links:
                            if link not in self.visited_urls and link not in queue:
                                queue.append(link)
                    except:
                        pass
            
            # Задержка между запросами
            time.sleep(self.delay)
        
        return collected_count
    
    def collect_from_multiple_urls(self, urls):
        """Собирает корпус с нескольких сайтов"""
        total_collected = 0
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Обрабатывается сайт {i}/{len(urls)}: {url}")
            collected = self.collect_from_url(url)
            total_collected += collected
            logger.info(f"Собрано страниц с этого сайта: {collected}")
            
            # Сбрасываем посещенные URL для нового сайта
            self.visited_urls.clear()
        
        return total_collected

def main():
    print("=== Сборщик корпуса грузинских текстов ===")
    print("Введите ссылки на сайты для сбора (по одной строке, пустая строка для завершения):")
    
    urls = []
    while True:
        url = input().strip()
        if not url:
            break
        if url.startswith(('http://', 'https://')):
            urls.append(url)
        else:
            print("Ошибка: ссылка должна начинаться с http:// или https://")
    
    if not urls:
        print("Не введено ни одной ссылки!")
        return
    
    # Настройки сбора
    max_pages = int(input("Максимальное количество страниц для сбора (по умолчанию 100): ") or "100")
    output_dir = input("Папка для сохранения (по умолчанию 'corpus'): ") or "corpus"
    delay = float(input("Задержка между запросами в секундах (по умолчанию 1): ") or "1")
    
    # Создаем сборщик
    collector = TextCorpusCollector(
        output_dir=output_dir,
        max_pages=max_pages,
        delay=delay
    )
    
    print(f"\nНачинаем сбор с {len(urls)} сайтов...")
    print(f"Будет собрано до {max_pages} страниц на сайт")
    print(f"Тексты будут сохранены в папку: {output_dir}")
    print("=" * 50)
    
    try:
        total_collected = collector.collect_from_multiple_urls(urls)
        
        print("\n" + "=" * 50)
        print(f"Сбор завершен!")
        print(f"Всего собрано текстовых файлов: {total_collected}")
        print(f"Файлы сохранены в папке: {os.path.abspath(output_dir)}")
        
    except KeyboardInterrupt:
        print("\nСбор прерван пользователем")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")

# Дополнительная утилита для анализа собранного корпуса
def analyze_corpus(corpus_dir):
    """Анализирует собранный корпус"""
    total_files = 0
    total_words = 0
    total_chars = 0
    
    print(f"\nАнализ корпуса в папке '{corpus_dir}':")
    
    for filename in os.listdir(corpus_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(corpus_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Считаем только грузинские слова
                    georgian_words = re.findall(r'[\u10A0-\u10FF]+', content)
                    total_files += 1
                    total_words += len(georgian_words)
                    total_chars += len(content)
            except Exception as e:
                print(f"Ошибка при чтении {filename}: {e}")
    
    print(f"Всего файлов: {total_files}")
    print(f"Всего грузинских слов: {total_words}")
    print(f"Общий объем текста: {total_chars} символов")
    
    if total_files > 0:
        print(f"Среднее количество слов на файл: {total_words/total_files:.1f}")

if __name__ == "__main__":
    main()
    
    # После завершения сбора можно проанализировать корпус
    corpus_dir = "corpus"
    if os.path.exists(corpus_dir) and os.listdir(corpus_dir):
        analyze_corpus(corpus_dir)