import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"
MIN_LENGTH = 4
MAX_LENGTH = 64


def load_history():
    """Загружает историю из JSON-файла."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """Сохраняет историю в JSON-файл."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        # Переменные настроек
        self.length_var = tk.IntVar(value=12)
        self.digits_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        # История
        self.history = load_history()

        self.create_widgets()
        self.refresh_history_table()

    def create_widgets(self):
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Длина
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        length_scale = ttk.Scale(settings_frame, from_=MIN_LENGTH, to=MAX_LENGTH,
                                 orient="horizontal", variable=self.length_var,
                                 command=self.on_length_change)
        length_scale.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.length_label = ttk.Label(settings_frame, text=str(self.length_var.get()))
        self.length_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.digits_var).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(settings_frame, text="Строчные буквы (a-z)", variable=self.lower_var).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(settings_frame, text="Заглавные буквы (A-Z)", variable=self.upper_var).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$...)", variable=self.special_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Кнопка генерации
        gen_button = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        gen_button.grid(row=3, column=0, columnspan=3, pady=10)

        # Фрейм истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица
        columns = ("№", "Пароль", "Длина", "Дата")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        self.tree.heading("№", text="№")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Дата", text="Дата")
        self.tree.column("№", width=40, anchor="center")
        self.tree.column("Пароль", width=300, anchor="w")
        self.tree.column("Длина", width=60, anchor="center")
        self.tree.column("Дата", width=150, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        hist_btn_frame = ttk.Frame(self.root)
        hist_btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(hist_btn_frame, text="Копировать выделенный", command=self.copy_password).pack(side="left", padx=5)
        ttk.Button(hist_btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)

    def on_length_change(self, event=None):
        """Обновляет метку длины при движении ползунка."""
        self.length_label.config(text=str(int(float(self.length_var.get()))))

    def generate_password(self):
        """Генерирует пароль согласно выбранным настройкам и добавляет в историю."""
        length = int(float(self.length_var.get()))
        if length < MIN_LENGTH or length > MAX_LENGTH:
            messagebox.showerror("Ошибка", f"Длина пароля должна быть от {MIN_LENGTH} до {MAX_LENGTH}.")
            return

        chars = ""
        if self.digits_var.get():
            chars += string.digits
        if self.lower_var.get():
            chars += string.ascii_lowercase
        if self.upper_var.get():
            chars += string.ascii_uppercase
        if self.special_var.get():
            chars += string.punctuation

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов.")
            return

        password = ''.join(random.choice(chars) for _ in range(length))

        # Добавление в историю
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "password": password,
            "length": length,
            "date": now
        }
        self.history.append(entry)
        save_history(self.history)
        self.refresh_history_table()

    def refresh_history_table(self):
        """Обновляет таблицу истории."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, entry in enumerate(self.history, start=1):
            self.tree.insert("", "end", values=(i, entry["password"], entry["length"], entry["date"]))

    def copy_password(self):
        """Копирует выделенный пароль в буфер обмена."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пароль в таблице.")
            return
        password = self.tree.item(selected[0])["values"][1]
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.root.update()
        messagebox.showinfo("Готово", "Пароль скопирован в буфер обмена.")

    def clear_history(self):
        """Очищает историю после подтверждения."""
        if messagebox.askyesno("Подтверждение", "Удалить всю историю паролей?"):
            self.history.clear()
            save_history(self.history)
            self.refresh_history_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
    
