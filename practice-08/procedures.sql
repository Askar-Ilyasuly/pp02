CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE i INTEGER;
BEGIN
    FOR i IN 1 .. array_upper(p_names, 1) LOOP
        -- ПРОВЕРКА: Длина >= 10 И номер состоит ТОЛЬКО из цифр
        IF length(p_phones[i]) >= 10 AND p_phones[i] ~ '^[0-9]+$' THEN
            INSERT INTO contacts(name, phone) VALUES (p_names[i], p_phones[i])
            ON CONFLICT (name) DO UPDATE SET phone = EXCLUDED.phone;
        ELSE
            -- Можно добавить RAISE NOTICE для отладки, если хочешь видеть, что пропущено
            RAISE NOTICE 'Контакт % с номером % пропущен (неверный формат)', p_names[i], p_phones[i];
        END IF;
    END LOOP;
END; $$;