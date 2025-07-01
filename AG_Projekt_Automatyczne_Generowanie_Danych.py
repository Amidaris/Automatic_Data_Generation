# -*- coding: utf-8 -*-

# Projekt: Automatyczne generowanie danych 
# ! - uruchamianie z poziomu GoogleColaboratory
# !pip install faker pandas openpyxl matplotlib db-sqlite3

# Importy
import pandas as pd
import random
import sqlite3
from faker import Faker
import matplotlib.pyplot as plt

# Inicjalizacja Faker i seed
fake = Faker('pl-PL')
Faker.seed(42)
random.seed(42)

# Liczba rekordów
num_records = 500

# Zbiór danych z użyciem 20 metod Faker i metod random
data = []
for _ in range(num_records):
    gender = random.choice(["Kobieta", "Mężczyzna"])

    if gender == "Kobieta":
        first_name = fake.first_name_female()
        last_name = fake.last_name()
    else:
        first_name = fake.first_name_male()
        last_name = fake.last_name()

    record = {
        "id": fake.uuid4(),
        "imię": first_name,
        "nazwisko": last_name,
        "płeć": gender,
        "pesel": fake.pesel(),
        "adres": fake.address(),
        "kraj": fake.country(),
        "miasto": fake.city(),
        "postcode": fake.postcode(),
        "stanowisko": fake.job(),
        "nr_ubezpieczenia": fake.ssn(),
        "email": fake.email(),
        "telefon": fake.phone_number(),
        "rachunek_bankowy": fake.credit_card_number(),
        "login": fake.user_name(),
        "hasło": fake.password(),
        "data_urodzenia": fake.date_of_birth(minimum_age=18, maximum_age=70),
        "zatrudnienie_od": fake.date_between(start_date='-10y', end_date='-1d'),
        "wynagrodzenie": round(random.uniform(4666.0, 15000.0), 2),
        "stopień niepełnosprawności": random.choice(["Brak", "Lekki", "Średni", "Znaczny"]),
    }
    data.append(record)

df = pd.DataFrame(data)

print(df)

# Obliczenia w Pandas

# Liczba kobiet i mężczyzn w firmie
gender_counts = df["płeć"].value_counts()
print(gender_counts)

# Wiek pracownika
import datetime

# Pobranie bieżącej daty
today = datetime.date.today()

# Obliczenie wieku z uwzględnieniem miesiąca i dnia
df["wiek"] = df["data_urodzenia"].apply(lambda dob: today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))

print(df[["imię", "nazwisko", "data_urodzenia", "wiek"]])

# Obliczenie stażu pracy poszczególnych pracowników
df["staż_pracy"] = df["zatrudnienie_od"].apply(lambda start_date: today.year - start_date.year - ((today.month, today.day) < (start_date.month, start_date.day)))

print(df[["imię", "nazwisko", "zatrudnienie_od", "staż_pracy"]])

# Średnie wynagrodzenie w podziale na płeć
avg_salary_by_gender = df.groupby("płeć")["wynagrodzenie"].mean()

print(avg_salary_by_gender)

# Obliczenie średniego wynagrodzenia dla każdej płci
avg_salary_by_gender = df.groupby("płeć")["wynagrodzenie"].mean()
print(avg_salary_by_gender)

# Wyliczenie ogólnej różnicy w średnim wynagrodzeniu (Mężczyźni - Kobiety)
salary_difference = avg_salary_by_gender["Mężczyzna"] - avg_salary_by_gender["Kobieta"]
print(f"Różnica w średnim wynagrodzeniu: {salary_difference:.2f} PLN")

# Obliczenie średniego wynagrodzenia dla grup wiekowych
# Grupowanie wieku w przedziały (np. co 5 lat)
df["przedział_wiekowy"] = pd.cut(df["wiek"], bins=[18, 25, 35, 45, 55, 65, 75], labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66-75"])

# Obliczenie średniego wynagrodzenia dla każdej grupy wiekowej
avg_salary_by_age = df.groupby("przedział_wiekowy")["wynagrodzenie"].mean()

print(avg_salary_by_age)

# Eksport do plików
csv_path = "dane_fake.csv"
xlsx_path = "dane_fake.xlsx"
db_path = "dane_fake.db"

df.to_csv(csv_path, index=False)
df.to_excel(xlsx_path, index=False)

# Bazy Danych i SQL

conn = sqlite3.connect(db_path)
df.to_sql("pracownicy", conn, if_exists="replace", index=False)

df_sql = pd.read_sql("SELECT * FROM pracownicy", conn)
print(df_sql.head())

# Średnie wynagrodzenie dla kobiet i mężczyzn ze względu na staż pracy w firmie
query = """
SELECT
    płeć,
    CASE
        WHEN staż_pracy BETWEEN 0 AND 5 THEN '0-5 lat'
        WHEN staż_pracy BETWEEN 6 AND 10 THEN '6-10 lat'
        ELSE '11+ lat'
    END AS przedział_stażu,
    AVG(wynagrodzenie) AS średnie_wynagrodzenie
FROM pracownicy
GROUP BY płeć, przedział_stażu
ORDER BY płeć, przedział_stażu;
"""

df_sql = pd.read_sql(query, conn)

print(df_sql)

conn.close()

# Wizualizacja

# Tworzenie wykresu - średnie wynagrodzenie według wieku
avg_salary_by_age.plot(kind="bar", figsize=(10, 6), color="purple")
plt.title("Średnie wynagrodzenie według wieku")
plt.xlabel("Grupa wiekowa")
plt.ylabel("Średnie wynagrodzenie (PLN)")
plt.xticks(rotation=0)
plt.savefig("średnie_wynagrodzeni_wedlug_wieku.png", dpi=300, bbox_inches="tight")
plt.show()

# Tworzenie dwóch wykresów osobno dla mężczyzn i osobno dla kobiet
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Podział na grupy wiekowe
df["przedział_wiekowy"] = pd.cut(df["wiek"], bins=[18, 25, 35, 45, 55, 65, 75], labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66-75"])

# Obliczenie średniego wynagrodzenia dla każdej grupy wiekowej osobno dla kobiet i mężczyzn
avg_salary_women = df[df["płeć"] == "Kobieta"].groupby("przedział_wiekowy")["wynagrodzenie"].mean()
avg_salary_men = df[df["płeć"] == "Mężczyzna"].groupby("przedział_wiekowy")["wynagrodzenie"].mean()

# Wykres dla kobiet
avg_salary_women.plot(kind="bar", ax=axes[0], color="pink")
axes[0].set_title("Średnie wynagrodzenie - Kobiety")
axes[0].set_xlabel("Grupa wiekowa")
axes[0].set_ylabel("Średnie wynagrodzenie (PLN)")
axes[0].set_xticklabels(avg_salary_women.index, rotation=0)

# Wykres dla mężczyzn
avg_salary_men.plot(kind="bar", ax=axes[1], color="blue")
axes[1].set_title("Średnie wynagrodzenie - Mężczyźni")
axes[1].set_xlabel("Grupa wiekowa")
axes[1].set_ylabel("Średnie wynagrodzenie (PLN)")
axes[1].set_xticklabels(avg_salary_men.index, rotation=0)

# Zapisanie wykresu do pliku PNG
plt.savefig("wynagrodzenie_wiek_kobiety_mężczyźni.png", dpi=300, bbox_inches="tight")

# Wyświetlenie wykresu
plt.show()
