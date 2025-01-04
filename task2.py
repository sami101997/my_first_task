import csv
import sqlite3
import phonenumbers
from phonenumbers import geocoder, carrier

class Contact:
    def __init__(self, name, phone_number, country_code):
        self.name = name
        self.phone_number = phone_number
        self.country_code = country_code

class ContactManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            print(f"Connected to {self.db_name} database")
        except sqlite3.Error as e:
            print(e)

    def create_table(self):
        try:
            with self.conn:
                c = self.conn.cursor()
                query = """CREATE TABLE IF NOT EXISTS contacts (
                                name TEXT,
                                phone_number TEXT UNIQUE,
                                country_code TEXT
                            )"""
                c.execute(query)
                print("Table created")
        except sqlite3.Error as e:
            print(e)

    def clear_contacts(self):
        """Clears the contacts table before inserting new data."""
        try:
            with self.conn:
                c = self.conn.cursor()
                query = "DELETE FROM contacts"
                c.execute(query)
                print("Contacts table cleared.")
        except sqlite3.Error as e:
            print(e)

    def insert_or_update_contact(self, contact):
        try:
            with self.conn:
                c = self.conn.cursor()
                query = "SELECT * FROM contacts WHERE phone_number = ?"
                c.execute(query, (contact.phone_number,))
                existing_contact = c.fetchone()

                if existing_contact:
                    existing_name = existing_contact[0]
                    existing_country_code = existing_contact[2]
                    
                    merged_name = self.merged_names(existing_name, contact.name)

                    merged_country_code = existing_country_code  
                    update_query = """
                    UPDATE contacts
                    SET name = ?, country_code = ?
                    WHERE phone_number = ?
                    """
                    c.execute(update_query, (merged_name, merged_country_code, contact.phone_number))
                    print(f"Merged contact: {contact.phone_number} -> {merged_name}")
                else:
                    insert_query = "INSERT INTO contacts (name, phone_number, country_code) VALUES (?, ?, ?)"
                    c.execute(insert_query, (contact.name, contact.phone_number, contact.country_code))
                    print(f"Inserted new contact: {contact.name} - {contact.phone_number}")

        except sqlite3.Error as e:
            print(e)

    def merged_names(self, existing_name, new_name):
        """
        Merge names if they are from the same person. 
        This can be a simple merging strategy or a more complex logic (e.g., fuzzy matching).
        For simplicity, this example just combines the names with a slash if they're different.
        """
        if existing_name != new_name:
            merged_name = f"{existing_name} / {new_name}"
        else:
            merged_name = existing_name
        return merged_name

    def export_to_csv(self, file_name):
        try:
            with self.conn:
                c = self.conn.cursor()
                query = """SELECT name, phone_number FROM contacts ORDER BY name DESC"""
                c.execute(query)
                rows = c.fetchall()
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Name", "Phone Number"])
                    writer.writerows(rows)
                print(f"Contacts exported to {file_name}")
        except sqlite3.Error as e:
            print(e)

class PhoneNumberNormalizer:
    def normalize_phone_number(self, phone_number, country_code):
        try:
            x = phonenumbers.parse(phone_number, country_code)
            return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            return None

def main():
    db_name = "contacts.db"
    csv_files = ["contacts.csv", "contacts2.csv"]
    export_file_name = "google_contacts.csv"

    contact_manager = ContactManager(db_name)
    contact_manager.create_connection()
    contact_manager.create_table()

    contact_manager.clear_contacts()

    phone_number_normalizer = PhoneNumberNormalizer()

    for file_name in csv_files:
        try:
            with open(file_name, 'r') as file:
                reader = csv.reader(file)
                next(reader)  
                for row in reader:
                    name = row[0]
                    phone_number = row[2]
                    country_code = row[1]
                    normalized_phone_number = phone_number_normalizer.normalize_phone_number(phone_number, country_code)
                    if normalized_phone_number:
                        contact = Contact(name, normalized_phone_number, country_code)
                        contact_manager.insert_or_update_contact(contact)
                        contact_manager.merged_names(name, normalized_phone_number)
        except FileNotFoundError:
            print(f"File {file_name} not found")

    contact_manager.export_to_csv(export_file_name)
    contact_manager.conn.close()

if __name__ == "__main__":
    main()
