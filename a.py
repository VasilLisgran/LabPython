import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import calendar

CELL_W = 70
CELL_H = 60
COLS = 12

halls = ["Большой зал", "Малый зал", "Переговорная", "Конференц-зал", "Учебный зал"]
orgs = ["ООО Вектор", "ЗАО Старт", "ИП Петров", "Школа Знание", "Компания Альфа"]
months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
current_date = date.today().strftime("%d.%m.%Y")

bookings = [
    {"date": current_date, "hall": "Большой зал", "start": 4, "end": 12, "org": "ООО Вектор", "event": "Стратегическая сессия"},
    {"date": current_date, "hall": "Большой зал", "start": 20, "end": 30, "org": "ЗАО Старт", "event": "Презентация продукта"},
    {"date": current_date, "hall": "Малый зал", "start": 0, "end": 6, "org": "ИП Петров", "event": "Консультация"},
    {"date": current_date, "hall": "Переговорная", "start": 8, "end": 14, "org": "Компания Альфа", "event": "Переговоры с поставщиком"},
]

start_cell = None
end_cell = None
picking = False
cal_win = None
cal_year = 0
cal_month = 0
cal_frame = None
cal_title = None
edit_win = None
edit_n = 0

root = tk.Tk()
root.title("Занятость залов")

hall_var = tk.StringVar(value=halls[0])
date_var = tk.StringVar(value=current_date)
org_var = tk.StringVar(value=orgs[0])
event_var = tk.StringVar()
info_var = tk.StringVar()
edit_date = tk.StringVar()
edit_hall = tk.StringVar()
edit_org = tk.StringVar()
edit_event = tk.StringVar()
edit_start = tk.StringVar()
edit_end = tk.StringVar()


def time_str(i):
    t = 9 * 60 + i * 15
    return f"{t // 60:02d}:{t % 60:02d}"


times = [time_str(i) for i in range(49)]


def duration_str(cells):
    minutes = cells * 15
    return f"{minutes // 60} ч. {minutes % 60} мин."


def update_info():
    org = org_var.get().strip()
    if org == "":
        org = "не выбрана"
    if start_cell is None:
        info_var.set(f"Организация: {org} | Время: не выбрано")
    else:
        info_var.set(f"Организация: {org} | Время: {time_str(start_cell)} - {time_str(end_cell + 1)} ({duration_str(end_cell - start_cell + 1)})")


def find_booking(i):
    for n, b in enumerate(bookings):
        if b["date"] == current_date and b["hall"] == hall_var.get() and b["start"] <= i < b["end"]:
            return n
    return None


def is_busy(a, b):
    for k in range(a, b + 1):
        if find_booking(k) is not None:
            return True
    return False


def add_org(org):
    if org != "" and org not in orgs:
        orgs.append(org)
        org_box["values"] = orgs


def fill_tree():
    tree.delete(*tree.get_children())
    items = []
    for n in range(len(bookings)):
        if bookings[n]["date"] == current_date:
            items.append((bookings[n]["start"], n))
    items.sort()
    for start, n in items:
        b = bookings[n]
        t = time_str(b["start"]) + " - " + time_str(b["end"])
        tree.insert("", "end", iid=str(n), values=(t, b["hall"], b["org"], b["event"]))


