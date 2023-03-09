# unit3_project.py
import sqlite3

from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from passlib.context import CryptContext
from kivymd.uix.pickers import MDDatePicker
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

import email_validator
import re
from datetime import datetime

# Password hashing
pwd_config = CryptContext(schemes=["pbkdf2_sha256"],
                          default="pbkdf2_sha256",
                          pbkdf2_sha256__default_rounds=30000
                          )

# Function to hash a password
def hash_password(user_password):
    return pwd_config.hash(user_password)

# Function to check if a password matches a hash
def check_password(hashed_password, user_password):
    return pwd_config.verify(user_password, hashed_password)

# Class for handling login and signup database operations
class database_handler_login_signup():
    def __init__(self, namedb: str):
        self.connection = sqlite3.connect(namedb)
        self.cursor = self.connection.cursor()

    def run_save(self, query):
        self.cursor.execute(query)
        self.connection.commit()

    # Create the users table if it doesn't exist
    def create_table(self):
        query = f"""CREATE TABLE if not exists users(
            id INTEGER PRIMARY KEY not NULL,
            email text not NULL unique,
            password text not NULL,
            username text not NULL unique
            )"""
        self.run_query(query)

    # Function to execute a console query
    def run_query(self, query: str):
        self.cursor.execute(query)
        self.connection.commit()

    # Function to search the database
    def search(self, query):
        result = self.cursor.execute(query).fetchall()
        return result

    # Function to close the database
    def close(self):
        self.connection.close()

    # Function to insert a new user into the database
    def insert(self, email, username, password):
        query = f"INSERT into users (email, password, username) VALUES ('{email}', '{password}', '{username}')"
        self.run_query(query)

# Class for handling item database operations
class database_handler_items():
    def __init__(self, namedb: str):
        self.connection = sqlite3.connect(namedb)
        self.cursor = self.connection.cursor()

    # Create the items table if it doesn't exist
    def create_table(self):
        query = f"""CREATE TABLE if not exists items(
            id INTEGER PRIMARY KEY not NULL,
            customer_id int,
            date text,
            item text,
            size text,
            item_id int
            )"""
        self.run_query(query)

    # Function to execute a console query
    def run_query(self, query: str):
        self.cursor.execute(query)
        self.connection.commit()

    # Function to search the database
    def search(self, query):
        result = self.cursor.execute(query).fetchall()
        return result

    # Function to close the database
    def close(self):
        self.connection.close()

    # Function to insert a new item into the database
    def insert(self, customer_id, date, item, size, item_id):
        query = f"INSERT into items (customer_id, date, item, size, item_id) VALUES ('{customer_id}', '{date}', '{item}', '{size}', '{item_id}')"
        self.run_query(query)

    def run_save(self, query):
        self.cursor.execute(query)
        self.connection.commit()

# Class for handling the LoginScree
class LoginScreen(MDScreen):
    # Define a method that handles login attempts
    def try_login(self):
        # Get the email and password entered by the user
        email_entered = self.ids.email_in.text
        pass_entered = self.ids.passwd_in.text

        # Check if the email and password fields are empty
        if email_entered == "":
            # Set the error flag for the email field to True
            self.ids.email_in.error = True

        if pass_entered == "":
            # Set the error flag for the password field to True
            self.ids.passwd_in.error = True

        else:
            # Create a database handler object
            db = database_handler_login_signup(namedb="unit3_project_database.db")
            # Create a query to select the password associated with the email entered
            query = f"SELECT password FROM users WHERE email = '{email_entered}'"
            # Execute the query and get the result
            result = db.search(query)
            # Check if there is exactly one result
            if len(result) == 1:
                # Check if the entered password matches the one in the database
                if check_password(result[0][0], pass_entered):
                    # If the passwords match, print a success message, switch to the HomeScreen, and clear the email and password fields
                    print(f"Login successfull")
                    self.parent.current = "HomeScreen"
                    self.ids.email_in.text = ""
                    self.ids.passwd_in.text = ""
                else:
                    # Create and open the alert dialog to say that the email or password is wrong
                    dialog = MDDialog(title="Login error",
                                      text=f"Entered email or password is wrong")
                    dialog.open()
            else:
                dialog = MDDialog(title="Login error",
                                  text=f"Entered email or password is wrong")
                dialog.open()

    # Define a method that switches to the SignupScreen and clears the email and password fields
    def try_signup(self):
        self.parent.current = "SignupScreen"
        self.ids.email_in.text = ""
        self.ids.passwd_in.text = ""

    # Define a method that toggles the visibility of the password field
    def toggle_show_password(self):
        # Invert the value of the show_password attribute
        self.show_password = not self.show_password
        # Set the password attribute of the password field to the opposite of the show_password attribute
        self.ids.passwd_in.password = not self.show_password

    # Define the build method that returns None
    def build(self):
        return None

