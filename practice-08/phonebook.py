import psycopg2
import csv
import os
from connect import connect

# --- ФУНКЦИИ (Practice 7 & 8) ---

def import_from_csv(filename):
    # Проверяем наличие файла
    if not os.path.exists(filename):
        print(f"❌ Ошибка: Файл не найден по пути: {filename}")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader) # Пропускаем заголовок
        except StopIteration:
            print("Файл пуст.")
            return
            
        with connect() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    if len(row) == 2:
                        cur.execute("""
                            INSERT INTO contacts (name, phone) 
                            VALUES (%s, %s) 
                            ON CONFLICT (name) DO NOTHING
                        """, row)
            conn.commit()
    print(f"✅ CSV импортирован из: {filename}")

def insert_console():
    name = input("Имя: ")
    phone = input("Телефон: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
        conn.commit()
    print("Контакт добавлен.")

def update_old():
    target = input("Кого обновить? ")
    new_phone = input("Новый телефон: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE contacts SET phone = %s WHERE name = %s", (new_phone, target))
        conn.commit()
    print("Данные обновлены.")

def search_func():
    pattern = input("Что искать? ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
            results = cur.fetchall()
            for row in results: print(row)
            if not results: print("Ничего не найдено.")

def delete_old():
    target = input("Кого удалить? ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE name = %s", (target,))
        conn.commit()
    print("Удалено.")

def get_pagination():
    try:
        limit = int(input("Лимит: "))
        offset = int(input("Смещение (offset): "))
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
                for row in cur.fetchall(): print(row)
    except ValueError:
        print("Ошибка: введите числа.")

# --- ПРОЦЕДУРЫ (Practice 8) ---

def upsert_proc():
    name = input("Имя: ")
    phone = input("Телефон: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
    print("Upsert выполнен.")

def bulk_insert_proc():
    names = input("Имена (через запятую): ").split(',')
    phones = input("Телефоны (через запятую): ").split(',')
    names = [n.strip() for n in names]
    phones = [p.strip() for p in phones]
    
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL bulk_insert_contacts(%s, %s)", (names, phones))
        conn.commit()
    print("Массовая вставка завершена.")

def delete_proc():
    target = input("Имя или телефон для удаления: ")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (target,))
        conn.commit()
    print("Удаление выполнено.")

def show_all():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM contacts ORDER BY id")
            for row in cur.fetchall(): print(row)

# --- МЕНЮ ---

def main():
    # ПУТЬ ДЛЯ АСКАРА:
    csv_full_path = r"C:\Users\Askar\Desktop\pp2 (1)\practice-08\contacts.csv"

    while True:
        print("\n" + "="*30)
        print("МЕНЮ ТЕЛЕФОННОЙ КНИГИ")
        print("1. Insert CSV (Путь Аскара)")
        print("2. Insert console")
        print("3. Update (old)")
        print("4. Search (function)")
        print("5. Delete (old)")
        print("6. Exit")
        print("7. Pagination")
        print("8. Insert/Update (procedure)")
        print("9. Bulk insert")
        print("10. Delete (procedure)")
        print("11. Show all contacts")
        print("="*30)
        
        choice = input("Выберите пункт: ")
        
        try:
            if choice == "1": import_from_csv(csv_full_path)
            elif choice == "2": insert_console()
            elif choice == "3": update_old()
            elif choice == "4": search_func()
            elif choice == "5": delete_old()
            elif choice == "6": break
            elif choice == "7": get_pagination()
            elif choice == "8": upsert_proc()
            elif choice == "9": bulk_insert_proc()
            elif choice == "10": delete_proc()
            elif choice == "11": show_all()
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
