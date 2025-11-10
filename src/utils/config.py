import argparse
import sys
from .errors import ConfigurationError

class Config:
    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.test_mode = False
        self.test_repo_path = None
        self.ascii_tree = False
        self.install_order = False
        self.plantuml = False
        self.max_depth = None
        
    def parse_arguments(self):
        """Парсинг аргументов командной строки"""
        parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей пакетов Alpine Linux',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Обязательные параметры
        parser.add_argument(
            'package',
            help='Имя анализируемого пакета'
        )
        
        # Опциональные параметры
        parser.add_argument(
            '--repository',
            '-r',
            help='URL репозитория или путь к файлу тестового репозитория'
        )
        
        parser.add_argument(
            '--test-mode',
            '-t',
            action='store_true',
            help='Режим работы с тестового репозитория'
        )
        
        parser.add_argument(
            '--ascii-tree',
            '-a',
            action='store_true',
            help='Вывод зависимостей в формате ASCII-дерева'
        )
        
        parser.add_argument(
            '--install-order',
            '-i',
            action='store_true',
            help='Вывести порядок загрузки зависимостей'
        )
        
        parser.add_argument(
            '--plantuml',
            '-p',
            action='store_true',
            help='Сгенерировать PlantUML диаграмму зависимостей'
        )
        
        parser.add_argument(
            '--max-depth',
            '-d',
            type=int,
            default=10,
            help='Максимальная глубина анализа зависимостей (по умолчанию: 10)'
        )
        
        return parser.parse_args()
    
    def validate_config(self):
        """Валидация конфигурации"""
        errors = []
        
        if not self.package_name:
            errors.append("Не указано имя пакета")
            
        if self.test_mode and not self.test_repo_path:
            errors.append("В тестовом режиме должен быть указан путь к тестовому репозиторию")
            
        if not self.test_mode and not self.repository_url:
            errors.append("Должен быть указан URL репозитория")
            
        if self.max_depth <= 0:
            errors.append("Максимальная глубина должна быть положительным числом")
            
        if errors:
            raise ConfigurationError("\n".join(errors))
    
    def load_from_args(self):
        """Загрузка конфигурации из аргументов командной строки"""
        try:
            args = self.parse_arguments()
            
            self.package_name = args.package
            self.repository_url = args.repository
            self.test_mode = args.test_mode
            self.ascii_tree = args.ascii_tree
            self.install_order = args.install_order
            self.plantuml = args.plantuml
            self.max_depth = args.max_depth
            
            # Если включен тестовый режим, repository_url становится путем к файлу
            if self.test_mode and self.repository_url:
                self.test_repo_path = self.repository_url
                self.repository_url = None
            
            self.validate_config()
            
        except argparse.ArgumentError as e:
            raise ConfigurationError(f"Ошибка в аргументах командной строки: {e}")
        except Exception as e:
            raise ConfigurationError(f"Неожиданная ошибка при загрузке конфигурации: {e}")
    
    def display_config(self):
        """Вывод конфигурации в формате ключ-значение"""
        print("Текущая конфигурация:")
        print(f"  Имя пакета: {self.package_name}")
        print(f"  URL репозитория: {self.repository_url}")
        print(f"  Режим тестирования: {self.test_mode}")
        print(f"  Путь к тестовому репозиторию: {self.test_repo_path}")
        print(f"  Вывод ASCII-дерева: {self.ascii_tree}")
        print(f"  Вывод порядка установки: {self.install_order}")
        print(f"  Генерация PlantUML: {self.plantuml}")
        print(f"  Максимальная глубина: {self.max_depth}")