# Class for handling the SignupScreen
class SignupScreen(MDScreen):
    def validate_email(self, email):
        try:
            # Validate the email using email_validator module
            email_validator.validate_email(email)
            return True
        except:
            return False

    def validate_username(self, username):
        if not username:
            return False
        return True

    def try_cancel(self):
        # Change the current screen to LoginScreen and clear all the fields.
        self.parent.current = "LoginScreen"
        self.ids.e_passwd.text = ""
        self.ids.c_passwd.text = ""
        self.ids.uname.text = ""
        self.ids.email.text = ""

    def try_register(self):
        # Get the passwords entered by the user.
        passwd1 = self.ids.e_passwd.text
        passwd2 = self.ids.c_passwd.text

        username = self.ids.uname.text
        if not self.validate_username(username=username):
            # Show error message if username is blank
            self.ids.uname.error = True
            return

        email = self.ids.email.text
        # Validate the email
        if not self.validate_email(email):
            # Show error message if email is invalid
            self.ids.email.error = True
            self.ids.email.helper_text_mode = "on_error"
            self.ids.email.helper_text = "Invalid email"
            return

        if not passwd1 or not passwd2:
            if not passwd1:
                self.ids.e_passwd.error = True
                self.ids.e_passwd.helper_text_mode = "on_error"
                self.ids.e_passwd.helper_text = "Password cannot be empty"
            else:
                self.ids.c_passwd.error = True
                self.ids.c_passwd.helper_text_mode = "on_error"
                self.ids.c_passwd.helper_text = "Password cannot be empty"
            return

        pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+]).{8,}$'

        # Check if the password matches the pattern
        if not re.match(pattern, passwd1):
            self.ids.e_passwd.error = True
            self.ids.e_passwd.helper_text_mode = "on_error"
            self.ids.e_passwd.helper_text = "Password doesn't meet the requirements"
            dialog = MDDialog(title="Password doesn't meet the requirements",
                              text="The password entered must be:\n- At least 8 characters,\n- One capital letter,\n- One lowercase letter,\n- One symbol: !@#$%^&*()_+")
            dialog.open()
            return

        # Check if the two passwords match. If not, set the error flag on both fields.
        if passwd1 != passwd2:
            self.ids.e_passwd.error = True
            self.ids.c_passwd.error = True
            self.ids.e_passwd.helper_text_mode = "on_error"
            self.ids.c_passwd.helper_text_mode = "on_error"
            self.ids.e_passwd.helper_text = "Passwords don't match"
            self.ids.c_passwd.helper_text = "Passwords don't match"
            return

        # Insert the new user into the database and change the current screen to LoginScreen.
        db.insert(email=self.ids.email.text, username=self.ids.uname.text,
                  password=hash_password(self.ids.c_passwd.text))
        # Create and open the alert dialog to say that the account has created successfully

        dialog = MDDialog(title="New account",
                          text=f"The account with the username {username} has created successfully, please log in to your account")
        dialog.open()
        self.parent.current = "LoginScreen"
        self.ids.e_passwd.text = ""
        self.ids.c_passwd.text = ""
        self.ids.uname.text = ""
        self.ids.email.text = ""

    def toggle_show_password(self):
        # Toggle the show_password flag and update the password visibility of both fields.
        self.show_password = not self.show_password
        self.ids.e_passwd.password = not self.show_password
        self.ids.c_passwd.password = not self.show_password

# Class for handling the HomeScreen
class HomeScreen(MDScreen):

    # Function to log out the user
    def try_logout(self):
        # Create an MDDialog to confirm whether the user wants to sign out or not
        self.sign_out_confirmation_dialog = MDDialog(
            title="Log Out",
            text="Are you sure you want to log out?",
            buttons=[
                MDFlatButton(
                    text="Yes",
                    on_release=self.log_out_user # Call the log_out_user function when the button is pressed
                ),
                MDFlatButton(
                    text="No",
                    on_release=self.dismiss_dialog # Call the dismiss_dialog function when the button is pressed
                ),
            ],
        )
        self.sign_out_confirmation_dialog.open() # Open the dialog


    def log_out_user(self, instance):
        # Perform the signout actions
        print("User logging out")
        self.parent.current = "LoginScreen"
        self.sign_out_confirmation_dialog.dismiss()

    def dismiss_dialog(self, instance):
        self.sign_out_confirmation_dialog.dismiss()

    # Function to add a new item
    def try_newitem(self):
        print("Trying adding new item")
        self.parent.current = 'NewitemScreen'

    def build(self):
        return

