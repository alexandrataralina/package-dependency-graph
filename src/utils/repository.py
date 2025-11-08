import urllib.request
import urllib.error
from .errors import RepositoryError, PackageNotFoundError

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
            # Пробуем разные возможные URL для APKINDEX
            possible_urls = [
                f"{self.repository_url.rstrip('/')}/x86_64/APKINDEX.tar.gz",
                f"{self.repository_url.rstrip('/')}/aarch64/APKINDEX.tar.gz",
                f"{self.repository_url.rstrip('/')}/APKINDEX.tar.gz",
                f"{self.repository_url.rstrip('/')}/x86_64/APKINDEX",
                f"{self.repository_url.rstrip('/')}/aarch64/APKINDEX", 
                f"{self.repository_url.rstrip('/')}/APKINDEX"
            ]
            
            index_content = None
            last_error = None
            
            for index_url in possible_urls:
                try:
                    print(f"Попытка доступа к: {index_url}")
                    response = urllib.request.urlopen(index_url)
                    
                    # Если это tar.gz архив
                    if index_url.endswith('.tar.gz'):
                        import tarfile
                        import io
                        
                        # Читаем архив в память
                        tar_data = io.BytesIO(response.read())
                        with tarfile.open(fileobj=tar_data, mode='r:gz') as tar:
                            # Ищем файл APKINDEX в архиве
                            for member in tar.getmembers():
                                if member.name == 'APKINDEX':
                                    index_file = tar.extractfile(member)
                                    index_content = index_file.read().decode('utf-8')
                                    break
                    else:
                        # Обычный текстовый файл
                        index_content = response.read().decode('utf-8')
                    
                    if index_content:
                        print("Успешно получен индекс репозитория")
                        return self._parse_apkindex(index_content, package_name)
                        
                except urllib.error.HTTPError as e:
                    last_error = f"Ошибка HTTP {e.code} для {index_url}"
                    continue
                except Exception as e:
                    last_error = f"Ошибка для {index_url}: {e}"
                    continue
            
            # Если ни один URL не сработал
            raise RepositoryError(f"Не удалось получить APKINDEX. Последняя ошибка: {last_error}")
            
        except urllib.error.URLError as e:
            raise RepositoryError(f"Ошибка сети: {e}")
        except Exception as e:
            raise RepositoryError(f"Неожиданная ошибка: {e}")




    def _parse_apkindex(self, index_content, package_name):
        """Парсинг APKINDEX формата"""
        packages = self._parse_apkindex_packages(index_content)
        
        if package_name not in packages:
            raise PackageNotFoundError(f"Пакет '{package_name}' не найден в репозитории")
        
        package_info = packages[package_name]
        dependencies = package_info.get('D', [])
        
        # Обрабатываем зависимости - убираем версии и условия
        clean_dependencies = []
        for dep in dependencies:
            # Убираем версии (всё что после =, <, >, ~)
            clean_dep = dep.split('=')[0].split('<')[0].split('>')[0].split('~')[0]
            # Убираем условия установки (всё что начинается с !)
            if not clean_dep.startswith('!'):
                clean_dependencies.append(clean_dep.strip())
        
        return clean_dependencies
    
    def _parse_apkindex_packages(self, index_content):
        """Парсинг всех пакетов из APKINDEX"""
        packages = {}
        current_package = {}
        
        for line in index_content.split('\n'):
            line = line.strip()
            
            if not line:
                # Пустая строка - конец описания пакета
                if current_package and 'P' in current_package:
                    package_name = current_package['P']
                    packages[package_name] = current_package.copy()
                current_package = {}
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'P':  # Package name
                    current_package['P'] = value
                elif key == 'D':  # Dependencies
                    # Зависимости разделены пробелами
                    current_package['D'] = value.split() if value else []
                elif key == 'o':  # Origin (для отслеживания виртуальных пакетов)
                    current_package['o'] = value
        
        return packages
