from collections import UserDict
from datetime import datetime
import pickle
from art import logo


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones) if self.phones else "—"
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "—"
        return f"{self.name.value}: {phones} | Birthday: {bday}"


# ==== Клас AddressBook =====
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        result = {}

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = record.birthday.value.replace(year=today.year)

            if bday < today:
                bday = bday.replace(year=today.year + 1)

            delta_days = (bday - today).days
            if 0 <= delta_days < 7:
                weekday = bday.strftime("%A")

                if weekday in ("Saturday", "Sunday"):
                    weekday = "Monday"

                result.setdefault(weekday, []).append(record.name.value)

        return result

    def save_data(self, filename="addressbook.pk1"):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    def load_addressbook(filename="addressbook.pk1"):
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return AddressBook()


def start():
    print(logo)
    print("Привіт! Я твоя адресна книга. Ось що я можу:")
    print(
        "/add — додати запис\n/change — змінити телефон\n/show — показати запис\n/birthdays — найближчі дні народження\n/help — список команд\n/exit — вийти"
    )


def add_contact(book):
    name = input("Введіть ім'я: ").strip()
    phone = input("Введіть телефон (10 цифр): ").strip()
    bday = input("Введіть день народження (необов'язково, ДД.MM.YYYY): ").strip()

    try:
        record = Record(name)
        record.add_phone(phone)
        if bday:
            record.add_birthday(bday)
        book.add_record(record)
        book.save_data()
        print("✅ Запис додано!")
    except ValueError as e:
        print(f"Помилка: {e}")


def change_phone(book):
    name = input("Введіть ім'я: ").strip()
    record = book.find(name)
    if not record:
        print("Контакт не знайдено.")
        return
    old_phone = input("Введіть старий телефон: ").strip()
    new_phone = input("Введіть новий телефон: ").strip()
    try:
        record.change_phone(old_phone, new_phone)
        book.save_data()
        print("✅ Телефон змінено!")
    except ValueError as e:
        print(f"Помилка: {e}")


def show_contact(book):
    name = input("Введіть ім'я: ").strip()
    record = book.find(name)
    if record:
        print(record)
    else:
        print("Запис не знайдено.")


def show_birthdays(book):
    bdays = book.get_upcoming_birthdays()
    if not bdays:
        print("Ніхто не святкує найближчі 7 днів 🎉")
        return
    for day, names in bdays.items():
        print(f"{day}: {', '.join(names)}")


def show_help():
    print(
        """
/add — додати запис
/change — змінити телефон
/show — показати запис
/birthdays — найближчі дні народження
/help — список команд
/exit — вийти
"""
    )


def main():
    book = AddressBook.load_addressbook()
    start()

    while True:
        command = input("\nВведіть команду: ").strip().lower()
        if command in ("/exit", "exit", "вихід"):
            book.save_data()
            print("📘 Дані збережено. До зустрічі!")
            break
        elif command in ("/add", "add"):
            add_contact(book)
        elif command in ("/change", "change"):
            change_phone(book)
        elif command in ("/show", "show"):
            show_contact(book)
        elif command in ("/birthdays", "birthdays"):
            show_birthdays(book)
        elif command in ("/help", "help"):
            show_help()
        elif command in ("/start", "привіт"):
            start()
        else:
            print("Невідома команда. Напишіть /help")


if __name__ == "__main__":
    main()
