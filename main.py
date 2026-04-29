import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

# ВСТАВЬТЕ ВАШ КЛЮЧ НИЖЕ
API_KEY = "ВАШ_КЛЮЧ_API" 
HISTORY_FILE = 'conversion_history.json'

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x550")

        self.history = self.load_history()
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "KZT"]

        self.setup_ui()

    def setup_ui(self):
        # Панель ввода
        frame_input = ttk.LabelFrame(self.root, text="Параметры конвертации", padding=15)
        frame_input.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame_input, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.entry_amount = ttk.Entry(frame_input)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="Из:").grid(row=0, column=2, padx=5)
        self.combo_from = ttk.Combobox(frame_input, values=self.currencies, width=8, state="readonly")
        self.combo_from.set("USD")
        self.combo_from.grid(row=0, column=3, padx=5)

        ttk.Label(frame_input, text="В:").grid(row=0, column=4, padx=5)
        self.combo_to = ttk.Combobox(frame_input, values=self.currencies, width=8, state="readonly")
        self.combo_to.set("RUB")
        self.combo_to.grid(row=0, column=5, padx=5)

        self.btn_convert = ttk.Button(frame_input, text="Конвертировать", command=self.convert)
        self.btn_convert.grid(row=1, column=0, columnspan=6, pady=15)

        # Результат
        self.label_result = ttk.Label(self.root, text="Результат: ---", font=("Arial", 12, "bold"))
        self.label_result.pack(pady=10)

        # История
        frame_hist = ttk.LabelFrame(self.root, text="История операций", padding=10)
        frame_hist.pack(padx=10, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(frame_hist, columns=("date", "from", "to", "res"), show="headings")
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("from", text="Исходная сумма")
        self.tree.heading("to", text="Валюта")
        self.tree.heading("res", text="Итог")
        
        self.tree.column("date", width=120)
        self.tree.column("res", width=100)
        
        self.tree.pack(fill="both", expand=True)

        self.refresh_table()

    def convert(self):
        # 1. Проверка API-ключа
        if API_KEY == "ВАШ_КЛЮЧ_API" or not API_KEY:
            messagebox.showerror("Ошибка API", "Пожалуйста, вставьте ваш реальный API-ключ в код!")
            return

        # 2. Валидация суммы
        amount_str = self.entry_amount.get()
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Введите положительное число в поле суммы!")
            return

        # 3. Валидация выбора валют
        from_curr = self.combo_from.get()
        to_curr = self.combo_to.get()
        if not from_curr or not to_curr:
            messagebox.showwarning("Ошибка", "Выберите валюты из списка!")
            return

        # 4. Запрос к API
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_curr}/{to_curr}/{amount}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("result") == "success":
                result = round(data["conversion_result"], 2)
                res_text = f"{amount} {from_curr} = {result} {to_curr}"
                self.label_result.config(text=f"Результат: {res_text}")

                # Сохранение и обновление (методы теперь ВНУТРИ класса)
                new_entry = {
                    "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                    "from": f"{amount} {from_curr}",
                    "to": to_curr,
                    "result": f"{result}"
                }
                self.history.append(new_entry)
                self.save_history()
                self.refresh_table()
            else:
                error_msg = data.get("error-type", "Unknown error")
                messagebox.showerror("Ошибка API", f"Сервер вернул ошибку: {error_msg}")
        except Exception as e:
            messagebox.showerror("Ошибка сети", f"Не удалось связаться с сервером: {e}")

    def load_history(self):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for h in reversed(self.history):
            self.tree.insert("", "end", values=(h['date'], h['from'], h['to'], h['result']))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()