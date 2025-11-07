class ConfigurationError(Exception):
    """Базовое исключение для ошибок конфигурации"""
    pass

class PackageNotFoundError(ConfigurationError):
    """Ошибка: пакет не найден"""
    pass

class RepositoryError(ConfigurationError):
    """Ошибка: проблема с репозиторием"""
    pass

class DepthLimitError(ConfigurationError):
    """Ошибка: превышена глубина анализа"""
    pass