def draw():
    canvas.delete("all")
    for i in range(48):
        x = 10 + (i % COLS) * CELL_W
        y = 10 + (i // COLS) * (CELL_H + 10)
        n = find_booking(i)
        color = "#b7e4b7"
        if n is not None:
            color = "#e05555"
        elif start_cell is not None and start_cell <= i <= end_cell:
            color = "#6aa9ff"
        canvas.create_rectangle(x, y, x + CELL_W, y + CELL_H, fill=color, outline="gray")
        canvas.create_text(x + 3, y + 3, text=time_str(i), anchor="nw", font=("Arial", 7))
        if n is not None and (i == bookings[n]["start"] or i % COLS == 0):
            b = bookings[n]
            w = (min(b["end"], i // COLS * COLS + COLS) - i) * CELL_W - 6
            canvas.create_text(x + 3, y + 20, text=b["org"], anchor="nw", width=w, fill="white", font=("Arial", 9, "bold"))


def reset_selection():
    global start_cell, end_cell, picking
    start_cell = None
    end_cell = None
    picking = False
    update_info()
    draw()


def on_click(event):
    global start_cell, end_cell, picking
    c = (event.x - 10) // CELL_W
    r = (event.y - 10) // (CELL_H + 10)
    if c < 0 or c >= COLS or r < 0 or r > 3:
        return
    i = r * COLS + c
    n = find_booking(i)
    if n is not None:
        tree.selection_set(str(n))
        tree.see(str(n))
        return
    if picking:
        a = min(start_cell, i)
        b = max(start_cell, i)
        if is_busy(a, b):
            messagebox.showwarning("Ошибка", "В выбранном интервале есть занятое время")
            return
        start_cell = a
        end_cell = b
        picking = False
    else:
        start_cell = i
        end_cell = i
        picking = True
    update_info()
    draw()


def on_hall_change(event=None):
    reset_selection()


def open_calendar():
    global cal_win, cal_year, cal_month, cal_frame, cal_title
    if cal_win is not None and cal_win.winfo_exists():
        return
    d = datetime.strptime(current_date, "%d.%m.%Y")
    cal_year = d.year
    cal_month = d.month
    cal_win = tk.Toplevel(root)
    cal_win.title("Выбор даты")
    tk.Button(cal_win, text="<", command=prev_month).grid(row=0, column=0, padx=5, pady=5)
    cal_title = tk.Label(cal_win, font=("Arial", 11, "bold"))
    cal_title.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(cal_win, text=">", command=next_month).grid(row=0, column=2, padx=5, pady=5)
    cal_frame = tk.Frame(cal_win)
    cal_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
    show_month()


def show_month():
    for w in cal_frame.winfo_children():
        w.destroy()
    cal_title.config(text=months[cal_month - 1] + " " + str(cal_year))
    for c in range(7):
        tk.Label(cal_frame, text=days[c], width=4).grid(row=0, column=c)
    weeks = calendar.monthcalendar(cal_year, cal_month)
    for r in range(len(weeks)):
        for c in range(7):
            if weeks[r][c] != 0:
                day = tk.Label(cal_frame, text=str(weeks[r][c]), width=4, relief="raised")
                day.grid(row=r + 1, column=c, padx=1, pady=1)
                day.bind("<Button-1>", pick_day)


def prev_month():
    global cal_year, cal_month
    cal_month -= 1
    if cal_month == 0:
        cal_month = 12
        cal_year -= 1
    show_month()


def next_month():
    global cal_year, cal_month
    cal_month += 1
    if cal_month == 13:
        cal_month = 1
        cal_year += 1
    show_month()


def pick_day(event):
    global current_date
    day = int(event.widget["text"])
    current_date = f"{day:02d}.{cal_month:02d}.{cal_year}"
    date_var.set(current_date)
    cal_win.destroy()
    fill_tree()
    reset_selection()


def book():
    org = org_var.get().strip()
    event = event_var.get().strip()
    if org == "" or event == "":
        messagebox.showwarning("Ошибка", "Укажите организацию и название мероприятия")
        return
    if start_cell is None:
        messagebox.showwarning("Ошибка", "Выберите время на ленте")
        return
    if is_busy(start_cell, end_cell):
        messagebox.showwarning("Ошибка", "Выбранное время уже занято")
        reset_selection()
        return
    bookings.append({"date": current_date, "hall": hall_var.get(), "start": start_cell, "end": end_cell + 1, "org": org, "event": event})
    add_org(org)
    event_var.set("")
    fill_tree()
    reset_selection()
    update_dashboard()


def delete_booking():
    sel = tree.selection()
    if len(sel) == 0:
        messagebox.showwarning("Ошибка", "Сначала выберите мероприятие в таблице")
        return
    if messagebox.askyesno("Удаление", "Удалить выбранное мероприятие?"):
        bookings.pop(int(sel[0]))
        fill_tree()
        reset_selection()
        update_dashboard()


def edit_booking():
    global edit_win, edit_n
    if edit_win is not None and edit_win.winfo_exists():
        return
    sel = tree.selection()
    if len(sel) == 0:
        messagebox.showwarning("Ошибка", "Сначала выберите мероприятие в таблице")
        return
    edit_n = int(sel[0])
    b = bookings[edit_n]
    edit_date.set(b["date"])
    edit_hall.set(b["hall"])
    edit_org.set(b["org"])
    edit_event.set(b["event"])
    edit_start.set(time_str(b["start"]))
    edit_end.set(time_str(b["end"]))
    edit_win = tk.Toplevel(root)
    edit_win.title("Изменение мероприятия")
    tk.Label(edit_win, text="Дата (ДД.ММ.ГГГГ)").grid(row=0, column=0, padx=8, pady=5, sticky="w")
    tk.Entry(edit_win, textvariable=edit_date, width=30).grid(row=0, column=1, padx=8, pady=5)
    tk.Label(edit_win, text="Зал").grid(row=1, column=0, padx=8, pady=5, sticky="w")
    ttk.Combobox(edit_win, textvariable=edit_hall, values=halls, state="readonly", width=27).grid(row=1, column=1, padx=8, pady=5)
    tk.Label(edit_win, text="Организация").grid(row=2, column=0, padx=8, pady=5, sticky="w")
    tk.Entry(edit_win, textvariable=edit_org, width=30).grid(row=2, column=1, padx=8, pady=5)
    tk.Label(edit_win, text="Мероприятие").grid(row=3, column=0, padx=8, pady=5, sticky="w")
    tk.Entry(edit_win, textvariable=edit_event, width=30).grid(row=3, column=1, padx=8, pady=5)
    tk.Label(edit_win, text="Начало").grid(row=4, column=0, padx=8, pady=5, sticky="w")
    ttk.Combobox(edit_win, textvariable=edit_start, values=times, state="readonly", width=27).grid(row=4, column=1, padx=8, pady=5)
    tk.Label(edit_win, text="Окончание").grid(row=5, column=0, padx=8, pady=5, sticky="w")
    ttk.Combobox(edit_win, textvariable=edit_end, values=times, state="readonly", width=27).grid(row=5, column=1, padx=8, pady=5)
    tk.Button(edit_win, text="Сохранить изменения", command=save_edit).grid(row=6, column=0, columnspan=2, pady=10)


def save_edit():
    org = edit_org.get().strip()
    event = edit_event.get().strip()
    try:
        day = datetime.strptime(edit_date.get().strip(), "%d.%m.%Y").strftime("%d.%m.%Y")
    except ValueError:
        messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ")
        return
    start = times.index(edit_start.get())
    end = times.index(edit_end.get())
    if org == "" or event == "" or start >= end:
        messagebox.showwarning("Ошибка", "Заполните поля и укажите правильное время")
        return
    for n, b in enumerate(bookings):
        if n != edit_n and b["date"] == day and b["hall"] == edit_hall.get() and start < b["end"] and end > b["start"]:
            messagebox.showwarning("Ошибка", "Это время пересекается с другой бронью")
            return
    bookings[edit_n] = {"date": day, "hall": edit_hall.get(), "start": start, "end": end, "org": org, "event": event}
    add_org(org)
    edit_win.destroy()
    fill_tree()
    reset_selection()
    update_dashboard()


def update_dashboard():
    dash_tree.delete(*dash_tree.get_children())
    now = datetime.now()
    minutes = now.hour * 60 + now.minute
    rows = []
    for n, b in enumerate(bookings):
        if b["date"] != now.strftime("%d.%m.%Y"):
            continue
        start = 9 * 60 + b["start"] * 15
        end = 9 * 60 + b["end"] * 15
        if start <= minutes < end:
            rows.append((b["start"], n, "Идёт сейчас"))
        elif 0 < start - minutes <= 30:
            rows.append((b["start"], n, "Скоро начнётся"))
    rows.sort()
    for start, n, status in rows:
        b = bookings[n]
        t = time_str(b["start"]) + " - " + time_str(b["end"])
        dash_tree.insert("", "end", values=(status, t, b["hall"], b["org"], b["event"]))
    if len(rows) == 0:
        dash_tree.insert("", "end", values=("Нет мероприятий", "", "", "", ""))


def dashboard_tick():
    update_dashboard()
    root.after(30000, dashboard_tick)


top = tk.Frame(root)
top.pack(padx=10, pady=10, fill="x")

tk.Label(top, text="Зал:").pack(side="left")
hall_box = ttk.Combobox(top, textvariable=hall_var, values=halls, state="readonly")
hall_box.pack(side="left", padx=5)
hall_box.bind("<<ComboboxSelected>>", on_hall_change)
tk.Label(top, text="Дата:").pack(side="left", padx=(20, 0))
tk.Label(top, textvariable=date_var, width=12, relief="sunken").pack(side="left", padx=5)
tk.Button(top, text="Календарь", command=open_calendar).pack(side="left")

tree = ttk.Treeview(root, columns=("time", "hall", "org", "event"), show="headings", height=4)
tree.heading("time", text="Время")
tree.heading("hall", text="Зал")
tree.heading("org", text="Организация")
tree.heading("event", text="Мероприятие")
tree.pack(padx=10, fill="x")
buttons = tk.Frame(root)
buttons.pack(pady=5)
tk.Button(buttons, text="Изменить", command=edit_booking).pack(side="left", padx=5)
tk.Button(buttons, text="Удалить", command=delete_booking).pack(side="left", padx=5)

canvas = tk.Canvas(root, width=860, height=290, bg="white")
canvas.pack(padx=10, pady=10)
canvas.bind("<Button-1>", on_click)

form = tk.Frame(root)
form.pack(padx=10, pady=(0, 10))

org_box = ttk.Combobox(form, textvariable=org_var, values=orgs)
org_box.grid(row=0, column=0, padx=5)
tk.Entry(form, textvariable=event_var, width=30).grid(row=0, column=1, padx=5)
tk.Button(form, text="Утвердить бронь", command=book).grid(row=0, column=2, padx=5)
tk.Label(form, textvariable=info_var).grid(row=1, column=0, columnspan=3, pady=5)

tk.Label(root, text="Сейчас идут и начнутся в ближайшие 30 минут:").pack(anchor="w", padx=10)
dash_tree = ttk.Treeview(root, columns=("status", "time", "hall", "org", "event"), show="headings", height=3)
dash_tree.heading("status", text="Статус")
dash_tree.heading("time", text="Время")
dash_tree.heading("hall", text="Зал")
dash_tree.heading("org", text="Организация")
dash_tree.heading("event", text="Мероприятие")
dash_tree.pack(padx=10, pady=(0, 10), fill="x")

org_var.trace_add("write", lambda *args: update_info())

fill_tree()
draw()
update_info()
update_dashboard()
root.after(30000, dashboard_tick)

root.mainloop()
