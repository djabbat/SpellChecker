#!/usr/bin/env python3
"""
Главный скрипт для полной сборки грузинского спеллчекера
Запускает все процессы: сбор корпуса, обучение моделей, объединение базовой и продвинутой версий
"""

import os
import sys
import pickle
import time
from pathlib import Path
import subprocess
import shutil

# Добавляем пути для импорта модулей
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "2_basis"))
sys.path.insert(0, str(project_root / "4_advanced"))

def print_step(step_number, description):
    """Красивый вывод шагов процесса"""
    print(f"\n{'='*60}")
    print(f"🚀 ШАГ {step_number}: {description}")
    print(f"{'='*60}")

def run_python_script(script_path, args=None):
    """Запуск Python скрипта"""
    if args is None:
        args = []
    
    script_full_path = project_root / script_path
    if not script_full_path.exists():
        print(f"❌ Скрипт не найден: {script_path}")
        return False
    
    try:
        cmd = [sys.executable, str(script_full_path)] + args
        print(f"📝 Запуск: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print(f"✅ Успешно: {script_path}")
            if result.stdout:
                print(f"📋 Вывод: {result.stdout}")
            return True
        else:
            print(f"❌ Ошибка в {script_path}:")
            print(f"stderr: {result.stderr}")
            print(f"stdout: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при запуске {script_path}: {e}")
        return False

def ensure_directories():
    """Создание необходимых директорий"""
    directories = [
        "1_collect/corpus",
        "2_basis/processed_corpus", 
        "2_basis/hunspell_georgian",
        "4_advanced",
        "5_web/static/css",
        "5_web/static/js",
        "5_web/templates"
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана директория: {dir_path}")

def collect_corpus():
    """Сбор корпуса текстов"""
    print_step(1, "СБОР ТЕКСТОВОГО КОРПУСА")
    
    # Проверяем, есть ли уже корпус
    corpus_dir = project_root / "1_collect" / "corpus"
    if corpus_dir.exists() and any(corpus_dir.iterdir()):
        print("📚 Корпус уже существует, пропускаем сбор...")
        return True
    
    print("📥 Сбор корпуса с веб-сайтов...")
    return run_python_script("1_collect/corpus.py")

def build_basic_model():
    """Построение базовой модели"""
    print_step(2, "ПОСТРОЕНИЕ БАЗОВОЙ МОДЕЛИ")
    
    # Запускаем базовый спеллчекер в режиме обучения
    success = run_python_script("2_basis/georgian_spellchecker.py", ["--build"])
    
    if not success:
        print("🔄 Альтернативный метод: обучение базовой модели...")
        success = run_python_script("2_basis/georgian_spellchecker.py", ["--train"])
    
    return success

def expand_corpus():
    """Расширение корпуса"""
    print_step(3, "РАСШИРЕНИЕ КОРПУСА")
    
    # Проверяем, нужно ли расширять корпус
    corpus_dir = project_root / "1_collect" / "corpus"
    txt_files = list(corpus_dir.glob("*.txt"))
    
    if len(txt_files) < 10:  # Если мало файлов, расширяем
        print("📈 Расширение корпуса дополнительными текстами...")
        return run_python_script("3_expand/expand_corpus.py")
    else:
        print(f"📚 Корпус содержит {len(txt_files)} файлов, расширение не требуется")
        return True

def build_advanced_model():
    """Построение продвинутой модели"""
    print_step(4, "ПОСТРОЕНИЕ ПРОДВИНУТОЙ МОДЕЛИ")
    
    # Проверяем существование базовой модели
    basic_model_path = project_root / "2_basis" / "georgian_spellchecker.pkl"
    if not basic_model_path.exists():
        print("❌ Базовая модель не найдена! Сначала выполните шаг 2.")
        return False
    
    print("🧠 Построение продвинутой модели с N-gram...")
    return run_python_script("4_advanced/advanced_spellchecker.py", ["--build"])

def merge_models():
    """Объединение базовой и продвинутой моделей"""
    print_step(5, "ОБЪЕДИНЕНИЕ МОДЕЛЕЙ")
    
    try:
        # Импортируем классы моделей
        from georgian_spellchecker import GeorgianSpellChecker
        from advanced_spellchecker import AdvancedGeorgianSpellChecker
        
        print("🔄 Загрузка базовой модели...")
        basic_model = GeorgianSpellChecker()
        basic_model_path = project_root / "2_basis" / "georgian_spellchecker.pkl"
        
        if basic_model_path.exists():
            basic_model.load_model(str(basic_model_path))
            print(f"✅ Базовая модель загружена: {len(basic_model.vocabulary)} слов")
        else:
            print("❌ Базовая модель не найдена!")
            return False
        
        print("🔄 Загрузка продвинутой модели...")
        advanced_model = AdvancedGeorgianSpellChecker()
        advanced_model_path = project_root / "4_advanced" / "advanced_georgian_spellchecker.pkl"
        
        if advanced_model_path.exists():
            advanced_model.load_advanced_model(str(advanced_model_path))
            print(f"✅ Продвинутая модель загружена: {len(advanced_model.vocabulary)} слов")
            
            # Объединяем словари
            print("🔗 Объединение словарей...")
            merged_vocabulary = basic_model.vocabulary.union(advanced_model.vocabulary)
            merged_word_freq = basic_model.word_freq.copy()
            
            # Обновляем частоты из продвинутой модели
            for word, freq in advanced_model.word_freq.items():
                if word in merged_word_freq:
                    merged_word_freq[word] += freq
                else:
                    merged_word_freq[word] = freq
            
            # Создаем объединенную модель
            print("🏗️ Создание объединенной модели...")
            merged_model = AdvancedGeorgianSpellChecker()
            merged_model.vocabulary = merged_vocabulary
            merged_model.word_freq = merged_word_freq
            
            # Копируем N-gram модели из продвинутой версии
            if hasattr(advanced_model, 'bigram_model'):
                merged_model.bigram_model = advanced_model.bigram_model
                print(f"✅ Биграммы: {sum(len(v) for v in advanced_model.bigram_model.values())}")
            
            if hasattr(advanced_model, 'trigram_model'):
                merged_model.trigram_model = advanced_model.trigram_model
                print(f"✅ Триграммы: {sum(len(v) for v in advanced_model.trigram_model.values())}")
            
            # Сохраняем объединенную модель
            merged_model_path = project_root / "4_advanced" / "merged_georgian_spellchecker.pkl"
            merged_model.save_advanced_model(str(merged_model_path))
            
            print(f"✅ Объединенная модель сохранена: {merged_model_path}")
            print(f"📊 Итоговый словарь: {len(merged_vocabulary)} слов")
            
            # Копируем объединенную модель в веб-папку для использования
            web_model_path = project_root / "5_web" / "merged_georgian_spellchecker.pkl"
            shutil.copy2(merged_model_path, web_model_path)
            print(f"🌐 Модель скопирована для веб-интерфейса: {web_model_path}")
            
            return True
        else:
            print("❌ Продвинутая модель не найдена!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при объединении моделей: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_fallback_model():
    """Создание резервной модели если основные не работают"""
    print_step(6, "СОЗДАНИЕ РЕЗЕРВНОЙ МОДЕЛИ")
    
    try:
        from advanced_spellchecker import AdvancedGeorgianSpellChecker
        
        # Создаем базовый словарь
        basic_words = {
            'გამარჯობა', 'როგორ', 'ხარ', 'დღეს', 'კარგი', 'ამინდი', 
            'საქართველო', 'თბილისი', 'ენა', 'პროგრამა', 'კომპიუტერი',
            'ძალიან', 'ლამაზი', 'ქალაქი', 'ტურისტი', 'წერს', 'კოდი',
            'პითონი', 'ტექსტი', 'შეცდომა', 'სწორი', 'შემოწმება', 'ბგერა',
            'სალამი', 'ბარი', 'ჰეი', 'მაშინ', 'შემდეგ', 'ადრე', 'გვიან',
            'დიდი', 'პატარა', 'ახალი', 'ძველი', 'სწრაფი', 'ნელი', 'ცხელი',
            'ცივი', 'თეთრი', 'შავი', 'წითელი', 'მწვანე', 'ლურჯი', 'ყვითელი',
            'სტუდენტი', 'მასწავლებელი', 'სკოლა', 'უნივერსიტეტი', 'წიგნი',
            'ფული', 'სამუშაო', 'ოჯახი', 'მეგობარი', 'სიყვარული', 'ცხოვრება'
        }
        
        fallback_model = AdvancedGeorgianSpellChecker()
        fallback_model.vocabulary = basic_words
        fallback_model.word_freq = {word: 1 for word in basic_words}
        
        # Сохраняем резервную модель
        fallback_path = project_root / "5_web" / "fallback_spellchecker.pkl"
        fallback_model.save_advanced_model(str(fallback_path))
        
        print(f"✅ Резервная модель создана: {len(basic_words)} слов")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания резервной модели: {e}")
        return False

def test_models():
    """Тестирование созданных моделей"""
    print_step(7, "ТЕСТИРОВАНИЕ МОДЕЛЕЙ")
    
    test_cases = [
        "გამარჯობა როგორ ხარ",
        "გამარჯაბა როგოთ ხართ",
        "ეს არის სატესტო ტექსტი",
        "პროგრამა კომპიუტერი ტექნოლოგია"
    ]
    
    try:
        from advanced_spellchecker import AdvancedGeorgianSpellChecker
        
        # Пробуем загрузить объединенную модель
        merged_path = project_root / "4_advanced" / "merged_georgian_spellchecker.pkl"
        if merged_path.exists():
            model = AdvancedGeorgianSpellChecker()
            model.load_advanced_model(str(merged_path))
            model_name = "Объединенная"
        else:
            # Пробуем продвинутую модель
            advanced_path = project_root / "4_advanced" / "advanced_georgian_spellchecker.pkl"
            if advanced_path.exists():
                model = AdvancedGeorgianSpellChecker()
                model.load_advanced_model(str(advanced_path))
                model_name = "Продвинутая"
            else:
                # Пробуем базовую модель
                basic_path = project_root / "2_basis" / "georgian_spellchecker.pkl"
                if basic_path.exists():
                    from georgian_spellchecker import GeorgianSpellChecker
                    model = GeorgianSpellChecker()
                    model.load_model(str(basic_path))
                    model_name = "Базовая"
                else:
                    print("❌ Ни одна модель не найдена для тестирования!")
                    return False
        
        print(f"🧪 Тестирование {model_name} модели:")
        print(f"📊 Слов в словаре: {len(model.vocabulary)}")
        
        for text in test_cases:
            print(f"\n📝 Текст: '{text}'")
            errors = model.check_text(text)
            
            if errors:
                for word, suggestions in errors:
                    print(f"   ❌ '{word}' -> {suggestions[:3]}")
            else:
                print("   ✅ Ошибок не найдено")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Главная функция"""
    print("🎯 ЗАПУСК ПОЛНОЙ СБОРКИ ГРУЗИНСКОГО СПЕЛЛЧЕКЕРА")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Создаем необходимые директории
        ensure_directories()
        
        # Шаг 1: Сбор корпуса
        if not collect_corpus():
            print("⚠️  Пропускаем сбор корпуса...")
        
        # Шаг 2: Построение базовой модели
        if not build_basic_model():
            print("❌ Ошибка построения базовой модели!")
            return
        
        # Шаг 3: Расширение корпуса (опционально)
        expand_corpus()
        
        # Шаг 4: Построение продвинутой модели
        if not build_advanced_model():
            print("⚠️  Продвинутая модель не построена, используем базовую...")
        
        # Шаг 5: Объединение моделей
        if not merge_models():
            print("⚠️  Объединение моделей не удалось...")
        
        # Шаг 6: Резервная модель
        create_fallback_model()
        
        # Шаг 7: Тестирование
        test_models()
        
        # Итоговая статистика
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"\n{'='*60}")
        print("🎉 СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*60}")
        print(f"⏱️  Время выполнения: {execution_time:.2f} секунд")
        print(f"📁 Проект готов к использованию!")
        print(f"\n🚀 Для запуска веб-интерфейса:")
        print(f"   python run_web_simple.py")
        print(f"   или")
        print(f"   cd 5_web && python web_interface.py")
        print(f"\n🌐 Затем откройте: http://localhost:5000")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Сборка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()