# Class for handling the NewitemScreen
class NewitemScreen(MDScreen):

    def show_date_picker(self):
        calendar = MDDatePicker()
        calendar.bind(on_save=self.get_date)
        calendar.open()
        
    def get_date(self, instance, date, date_range):
        date = date.strftime("%d-%m-%Y")
        self.ids.date_picker.text = str(date)
    
    input_format = "%d-%m-%Y" # input format for date text field

    def validate_customer_id(self, text):
        """
        Validate the customer ID entered in the customer_id MDTextField.
        """
        try:
            customer_id = int(text)
        except ValueError:
            self.ids.customer_id.error = True

    def validate_item_id(self, text):
        """
        Validate the item ID entered in the item_id MDTextField.
        """
        try:
            item_id = int(text)
        except ValueError:
            self.ids.item_id.error = True

    def try_add(self):
        # Create a database handler object
        db_items = database_handler_items(namedb="unit3_project_database.db")
        # Insert the new item into the database
        db_items.insert(self.ids.customer_id.text, self.ids.date_picker.text, self.ids.item.text, self.ids.size.value, self.ids.item_id.text)
        print("Item added")

        # Create and open the alert dialog to confirm item has been added
        dialog = MDDialog(title="Thank you, item added!", text=f"Your item ID: {self.ids.item_id.text} has been successfully added.")
        dialog_buttons = [MDFlatButton(text="OK", on_release=dialog.dismiss, md_bg_color=[1, 1, 1, 1])]
        dialog.buttons = dialog_buttons
        dialog.open()

        # Clear the input fields and switch to HomeScreen
        self.ids.customer_id.text = ""
        self.ids.date_picker.text = "Pick a date"
        self.ids.item.text = ""
        self.ids.size.value = 16.5
        self.ids.size_label.text = "16.5"
        self.ids.item_id.text = ""
        self.parent.current= 'HomeScreen'

    def try_cancel(self):
        # Clear the input fields and switch to HomeScreen
        self.parent.current = 'HomeScreen'
        self.ids.customer_id.text = ""
        self.ids.date_picker.text = "Pick a date"
        self.ids.item.text = ""
        self.ids.size.value = 16.5
        self.ids.size_label.text = "16.5"
        self.ids.item_id.text = ""

    def build(self):
        return

# Class for handling the BorrowedItemsScreen
class BorrowedItemsScreen(MDScreen):
    # class_variable
    data_table = None

    def update(self):
        # Read the database and update the table
        db = database_handler_items("unit3_project_database.db")
        query = "SELECT customer_id, date, item, size, item_id from items"
        data = db.search(query)
        print(data)
        db.close()
        self.data_table.update_row_data(None, data)

    def delete(self):
        # Function to delete checked rows in the table
        checked_rows = self.data_table.get_row_checks() # Get the checked rows
        print(checked_rows)
        # delete
        db = database_handler_items("unit3_project_database.db")
        for r in checked_rows:
            item_id = r[4]  # use item_id instead of id
            print(item_id)
            query = f"delete from items where item_id = {item_id}"  # use item_id instead of id
            print(query)
            db.run_save(query)
            # Create and open the alert dialog to confirm item has been deleted
            dialog = MDDialog(title="Thank you, item deleted!",
                              text=f"Your item ID: {item_id} has been successfully deleted.")
            dialog.open()
        db.close()
        self.update()

    def on_pre_enter(self, *args):
        # Code to run before the screen is created
        self.data_table = MDDataTable(
            size_hint=(.9, .75),
            pos_hint={"center_x": .5, "center_y": .5},
            use_pagination=True,
            check=True,
            background_color = "#689ebd",
            # Title of the columns
            column_data=[("Customer ID", 40),
                         ("Date", 25),
                         ("Kind", 25),
                         ("Item ID", 20),
                         ("Size", 50)]
        )

        # Add functions for events of the mouse
        self.data_table.bind(on_check_press=self.check_pressed)
        self.add_widget(self.data_table)  # Add the table to the GUI
        self.update()

    def check_pressed(self, table, current_row):
        # Function to handle when a check mark is pressed
        print("a check mark was pressed", current_row)

# Class to run the application
class unit3_project(MDApp):
    def build(self):
        return

db = database_handler_login_signup(namedb="unit3_project_database.db") # Create a database handler object
db.create_table() # Create the table
print("Database created") # Print a message to the console that the database has been created

db_items = database_handler_items(namedb="unit3_project_database.db") # Create a database handler object
db_items.create_table() # Create the table
print("Database created") # Print a message to the console that the database has been created

test = unit3_project() # Create an object of the application
test.run() # Run the application
print("App running") # Print a message to the console that the application is running

db.close() # Close the database
db_items.close() # Close the database
print("Database closed") # Print a message to the console that the database has been closed
