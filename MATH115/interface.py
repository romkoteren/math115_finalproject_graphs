import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
import random
import math


# =============================================================================
# ЧАСТИНА 1: ЛОГІКА ПРОЄКТУ (Backend)
# Цей клас відповідає за математичну частину та структуру даних.
# =============================================================================
class GraphProject:
    def __init__(self, n):
        """
        Конструктор класу.
        n: кількість вершин у графі.
        Використовується матриця суміжності.
        """
        self.n = n
        # Створюємо матрицю n x n, заповнену нулями (немає ребер)
        self.matrix = [[0 for _ in range(n)] for _ in range(n)]

    def generate_random(self, density):
        """
        Генерування випадкового графу за моделлю Ердеша-Реньї.
        density: щільність графу (0.0 - 1.0).
        """
        # Очищуємо матрицю перед новою генерацією
        self.matrix = [[0 for _ in range(self.n)] for _ in range(self.n)]

        # Максимальна кількість ребер для орієнтованого графу: n * (n - 1) [cite: 74]
        max_edges = self.n * (self.n - 1)
        target_edges = int(max_edges * density)

        count = 0
        # Додаємо ребра випадковим чином, поки не досягнемо потрібної кількості
        while count < target_edges:
            u = random.randint(0, self.n - 1)
            v = random.randint(0, self.n - 1)

            # Перевірка:
            # 1. u != v (граф простий, без петель)
            # 2. matrix[u][v] == 0 (ребро ще не існує)
            if u != v and self.matrix[u][v] == 0:
                self.matrix[u][v] = 1
                count += 1

    def floyd_warshall(self):
        """
        Алгоритм Уоршелла для побудови матриці досяжності (транзитивного замикання).
        Складність: O(n^3).
        """
        # Створюємо копію матриці, щоб не змінювати початковий граф
        reach = [row[:] for row in self.matrix]

        # Три вкладені цикли - основа алгоритму
        for k in range(self.n):  # Проміжна вершина
            for i in range(self.n):  # Початкова вершина
                # Оптимізація: якщо немає шляху i -> k, то немає сенсу перевіряти далі
                if reach[i][k] == 1:
                    for j in range(self.n):  # Кінцева вершина
                        # Якщо є шлях i -> k ТА шлях k -> j, то є шлях i -> j
                        if reach[k][j] == 1:
                            reach[i][j] = 1
        return reach


# =============================================================================
# ЧАСТИНА 2: ВІЗУАЛІЗАЦІЯ
# =============================================================================
class DraggableGraph:
    def __init__(self, ax, canvas, graph, pos):
        self.ax = ax  # Осі графіку Matplotlib
        self.canvas = canvas  # Полотно, на якому малюємо
        self.graph = graph  # Об'єкт графу NetworkX
        self.pos = pos  # Словник координат вершин {id: (x, y)}
        self.dragged_node = None  # Вершина, яку зараз тягнуть (None, якщо ніяку)

        # Підписуємося на події миші (клік, рух, відпускання)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        """Обробка натискання кнопки миші"""
        if event.inaxes != self.ax: return  # Ігноруємо кліки поза графіком

        # Перевіряємо, чи клікнули ми поруч із якоюсь вершиною
        for node, (x, y) in self.pos.items():
            # math.hypot рахує відстань між курсором і центром вершини
            if math.hypot(x - event.xdata, y - event.ydata) < 0.15:  # 0.15 - радіус чутливості
                self.dragged_node = node
                break

    def on_motion(self, event):
        """Обробка руху миші (перетягування)"""
        if self.dragged_node is not None and event.inaxes == self.ax:
            # Оновлюємо координати обраної вершини
            self.pos[self.dragged_node] = (event.xdata, event.ydata)
            self.update_plot()  # Перемальовуємо граф

    def on_release(self, event):
        """Обробка відпускання кнопки миші"""
        self.dragged_node = None  # Скидаємо вибір

    def update_plot(self):
        """Перемальовування графу з новими координатами"""
        self.ax.clear()  # Очищуємо попередній кадр

        # Малюємо граф за допомогою NetworkX
        nx.draw(self.graph, self.pos, ax=self.ax,
                with_labels=True,
                node_color='skyblue',
                node_size=500,
                edge_color='gray',
                arrows=True)  # arrows=True важливе для орієнтованих графів

        self.canvas.draw_idle()  # Оптимізований метод оновлення полотна


