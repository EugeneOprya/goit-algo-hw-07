from collections import UserDict
from datetime import datetime, date, timedelta


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data.get("name"):
            self.data.pop(name, None)

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue
            birthday_date = record.birthday.value.date()
            birthday_this_year = birthday_date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            delta = (birthday_this_year - today).days
            if 0 <= delta <= days:
                congratulation_date = birthday_this_year
                weekday = congratulation_date.weekday()
                if weekday == 5:
                    congratulation_date += timedelta(days=2)
                elif weekday == 6:
                    congratulation_date += timedelta(days=1)
                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )
        return upcoming_birthdays


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        birthday_str = (
            self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Not set"
        )
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday_str}"

    def add_phone(self, number):
        number = Phone(number)
        self.phones.append(number)

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def remove_phone(self, number):
        phone_obj = self.find_phone(number)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_number, new_number):
        edit_phone = self.find_phone(old_number)

        if not edit_phone:
            raise ValueError

        new_phone_obj = Phone(new_number)

        for i, p in enumerate(self.phones):
            if p.value == old_number:
                self.phones[i] = new_phone_obj
                return

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) if str(e) else "Enter arguments correctly."
        except KeyError:
            return "User not found"
        except IndexError:
            return "Enter user name"

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.lower().strip()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    return "Contact not found."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Birthday not found or contact doesn't exist."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    return "Contact not found."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones)
    return "Contact not found."


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(
        [f"{item['name']}: {item['congratulation_date']}" for item in upcoming]
    )


def main():
    book = AddressBook()

    print("Welcome to the assistant bot!")
    print("Available commands:")
    print("close, exit - exit")
    print("hello - greeting")
    print("add - add contact")
    print("change - change username phone")
    print("phone - show phone for username")
    print("all - show book")
    print("add-birthday - add a birthday")
    print("show-birthday - show a birthday")
    print("birthdays - show upcoming birthdays")
    print("-" * 20)

    while True:
        user_input = input("Enter a command: ")

        if not user_input.strip():
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            if not book.data:
                print("Address book is empty.")
            else:
                print(book)
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
