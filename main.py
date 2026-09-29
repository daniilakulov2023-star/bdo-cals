import math

from recipes import RECIPES


def collect_resources(item_name, amount, totals=None):
    """Рекурсивно собирает базовые ресурсы."""
    if totals is None:
        totals = {}

    if item_name not in RECIPES:
        totals[item_name] = totals.get(item_name, 0) + amount
        return totals

    recipe = RECIPES[item_name]
    if not recipe["ingredients"]:
        totals[item_name] = totals.get(item_name, 0) + amount
        return totals

    crafts = math.ceil(amount / recipe["output"])
    for ing_name, per_craft in recipe["ingredients"].items():
        collect_resources(ing_name, per_craft * crafts, totals)

    return totals


if __name__ == "__main__":
    result = collect_resources("Эликсир Гармонии", 50)
    print("Ресурсы для 50 Эликсиров Гармонии:")
    for name, count in sorted(result.items()):
        print(f"  {name}: {count}")