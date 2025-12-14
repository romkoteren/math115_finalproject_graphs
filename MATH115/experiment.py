import random
import time
import copy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# --- 1. Клас Графу та Алгоритм  ---
class GraphProject:
    def __init__(self, n):
        self.n = n
        # Ініціалізація матриці нулями
        self.matrix = [[0 for _ in range(n)] for _ in range(n)]

    def generate_random(self, density):
        """
        Генерує випадковий орієнтований граф заданої щільності.
        density: 0.0 - 1.0
        """
        # Очищуємо матрицю
        self.matrix = [[0 for _ in range(self.n)] for _ in range(self.n)]

        max_edges = self.n * (self.n - 1)
        target_edges = int(max_edges * density)

        count = 0
        # Для щільних графів ефективніше спочатку заповнити, а потім видаляти,
        # але для навчальної задачі (N <= 200) random.randint підійде.
        while count < target_edges:
            u = random.randint(0, self.n - 1)
            v = random.randint(0, self.n - 1)

            if u != v and self.matrix[u][v] == 0:
                self.matrix[u][v] = 1
                count += 1

    def warshall_algorithm(self):
        """
        Класичний алгоритм Уоршелла для побудови транзитивного замикання.
        """
        # Робимо глибоку копію, щоб не змінювати оригінальну матрицю
        # (хоча для експерименту це не критично, але правильний тон)
        reach = [row[:] for row in self.matrix]

        n = self.n
        for k in range(n):
            for i in range(n):
                # Оптимізація: якщо з i в k немає шляху, то внутрішній цикл не має сенсу
                if reach[i][k] == 1:
                    for j in range(n):
                        if reach[k][j] == 1:
                            reach[i][j] = 1

        return reach


# --- 2. Експериментальна частина ---

def run_experiments():
    # [cite_start]Параметри згідно з методичкою [cite: 83, 85]
    # Розміри від 20 до 200 (крок 20 дасть 10 точок)
    sizes = list(range(20, 201, 20))

    # [cite_start]Щільності: 5 різних значень [cite: 85]
    densities = [0.1, 0.3, 0.5, 0.7, 0.9]

    # [cite_start]Кількість повторів для усереднення [cite: 82]
    repeats = 20

    # Словник для збереження результатів: {density: [time_for_size_20, time_for_size_40...]}
    results = {d: [] for d in densities}

    print(f"Починаємо експерименти...")
    print(f"Розміри: {sizes}")
    print(f"Щільності: {densities}")
    print("-" * 50)

    for density in densities:
        print(f"Тестування для щільності {density * 100}%: ", end="")

        for n in sizes:
            total_time = 0

            # Повторюємо експеримент `repeats` разів
            for _ in range(repeats):
                # 1. Генерація (не входить у час заміру)
                g = GraphProject(n)
                g.generate_random(density)

                # 2. Замір часу
                start_time = time.time()
                g.warshall_algorithm()
                end_time = time.time()

                total_time += (end_time - start_time)

            # Середній час
            avg_time = total_time / repeats
            results[density].append(avg_time)
            print(".", end="", flush=True)  # Індикатор прогресу

        print(" Готово!")

    return sizes, results


# --- 3. Візуалізація та Збереження ---

def plot_and_save_results(sizes, results):
    # Створюємо DataFrame для зручного збереження в CSV
    df_data = {"Size": sizes}
    for density, times in results.items():
        df_data[f"Density {density}"] = times

    df = pd.DataFrame(df_data)
    # Зберігаємо таблицю
    df.to_csv("experiment_results.csv", index=False)
    print("\nРезультати збережено у 'experiment_results.csv'")

    # Побудова графіка
    plt.figure(figsize=(10, 6))

    for density, times in results.items():
        plt.plot(sizes, times, marker='o', label=f'Density {density}')

    plt.title('Залежність часу виконання алгоритму Уоршелла від розміру графу')
    plt.xlabel('Кількість вершин (N)')
    plt.ylabel('Середній час виконання (сек)')
    plt.legend()
    plt.grid(True)

    # Збереження графіка
    plt.savefig("warshall_complexity.png")
    print("Графік збережено як 'warshall_complexity.png'")
    plt.show()


# --- Запуск ---
if __name__ == "__main__":
    sizes, results = run_experiments()
    plot_and_save_results(sizes, results)