from .errors import ConfigurationError

class PlantUMLVisualizer:
    def __init__(self, dependency_graph):
        self.dependency_graph = dependency_graph
        self.plantuml_code = ""
    
    def generate_plantuml(self, root_package):
        """Генерация кода PlantUML для графа зависимостей"""
        if root_package not in self.dependency_graph.graph:
            raise ConfigurationError(f"Пакет '{root_package}' не найден в графе")
        
        plantuml = ["@startuml", "hide empty description", "skinparam monochrome true"]
        
        # Добавляем все узлы и связи
        visited = set()
        
        def add_connections(package):
            if package in visited:
                return
            visited.add(package)
            
            dependencies = self.dependency_graph.graph.get(package, [])
            for dep in dependencies:
                # Добавляем связь
                plantuml.append(f'"{package}" --> "{dep}"')
                # Рекурсивно добавляем зависимости
                add_connections(dep)
        
        # Начинаем с корневого пакета
        add_connections(root_package)
        
        # Добавляем стили для корневого пакета
        plantuml.append(f'"{root_package}" #LightBlue')
        
        plantuml.append("@enduml")
        self.plantuml_code = "\n".join(plantuml)
        return self.plantuml_code
    
    def generate_simple_plantuml(self, root_package):
        """Упрощенная версия для лучшей читаемости"""
        if root_package not in self.dependency_graph.graph:
            raise ConfigurationError(f"Пакет '{root_package}' не найден в графе")
        
        plantuml = [
            "@startuml",
            "left to right direction",
            "skinparam nodesep 10",
            "skinparam ranksep 50",
            "skinparam packageStyle rect",
            "skinparam shadowing false",
            ""
        ]
        
        # Группируем по уровням глубины
        levels = {}
        for package in self.dependency_graph.graph:
            depth = self.dependency_graph.depth_map.get(package, 0)
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(package)
        
        # Добавляем пакеты сгруппированные по уровням
        for depth in sorted(levels.keys()):
            if depth == 0:
                # Корневой пакет
                plantuml.append(f'rectangle "{root_package}" as {root_package.replace(".", "_")} #LightBlue')
            else:
                for package in levels[depth]:
                    plantuml.append(f'rectangle "{package}" as {package.replace(".", "_").replace(":", "_").replace("/", "_")}')
        
        plantuml.append("")
        
        # Добавляем связи
        visited_connections = set()
        for package, dependencies in self.dependency_graph.graph.items():
            for dep in dependencies:
                connection = f'{package.replace(".", "_").replace(":", "_").replace("/", "_")} --> {dep.replace(".", "_").replace(":", "_").replace("/", "_")}'
                if connection not in visited_connections:
                    plantuml.append(connection)
                    visited_connections.add(connection)
        
        plantuml.append("@enduml")
        self.plantuml_code = "\n".join(plantuml)
        return self.plantuml_code
    
    def save_plantuml_to_file(self, filename):
        """Сохранить PlantUML код в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.plantuml_code)
        print(f"PlantUML код сохранен в файл: {filename}")
    
    def display_plantuml_info(self):
        """Вывести информацию о сгенерированном PlantUML коде"""
        if not self.plantuml_code:
            print("PlantUML код не сгенерирован")
            return
        
        lines = self.plantuml_code.split('\n')
        print(f"\n📊 PlantUML код ({len(lines)} строк):")
        print("=" * 50)
        for line in lines:
            print(f"  {line}")
        print("=" * 50)
        
        # Статистика
        nodes = set()
        connections = 0
        for line in lines:
            if '-->' in line:
                connections += 1
            elif 'rectangle' in line:
                nodes.add(line.split('"')[1] if '"' in line else "")
        
        print(f"\n📈 Статистика диаграммы:")
        print(f"  Узлов: {len(nodes)}")
        print(f"  Связей: {connections}")
        
        print(f"\n🌐 Как использовать:")
        print(f"  1. Скопируйте код выше")
        print(f"  2. Перейдите на: http://www.plantuml.com/plantuml/")
        print(f"  3. Вставьте код и нажмите 'Submit'")
        print(f"  4. Получите готовую диаграмму!")
    
    def compare_with_apk_tools(self, package_name):
        """Сравнение с штатными инструментами визуализации"""
        print(f"\n🔍 Сравнение с штатными инструментами Alpine Linux:")
        print(f"Пакет: {package_name}")
        
        print(f"\n📋 Наша реализация (PlantUML):")
        print(f"  ✅ Генерирует текстовое представление графа")
        print(f"  ✅ Поддерживает визуализацию в браузере")
        print(f"  ✅ Показывает направление зависимостей")
        print(f"  ✅ Группирует по уровням глубины")
        
        print(f"\n📋 Штатные инструменты Alpine (apk):")
        print(f"  ✅ apk info -R {package_name} - показывает зависимости")
        print(f"  ✅ apk search -v {package_name} - показывает информацию")
        print(f"  ❌ Нет встроенной графической визуализации")
        print(f"  ❌ Нет генерации диаграмм зависимостей")
        
        print(f"\n💡 Основные расхождения:")
        print(f"  1. Наш инструмент генерирует графические диаграммы")
        print(f"  2. Штатные инструменты показывают только текстовый список")
        print(f"  3. PlantUML позволяет видеть структуру графа")
        print(f"  4. Наш подход лучше для анализа сложных зависимостей")
        
        print(f"\n🎯 Преимущества нашего подхода:")
        print(f"  • Визуальное представление сложных зависимостей")
        print(f"  • Возможность увидеть циклические зависимости")
        print(f"  • Понимание структуры графа на одном взгляде")
        print(f"  • Легкое разделение на уровни вложенности")
