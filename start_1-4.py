# web_interface.py
#!/usr/bin/env python3
"""
Веб-интерфейс для грузинского спеллчекера
"""

from flask import Flask, render_template, request, jsonify
import pickle
from collections import Counter
import re
import os
from pathlib import Path

app = Flask(__name__)

class WebSpellChecker:
    def __init__(self):
        self.vocabulary = set()
        self.word_freq = Counter()
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Загружает модель или создает базовую"""
        model_path = "spellchecker_model.pkl"
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                self.vocabulary = set(data['vocabulary'])
                self.word_freq = Counter(data['word_freq'])
                print(f"✅ Модель загружена. Слов: {len(self.vocabulary)}")
                return
            except Exception as e:
                print(f"❌ Ошибка загрузки модели: {e}")
        
        # Создаем базовую модель
        print("📝 Создаем базовую модель...")
        self.vocabulary = {
            'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
            'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი',
            'ძალიან', 'ლამაზი', 'ქალაქი', 'ტურისტი', 'წერს', 'კოდი',
            'სალამი', 'ბარი', 'ჰეი', 'მაშინ', 'შემდეგ', 'ადრე', 'გვიან',
            'დიდი', 'პატარა', 'ახალი', 'ძველი', 'სწრაფი', 'ნელი', 'ცხელი',
            'ცივი', 'თეთრი', 'შავი', 'წითელი', 'მწვანე', 'ლურჯი', 'ყვითელი',
            'სტუდენტი', 'მასწავლებელი', 'სკოლა', 'უნივერსიტეტი', 'წიგნი',
            'ფული', 'სამუშაო', 'ოჯახი', 'მეგობარი', 'სიყვარული', 'ცხოვრება'
        }
        self.word_freq = Counter(self.vocabulary)
        
        # Сохраняем модель
        self.save_model(model_path)
    
    def save_model(self, filename):
        """Сохраняет модель"""
        with open(filename, 'wb') as f:
            pickle.dump({
                'vocabulary': list(self.vocabulary),
                'word_freq': dict(self.word_freq)
            }, f)
        print(f"💾 Модель сохранена: {filename}")
    
    def levenshtein_distance(self, s1, s2):
        """Расстояние Левенштейна"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    
    def is_correct(self, word):
        """Проверяет правильность слова"""
        return word in self.vocabulary
    
    def suggest_corrections(self, word, max_suggestions=5):
        """Предлагает исправления"""
        if self.is_correct(word):
            return [word]
        
        candidates = []
        for candidate in self.vocabulary:
            distance = self.levenshtein_distance(word, candidate)
            if distance <= 2:
                candidates.append((candidate, distance))
        
        # Сортируем по расстоянию и частоте
        candidates.sort(key=lambda x: (x[1], -self.word_freq.get(x[0], 0)))
        return [candidate for candidate, distance in candidates[:max_suggestions]]
    
    def check_text(self, text):
        """Проверяет текст"""
        # Токенизация грузинского текста
        words = re.findall(r'[\u10A0-\u10FF]+', text)
        errors = []
        
        for word in words:
            if len(word) > 1 and not self.is_correct(word):  # Игнорируем слишком короткие слова
                suggestions = self.suggest_corrections(word)
                errors.append({
                    'word': word,
                    'suggestions': suggestions,
                    'start_pos': text.find(word),
                    'end_pos': text.find(word) + len(word)
                })
        
        return errors

# Создаем экземпляр спеллчекера
spell_checker = WebSpellChecker()