# =============================================================================
# ЧАСТИНА 3: ГОЛОВНЕ ВІКНО ПРОГРАМИ (GUI)
# Використовує бібліотеку Tkinter.
# =============================================================================
class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DM Project: Interactive Graph (Warshall Algorithm)")
        self.root.geometry("1100x750")  # Розмір вікна

        self.graph_logic = None  # Тут буде об'єкт GraphProject
        self.draggable_helper = None  # Тут буде об'єкт DraggableGraph
        self.pos = None  # Збереження позицій вершин, щоб вони не стрибали

        # --- Ліва панель (Кнопки та ввід даних) ---
        control_frame = ttk.LabelFrame(root, text="Налаштування")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Поле вводу кількості вершин
        ttk.Label(control_frame, text="Кількість вершин (N):").pack(pady=5)
        self.entry_n = ttk.Entry(control_frame)
        self.entry_n.insert(0, "10")  # Значення за замовчуванням
        self.entry_n.pack(pady=5)

        # Поле вводу щільності
        ttk.Label(control_frame, text="Щільність (0.0 - 1.0):").pack(pady=5)
        self.entry_density = ttk.Entry(control_frame)
        self.entry_density.insert(0, "0.2")
        self.entry_density.pack(pady=5)

        # Кнопка генерації
        self.btn_generate = ttk.Button(control_frame, text="Генерувати Граф", command=self.generate_graph)
        self.btn_generate.pack(pady=15, fill=tk.X)

        # Кнопка запуску алгоритму (спочатку неактивна)
        self.btn_run = ttk.Button(control_frame, text="Запустити Уоршелла", command=self.run_algorithm,
                                  state=tk.DISABLED)
        self.btn_run.pack(pady=5, fill=tk.X)

        # Інструкція для користувача
        ttk.Label(control_frame, text="Інструкція:").pack(pady=(20, 5))
        lbl_instr = tk.Label(control_frame,
                             text="1. Щоб рухати вершини:\n   вимкніть 'Pan' у меню знизу.\n\n2. Щоб рухати все поле:\n   увімкніть 'Pan' (хрестик).",
                             justify=tk.LEFT, fg="gray40")
        lbl_instr.pack(pady=5)

        # --- Права панель (Місце для графіка) ---
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Створення фігури Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        # Інтеграція Matplotlib у Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Додавання панелі інструментів (Zoom, Pan, Save)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_graph(self):
        """Метод, що викликається при натисканні 'Генерувати Граф'"""
        try:
            # Зчитування даних з полів
            n = int(self.entry_n.get())
            density = float(self.entry_density.get())

            # Валідація даних
            if not (0 <= density <= 1): raise ValueError

            # 1. Створення логічного графу
            self.graph_logic = GraphProject(n)
            self.graph_logic.generate_random(density)

            # Активуємо кнопку запуску алгоритму
            self.btn_run.config(state=tk.NORMAL)

            # 2. Підготовка до візуалізації (NetworkX)
            self.G = nx.DiGraph()
            for i in range(n): self.G.add_node(i)  # Додаємо вершини

            # Додаємо ребра на основі матриці суміжності
            for i in range(n):
                for j in range(n):
                    if self.graph_logic.matrix[i][j] == 1:
                        self.G.add_edge(i, j)

            # Обчислюємо початкові позиції (по колу) один раз
            self.pos = nx.circular_layout(self.G)

            # Малюємо граф
            self.draw_interactive(title="Початковий Граф")

        except ValueError:
            messagebox.showerror("Помилка", "Перевірте, чи правильно введені числа!")

    def run_algorithm(self):
        """Метод, що викликається при натисканні 'Запустити Уоршелла'"""
        if not self.graph_logic: return

        # Виконуємо алгоритм
        reach_matrix = self.graph_logic.floyd_warshall()

        # Якщо граф невеликий, оновлюємо візуалізацію
        if self.graph_logic.n <= 20:
            # Очищуємо старі ребра
            self.G.clear_edges()
            # Додаємо нові ребра з матриці досяжності
            for i in range(len(reach_matrix)):
                for j in range(len(reach_matrix)):
                    if reach_matrix[i][j] == 1:
                        self.G.add_edge(i, j)

            # Малюємо результат (використовуючи ті самі позиції вершин!)
            self.draw_interactive(title="Матриця досяжності (Результат)")
        else:
            messagebox.showinfo("Інфо", "Алгоритм виконано! (Граф завеликий для візуалізації результату)")

    def draw_interactive(self, title):
        """Допоміжний метод для малювання та підключення перетягування"""
        self.ax.clear()

        # Малюємо статичну картинку
        nx.draw(self.G, self.pos, ax=self.ax,
                with_labels=True,
                node_color='skyblue',
                node_size=500,
                edge_color='gray',
                arrows=True)
        self.ax.set_title(title)
        self.canvas.draw()

        # Підключаємо клас DraggableGraph для інтерактивності
        self.draggable_helper = DraggableGraph(self.ax, self.canvas, self.G, self.pos)


# Точка входу в програму
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()