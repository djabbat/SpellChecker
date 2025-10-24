#!/usr/bin/env python3
"""
ქართული სპელჩეკერის ვებ ინტერფეისის გამშვები ფაილი
"""

import os
import sys
from pathlib import Path

def main():
    """ვებ სერვერის გაშვების მთავარი ფუნქცია"""
    try:
        # Добавляем корневую директорию проекта в путь
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Прямой импорт из файла
        import importlib.util
        
        # Загружаем модуль напрямую из файла
        web_interface_path = project_root / "5_web" / "web_interface.py"
        if not web_interface_path.exists():
            print(f"❌ ფაილი ვერ მოიძებნა: {web_interface_path}")
            sys.exit(1)
            
        spec = importlib.util.spec_from_file_location("web_interface", web_interface_path)
        web_interface = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(web_interface)
        
        app = web_interface.app
        
        print("=" * 60)
        print("🌐 ქართული სპელჩეკერი - ვებ ინტერფეისი")
        print("=" * 60)
        print("გახსენით ბრაუზერი და გადადით მისამართზე:")
        print("👉 http://localhost:5000")
        print("=" * 60)
        print("შესაჩერებლად დააჭირეთ Ctrl+C")
        print("=" * 60)
        
        # გაუშვი Flask აპლიკაცია
        app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=True, 
            threaded=True,
            use_reloader=False  # Отключаем reloader для избежания проблем с импортом
        )
        
    except ImportError as e:
        print(f"❌ შეცდომა: ვერ მოიძებნა საჭირო მოდულები")
        print(f"დეტალები: {e}")
        print("\nდარწმუნდით, რომ ყველა საჭირო ბიბლიოთეკა დაყენებულია:")
        print("pip install flask beautifulsoup4 requests")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 სერვერი შეჩერებულია")
        sys.exit(0)
    except Exception as e:
        print(f"❌ კრიტიკული შეცდომა: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()