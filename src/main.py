#!/usr/bin/env python3
import sys
import os

# Добавляем папку src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import Config
from src.utils.errors import ConfigurationError
from src.utils.repository import RepositoryManager
from src.utils.dependency_graph import DependencyGraph

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
        
        # Создаем граф зависимостей
        dependency_graph = DependencyGraph(repo_manager, config.max_depth)
        
        print(f"\nПостроение графа зависимостей для пакета: {config.package_name}")
        print(f"Максимальная глубина: {config.max_depth}")
        
        # Строим граф
        cycles = dependency_graph.build_graph(config.package_name)
        
        # Выводим информацию о циклических зависимостях
        if cycles:
            print(f"\n⚠️  Обнаружены циклические зависимости: {cycles}")
        else:
            print("✓ Циклические зависимости не обнаружены")
        
        # Выводим все зависимости
        all_deps = dependency_graph.get_all_dependencies(config.package_name)
        print(f"\nВсе зависимости пакета '{config.package_name}' (транзитивные):")
        if all_deps:
            for i, dep in enumerate(all_deps, 1):
                depth = dependency_graph.depth_map.get(dep, 0)
                print(f"  {i}. {dep} (глубина: {depth})")
        else:
            print("  (нет зависимостей)")
        
        # Выводим дерево зависимостей если включен режим ASCII-дерева
        if config.ascii_tree:
            print(f"\nДерево зависимостей '{config.package_name}':")
            dependency_graph.print_ascii_tree(config.package_name)
        
        # Выводим статистику
        print(f"\n📊 Статистика графа:")
        print(f"  Всего узлов: {len(dependency_graph.graph)}")
        print(f"  Прямые зависимости: {len(dependency_graph.graph.get(config.package_name, []))}")
        print(f"  Всего транзитивных зависимостей: {len(all_deps)}")
        
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
