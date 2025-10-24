# web_interface.py
import os
import sys
import pickle
import re
from pathlib import Path
from collections import Counter, defaultdict
from flask import Flask, request, jsonify, render_template

# Настройка путей
current_dir = Path(__file__).parent
project_root = current_dir.parent

# Пути к моделям согласно новой структуре
possible_paths = [
    current_dir,
    project_root / "2_basis",
    project_root / "4_advanced", 
    project_root,
    Path("."),
    Path(".."),
    Path("../2_basis"),
    Path("../4_advanced")
]

for path in possible_paths:
    if path.exists():
        sys.path.insert(0, str(path))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'georgian-spellchecker-secret-key'

# Базовые классы для работы
class OptimizedSpellChecker:
    def __init__(self):
        self.vocabulary = set()
        self.word_freq = Counter()
        self._cached_distances = {}
        
    def tokenize_georgian(self, text: str):
        """Быстрая токенизация грузинского текста"""
        words = re.findall(r'[\u10A0-\u10FF]{2,}', text)
        return words
    
    def is_correct(self, word: str):
        return word in self.vocabulary
    
    def optimized_levenshtein(self, s1: str, s2: str):
        """Оптимизированное расстояние Левенштейна с кэшированием"""
        cache_key = (s1, s2)
        if cache_key in self._cached_distances:
            return self._cached_distances[cache_key]
            
        if s1 == s2:
            self._cached_distances[cache_key] = 0
            return 0
            
        len1, len2 = len(s1), len(s2)
        if abs(len1 - len2) > 2:
            self._cached_distances[cache_key] = 3
            return 3
            
        if len1 < len2:
            return self.optimized_levenshtein(s2, s1)
            
        if len2 == 0:
            return len1
            
        previous_row = list(range(len2 + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        result = previous_row[-1]
        self._cached_distances[cache_key] = result
        return result
    
    def generate_candidates_fast(self, word: str, max_distance: int = 1):
        """Быстрая генерация кандидатов с оптимизациями"""
        if self.is_correct(word):
            return [word]
        
        candidates = []
        word_len = len(word)
        
        for candidate in self.vocabulary:
            if abs(len(candidate) - word_len) > 2:
                continue
                
            if word_len > 2 and candidate[:2] != word[:2]:
                continue
                
            distance = self.optimized_levenshtein(word, candidate)
            if distance <= max_distance:
                candidates.append((candidate, distance))
                
                if len(candidates) >= 20:
                    break
        
        candidates.sort(key=lambda x: (x[1], -self.word_freq.get(x[0], 0)))
        return [candidate for candidate, distance in candidates[:5]]
    
    def suggest_corrections(self, word: str, max_suggestions: int = 3):
        candidates = self.generate_candidates_fast(word)
        return candidates[:max_suggestions]
    
    def check_text_fast(self, text: str, max_errors: int = 50):
        """Быстрая проверка текста с ограничением количества ошибок"""
        words = self.tokenize_georgian(text)
        errors = []
        
        for word in words:
            if not self.is_correct(word):
                suggestions = self.suggest_corrections(word)
                errors.append({
                    'word': word,
                    'suggestions': suggestions,
                    'start_pos': text.find(word),
                    'end_pos': text.find(word) + len(word)
                })
                
                if len(errors) >= max_errors:
                    break
        
        return errors

def load_vocabulary_from_file(file_path):
    """Загрузка словаря из файла"""
    vocabulary = set()
    word_freq = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '\t' in line:
                        parts = line.split('\t')
                        word = parts[0].strip()
                        if len(parts) > 1:
                            try:
                                freq = int(parts[1])
                                word_freq[word] = freq
                            except:
                                word_freq[word] = 1
                    else:
                        word = line.strip()
                        word_freq[word] = 1
                    
                    if word and any('\u10A0' <= char <= '\u10FF' for char in word):
                        vocabulary.add(word)
        
        print(f"   📖 Загружено {len(vocabulary)} слов из {file_path.name}")
        return vocabulary, word_freq
        
    except Exception as e:
        print(f"   ❌ Ошибка загрузки {file_path}: {e}")
        return set(), {}

def initialize_spellcheckers():
    """Инициализация спеллчекеров с реальным словарем"""
    global checker, model_info
    
    print("🔍 ინიციალიზაცია სპელჩეკერის...")
    
    checker = OptimizedSpellChecker()
    
    # Пытаемся загрузить словарь из разных мест согласно новой структуре
    vocabulary_sources = [
        project_root / "2_basis" / "processed_corpus" / "vocabulary.txt",
        project_root / "2_basis" / "hunspell_georgian" / "ka_GE.dic",
        project_root / "2_basis" / "georgian_spellchecker.pkl",
        project_root / "4_advanced" / "advanced_georgian_spellchecker.pkl",
    ]
    
    loaded_vocabulary = False
    best_vocabulary = set()
    best_word_freq = {}
    best_source = ""
    
    for source_path in vocabulary_sources:
        if source_path.exists():
            print(f"   🔍 ვამოწმებთ {source_path}...")
            try:
                if source_path.suffix == '.pkl':
                    with open(source_path, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    vocabulary = set()
                    word_freq = {}
                    
                    if 'vocabulary' in model_data:
                        vocabulary = set(model_data['vocabulary'])
                    elif 'word_freq' in model_data:
                        vocabulary = set(model_data['word_freq'].keys())
                    
                    if 'word_freq' in model_data:
                        word_freq = model_data['word_freq']
                    else:
                        word_freq = {word: 1 for word in vocabulary}
                        
                elif source_path.suffix == '.txt' or source_path.name == 'ka_GE.dic':
                    vocabulary, word_freq = load_vocabulary_from_file(source_path)
                else:
                    continue
                
                if vocabulary and len(vocabulary) > len(best_vocabulary):
                    best_vocabulary = vocabulary
                    best_word_freq = word_freq
                    best_source = source_path.name
                    print(f"   ✅ ვიპოვეთ ლექსიკონი {len(vocabulary)} სიტყვით")
                    
            except Exception as e:
                print(f"   ❌ შეცდომა ფაილის ჩატვირთვისას {source_path}: {e}")
                continue
    
    if best_vocabulary:
        checker.vocabulary = best_vocabulary
        checker.word_freq = Counter(best_word_freq)
        model_info = {
            "type": "production", 
            "vocabulary_size": len(best_vocabulary),
            "source": best_source
        }
        print(f"✅ ლექსიკონი ჩაიტვირთა {best_source}-დან")
        print(f"📊 სიტყვები ლექსიკონში: {len(best_vocabulary)}")
        loaded_vocabulary = True
    else:
        print("⚠️  რეალური ლექსიკონები ვერ მოიძებნა. ვიყენებთ ძირითად ტესტურ ლექსიკონს.")
        test_vocabulary = {
            'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
            'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი',
            'ძალიან', 'ლამაზი', 'ქალაქი', 'ტურისტი', 'წერს', 'კოდი',
            'პითონი', 'ტექსტი', 'შეცდომა', 'სწორი', 'შემოწმება', 'ბგერა'
        }
        
        checker.vocabulary = test_vocabulary
        checker.word_freq = {word: 1 for word in test_vocabulary}
        model_info = {
            "type": "test", 
            "vocabulary_size": len(test_vocabulary),
            "source": "basic_test"
        }
        print(f"✅ შეიქმნა ძირითადი ტესტური ლექსიკონი {len(test_vocabulary)} სიტყვით")
        loaded_vocabulary = True
    
    return loaded_vocabulary

# Инициализируем при старте
initialize_spellcheckers()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', model_info=model_info)

@app.route('/check', methods=['POST'])
def check_text():
    """API для проверки текста"""
    if not checker:
        return jsonify({'error': 'სპელჩეკერი არ ინიციალიზირებულია'}), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'errors': [], 'stats': {'total_words': 0, 'error_count': 0}})
    
    try:
        errors = checker.check_text_fast(text, max_errors=100)
        
        return jsonify({
            'errors': errors,
            'stats': {
                'total_words': len(checker.tokenize_georgian(text)),
                'error_count': len(errors)
            }
        })
        
    except Exception as e:
        print(f"❌ შეცდომა ტექსტის შემოწმებისას: {e}")
        return jsonify({'error': f'შეცდომა ტექსტის შემოწმებისას: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    """Получение статистики модели"""
    return jsonify(model_info)

@app.route('/health')
def health_check():
    """Проверка работоспособности"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("=" * 60)
    print("🇬🇪 ქართული სპელჩეკერი - ვებ ინტერფეისი")
    print("=" * 60)
    print(f"📍 მოდელის ტიპი: {model_info['type']}")
    print(f"📊 სიტყვები ლექსიკონში: {model_info['vocabulary_size']}")
    if model_info.get('source'):
        print(f"📁 წყარო: {model_info['source']}")
    print(f"🌐 სერვერი გაშვებულია: http://localhost:5000")
    print("=" * 60)
    print("✨ გახსენით ბრაუზერი და გადადით მისამართზე ზემოთ!")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)