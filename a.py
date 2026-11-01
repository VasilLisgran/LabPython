import tkinter as tk
from tkinter import ttk

CELL_W = 70
CELL_H = 60
COLS = 12

halls = ["Большой зал", "Малый зал", "Переговорная"]
orgs = ["ООО Вектор", "ЗАО Старт", "ИП Петров", "Школа Знание", "Компания Альфа"]

bookings = [
    {"hall": "Большой зал", "start": 4, "end": 12, "org": "ООО Вектор", "event": "Стратегическая сессия"},
    {"hall": "Большой зал", "start": 20, "end": 30, "org": "ЗАО Старт", "event": "Презентация продукта"},
    {"hall": "Малый зал", "start": 0, "end": 6, "org": "ИП Петров", "event": "Консультация"},
]

start_cell = None
end_cell = None
picking = False

root = tk.Tk()
root.title("Занятость залов")

hall_var = tk.StringVar(value=halls[0])
org_var = tk.StringVar(value=orgs[0])
event_var = tk.StringVar()
info_var = tk.StringVar(value="Время не выбрано")


def time_str(i):
    t = 9 * 60 + i * 15
    return f"{t // 60:02d}:{t % 60:02d}"


def draw():
    canvas.delete("all")
    for i in range(48):
        x = 10 + (i % COLS) * CELL_W
        y = 10 + (i // COLS) * (CELL_H + 10)
        color = "#b7e4b7"
        for b in bookings:
            if b["hall"] == hall_var.get() and b["start"] <= i < b["end"]:
                color = "#e05555"
        if start_cell is not None and start_cell <= i <= end_cell:
            color = "#ffe066"
        canvas.create_rectangle(x, y, x + CELL_W, y + CELL_H, fill=color, outline="gray")
        canvas.create_text(x + 3, y + 3, text=time_str(i), anchor="nw", font=("Arial", 7))
    for b in bookings:
        if b["hall"] == hall_var.get():
            x = 10 + (b["start"] % COLS) * CELL_W
            y = 10 + (b["start"] // COLS) * (CELL_H + 10)
            canvas.create_text(x + 5, y + 30, text=b["org"], anchor="w", fill="white")


def on_click(event):
    global start_cell, end_cell, picking
    c = (event.x - 10) // CELL_W
    r = (event.y - 10) // (CELL_H + 10)
    if c < 0 or c >= COLS or r < 0 or r > 3:
        return
    i = r * COLS + c
    if picking:
        if i < start_cell:
            end_cell = start_cell
            start_cell = i
        else:
            end_cell = i
        picking = False
    else:
        start_cell = i
        end_cell = i
        picking = True
    minutes = (end_cell - start_cell + 1) * 15
    info_var.set(f"Организация: {org_var.get()} | Время: {time_str(start_cell)} - {time_str(end_cell + 1)} ({minutes} мин.)")
    draw()


def on_hall_change(event=None):
    draw()


def book():
    print("пока не работает")


top = tk.Frame(root)
top.pack(padx=10, pady=10, fill="x")

tk.Label(top, text="Зал:").pack(side="left")
hall_box = ttk.Combobox(top, textvariable=hall_var, values=halls, state="readonly")
hall_box.pack(side="left", padx=5)
hall_box.bind("<<ComboboxSelected>>", on_hall_change)

tree = ttk.Treeview(root, columns=("time", "org", "event"), show="headings", height=5)
tree.heading("time", text="Время")
tree.heading("org", text="Организация")
tree.heading("event", text="Мероприятие")
tree.pack(padx=10, fill="x")

for b in bookings:
    t = time_str(b["start"]) + " - " + time_str(b["end"])
    tree.insert("", "end", values=(t, b["org"], b["event"]))

canvas = tk.Canvas(root, width=860, height=290, bg="white")
canvas.pack(padx=10, pady=10)
canvas.bind("<Button-1>", on_click)

form = tk.Frame(root)
form.pack(padx=10, pady=(0, 10))

ttk.Combobox(form, textvariable=org_var, values=orgs).grid(row=0, column=0, padx=5)
tk.Entry(form, textvariable=event_var, width=30).grid(row=0, column=1, padx=5)
tk.Button(form, text="Утвердить бронь", command=book).grid(row=0, column=2, padx=5)
tk.Label(form, textvariable=info_var).grid(row=1, column=0, columnspan=3, pady=5)

draw()

root.mainloop()
