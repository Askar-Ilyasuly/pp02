
import psycopg2
import csv
from connect import connect

# --- БАЗОВЫЕ ОПЕРАЦИИ (SQL) ---

def create_table():
    """Создает таблицу, если ее нет"""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE,
                    phone VARCHAR(20)
                )
            """)
        conn.commit()

def import_csv(filepath):
    """Импорт данных из CSV"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Пропускаем заголовок (name,phone)
        with connect() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    if len(row) == 2:
                        # ON CONFLICT защищает от ошибок, если имя уже есть
                        cur.execute("""
                            INSERT INTO phonebook (name, phone) VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, (row[0], row[1]))
            conn.commit()
    print("✅ Данные из CSV успешно импортированы!")

def add_contact(name, phone):
    """Ввод данных через консоль"""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO phonebook (name, phone) VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE SET phone = EXCLUDED.phone
            """, (name, phone))
        conn.commit()
    print(f"✅ Контакт '{name}' добавлен/обновлен.")

def update_contact(name, new_name, new_phone):
    """Обновление имени или телефона"""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE phonebook 
                SET name = %s, phone = %s 
                WHERE name = %s
            """, (new_name, new_phone, name))
        conn.commit()
    print(f"✅ Контакт обновлен.")

def query_contacts(filter_type, search_term):
    """Поиск по фильтрам"""
    with connect() as conn:
        with conn.cursor() as cur:
            if filter_type == 'name':
                cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", (f"%{search_term}%",))
            elif filter_type == 'phone':
                cur.execute("SELECT * FROM phonebook WHERE phone ILIKE %s", (f"%{search_term}%",))
            return cur.fetchall()

def delete_contact(identity):
    """Удаление по имени или телефону"""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM phonebook WHERE name = %s OR phone = %s", (identity, identity))
        conn.commit()
    print(f"🗑️ Запись '{identity}' удалена.")


# --- ИНТЕРАКТИВНОЕ МЕНЮ ---
if __name__ == "__main__":
    # При запуске программы сразу создаем таблицу, если ее нет
    create_table()
    
    while True:
        print("\n" + "="*35)
        print("📗 PRACTICE 7: PHONEBOOK MENU")
        print("1. Импорт контактов из CSV")
        print("2. Добавить контакт вручную")
        print("3. Обновить контакт")
        print("4. Искать контакты (Фильтры)")
        print("5. Удалить контакт")
        print("0. Выход")
        print("="*35)
        
        choice = input("Выберите пункт: ")
        
        if choice == '1':
            try:
                import_csv('contacts.csv')
            except FileNotFoundError:
                print("❌ Файл contacts.csv не найден в папке!")
                
        elif choice == '2':
            name = input("Введите имя: ")
            phone = input("Введите телефон: ")
            add_contact(name, phone)
            
        elif choice == '3':
            old_name = input("Кого хотите обновить (введите текущее имя)? ")
            new_name = input("Введите НОВОЕ имя: ")
            new_phone = input("Введите НОВЫЙ телефон: ")
            update_contact(old_name, new_name, new_phone)
            
        elif choice == '4':
            print("1 - Поиск по имени\n2 - Поиск по телефону")
            f_choice = input("Выберите фильтр: ")
            term = input("Что ищем?: ")
            
            if f_choice == '1':
                results = query_contacts('name', term)
            else:
                results = query_contacts('phone', term)
                
            if results:
                print("\n🔍 Результаты:")
                for r in results:
                    print(f"ID: {r[0]} | Имя: {r[1]} | Тел: {r[2]}")
            else:
                print("\nНичего не найдено.")
                
        elif choice == '5':
            identity = input("Введите имя или телефон для удаления: ")
            delete_contact(identity)
            
        elif choice == '0':
            print("Выход...")
            break
        else:
            print("❌ Неверный ввод.")
