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
        queue.append((root_package, 0))  # (package, depth)
        self.graph = {}
        self.visited = set()
        self.depth_map = {root_package: 0}
        cycles = []
        
        while queue:
            current_package, depth = queue.popleft()
            
            # Проверка максимальной глубины
            if depth >= self.max_depth:
                continue
                
            # Если пакет уже посещен на меньшей глубине, пропускаем
            if current_package in self.visited:
                # Проверяем на циклические зависимости
                if current_package in self.get_ancestors(current_package):
                    cycles.append(current_package)
                continue
                
            self.visited.add(current_package)
            
            try:
                # Получаем зависимости текущего пакета
                dependencies = self.repository_manager.get_package_dependencies(current_package)
                self.graph[current_package] = dependencies
                
                # Добавляем зависимости в очередь
                for dep in dependencies:
                    if dep not in self.depth_map or self.depth_map[dep] > depth + 1:
                        self.depth_map[dep] = depth + 1
                    queue.append((dep, depth + 1))
                    
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
