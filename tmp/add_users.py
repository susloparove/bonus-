from server.users import add_user

if __name__ == "__main__":
    # Добавляем администратора
    try:
        add_user("Администратор", "1111", role="admin")
        print("Администратор добавлен.")
    except Exception as e:
        print(f"Ошибка при добавлении администратора: {e}")

    # Добавляем продавца
    try:
        add_user("Продавцова Аня", "2222", role="seller")
        print("Продавцова Аня добавлена.")
    except Exception as e:
        print(f"Ошибка при добавлении Продавцовой Ани: {e}")