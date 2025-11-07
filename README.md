# Визуализатор графа зависимостей пакетов Alpine Linux

Инструмент для анализа и визуализации зависимостей пакетов Alpine Linux.

## Использование

python src/main.py <package_name> [опции]

Опции
* --repository, -r: URL репозитория или путь к тестовому файлу
* --test-mode, -t: Включить тестовый режим
* --ascii-tree, -a: Вывод в формате ASCII-дерева
* --max-depth, -d: Максимальная глубина анализа (по умолчанию: 10)

Примеры
# Анализ пакета с реальным репозиторием
python src/main.py nginx --repository http://dl-cdn.alpinelinux.org/alpine/v3.18/main

# Анализ в тестовом режиме
python src/main.py A --repository test_repo.txt --test-mode

# С выводом ASCII-дерева и ограничением глубины
python src/main.py python3 --repository http://dl-cdn.alpinelinux.org/alpine/v3.18/main --ascii-tree --max-depth 3