@app.route('/')
def index():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html lang="ka">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🇬🇪 Грузинский Спеллчекер</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .content {
                padding: 30px;
            }
            
            .textarea-container {
                margin-bottom: 20px;
            }
            
            textarea {
                width: 100%;
                height: 200px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                resize: vertical;
                transition: border-color 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .button-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .check-btn {
                background: #27ae60;
                color: white;
                flex: 2;
            }
            
            .check-btn:hover {
                background: #219a52;
                transform: translateY(-2px);
            }
            
            .clear-btn {
                background: #e74c3c;
                color: white;
                flex: 1;
            }
            
            .clear-btn:hover {
                background: #c0392b;
                transform: translateY(-2px);
            }
            
            .results {
                margin-top: 20px;
            }
            
            .error-item {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                animation: fadeIn 0.5s;
            }
            
            .error-word {
                font-weight: bold;
                color: #e74c3c;
                font-size: 1.1em;
            }
            
            .suggestions {
                margin-top: 8px;
            }
            
            .suggestion {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 5px 12px;
                margin: 2px;
                border-radius: 20px;
                font-size: 0.9em;
                cursor: pointer;
                transition: background 0.3s;
            }
            
            .suggestion:hover {
                background: #2980b9;
            }
            
            .no-errors {
                text-align: center;
                padding: 30px;
                color: #27ae60;
                font-size: 1.2em;
            }
            
            .stats {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                text-align: center;
                font-size: 0.9em;
                color: #6c757d;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .highlight {
                background-color: #ffeb3b;
                padding: 2px 4px;
                border-radius: 3px;
            }
            
            @media (max-width: 600px) {
                .container {
                    margin: 10px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .button-group {
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🇬🇪 ქართული მართლწერის შემოწმება</h1>
                <p>გადაამოწმეთ თქვენი ქართული ტექსტი</p>
            </div>
            
            <div class="content">
                <div class="textarea-container">
                    <textarea 
                        id="textInput" 
                        placeholder="ჩაწერეთ ქართული ტექსტი აქ... 
მაგალითი: გამარჯაბა როგოთ ხართ დღეს კარგი ამინდია"
                    ></textarea>
                </div>
                
                <div class="button-group">
                    <button class="check-btn" onclick="checkText()">
                        🔍 შემოწმება
                    </button>
                    <button class="clear-btn" onclick="clearText()">
                        🗑️ გასუფთავება
                    </button>
                </div>
                
                <div id="results" class="results">
                    <div class="no-errors" id="noErrors" style="display: none;">
                        ✅ ტექსტში შეცდომები არ არის!
                    </div>
                </div>
                
                <div class="stats">
                    სისტემა შეიცავს <strong id="wordCount">""" + str(len(spell_checker.vocabulary)) + """</strong> სიტყვას
                </div>
            </div>
        </div>

        <script>
            let originalText = '';
            
            function checkText() {
                const text = document.getElementById('textInput').value;
                originalText = text;
                
                if (!text.trim()) {
                    alert('გთხოვთ, ჩაწერეთ ტექსტი!');
                    return;
                }
                
                // Показываем загрузку
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #667eea;">⏳ მიმდინარეობს შემოწმება...</div>';
                
                fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                })
                .then(response => response.json())
                .then(data => {
                    displayResults(data.errors, text);
                })
                .catch(error => {
                    console.error('Error:', error);
                    resultsDiv.innerHTML = '<div style="color: red; text-align: center;">❌ შეცდომა მოხდა შემოწმებისას</div>';
                });
            }
            
            function displayResults(errors, originalText) {
                const resultsDiv = document.getElementById('results');
                const noErrorsDiv = document.getElementById('noErrors');
                
                if (errors.length === 0) {
                    noErrorsDiv.style.display = 'block';
                    resultsDiv.innerHTML = '';
                    return;
                }
                
                noErrorsDiv.style.display = 'none';
                
                let html = '<h3 style="margin-bottom: 15px; color: #2c3e50;">📋 ნაპოვნი შეცდომები:</h3>';
                
                errors.forEach(error => {
                    html += `
                        <div class="error-item">
                            <div class="error-word">"${error.word}"</div>
                            <div class="suggestions">
                                <strong>შემოთავაზებები:</strong> 
                    `;
                    
                    error.suggestions.forEach(suggestion => {
                        html += `<span class="suggestion" onclick="replaceWord('${error.word}', '${suggestion}')">${suggestion}</span>`;
                    });
                    
                    html += `
                            </div>
                        </div>
                    `;
                });
                
                resultsDiv.innerHTML = html;
            }
            
            function replaceWord(oldWord, newWord) {
                const textarea = document.getElementById('textInput');
                let text = originalText;
                
                // Заменяем только первое вхождение
                text = text.replace(oldWord, newWord);
                textarea.value = text;
                originalText = text;
                
                // Перепроверяем текст
                checkText();
            }
            
            function clearText() {
                document.getElementById('textInput').value = '';
                document.getElementById('results').innerHTML = '';
                document.getElementById('noErrors').style.display = 'none';
                originalText = '';
            }
            
            // Автоматическая проверка при вводе (с задержкой)
            let checkTimeout;
            document.getElementById('textInput').addEventListener('input', function() {
                clearTimeout(checkTimeout);
                checkTimeout = setTimeout(() => {
                    if (this.value.length > 10) {
                        checkText();
                    }
                }, 1000);
            });
            
            // Загружаем пример текста при загрузке страницы
            window.addEventListener('load', function() {
                const exampleText = "გამარჯაბა როგოთ ხართ დღეს კარგი ამინდია თბილისი ლამაზი ქალაქია";
                document.getElementById('textInput').value = exampleText;
                originalText = exampleText;
            });
        </script>
    </body>
    </html>
    """

@app.route('/check', methods=['POST'])
def check_text():
    """API endpoint для проверки текста"""
    data = request.get_json()
    text = data.get('text', '')
    
    errors = spell_checker.check_text(text)
    
    return jsonify({
        'errors': errors,
        'total_errors': len(errors),
        'text_length': len(text)
    })

@app.route('/add_word', methods=['POST'])
def add_word():
    """Добавление нового слова в словарь"""
    data = request.get_json()
    word = data.get('word', '')
    
    if word and all('\u10A0' <= char <= '\u10FF' for char in word):
        spell_checker.vocabulary.add(word)
        spell_checker.word_freq[word] = spell_checker.word_freq.get(word, 0) + 1
        spell_checker.save_model("spellchecker_model.pkl")
        
        return jsonify({
            'success': True,
            'message': f'სიტყვა "{word}" დაემატა ლექსიკონს',
            'total_words': len(spell_checker.vocabulary)
        })
    
    return jsonify({
        'success': False,
        'message': 'არასწორი სიტყვა'
    }), 400

@app.route('/stats')
def get_stats():
    """Статистика словаря"""
    return jsonify({
        'total_words': len(spell_checker.vocabulary),
        'most_common': dict(spell_checker.word_freq.most_common(10))
    })

if __name__ == '__main__':
    print("🚀 Запуск веб-интерфейса грузинского спеллчекера...")
    print("📍 Адрес: http://localhost:5000")
    print("📍 Адрес для сети: http://0.0.0.0:5000")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)