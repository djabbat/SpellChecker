# 🇬🇪 Georgian SpellChecker / ქართული მართლწერის შემოწმება

[English](#english) | [Русский](#russian) | [ქართული](#georgian)

---
<!-- markdownlint-disable MD033 -->
<div id="english"></div>

## English

### Georgian Language Spell Checker

A powerful AI-based spell checking system for the Georgian language with a modern web interface.

### Features

- ✅ **Automatic spell checking** - Text is checked in real-time as you type
- 🔴 **Visual error highlighting** - Errors are underlined with bold red lines
- 💡 **Smart suggestions** - Context-aware correction suggestions
- 🖱️ **One-click correction** - Click on errors to see and apply fixes
- 🌐 **Modern web interface** - Clean, responsive design
- ⚡ **Fast processing** - Optimized algorithms for quick checking

### Project Structure

``` text

SpellChecker/
├── 1_collect/                 # Text corpus collection
│   └── corpus.py
├── 2_basis/                   # Basic spell checker models
│   ├── georgian_spellchecker.pkl
│   ├── georgian_spellchecker.py
│   ├── hunspell_georgian/
│   │   ├── ka_GE.aff
│   │   └── ka_GE.dic
│   └── processed_corpus/
│       └── vocabulary.txt
├── 3_expand/                  # Corpus expansion tools
│   ├── 1.Collect a text corpus/
│   └── expand_corpus.py
├── 4_advanced/                # Advanced N-gram models
│   ├── advanced_georgian_spellchecker.pkl
│   └── advanced_spellchecker.py
├── 5_web/                     # Web interface
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/
│   │   └── index.html
│   ├── web_interface.py
│   └── __init__.py
├── run_web.py                 # Web server launcher
├── run_web_simple.py          # Simple launcher
├── start_1-4.py              # Model training script
└── ReadMe.md

```

### Quick Start

#### Method 1: Direct Launch

```bash
cd 5_web
python web_interface.py
```

#### Method 2: Using Launcher

```bash
python run_web_simple.py
```

Then open your browser and go to: `http://localhost:5000`

### Usage

1. **Start typing** Georgian text in the text area
2. **Errors are automatically highlighted** with red underlines
3. **Click on underlined words** to see correction suggestions
4. **Click on a suggestion** to replace the error
5. If no suggestions are available, you'll see "არ იძებნება"

### Model Training

To train or update the spell checking models:

```bash
python start_1-4.py
```

### Requirements

- Python 3.7+
- Flask
- BeautifulSoup4
- Requests

Install dependencies:

```bash
pip install flask beautifulsoup4 requests
```

### Technology

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Spell Checking**: Levenshtein distance, N-gram models
- **Data Processing**: Custom corpus processing pipelines

---

<div id="russian"></div>

## Русский

### Спеллчекер для грузинского языка

Мощная система проверки орфографии для грузинского языка с современным веб-интерфейсом на основе искусственного интеллекта.

### Возможности

- ✅ **Автоматическая проверка** - Текст проверяется в реальном времени при вводе
- 🔴 **Визуальное выделение ошибок** - Ошибки подчеркиваются жирными красными линиями
- 💡 **Умные предложения** - Контекстно-зависимые варианты исправления
- 🖱️ **Исправление в один клик** - Нажмите на ошибку для просмотра и применения исправлений
- 🌐 **Современный веб-интерфейс** - Чистый, адаптивный дизайн
- ⚡ **Быстрая обработка** - Оптимизированные алгоритмы для быстрой проверки

### Структура проекта

``` text
SpellChecker/
├── 1_collect/                 # Сбор текстового корпуса
│   └── corpus.py
├── 2_basis/                   # Базовые модели спеллчекера
│   ├── georgian_spellchecker.pkl
│   ├── georgian_spellchecker.py
│   ├── hunspell_georgian/
│   │   ├── ka_GE.aff
│   │   └── ka_GE.dic
│   └── processed_corpus/
│       └── vocabulary.txt
├── 3_expand/                  # Инструменты расширения корпуса
│   ├── 1.Collect a text corpus/
│   └── expand_corpus.py
├── 4_advanced/                # Продвинутые N-gram модели
│   ├── advanced_georgian_spellchecker.pkl
│   └── advanced_spellchecker.py
├── 5_web/                     # Веб-интерфейс
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/
│   │   └── index.html
│   ├── web_interface.py
│   └── __init__.py
├── run_web.py                 # Запуск веб-сервера
├── run_web_simple.py          # Простой запуск
├── start_1-4.py              # Скрипт обучения моделей
└── ReadMe.md
```

### Быстрый старт

#### Способ 1: Прямой запуск

```bash
cd 5_web
python web_interface.py
```

#### Способ 2: Использование лаунчера

```bash
python run_web_simple.py
```

Затем откройте браузер и перейдите по адресу: `http://localhost:5000`

### Использование

1. **Начните вводить** грузинский текст в текстовой области
2. **Ошибки автоматически выделяются** красным подчеркиванием
3. **Нажмите на подчеркнутые слова** чтобы увидеть варианты исправления
4. **Нажмите на предложение** для замены ошибки
5. Если вариантов исправления нет, вы увидите "არ იძებნება"

### Обучение моделей

Для обучения или обновления моделей проверки орфографии:

```bash
python start_1-4.py
```

### Требования

- Python 3.7+
- Flask
- BeautifulSoup4
- Requests

Установите зависимости:

```bash
pip install flask beautifulsoup4 requests
```

### Технологии

- **Бэкенд**: Python, Flask
- **Фронтенд**: HTML5, CSS3, JavaScript
- **Проверка орфографии**: Расстояние Левенштейна, N-gram модели
- **Обработка данных**: Пользовательские пайплайны обработки корпуса

---

<div id="georgian"></div>

## ქართული

### ქართული მართლწერის შემოწმება

ძლიერი AI-ზე დაფუძნებული მართლწერის შემოწმების სისტემა ქართული ენისთვის თანამედროვე ვებ ინტერფეისით.

### შესაძლებლობები

- ✅ **ავტომატური შემოწმება** - ტექსტი შემოწმდება რეალურ დროში აკრეფისას
- 🔴 **ვიზუალური შეცდომების ხაზგასმა** - შეცდომები ხაზგასმულია სქელი წითელი ხაზებით
- 💡 **ჭკვიანი შემოთავაზებები** - კონტექსტური გამოსწორების ვარიანტები
- 🖱️ **ერთწერტილიანი გამოსწორება** - დააწკაპუნეთ შეცდომაზე გამოსწორებების სანახავად და გამოსაყენებლად
- 🌐 **თანამედროვე ვებ ინტერფეისი** - სუფთა, ადაპტირებადი დიზაინი
- ⚡ **სწრაფი დამუშავება** - ოპტიმიზირებული ალგორითმები სწრაფი შემოწმებისთვის

### პროექტის სტრუქტურა

```SpellChecker/
├── 1_collect/                 # ტექსტური კორპუსის შეგროვება
│   └── corpus.py
├── 2_basis/                   # ძირითადი სპელჩეკერის მოდელები
│   ├── georgian_spellchecker.pkl
│   ├── georgian_spellchecker.py
│   ├── hunspell_georgian/
│   │   ├── ka_GE.aff
│   │   └── ka_GE.dic
│   └── processed_corpus/
│       └── vocabulary.txt
├── 3_expand/                  # კორპუსის გაფართოების ინსტრუმენტები
│   ├── 1.Collect a text corpus/
│   └── expand_corpus.py
├── 4_advanced/                # მოწინავე N-gram მოდელები
│   ├── advanced_georgian_spellchecker.pkl
│   └── advanced_spellchecker.py
├── 5_web/                     # ვებ ინტერფეისი
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   ├── templates/
│   │   └── index.html
│   ├── web_interface.py
│   └── __init__.py
├── run_web.py                 # ვებ სერვერის გამშვები
├── run_web_simple.py          # მარტივი გამშვები
├── start_1-4.py              # მოდელების სასწავლო სკრიპტი
└── ReadMe.md
```

### სწრაფი დაწყება

#### მეთოდი 1: პირდაპირი გაშვება

```bash
cd 5_web
python web_interface.py
```

#### მეთოდი 2: გამშვების გამოყენება

```bash
python run_web_simple.py
```

შემდეგ გახსენით ბრაუზერი და გადადით მისამართზე: `http://localhost:5000`

### გამოყენება

1. **დაიწყეთ ქართული ტექსტის აკრეფა** ტექსტურ ველში
2. **შეცდომები ავტომატურად ხაზგასმულია** წითელი ხაზგასმით
3. **დააწკაპუნეთ ხაზგასმულ სიტყვებზე** გამოსწორების ვარიანტების სანახავად
4. **დააწკაპუნეთ შემოთავაზებაზე** შეცდომის შესაცვლელად
5. თუ გამოსწორების ვარიანტები არ არის, დაინახავთ "არ იძებნება"

### მოდელების ტრენინგი

მართლწერის შემოწმების მოდელების სასწავლად ან განახლებისთვის:

```bash
python start_1-4.py
```

### მოთხოვნები

- Python 3.7+
- Flask
- BeautifulSoup4
- Requests

დააინსტალირეთ დამოკიდებულებები:

```bash
pip install flask beautifulsoup4 requests
```

### ტექნოლოგიები

- **ბექენდი**: Python, Flask
- **ფრონტენდი**: HTML5, CSS3, JavaScript
- **მართლწერის შემოწმება**: ლევენშტეინის დისტანცია, N-gram მოდელები
- **მონაცემთა დამუშავება**: მომხმარებლის კორპუსის დამუშავების პაიპლაინები

``` ## Файл: `README_QUICK.md` (краткая версия)

```markdown
# Georgian SpellChecker - Quick Start

## 🚀 Quick Launch

```bash
# Method 1: Direct launch
cd 5_web
python web_interface.py

# Method 2: Using launcher  
python run_web_simple.py
```

Then open: **<http://localhost:5000>**

## 📝 How to Use

1. Type Georgian text in the text area
2. Errors are automatically underlined in red
3. Click on underlined words to see suggestions
4. Click on a suggestion to replace the error
5. If no suggestions: "არ იძებნება" will appear

## 🔧 Model Training

```bash
python start_1-4.py
```

## 📦 Requirements

```bash
pip install flask beautifulsoup4 requests
```

## 📁 Project Structure

- `1_collect/` - Text corpus collection
- `2_basis/` - Basic spell checker models  
- `3_expand/` - Corpus expansion tools
- `4_advanced/` - Advanced N-gram models
- `5_web/` - Web interface
