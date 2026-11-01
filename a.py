import tkinter as tk
from tkinter import ttk
 
W = 70
H = 60
halls = ["Большой зал", "Малый зал", "Переговорная"]
orgs = ["ООО Вектор", "ЗАО Старт", "ИП Петров", "Школа Знание", "Компания Альфа"]
bookings = [
    ["Большой зал", 4, 12, "ООО Вектор", "Стратегическая сессия"],
    ["Большой зал", 20, 30, "ЗАО Старт", "Презентация продукта"],
    ["Малый зал", 0, 6, "ИП Петров", "Консультация"],
]
first = last = None
picking = False
 
root = tk.Tk()
root.title("Занятость залов")
hall_var = tk.StringVar(value=halls[0])
org_var = tk.StringVar(value=orgs[0])
event_var = tk.StringVar()
info_var = tk.StringVar(value="Время не выбрано")
