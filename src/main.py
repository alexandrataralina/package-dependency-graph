#!/usr/bin/env python3
import sys
import os

# Добавляем папку src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Config
from src.utils.errors import ConfigurationError
from src.utils.repository import RepositoryManager

def main():
    """Основная функция приложения"""
    try:
        # Инициализация и загрузка конфигурации
        config = Config()
        config.load_from_args()
        
        # Вывод конфигурации (требование этапа 1)
        config.display_config()
        
        # Создаем менеджер репозитория
        repo_manager = RepositoryManager(
            repository_url=config.repository_url,
            test_mode=config.test_mode,
            test_repo_path=config.test_repo_path
        )
        
        # Получаем прямые зависимости (требование этапа 2)
        print(f"\nПолучение прямых зависимостей для пакета: {config.package_name}")
        
        dependencies = repo_manager.get_package_dependencies(config.package_name)
        
        # Выводим прямые зависимости (требование этапа 2)
        print(f"Прямые зависимости пакета '{config.package_name}':")
        if dependencies:
            for i, dep in enumerate(dependencies, 1):
                print(f"  {i}. {dep}")
        else:
            print("  (нет зависимостей)")
        
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

        
        
        
