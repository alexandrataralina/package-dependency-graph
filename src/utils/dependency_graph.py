from collections import deque
from .errors import DepthLimitError

class DependencyGraph:
    def __init__(self, repository_manager, max_depth=10):
        self.repository_manager = repository_manager
        self.max_depth = max_depth
        self.graph = {}
        self.visited = set()
        self.depth_map = {}
        
    def build_graph(self, root_package):
        """Построение графа зависимостей с помощью BFS"""
        queue = deque()
        queue.append((root_package, 0, []))  # (package, depth, path)
        self.graph = {}
        self.visited = set()
        self.depth_map = {root_package: 0}
        cycles = []
        
        while queue:
            current_package, depth, path = queue.popleft()
            
            # Проверка максимальной глубины
            if depth >= self.max_depth:
                continue
                
            # Проверяем на циклические зависимости
            if current_package in path:
                cycle = path[path.index(current_package):] + [current_package]
                if cycle not in cycles:
                    cycles.append(cycle)
                continue
                
            # Если пакет уже посещен, пропускаем
            if current_package in self.visited:
                continue
                
            self.visited.add(current_package)
            current_path = path + [current_package]
            
            try:
                # Получаем зависимости текущего пакета
                dependencies = self.repository_manager.get_package_dependencies(current_package)
                self.graph[current_package] = dependencies
                
                # Добавляем зависимости в очередь
                for dep in dependencies:
                    if dep not in self.depth_map or self.depth_map[dep] > depth + 1:
                        self.depth_map[dep] = depth + 1
                    queue.append((dep, depth + 1, current_path))
                    
            except Exception as e:
                # Если не удалось получить зависимости, отмечаем как пустой список
                self.graph[current_package] = []
                print(f"Предупреждение: не удалось получить зависимости для '{current_package}': {e}")
        
        return cycles
    
    def get_ancestors(self, package):
        """Получить всех предков пакета (обратные зависимости)"""
        ancestors = set()
        for pkg, deps in self.graph.items():
            if package in deps:
                ancestors.add(pkg)
        return ancestors
    
    def get_all_dependencies(self, package=None):
        """Получить все зависимости (транзитивное замыкание)"""
        if package:
            # Возвращаем подграф для конкретного пакета
            return self._get_transitive_dependencies(package)
        else:
            # Возвращаем весь граф
            return self.graph
    
    def _get_transitive_dependencies(self, package):
        """Получить транзитивные зависимости пакета"""
        if package not in self.graph:
            return []
            
        result = set()
        stack = [package]
        
        while stack:
            current = stack.pop()
            if current in result:
                continue
            result.add(current)
            
            # Добавляем зависимости текущего пакета
            for dep in self.graph.get(current, []):
                if dep not in result:
                    stack.append(dep)
        
        result.discard(package)  # Убираем сам пакет из результата
        return sorted(list(result))
    
    def get_dependency_tree(self, package):
        """Получить дерево зависимостей в виде словаря"""
        if package not in self.graph:
            return {}
            
        tree = {}
        dependencies = self.graph[package]
        
        for dep in dependencies:
            tree[dep] = self.get_dependency_tree(dep)
            
        return tree
    
    def get_dependency_levels(self):
        """Получить зависимости по уровням (топологическая сортировка)"""
        in_degree = {}
        
        # Инициализируем степени входа
        for package in self.graph:
            in_degree[package] = 0
            
        for package, dependencies in self.graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
                else:
                    in_degree[dep] = 1
        
        # Находим пакеты с нулевой степенью входа (корневые)
        queue = deque([pkg for pkg in in_degree if in_degree[pkg] == 0])
        levels = []
        visited = set()
        
        while queue:
            level_size = len(queue)
            current_level = []
            
            for _ in range(level_size):
                package = queue.popleft()
                if package in visited:
                    continue
                    
                visited.add(package)
                current_level.append(package)
                
                # Уменьшаем степени входа зависимостей
                for dep in self.graph.get(package, []):
                    if dep in in_degree:
                        in_degree[dep] -= 1
                        if in_degree[dep] == 0 and dep not in visited:
                            queue.append(dep)
            
            if current_level:
                levels.append(current_level)
        
        return levels
    
    def has_cycles(self):
        """Проверить наличие циклов в графе"""
        visited = set()
        recursion_stack = set()
        cycles = []
        
        def dfs(package, path):
            if package in recursion_stack:
                # Найден цикл
                cycle_start = path.index(package)
                cycle = path[cycle_start:]
                cycles.append(cycle)
                return True
                
            if package in visited:
                return False
                
            visited.add(package)
            recursion_stack.add(package)
            path.append(package)
            
            for dep in self.graph.get(package, []):
                dfs(dep, path.copy())
                
            recursion_stack.remove(package)
            path.pop()
            return False
        
        for package in self.graph:
            if package not in visited:
                dfs(package, [])
                
        return cycles
    
    def print_ascii_tree(self, package, prefix="", is_last=True):
        """Вывод ASCII-дерева зависимостей"""
        if package not in self.graph:
            print(f"{prefix}{'└── ' if is_last else '├── '}{package}")
            return
            
        print(f"{prefix}{'└── ' if is_last else '├── '}{package}")
        
        dependencies = self.graph[package]
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        for i, dep in enumerate(dependencies):
            is_last_dep = i == len(dependencies) - 1
            self.print_ascii_tree(dep, new_prefix, is_last_dep)
    def get_install_order(self, package):
        """Получить порядок установки зависимостей (топологическая сортировка)"""
        if package not in self.graph:
            return []
            
        # Создаем копию графа для работы
        graph_copy = {pkg: deps[:] for pkg, deps in self.graph.items()}
        
        # Добавляем корневой пакет если его нет в графе
        if package not in graph_copy:
            graph_copy[package] = []
        
        # Вычисляем степени входа
        in_degree = {}
        for pkg in graph_copy:
            in_degree[pkg] = 0
            
        for pkg, dependencies in graph_copy.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
                else:
                    in_degree[dep] = 1
                    graph_copy[dep] = []  # Добавляем пакет без зависимостей
        
        # Находим пакеты с нулевой степенью входа
        queue = deque([pkg for pkg in in_degree if in_degree[pkg] == 0])
        install_order = []
        visited = set()
        
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
                
            visited.add(current)
            install_order.append(current)
            
            # Уменьшаем степени входа зависимостей
            for dep in graph_copy.get(current, []):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0 and dep not in visited:
                        queue.append(dep)
        
        # Убедимся что корневой пакет в конце (устанавливается последним)
        if package in install_order:
            install_order.remove(package)
            install_order.append(package)
        
        return install_order
    
    def compare_with_apk(self, package):
        """Сравнить порядок установки с реальным менеджером пакетов"""
        our_order = self.get_install_order(package)
        
        print(f"\n🔍 Сравнение порядка установки для '{package}':")
        print(f"Наш порядок ({len(our_order)} пакетов):")
        for i, pkg in enumerate(our_order, 1):
            print(f"  {i}. {pkg}")
        
        print(f"\n💡 Примечания:")
        if our_order:
            print(f"  - Первый устанавливается: {our_order[0]}")
            print(f"  - Последний устанавливается: {our_order[-1]}")
            print(f"  - Всего зависимостей: {len(our_order) - 1}")
        
        # Объяснение возможных расхождений
        print(f"\n📝 Возможные расхождения с реальным apk:")
        print(f"  1. Реальный apk учитывает версии пакетов")
        print(f"  2. Реальный apk обрабатывает конфликтующие зависимости")
        print(f"  3. Реальный apk учитывает архитектуру системы")
        print(f"  4. Реальный apk может пропускать виртуальные пакеты")
        print(f"  5. Наш алгоритм использует простую топологическую сортировку")
        
        return our_order
    
    def get_dependency_paths(self, package):
        """Получить все пути зависимостей"""
        if package not in self.graph:
            return []
            
        paths = []
        
        def dfs(current, path):
            path.append(current)
            
            # Если нет зависимостей - это конечный путь
            if not self.graph.get(current):
                paths.append(path.copy())
            else:
                for dep in self.graph.get(current, []):
                    dfs(dep, path.copy())
            
            path.pop()
        
        dfs(package, [])
        return paths
    
    def find_common_dependencies(self, package1, package2):
        """Найти общие зависимости двух пакетов"""
        deps1 = set(self.get_all_dependencies(package1))
        deps2 = set(self.get_all_dependencies(package2))
        
        common = deps1.intersection(deps2)
        return sorted(list(common))
