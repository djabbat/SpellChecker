#!/usr/bin/env python3
"""
Простой лаунчер для веб-интерфейса
"""

import os
import sys
from pathlib import Path

def main():
    """Главная функция запуска"""
    project_root = Path(__file__).parent
    
    # Добавляем пути
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "5_web"))
    
    try:
        # Импортируем и запускаем веб-интерфейс
        from web_interface import app
        
        print("=" * 50)
        print("🌐 Georgian SpellChecker - Web Interface")
        print("=" * 50)
        print("Open your browser and go to: http://localhost:5000")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()