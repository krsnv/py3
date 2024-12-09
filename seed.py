import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


def create_connection():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("teachers.db")
    if not db.open():
        print("Не удалось подключиться к базе данных.")
        sys.exit(1)
    return db


def seed_database():
    db = create_connection()
    query = QSqlQuery()
    query.exec_(
        """CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        group_name TEXT NOT NULL
    )"""
    )

    teachers_data = [
        ("Иванов Иван", "Математика", "Группа 1"),
        ("Петров Петр", "Физика", "Группа 2"),
        ("Сидоров Сидор", "Химия", "Группа 1"),
        ("Кузнецов Алексей", "Биология", "Группа 3"),
        ("Андреев Андрей", "География", "Группа 2"),
        ("Васильев Василий", "История", "Группа 1"),
        ("Смирнова Анна", "Литература", "Группа 4"),
        ("Тимофеев Тимофей", "Информатика", "Группа 3"),
        ("Федорова Екатерина", "Иностранные языки", "Группа 4"),
        ("Дмитриев Дмитрий", "Философия", "Группа 2"),
    ]

    for name, subject, group in teachers_data:
        query.prepare(
            "INSERT INTO teachers (name, subject, group_name) VALUES (:name, :subject, :group)"
        )
        query.bindValue(":name", name)
        query.bindValue(":subject", subject)
        query.bindValue(":group", group)
        if not query.exec_():
            print(f"Ошибка при добавлении учителя {name}: {query.lastError().text()}")
        else:
            print(f"Учитель {name} добавлен успешно.")

    print("Данные успешно добавлены в базу данных.")


if __name__ == "__main__":
    seed_database()
