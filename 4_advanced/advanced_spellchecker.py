#!/usr/bin/env python3
"""
Продвинутый грузинский спеллчекер с N-gram моделями
"""

import pickle
from collections import defaultdict, Counter
from pathlib import Path
import re
from typing import List, Tuple, Set

# Импортируем базовый класс из того же файла или создаем его
class GeorgianSpellChecker:
    def __init__(self):
        self.vocabulary = set()
        self.word_freq = Counter()
        self.ngram_models = {}
        
    def load_corpus(self, corpus_path: str) -> None:
        """Загрузка корпуса из папки"""
        corpus_dir = Path(corpus_path)
        
        if not corpus_dir.exists():
            parent_corpus = Path("..") / corpus_path
            if parent_corpus.exists():
                corpus_dir = parent_corpus
                print(f"Корпус найден в: {parent_corpus}")
        
        print("Загрузка корпуса...")
        total_files = 0
        
        for file_path in corpus_dir.glob("**/*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                words = self.tokenize_georgian(content)
                if words:
                    self.vocabulary.update(words)
                    self.word_freq.update(words)
                
                total_files += 1
                
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {e}")
        
        print(f"Загрузка завершена. Файлов: {total_files}, Уникальных слов: {len(self.vocabulary)}")
    
    def tokenize_georgian(self, text: str) -> List[str]:
        """Токенизация грузинского текста"""
        text = re.sub(r'[^\u10A0-\u10FF\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        words = text.strip().split()
        return [word for word in words if len(word) > 1]
    
    def is_correct(self, word: str) -> bool:
        return word in self.vocabulary
    
    def generate_candidates(self, word: str, max_distance: int = 2) -> List[str]:
        """Генерация кандидатов для исправления"""
        def levenshtein_distance(s1: str, s2: str) -> int:
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
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
        
        candidates = []
        if self.is_correct(word):
            return [word]
        
        for candidate in self.vocabulary:
            distance = levenshtein_distance(word, candidate)
            if distance <= max_distance:
                candidates.append((candidate, distance))
        
        candidates.sort(key=lambda x: (x[1], -self.word_freq.get(x[0], 0)))
        return [candidate for candidate, distance in candidates[:10]]
    
    def suggest_corrections(self, word: str, max_suggestions: int = 5) -> List[str]:
        candidates = self.generate_candidates(word)
        return candidates[:max_suggestions]
    
    def save_model(self, model_path: str) -> None:
        model_data = {
            'vocabulary': list(self.vocabulary),
            'word_freq': dict(self.word_freq),
            'ngram_models': self.ngram_models
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Модель сохранена: {model_path}")
    
    def load_model(self, model_path: str) -> None:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        self.vocabulary = set(model_data['vocabulary'])
        self.word_freq = Counter(model_data['word_freq'])
        self.ngram_models = model_data['ngram_models']
        print(f"Модель загружена. Уникальных слов: {len(self.vocabulary)}")

class AdvancedGeorgianSpellChecker(GeorgianSpellChecker):
    def __init__(self):
        super().__init__()
        self.bigram_model = defaultdict(Counter)
        self.trigram_model = defaultdict(Counter)
        self.context_window = 3
    
    def build_advanced_ngram_models(self, corpus_path: str):
        """Построение улучшенных N-gram моделей с реальными данными"""
        print("Построение улучшенных N-gram моделей...")
        
        corpus_dir = Path(corpus_path)
        all_sentences = []
        
        # Собираем все предложения из корпуса
        for file_path in corpus_dir.glob("**/*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Разбиваем на предложения (простой метод)
                sentences = re.split(r'[.!?]', content)
                for sentence in sentences:
                    words = self.tokenize_georgian(sentence)
                    if len(words) >= 2:  # Только предложения с 2+ словами
                        all_sentences.append(words)
                        
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {e}")
        
        # Строим N-gram модели
        bigram_count = 0
        trigram_count = 0
        
        for sentence in all_sentences:
            # Биграммы
            for i in range(len(sentence) - 1):
                self.bigram_model[sentence[i]][sentence[i + 1]] += 1
                bigram_count += 1
            
            # Триграммы
            for i in range(len(sentence) - 2):
                key = (sentence[i], sentence[i + 1])
                self.trigram_model[key][sentence[i + 2]] += 1
                trigram_count += 1
        
        print(f"N-gram модели построены! Биграмм: {bigram_count}, Триграмм: {trigram_count}")
        print(f"Уникальных биграмм: {len(self.bigram_model)}")
        print(f"Уникальных триграмм: {len(self.trigram_model)}")
    
    def suggest_with_context(self, word: str, previous_words: List[str] = None, max_suggestions: int = 5) -> List[str]:
        """Предложение исправлений с учетом контекста"""
        candidates = self.generate_candidates(word)
        
        if not candidates or not previous_words:
            return candidates[:max_suggestions]
        
        # Используем контекст для ранжирования кандидатов
        scored_candidates = []
        
        for candidate in candidates:
            score = 0
            
            # Учитываем предыдущее слово (биграмма)
            if len(previous_words) >= 1:
                prev_word = previous_words[-1]
                if prev_word in self.bigram_model:
                    score += self.bigram_model[prev_word].get(candidate, 0) * 2
            
            # Учитываем два предыдущих слова (триграмма)
            if len(previous_words) >= 2:
                prev_key = (previous_words[-2], previous_words[-1])
                if prev_key in self.trigram_model:
                    score += self.trigram_model[prev_key].get(candidate, 0) * 3
            
            # Учитываем частотность слова
            score += self.word_freq.get(candidate, 0) * 0.1
            
            scored_candidates.append((candidate, score))
        
        # Сортируем по score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        return [candidate for candidate, score in scored_candidates[:max_suggestions]]
    
    def check_text_with_context(self, text: str) -> List[Tuple[str, List[str], List[str]]]:
        """Проверка текста с учетом контекста"""
        words = self.tokenize_georgian(text)
        errors = []
        
        for i, word in enumerate(words):
            if not self.is_correct(word):
                # Берем предыдущие слова для контекста
                context_start = max(0, i - self.context_window)
                previous_words = words[context_start:i]
                
                suggestions = self.suggest_with_context(word, previous_words)
                errors.append((word, suggestions, previous_words))
        
        return errors
    
    def save_advanced_model(self, model_path: str):
        """Сохранение продвинутой модели"""
        model_data = {
            'vocabulary': list(self.vocabulary),
            'word_freq': dict(self.word_freq),
            'bigram_model': dict(self.bigram_model),
            'trigram_model': {str(k): v for k, v in self.trigram_model.items()},
            'ngram_models': self.ngram_models
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Продвинутая модель сохранена: {model_path}")
    
    def load_advanced_model(self, model_path: str):
        """Загрузка продвинутой модели"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vocabulary = set(model_data['vocabulary'])
        self.word_freq = Counter(model_data['word_freq'])
        self.bigram_model = defaultdict(Counter, model_data['bigram_model'])
        
        # Восстанавливаем триграммы
        self.trigram_model = defaultdict(Counter)
        for k, v in model_data['trigram_model'].items():
            # Конвертируем ключ обратно в tuple
            if k.startswith('(') and k.endswith(')'):
                key_tuple = tuple(k[1:-1].replace("'", "").split(', '))
                self.trigram_model[key_tuple] = Counter(v)
        
        self.ngram_models = model_data['ngram_models']
        print(f"Продвинутая модель загружена. Слов: {len(self.vocabulary)}")

def test_advanced_spellchecker():
    """Тестирование продвинутого спеллчекера"""
    print("=== ТЕСТИРОВАНИЕ ПРОДВИНУТОГО СПЕЛЛЧЕКЕРА ===")
    
    checker = AdvancedGeorgianSpellChecker()
    
    # Пробуем загрузить существующую модель
    model_path = "georgian_spellchecker.pkl"
    advanced_model_path = "advanced_georgian_spellchecker.pkl"
    
    if Path(advanced_model_path).exists():
        print("Загружаем продвинутую модель...")
        checker.load_advanced_model(advanced_model_path)
    elif Path(model_path).exists():
        print("Загружаем базовую модель...")
        checker.load_model(model_path)
        
        # Строим N-gram модели на основе загруженного словаря
        print("Строим N-gram модели...")
        corpus_path = "../1.Collect a text corpus/corpus"
        if Path(corpus_path).exists():
            checker.build_advanced_ngram_models(corpus_path)
            checker.save_advanced_model(advanced_model_path)
        else:
            print("Корпус не найден для построения N-gram моделей")
    else:
        print("Модель не найдена. Сначала обучите базовую модель.")
        return
    
    # Тестовые примеры с контекстом
    test_cases = [
        "გამარჯობა როგორ ხარ დღეს",
        "გამარჯაბა როგოთ ხართ კარგად", 
        "ეს არის სატესტო ტექსტი შეცდომებით",
        "პროგრამა კომპიუტერი ტექნოლოგია"
    ]
    
    for text in test_cases:
        print(f"\nПроверка текста: '{text}'")
        errors = checker.check_text_with_context(text)
        
        if errors:
            for error_word, suggestions, context in errors:
                print(f"  Ошибка: '{error_word}'")
                print(f"  Контекст: {context}")
                print(f"  Предложения: {suggestions[:3]}")
        else:
            print("  ✓ Ошибок не найдено")
    
    # Демонстрация работы с контекстом
    print("\n=== ДЕМОНСТРАЦИЯ КОНТЕКСТНОЙ ПРОВЕРКИ ===")
    demo_words = [
        ("გამარჯაბა", ["დილა"]),  # "გამარჯაბა" после "დილა"
        ("როგოთ", ["გამარჯობა"]),  # "როგოთ" после "გამარჯობа"
    ]
    
    for word, context in demo_words:
        suggestions = checker.suggest_with_context(word, context)
        print(f"Слово '{word}' в контексте {context} -> {suggestions[:3]}")

def build_advanced_spellchecker():
    """Полная сборка продвинутого спеллчекера"""
    print("=== ПОСТРОЕНИЕ ПРОДВИНУТОГО СПЕЛЛЧЕКЕРА ===")
    
    checker = AdvancedGeorgianSpellChecker()
    
    # Загружаем или создаем базовую модель
    base_model_path = "../2.Cleaning and normalization/georgian_spellchecker.pkl"
    if Path(base_model_path).exists():
        print("Загружаем базовую модель...")
        checker.load_model(base_model_path)
    else:
        print("Базовая модель не найдена. Создаем новую...")
        # Здесь можно добавить создание базовой модели
        return
    
    # Строим N-gram модели
    corpus_path = "../1.Collect a text corpus/corpus"
    if Path(corpus_path).exists():
        checker.build_advanced_ngram_models(corpus_path)
    else:
        print("Корпус не найден!")
        return
    
    # Сохраняем продвинутую модель
    advanced_model_path = "advanced_georgian_spellchecker.pkl"
    checker.save_advanced_model(advanced_model_path)
    
    print("\n=== ПРОДВИНУТЫЙ СПЕЛЛЧЕКЕР ПОСТРОЕН ===")
    print(f"Модель: {advanced_model_path}")
    print(f"Слов в словаре: {len(checker.vocabulary)}")
    print(f"Биграмм: {sum(len(v) for v in checker.bigram_model.values())}")
    print(f"Триграмм: {sum(len(v) for v in checker.trigram_model.values())}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        build_advanced_spellchecker()
    else:
        test_advanced_spellchecker()
def build_complete_advanced_model(self, corpus_path: str = None, output_path: str = "advanced_georgian_spellchecker.pkl"):
    """Полное построение продвинутой модели"""
    print("🧠 Построение продвинутой модели...")
    
    # Сначала загружаем базовую модель если есть
    basic_model_path = "../2_basis/georgian_spellchecker.pkl"
    if Path(basic_model_path).exists():
        print("📥 Загрузка базовой модели...")
        self.load_model(basic_model_path)
    elif corpus_path:
        # Строим с нуля из корпуса
        print("📚 Обработка корпуса...")
        self.load_corpus(corpus_path)
    else:
        print("⚠️  Базовая модель не найдена, ищем корпус...")
        # Поиск корпуса
        possible_corpus_paths = [
            "../1_collect/corpus",
            "1_collect/corpus",
            "corpus"
        ]
        
        for path in possible_corpus_paths:
            if Path(path).exists():
                print(f"📚 Найден корпус: {path}")
                self.load_corpus(path)
                break
        else:
            print("❌ Корпус не найден!")
            return False
    
    # Строим N-gram модели
    print("🔨 Построение N-gram моделей...")
    if corpus_path:
        self.build_advanced_ngram_models(corpus_path)
    else:
        # Используем корпус из базовой модели
        corpus_path = "../1_collect/corpus"
        if Path(corpus_path).exists():
            self.build_advanced_ngram_models(corpus_path)
        else:
            print("⚠️  Корпус для N-gram не найден, пропускаем...")
    
    # Сохраняем продвинутую модель
    self.save_advanced_model(output_path)
    print(f"✅ Продвинутая модель сохранена: {output_path}")
    print(f"📊 Слов в словаре: {len(self.vocabulary)}")
    if hasattr(self, 'bigram_model'):
        print(f"📈 Биграмм: {sum(len(v) for v in self.bigram_model.values())}")
    if hasattr(self, 'trigram_model'):
        print(f"📈 Триграмм: {sum(len(v) for v in self.trigram_model.values())}")
    
    return True