import math
import customtkinter as ctk

from recipes import RECIPES

CURRENT_VERSION = "1.0.0"

RANK_COLORS = {
    "gold":  "#c9a227",
    "blue":  "#2f6fb0",
    "green": "#3a7d44",
}

INDENT = "    "        # 4 пробела = один уровень
SEPARATOR = "─" * 50   # разделитель между блоками


def build_tree(item_name, amount):
    recipe = RECIPES.get(item_name)
    if not recipe or not recipe["ingredients"]:
        return {"amount": amount, "children": {}}

    crafts = math.ceil(amount / recipe["output"])
    children = {}
    for ing_name, per_craft in recipe["ingredients"].items():
        children[ing_name] = build_tree(ing_name, per_craft * crafts)

    return {"amount": amount, "children": children}


def render_tree(name, node, indent=0, lines=None):
    if lines is None:
        lines = []

    recipe = RECIPES.get(name)
    rank = recipe["rank"] if recipe else "green"

    prefix = INDENT * indent

    # для золота и синих — заголовок с разделителем
    if rank == "gold":
        lines.append(f"{prefix}★ {name}: {node['amount']} шт.")
        lines.append(f"{prefix}{SEPARATOR}")
    elif rank == "blue":
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(f"{prefix}{SEPARATOR}")
        lines.append(f"{prefix}◆ {name}: {node['amount']} шт.")
        lines.append(f"{prefix}{SEPARATOR}")
    else:
        lines.append(f"{prefix}• {name}: {node['amount']} шт.")

    for child_name, child_node in node["children"].items():
        render_tree(child_name, child_node, indent + 1, lines)

    # после зелёного зелья — пустая строка
    if rank == "green" and node["children"]:
        lines.append("")

    return lines


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Калькулятор ресурсов BDO")
app.geometry("900x750")

title = ctk.CTkLabel(
    app,
    text="Калькулятор ресурсов BDO",
    font=ctk.CTkFont(size=20, weight="bold"),
)
title.pack(pady=(15, 10))

cards_frame = ctk.CTkScrollableFrame(app, label_text="Выбери предмет")
cards_frame.pack(padx=20, pady=5, fill="both", expand=True)

result_box = ctk.CTkTextbox(app, width=860, height=340)
result_box.pack(padx=20, pady=(10, 5), fill="both")


def copy_result():
    text = result_box.get("1.0", "end").strip()
    if not text:
        return
    app.clipboard_clear()
    app.clipboard_append(text)
    copy_button.configure(text="Скопировано!")
    app.after(1500, lambda: copy_button.configure(text="Копировать"))


copy_button = ctk.CTkButton(app, text="Копировать", command=copy_result)
copy_button.pack(padx=20, pady=(0, 15))


def on_calculate(item_name, entry_widget):
    try:
        amount = int(entry_widget.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        result_box.delete("1.0", "end")
        result_box.insert("end", "Введи целое число больше нуля.")
        return

    recipe = RECIPES.get(item_name)
    tree = build_tree(item_name, amount)

    lines = []

    # ─── шапка ───
    if recipe:
        crafts = math.ceil(amount / recipe["output"])
        real = crafts * recipe["output"]
        lines.append(f"Цель: {amount} × {item_name}")
        lines.append(f"Крафтов: {crafts} (на выходе {real} шт.)")
        lines.append("")

    lines.extend(render_tree(item_name, tree))

    result_box.delete("1.0", "end")
    result_box.insert("end", "\n".join(lines))


rank_order = {"gold": 0, "blue": 1, "green": 2}
sorted_items = sorted(
    RECIPES.items(),
    key=lambda kv: (rank_order.get(kv[1]["rank"], 99), kv[0]),
)

columns = 3
for index, (item_name, data) in enumerate(sorted_items):
    row = index // columns
    col = index % columns
    color = RANK_COLORS.get(data["rank"], "#444444")

    card = ctk.CTkFrame(cards_frame, fg_color=color, corner_radius=8)
    card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    label = ctk.CTkLabel(
        card,
        text=item_name,
        text_color="white",
        font=ctk.CTkFont(size=12, weight="bold"),
        wraplength=160,
    )
    label.pack(padx=8, pady=(8, 4))

    row_frame = ctk.CTkFrame(card, fg_color="transparent")
    row_frame.pack(padx=8, pady=(0, 8))

    entry = ctk.CTkEntry(row_frame, width=60)
    entry.insert(0, str(data["output"]))
    entry.pack(side="left", padx=(0, 5))

    btn = ctk.CTkButton(
        row_frame,
        text="+",
        width=30,
        command=lambda name=item_name, e=entry: on_calculate(name, e),
    )
    btn.pack(side="left")

for c in range(columns):
    cards_frame.grid_columnconfigure(c, weight=1)

app.mainloop()