#!/usr/bin/env python3
import sys
import os

# Добавляем папку src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Config
from src.utils.errors import ConfigurationError

def main():
    """Основная функция приложения"""
    try:
        # Инициализация и загрузка конфигурации
        config = Config()
        config.load_from_args()
        
        # Вывод конфигурации (требование этапа 1)
        config.display_config()
        
        # Здесь в следующих этапах будет основная логика
        print(f"\nАнализ пакета: {config.package_name}")
        
        if config.test_mode:
            print("Режим: ТЕСТИРОВАНИЕ")
            print(f"Используется тестовый файл: {config.test_repo_path}")
        else:
            print("Режим: РАБОЧИЙ")
            print(f"Используется репозиторий: {config.repository_url}")
            
        print(f"Максимальная глубина анализа: {config.max_depth}")
        
    except ConfigurationError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
