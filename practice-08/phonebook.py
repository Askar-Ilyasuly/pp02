import psycopg2
from connect import connect

# 1. Функция поиска
def search_contacts(pattern):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
            return cur.fetchall()

# 2. Процедура Upsert (добавить/обновить)
def upsert_contact(name, phone):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()

# 3. Массовая вставка
def bulk_add(names_list, phones_list):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL bulk_insert_contacts(%s, %s)", (names_list, phones_list))
        conn.commit()

# 4. Пагинация
def get_page(limit, offset):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            return cur.fetchall()

# 5. Удаление
def remove_contact(identity):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (identity,))
        conn.commit()


# --- ИНТЕРАКТИВНОЕ МЕНЮ ---
if __name__ == "__main__":
    while True:
        print("\n" + "="*30)
        print("📞 ТЕЛЕФОННАЯ КНИГА (МЕНЮ)")
        print("1. Найти контакт (поиск)")
        print("2. Добавить или обновить контакт")
        print("3. Добавить несколько контактов (массово)")
        print("4. Показать все контакты (пагинация)")
        print("5. Удалить контакт")
        print("0. Выйти")
        print("="*30)
        
        choice = input("Выберите действие (0-5): ")
        
        if choice == '1':
            pattern = input("Введите имя или номер для поиска: ")
            results = search_contacts(pattern)
            if results:
                print("\nНайдено:")
                for row in results:
                    print(f"- Имя: {row[0]}, Телефон: {row[1]}")
            else:
                print("\nНичего не найдено.")
                
        elif choice == '2':
            name = input("Введите имя: ")
            phone = input("Введите телефон: ")
            upsert_contact(name, phone)
            print(f"\n✅ Контакт '{name}' успешно сохранен!")
            
        elif choice == '3':
            print("\nВведите данные через запятую (например: Askar, Alina)")
            names_input = input("Имена: ")
            phones_input = input("Телефоны: ")
            
            # Разделяем строку по запятым и убираем лишние пробелы
            names = [n.strip() for n in names_input.split(',')]
            phones = [p.strip() for p in phones_input.split(',')]
            
            if len(names) == len(phones):
                bulk_add(names, phones)
                print("\n✅ Массовая вставка выполнена (номера короче 10 цифр проигнорированы).")
            else:
                print("\n❌ Ошибка: количество имен не совпадает с количеством телефонов!")
                
        elif choice == '4':
            try:
                limit = int(input("Сколько контактов показать (limit)? (например, 5): "))
                offset = int(input("С какой записи начать (offset)? (например, 0): "))
                results = get_page(limit, offset)
                print("\nСписок контактов:")
                for i, row in enumerate(results, start=1):
                    print(f"{i}. Имя: {row[0]}, Телефон: {row[1]}")
            except ValueError:
                print("\n❌ Ошибка: нужно вводить только числа.")
                
        elif choice == '5':
            identity = input("Введите имя или номер для удаления: ")
            remove_contact(identity)
            print(f"\n🗑️ Запись '{identity}' удалена (если она была в базе).")
            
        elif choice == '0':
            print("\nВыход из программы. До свидания!")
            break
            
        else:
            print("\n❌ Неверный выбор. Пожалуйста, введите число от 0 до 5.")