import urllib.request
import urllib.error
from .errors import RepositoryError, PackageNotFoundError
from .apk_parser import APKParser

class RepositoryManager:
    def __init__(self, repository_url=None, test_mode=False, test_repo_path=None):
        self.repository_url = repository_url
        self.test_mode = test_mode
        self.test_repo_path = test_repo_path
        self.packages_cache = {}
    
    def get_package_dependencies(self, package_name):
        """Получить прямые зависимости пакета"""
        if self.test_mode:
            return self._get_dependencies_from_test_file(package_name)
        else:
            return self._get_dependencies_from_apk_index(package_name)
    
    def _get_dependencies_from_test_file(self, package_name):
        """Получить зависимости из тестового файла"""
        try:
            with open(self.test_repo_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    
                    current_package, dependencies_str = line.split(':', 1)
                    current_package = current_package.strip()
                    
                    if current_package == package_name:
                        dependencies = [dep.strip() for dep in dependencies_str.split() if dep.strip()]
                        return dependencies
            
            raise PackageNotFoundError(f"Пакет '{package_name}' не найден в тестовом репозитории")
            
        except FileNotFoundError:
            raise RepositoryError(f"Тестовый файл '{self.test_repo_path}' не найден")
        except Exception as e:
            raise RepositoryError(f"Ошибка чтения тестового файла: {e}")
    
    def _get_dependencies_from_apk_index(self, package_name):
        """Получить зависимости из APK индекса Alpine Linux"""
        try:
            # Используем улучшенный парсер
            index_content = APKParser.download_apkindex(self.repository_url)
            packages = APKParser.parse_apkindex_content(index_content)
            
            if package_name not in packages:
                raise PackageNotFoundError(f"Пакет '{package_name}' не найден в репозитории")
            
            package_info = packages[package_name]
            dependencies = package_info.get('D', '').split()
            
            # Очищаем зависимости
            clean_dependencies = []
            for dep in dependencies:
                clean_dep = dep.split('=')[0].split('<')[0].split('>')[0].split('~')[0]
                if not clean_dep.startswith('!') and clean_dep:
                    clean_dependencies.append(clean_dep)
            
            return clean_dependencies
            
        except urllib.error.URLError as e:
            raise RepositoryError(f"Ошибка сети: {e}")
        except Exception as e:
            raise RepositoryError(f"Ошибка при получении зависимостей: {e}")
