"""
Завдання 1. Лінійний графік динаміки ВВП для України та іншої країни.
Практична робота 7. Візуалізація даних за допомогою Matplotlib.

Показник Світового банку: GDP (current US$), код NY.GDP.MKTP.CD
(ВВП у поточних доларах США). Дані завантажуються з відкритого API
Світового банку (https://api.worldbank.org) і кешуються у файлі gdp_data.csv.
Потрібні: pandas, matplotlib та доступ до інтернету при першому запуску.
"""
import json
import os
import urllib.request

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(BASE_DIR, "gdp_data.csv")
INDICATOR_CODE = "NY.GDP.MKTP.CD"
INDICATOR = "ВВП (млрд дол. США)"
YEARS = "2010:2023"
HOME = "Ukraine"
API = "https://api.worldbank.org/v2"


def api_get(url):
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_data():
    """Завантажує ВВП усіх країн за YEARS з API Світового банку."""
    countries = api_get(f"{API}/country?format=json&per_page=400")[1]
    real = {c["iso2Code"] for c in countries
            if c["region"]["value"] != "Aggregates"}
    url = (f"{API}/country/all/indicator/{INDICATOR_CODE}"
           f"?format=json&per_page=20000&date={YEARS}")
    rows = api_get(url)[1]
    data = [{"country": r["country"]["value"], "code": r["countryiso3code"],
             "year": int(r["date"]), "value": r["value"],
             "iso2": r["country"]["id"]}
            for r in rows if r["country"]["id"] in real]
    if not data:
        raise RuntimeError("API Світового банку не повернуло даних")
    return pd.DataFrame(data)


def load_data():
    """Повертає DataFrame: country, year, value (млрд дол. США)."""
    df = None
    if os.path.exists(CACHE):
        df = pd.read_csv(CACHE)
        if "value" not in df.columns or df.empty:
            df = None  # пошкоджений кеш - завантажуємо заново
    if df is None:
        print("Завантаження даних зі Світового банку...")
        df = download_data()
        df.to_csv(CACHE, index=False)
    df = df.dropna(subset=["value"]).copy()
    df["value"] = df["value"] / 1e9
    return df.sort_values(["country", "year"])


def ask_country(df, prompt):
    """Запитує назву країни (англійською) до коректного введення."""
    names = {c.lower(): c for c in df["country"].unique()}
    while True:
        name = input(prompt).strip().lower()
        if name in names:
            return names[name]
        print("Країну не знайдено. Приклад: Poland, Germany, United States.")


def series(df, country):
    s = df[df["country"] == country]
    return s["year"].to_numpy(), s["value"].to_numpy()


def plot_line(df, other):
    plt.figure(figsize=(9, 5))
    for country in (HOME, other):
        years, values = series(df, country)
        plt.plot(years, values, marker="o", label=country)
    plt.title(f"Динаміка ВВП: {HOME} та {other}")
    plt.xlabel("Рік")
    plt.ylabel(INDICATOR)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("task1_line.png", dpi=150)
    plt.show()


def main():
    df = load_data()
    other = ask_country(df, "Країна для порівняння з Україною: ")
    plot_line(df, other)


if __name__ == "__main__":
    main()