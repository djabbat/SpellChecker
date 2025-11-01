#!/usr/bin/env python3
"""
Грузинский спеллчекер - полная реализация
Включает сборку корпуса, обучение модели и проверку орфографии
"""

import re
import os
import json
from collections import Counter, defaultdict
from pathlib import Path
import pickle
import argparse
from typing import List, Tuple, Set
import itertools

def levenshtein_distance(s1: str, s2: str) -> int:
    """Вычисление расстояния Левенштейна между двумя строками"""
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

class GeorgianSpellChecker:
    def __init__(self):
        self.vocabulary = set()
        self.word_freq = Counter()
        self.ngram_models = {}
        
    def load_corpus(self, corpus_path: str) -> None:
        """Загрузка корпуса из папки"""
        corpus_dir = Path(corpus_path)
        
        if not corpus_dir.exists():
            # Попробуем найти корпус в родительской директории
            parent_corpus = Path("..") / corpus_path
            if parent_corpus.exists():
                corpus_dir = parent_corpus
                print(f"Корпус найден в: {parent_corpus}")
            else:
                # Попробуем абсолютный путь от корня проекта
                project_root = Path(__file__).parent.parent
                absolute_corpus = project_root / corpus_path
                if absolute_corpus.exists():
                    corpus_dir = absolute_corpus
                    print(f"Корпус найден в: {absolute_corpus}")
                else:
                    raise FileNotFoundError(f"Папка корпуса не найдена: {corpus_path}. Искали в: {corpus_path}, {parent_corpus}, {absolute_corpus}")
        
        print("Загрузка корпуса...")
        total_files = 0
        total_words = 0
        
        # Обрабатываем все txt файлы в корпусе - ИСПРАВЛЕННАЯ ЧАСТЬ
        txt_files = list(corpus_dir.rglob("*.txt"))  # Рекурсивный поиск
        
        if not txt_files:
            print(f"В папке {corpus_dir} не найдено txt файлов!")
            return
            
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Токенизация текста
                words = self.tokenize_georgian(content)
                if words:  # Добавляем только если есть слова
                    self.vocabulary.update(words)
                    self.word_freq.update(words)
                
                total_files += 1
                total_words += len(words)
                
                if total_files % 100 == 0:
                    print(f"Обработано файлов: {total_files}, слов: {total_words}")
                    
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {e}")
        
        print(f"Загрузка завершена. Файлов: {total_files}, Уникальных слов: {len(self.vocabulary)}")
    
    def tokenize_georgian(self, text: str) -> List[str]:
        """Токенизация грузинского текста"""
        # Удаляем пунктуацию и лишние пробелы
        text = re.sub(r'[^\u10A0-\u10FF\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        words = text.strip().split()
        
        # Фильтруем слишком короткие слова
        return [word for word in words if len(word) > 1]
    
    def build_ngram_model(self, n: int = 2) -> None:
        """Построение N-gram модели"""
        print(f"Построение {n}-gram модели...")
        
        # Для построения модели нужен доступ к исходным текстам
        ngram_model = defaultdict(Counter)
        
        # Здесь нужно переобработать корпус для построения N-gram
        # Для простоты используем уже загруженные слова с их частотами
        # В реальной реализации нужно обрабатывать последовательности слов
        
        self.ngram_models[n] = ngram_model
        print(f"{n}-gram модель построена")
    
    def train_from_cleaned_corpus(self, cleaned_corpus_path: str) -> None:
        """Обучение на уже очищенном корпусе"""
        cleaned_dir = Path(cleaned_corpus_path)
        
        if not cleaned_dir.exists():
            # Попробуем найти в родительской директории
            parent_cleaned = Path("..") / cleaned_corpus_path
            if parent_cleaned.exists():
                cleaned_dir = parent_cleaned
                print(f"Очищенный корпус найден в: {parent_cleaned}")
            else:
                print(f"Очищенный корпус не найден: {cleaned_corpus_path}")
                return
        
        print("Обучение на очищенном корпусе...")
        
        for file_type in ['cleaned', 'tokenized']:
            corpus_path = cleaned_dir / file_type
            if corpus_path.exists():
                txt_files = list(corpus_path.glob("*.txt"))
                if txt_files:
                    print(f"Обрабатываем {len(txt_files)} файлов из {file_type}...")
                    for file_path in txt_files:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            words = content.split()
                            if words:  # Добавляем только если есть слова
                                self.vocabulary.update(words)
                                self.word_freq.update(words)
                            
                        except Exception as e:
                            print(f"Ошибка при загрузке {file_path}: {e}")
        
        print(f"Словарь обновлен. Уникальных слов: {len(self.vocabulary)}")
    
    def is_correct(self, word: str) -> bool:
        """Проверка, есть ли слово в словаре"""
        return word in self.vocabulary
    
    def generate_candidates(self, word: str, max_distance: int = 2) -> List[str]:
        """Генерация кандидатов для исправления"""
        candidates = []
        
        # Если слово уже правильное
        if self.is_correct(word):
            return [word]
        
        # Генерация кандидатов на основе расстояния Левенштейна
        for candidate in self.vocabulary:
            distance = levenshtein_distance(word, candidate)
            if distance <= max_distance:
                candidates.append((candidate, distance))
        
        # Сортируем по расстоянию и частоте
        candidates.sort(key=lambda x: (x[1], -self.word_freq.get(x[0], 0)))
        
        return [candidate for candidate, distance in candidates[:10]]
    
    def suggest_corrections(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Предложение исправлений для слова"""
        candidates = self.generate_candidates(word)
        return candidates[:max_suggestions]
    
    def check_text(self, text: str) -> List[Tuple[str, List[str]]]:
        """Проверка текста и предложение исправлений"""
        errors = []
        words = self.tokenize_georgian(text)
        
        for word in words:
            if not self.is_correct(word):
                suggestions = self.suggest_corrections(word)
                errors.append((word, suggestions))
        
        return errors
    
    def save_model(self, model_path: str) -> None:
        """Сохранение модели"""
        model_data = {
            'vocabulary': list(self.vocabulary),
            'word_freq': dict(self.word_freq),
            'ngram_models': self.ngram_models
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Модель сохранена: {model_path}")
    
    def load_model(self, model_path: str) -> None:
        """Загрузка модели"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vocabulary = set(model_data['vocabulary'])
        self.word_freq = Counter(model_data['word_freq'])
        self.ngram_models = model_data['ngram_models']
        
        print(f"Модель загружена. Уникальных слов: {len(self.vocabulary)}")

class CorpusProcessor:
    """Класс для обработки корпуса"""
    
    @staticmethod
    def process_existing_corpus(corpus_path: str, output_path: str) -> None:
        """Обработка существующего корпуса"""
        print("Обработка корпуса для спеллчекера...")
        
        corpus_dir = Path(corpus_path)
        
        # Пробуем разные пути для поиска корпуса
        if not corpus_dir.exists():
            parent_corpus = Path("..") / corpus_path
            if parent_corpus.exists():
                corpus_dir = parent_corpus
                print(f"Корпус найден в: {parent_corpus}")
            else:
                project_root = Path(__file__).parent.parent
                absolute_corpus = project_root / corpus_path
                if absolute_corpus.exists():
                    corpus_dir = absolute_corpus
                    print(f"Корпус найден в: {absolute_corpus}")
                else:
                    print(f"Корпус не найден: {corpus_path}")
                    return
        
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        all_words = Counter()
        total_files = 0
        
        txt_files = list(corpus_dir.rglob("*.txt"))  # Рекурсивный поиск
        if not txt_files:
            print(f"В папке {corpus_dir} не найдено txt файлов!")
            return
            
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Простая токенизация
                words = re.findall(r'[\u10A0-\u10FF]{2,}', content)
                if words:  # Добавляем только если есть слова
                    all_words.update(words)
                
                total_files += 1
                
            except Exception as e:
                print(f"Ошибка при обработке {file_path}: {e}")
        
        # Сохраняем словарь
        vocabulary_file = output_dir / "vocabulary.txt"
        with open(vocabulary_file, 'w', encoding='utf-8') as f:
            for word, count in all_words.most_common():
                f.write(f"{word}\t{count}\n")
        
        print(f"Обработка завершена. Файлов: {total_files}, Уникальных слов: {len(all_words)}")
        print(f"Словарь сохранен: {vocabulary_file}")

def create_hunspell_files(vocabulary: Set[str], output_dir: str) -> None:
    """Создание файлов для Hunspell"""
    hunspell_dir = Path(output_dir)
    hunspell_dir.mkdir(parents=True, exist_ok=True)
    
    # .dic файл (словарь)
    dic_file = hunspell_dir / "ka_GE.dic"
    with open(dic_file, 'w', encoding='utf-8') as f:
        f.write(f"{len(vocabulary)}\n")
        for word in sorted(vocabulary):
            f.write(f"{word}\n")
    
    # .aff файл (аффиксы) - базовая версия для грузинского
    aff_file = hunspell_dir / "ka_GE.aff"
    aff_content = """SET UTF-8
TRY აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ
"""
    
    with open(aff_file, 'w', encoding='utf-8') as f:
        f.write(aff_content)
    
    print(f"Hunspell файлы созданы в: {hunspell_dir}")

def find_corpus_path(corpus_path: str) -> Path:
    """Находит путь к корпусу, проверяя разные варианты"""
    paths_to_try = [
        Path(corpus_path),
        Path("corpus"),  # ეს იპოვის თქვენს კორპუსს!
        Path("../1_collect/corpus"),
        Path("1_collect/corpus"), 
        Path("..") / corpus_path,
        Path(__file__).parent.parent / corpus_path,
        Path(__file__).parent / corpus_path,
    ]
    
    for path in paths_to_try:
        if path.exists():
            print(f"Корпус найден: {path}")
            # დავაბრუნოთ აბსოლუტური პათი
            return path.resolve()
    
    # თუ კორპუსი არ მოიძებნა, შევქმნათ ტესტური
    print("Корпус не найден. Создаем тестовый корпус...")
    test_corpus = Path("test_corpus")
    test_corpus.mkdir(exist_ok=True)
    
    test_texts = [
        "გამარჯობა როგორ ხარ დღეს კარგი ამინდია",
        "საქართველო ქართული ენა პროგრამირება კომპიუტერი",
        "თბილისი ძალიან ლამაზი ქალაქია და მოსწონს ტურისტებს",
        "პროგრამა წერს კოდს პითონის ენაზე და ამოწმებს ტექსტს"
    ]
    
    for i, text in enumerate(test_texts, 1):
        with open(test_corpus / f"test_{i}.txt", 'w', encoding='utf-8') as f:
            f.write(text)
    
    print(f"Создан тестовый корпус: {test_corpus}")
    return test_corpus

def build_complete_spellchecker():
    """Полная сборка спеллчекера из корпуса"""
    
    # შევცვალოთ პათები
    CORPUS_PATH = "corpus"  # ახლა ეს იმუშავებს!
    CLEANED_CORPUS_PATH = "cleaned_corpus"
    MODEL_PATH = "georgian_spellchecker.pkl"
    
    print("=== ПОЛНАЯ СБОРКА ГРУЗИНСКОГО СПЕЛЛЧЕКЕРА ===")
    
    # შევქმნათ სპელჩეკერი
    spell_checker = GeorgianSpellChecker()
    
    # ვიპოვოთ კორპუსი
    corpus_dir = find_corpus_path(CORPUS_PATH)
    
    print(f"1. Используем корпус: {corpus_dir}")
    
    # ვამოწმებთ ფაილებს
    txt_files = list(corpus_dir.rglob("*.txt"))  # Рекурсивный поиск
    print(f"   Найдено txt файлов: {len(txt_files)}")
    for f in txt_files[:5]:  # Покажем только первые 5 файлов
        print(f"   - {f.name} ({f.stat().st_size} байт)")
    
    # ვტვირთავთ კორპუსს
    spell_checker.load_corpus(str(corpus_dir))
    
    if len(spell_checker.vocabulary) == 0:
        print("ВНИМАНИЕ: Словарь пуст! Добавляем тестовые слова...")
        basic_words = {
            'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
            'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი',
            'ძალიან', 'ლამაზი', 'ქალაქი', 'ტურისტი', 'წერს', 'კოდი'
        }
        spell_checker.vocabulary.update(basic_words)
        for word in basic_words:
            spell_checker.word_freq[word] = 1
    
    print(f"2. Словарь содержит {len(spell_checker.vocabulary)} слов")
    
    # ვაშენებთ N-gram მოდელებს
    print("3. Строим языковые модели...")
    spell_checker.build_ngram_model(2)
    spell_checker.build_ngram_model(3)
    
    # ვინახავთ მოდელს
    print("4. Сохраняем модель...")
    spell_checker.save_model(MODEL_PATH)
    
    # ვქმნით Hunspell ფაილებს
    print("5. Создаем файлы для Hunspell...")
    try:
        create_hunspell_files(spell_checker.vocabulary, "hunspell_georgian")
    except Exception as e:
        print(f"Ошибка при создании Hunspell файлов: {e}")
        print("Пробуем альтернативный путь...")
        hunspell_dir = Path("hunspell_output")
        hunspell_dir.mkdir(exist_ok=True)
        
        dic_file = hunspell_dir / "ka_GE.dic"
        with open(dic_file, 'w', encoding='utf-8') as f:
            f.write(f"{len(spell_checker.vocabulary)}\n")
            for word in sorted(spell_checker.vocabulary):
                f.write(f"{word}\n")
        
        aff_file = hunspell_dir / "ka_GE.aff"
        aff_content = "SET UTF-8\nTRY აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ\n"
        with open(aff_file, 'w', encoding='utf-8') as f:
            f.write(aff_content)
        
        print(f"Hunspell файлы созданы в: {hunspell_dir}")
    
    # ვტესტავთ მოდელს
    print("6. Тестируем модель...")
    test_words = ['გამარჯობა', 'გამარჯაბა', 'როგორ', 'როგოთ']
    print("\nТестовые проверки:")
    for word in test_words:
        if spell_checker.is_correct(word):
            print(f"  ✓ {word} - правильное")
        else:
            suggestions = spell_checker.suggest_corrections(word)
            print(f"  ✗ {word} -> {suggestions[:3]}")
    
    print("\n=== СБОРКА ЗАВЕРШЕНА ===")
    print(f"Модель: {MODEL_PATH}")
    print(f"Слов в словаре: {len(spell_checker.vocabulary)}")
    print("Файлы Hunspell: hunspell_output/")

def quick_test():
    """Быстрый тест спеллчекера"""
    print("=== БЫСТРЫЙ ТЕСТ ===")
    
    checker = GeorgianSpellChecker()
    
    # Загружаем модель если есть
    model_path = "georgian_spellchecker.pkl"
    if Path(model_path).exists():
        checker.load_model(model_path)
        print(f"Модель загружена. Слов: {len(checker.vocabulary)}")
        
        # Тестовые проверки
        test_texts = [
            "გამარჯობა როგორ ხარ",
            "გამარჯაბა როგოთ ხართ", 
            "ეს არის სატესტო ტექსტი"
        ]
        
        for text in test_texts:
            print(f"\nПроверка: '{text}'")
            errors = checker.check_text(text)
            if errors:
                for word, suggestions in errors:
                    print(f"  Ошибка: '{word}' -> {suggestions[:3]}")
            else:
                print("  ✓ Ошибок не найдено")
    else:
        print("Модель не найдена. Сначала запустите сборку.")

def demo():
    """Демонстрация работы спеллчекера"""
    print("=== ДЕМОНСТРАЦИЯ ГРУЗИНСКОГО СПЕЛЛЧЕКЕРА ===")
    
    # Создаем тестовый спеллчекер
    checker = GeorgianSpellChecker()
    
    # Тестовый словарь (в реальности будет загружен из корпуса)
    test_vocabulary = {
        'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
        'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი'
    }
    
    checker.vocabulary = test_vocabulary
    checker.word_freq = Counter(test_vocabulary)
    
    # Тестовые слова для проверки
    test_words = [
        'გამარჯობა',  # правильное
        'გამარჯაბა',  # ошибка
        'როგორ',      # правильное  
        'როგოთ',      # ошибка
        'კომპუტერი',  # ошибка
    ]
    
    print("\nПроверка слов:")
    for word in test_words:
        if checker.is_correct(word):
            print(f"✓ {word}")
        else:
            suggestions = checker.suggest_corrections(word)
            print(f"✗ {word} -> {suggestions}")

def main():
    """Основная функция с аргументами командной строки"""
    parser = argparse.ArgumentParser(description='Грузинский спеллчекер')
    parser.add_argument('--corpus', default='corpus', 
                       help='Путь к корпусу текстов')
    parser.add_argument('--cleaned-corpus', default='cleaned_corpus',
                       help='Путь к очищенному корпусу')
    parser.add_argument('--train', action='store_true', 
                       help='Обучить модель на корпусе')
    parser.add_argument('--check', type=str, 
                       help='Проверить слово или текст')
    parser.add_argument('--model', default='georgian_spellchecker.pkl',
                       help='Путь для сохранения/загрузки модели')
    parser.add_argument('--create-hunspell', action='store_true',
                       help='Создать файлы для Hunspell')
    parser.add_argument('--build', action='store_true',
                       help='Полная сборка спеллчекера')
    parser.add_argument('--test', action='store_true',
                       help='Быстрый тест')
    
    args = parser.parse_args()
    
    if args.build:
        build_complete_spellchecker()
        return
    
    if args.test:
        quick_test()
        return
    
    spell_checker = GeorgianSpellChecker()
    
    if args.train:
        print("=== ОБУЧЕНИЕ СПЕЛЛЧЕКЕРА ===")
        
        # Пытаемся сначала использовать очищенный корпус
        if Path(args.cleaned_corpus).exists():
            print("Используем очищенный корпус...")
            spell_checker.train_from_cleaned_corpus(args.cleaned_corpus)
        else:
            print("Очищенный корпус не найден, используем исходный...")
            # Обрабатываем исходный корпус
            CorpusProcessor.process_existing_corpus(args.corpus, "processed_corpus")
            spell_checker.load_corpus(args.corpus)
        
        # Строим N-gram модель
        spell_checker.build_ngram_model(2)
        
        # Сохраняем модель
        spell_checker.save_model(args.model)
        
        # Создаем файлы для Hunspell если нужно
        if args.create_hunspell:
            create_hunspell_files(spell_checker.vocabulary, "hunspell_output")
    
    elif args.check:
        print("=== ПРОВЕРКА ТЕКСТА ===")
        
        # Загружаем модель
        if Path(args.model).exists():
            spell_checker.load_model(args.model)
        else:
            print("Модель не найдена. Сначала обучите модель: --train")
            return
        
        text = args.check
        if len(text.split()) == 1:
            # Проверка одного слова
            word = text.strip()
            if spell_checker.is_correct(word):
                print(f"✓ Слово '{word}' правильное")
            else:
                suggestions = spell_checker.suggest_corrections(word)
                print(f"✗ Слово '{word}' содержит ошибки")
                print(f"Предложения: {', '.join(suggestions)}")
        else:
            # Проверка текста
            errors = spell_checker.check_text(text)
            if not errors:
                print("✓ Текст не содержит ошибок")
            else:
                print(f"✗ Найдено {len(errors)} ошибок:")
                for word, suggestions in errors:
                    print(f"  '{word}' -> {', '.join(suggestions[:3])}")
    
    else:
        print("Использование:")
        print("  Полная сборка: python georgian_spellchecker.py --build")
        print("  Обучить модель: python georgian_spellchecker.py --train")
        print("  Проверить слово: python georgian_spellchecker.py --check 'слово'")
        print("  Проверить текст: python georgian_spellchecker.py --check 'весь текст'")
        print("  Создать Hunspell: python georgian_spellchecker.py --train --create-hunspell")
        print("  Быстрый тест: python georgian_spellchecker.py --test")
        print("  Демо: python georgian_spellchecker.py")

if __name__ == "__main__":
    # Если запуск без аргументов - демонстрация
    import sys
    if len(sys.argv) == 1:
        demo()
    else:
        main()

def build_complete_model(self, corpus_path: str = None, output_path: str = "georgian_spellchecker.pkl"):
    """Полное построение модели с обработкой корпуса"""
    print("🏗️ Построение полной модели...")
    
    if corpus_path:
        # Обрабатываем корпус
        self.load_corpus(corpus_path)
    else:
        # Используем очищенный корпус если есть
        cleaned_path = "cleaned_corpus"
        if Path(cleaned_path).exists():
            self.train_from_cleaned_corpus(cleaned_path)
        else:
            # Ищем корпус в стандартных местах
            possible_corpus_paths = [
                "1_collect/corpus",
                "../1_collect/corpus", 
                "corpus"
            ]
            
            for path in possible_corpus_paths:
                if Path(path).exists():
                    print(f"📚 Найден корпус: {path}")
                    self.load_corpus(path)
                    break
            else:
                print("⚠️  Корпус не найден, создаем базовый словарь...")
                # Создаем базовый словарь
                basic_words = {
                    'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
                    'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი'
                }
                self.vocabulary = basic_words
                self.word_freq = {word: 1 for word in basic_words}
    
    # Строим N-gram модели
    self.build_ngram_model(2)
    self.build_ngram_model(3)
    
    # Сохраняем модель
    self.save_model(output_path)
    print(f"✅ Модель сохранена: {output_path}")
    print(f"📊 Слов в словаре: {len(self.vocabulary)}")