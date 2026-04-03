-- Добавление или обновление (Upsert)
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO contacts (name, phone) VALUES (p_name, p_phone)
    ON CONFLICT (name) DO UPDATE SET phone = EXCLUDED.phone;
END; $$;

-- Массовая вставка с проверкой длины номера
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE i INTEGER;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        IF length(p_phones[i]) >= 10 THEN
            INSERT INTO contacts(name, phone) VALUES (p_names[i], p_phones[i])
            ON CONFLICT (name) DO UPDATE SET phone = EXCLUDED.phone;
        END IF;
    END LOOP;
END; $$;

-- Удаление по имени или телефону
CREATE OR REPLACE PROCEDURE delete_contact(p_id TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE name = p_id OR phone = p_id;
END; $$;