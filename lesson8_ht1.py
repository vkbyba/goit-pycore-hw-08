from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"An error occurred: {e}"
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone_number):
        if not (len(phone_number) == 10 and phone_number.isdigit()):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(phone_number)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(self.value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if not phone:
            raise ValueError("Old number not found.")
        self.add_phone(new_number)
        self.remove_phone(old_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def get_birthday(self):
        return self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "No birthday set"

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(phone.value for phone in self.phones)}, Birthday: {self.get_birthday()}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming_birthdays = []
        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)
                if today <= birthday_this_year <= today + timedelta(days=7):
                    upcoming_birthdays.append((name, record.get_birthday()))
        return upcoming_birthdays

    @staticmethod
    @input_error
    def add_contact(args, book):
        if len(args) < 2:
            return "Not enough arguments. Usage: add <name> <phone>"
        name, phone = args[0], args[1]
        record = book.data.get(name)
        if record is None:
            record = Record(name)
            book.add_record(record)
            message = "Contact added."
        else:
            message = "Contact updated."
            record.add_phone(phone)
        return message

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.data.get(name)
    if not record:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.data.get(name)
    if not record:
        return "Contact not found."
    if not record.birthday:
        return "Birthday not set."
    return f"{name}'s birthday is on {record.get_birthday()}."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(f"{name} on {birthday}" for name, birthday in upcoming_birthdays)

def parse_input(user_input):
    """Parse the user input and return the command and arguments."""
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    return command, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, pickle.PickleError):
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book) 
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(book.add_contact(args, book))
        

        elif command == "change":
            if len(args) < 3:
                print("Not enough arguments. Usage: change <name> <old_phone> <new_phone>")
            else:
                name, old_phone, new_phone = args
                record = book.data.get(name)
                if record:
                    record.edit_phone(old_phone, new_phone)
                    print("Phone number updated.")
                
                else:
                    print("Contact not found.")

        elif command == "phone":
            if len(args) < 1:
                print("Not enough arguments. Usage: phone <name>")
            else:
                name = args[0]
                record = book.data.get(name)
                if record:
                    print(f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}")
                else:
                    print("Contact not found.")

        elif command == "all":
            for name, record in book.items():
                print(f"{name}: {record}")

        elif command == "add-birthday":
            print(add_birthday(args, book))
        

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
