import urllib.request
import urllib.error
import gzip
import io
from .errors import RepositoryError, PackageNotFoundError

class APKParser:
    @staticmethod
    def parse_apkindex_content(content):
        """Парсинг содержимого APKINDEX"""
        packages = {}
        current_pkg = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line:
                # Сохраняем предыдущий пакет
                if current_pkg and 'P' in current_pkg:
                    packages[current_pkg['P']] = current_pkg.copy()
                current_pkg = {}
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key in ['P', 'D', 'o']:
                    current_pkg[key] = value
        
        return packages
    
    @staticmethod
    def download_apkindex(repository_url):
        """Скачивание APKINDEX с различными вариантами URL"""
        architectures = ['x86_64', 'aarch64', 'x86', 'armv7']
        urls_to_try = []
        
        # Генерируем возможные URL
        base_url = repository_url.rstrip('/')
        for arch in architectures:
            urls_to_try.append(f"{base_url}/{arch}/APKINDEX.tar.gz")
        
        urls_to_try.append(f"{base_url}/APKINDEX.tar.gz")
        
        for url in urls_to_try:
            try:
                print(f"Попытка: {url}")
                response = urllib.request.urlopen(url, timeout=10)
                return APKParser.extract_apkindex_from_tar_gz(response.read())
            except Exception as e:
                continue
        
        raise RepositoryError("Не удалось скачать APKINDEX ни по одному из URL")
    
    @staticmethod
    def extract_apkindex_from_tar_gz(data):
        """Извлечение APKINDEX из tar.gz архива"""
        try:
            import tarfile
            tar_data = io.BytesIO(data)
            with tarfile.open(fileobj=tar_data, mode='r:gz') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('APKINDEX') or member.name == 'APKINDEX':
                        index_file = tar.extractfile(member)
                        return index_file.read().decode('utf-8')
            raise RepositoryError("APKINDEX не найден в архиве")
        except Exception as e:
            raise RepositoryError(f"Ошибка распаковки архива: {e}")
