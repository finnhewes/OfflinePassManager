from tkinter import *
import secrets
import base64
from tkinter import messagebox, simpledialog
import pyperclip
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

IMG = "logo.png"  # I've included the logo file I made in the main repo, but feel free to substitute your own design


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate():
    generated_password = secrets.token_urlsafe(16)  # generates a 'true' random, url safe string, 16 bytes long
    #   enters the generated password into the password input box for you so you don't have to copy and paste it in
    pass_ent.insert(0, generated_password)
    #   copies the generated password to your clipboard, so you can quickly and easily paste it into the app/web page
    #   that is requesting a new password input
    pyperclip.copy(generated_password)


# --------------------------- SEARCH FOR DATA ------------------------------ #
#   Searches our generated text file for json data, and handles exceptions...
def data_search():
    website = web_ent.get()
    #   reject invalid website input
    if len(website) <= 1:
        messagebox.showerror(title="Whoops!", message="Please enter a website name and try again.")
    else:
        try:  # try to retrieve the previously saved password
            open("data.json")

        except FileNotFoundError:  # if the data file can't be found, the user is prompted to start saving some data
            messagebox.showerror(title="Whoops! File not found.", message="No data file exists yet! Start by saving "
                                                                          "some logins and passwords!")
        else:  # if the saved password file CAN be found, the program will open our data json file
            with open("data.json", mode="r") as data_file:
                data = json.load(data_file)
                try:  # try to find saved username and password data for the given website input
                    website_data = data[website]
                #   if this data CANNOT be found, the user is prompted to generate a new password for this site instead.
                except KeyError:
                    messagebox.showerror(title="Whoops! Data not found.",
                                         message="No details for this website exists yet! \n"
                                                 "Try generating a new password for this site instead.")
                #   if this data IS found, the program makes a popup window requesting the master password. if  entered
                #   correctly, the program makes another popup window populated with the saved (decrypted) login data
                else:
                    master_password = simpledialog.askstring('Input Master Password',
                                                             'Please enter your master password: ')
                    master_password_encoded = master_password.encode()  # convert entered pass into bytes

                    kdf2 = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                        backend=default_backend(),
                    )
                    generated_key = base64.urlsafe_b64encode(kdf2.derive(master_password_encoded))  # stores our new key

                    with open('config.config', 'r') as m:  # opens saved master key file
                        saved_key = m.read().encode()  # compared new key to saved key on file
                        if generated_key == saved_key:
                            email_data_encrypted = website_data["email"].encode()  # decrypt/decode this
                            email_data_decrypted = fern.decrypt(email_data_encrypted).decode()
                            password_data_encrypted = website_data["password"].encode()  # decrypt/decode this
                            password_data_decrypted = fern.decrypt(password_data_encrypted).decode()
                            # if we've made it this far, then we've authenticated, and we can display the login info.
                            messagebox.showinfo(title=website_data, message=f"Login: {email_data_decrypted}\n"
                                                                            f"Password:{password_data_decrypted}")
                            web_ent.delete(0, END)  # clears the website field, effectively "resetting" our gui window


# ---------------------------- SAVE PASSWORD ------------------------------- #
# saves our user inputted website and user inputted password, OR the password we randomly generated, to our json file
def save_entry():
    website = web_ent.get()
    email = em_ent.get()
    password = pass_ent.get()

    email_entry_encoded = email.encode()
    email_entry_encrypted = fern.encrypt(email_entry_encoded).decode()  # must be decoded to store in json
    password_entry_encoded = password.encode()
    password_entry_encrypted = fern.encrypt(password_entry_encoded).decode()  # must be decoded to store in json

    new_data = {
        website: {
            "email": email_entry_encrypted,
            "password": password_entry_encrypted,
        }
    }
    if len(website) <= 1:  # catch invalid website input
        messagebox.showerror(title="Whoops!", message="Please enter a website name and try again.")
    elif len(password) <= 1:  # catch invalid password input, prompts the user to try our "generate" button
        messagebox.showerror(title="Whoops!", message="Please enter a password, or click 'generate' to generate a "
                                                      "random password, and try again.")
    #   if both username and password inputs ARE valid, we will store them in our json file.
    else:
        try:  # try to open our data.json file
            open("data.json")
        except FileNotFoundError:  # if no file exists yet, we'll create a new one.
            with open("data.json", mode="w") as data_file:
                json.dump(new_data, data_file, indent=4)  # saving new data into json dict
        else:  # if file DOES exist, we'll read the file and update it with our newly inputted/generated data
            with open("data.json", mode="r") as data_file:
                data = json.load(data_file)  # reading old data
                data.update(new_data)  # updating old data with new data
            with open("data.json", mode="w") as data_file:
                json.dump(data, data_file, indent=4)  # saving updated data into dictionary
        finally:  # clear our input fields, effectively "resetting" our gui window and await a new input.
            web_ent.delete(0, END)
            pass_ent.delete(0, END)


# ---------------------------- UI SETUP ------------------------------- #
# General setup, using a basic grid format to place our elements
window = Tk()
window.title("Password Manager")
window.config(width=200, height=200, padx=50, pady=50)
canvas = Canvas(width=200, height=200, highlightthickness=0)

# Obligatory hacker themed logo
image = PhotoImage(file=IMG)
canvas.create_image(100, 100, image=image)
canvas.grid(row=0, column=1)

# Labels and Entry fields
web_lab = Label(text="Website:", highlightthickness=0)
web_lab.grid(row=1, column=0)
web_ent = Entry(width=21, highlightthickness=0)
web_ent.grid(row=1, column=1)
web_ent.focus()

em_lab = Label(text="E-Mail/Username:", highlightthickness=0)
em_lab.grid(row=2, column=0)
em_ent = Entry(width=36, highlightthickness=0)
em_ent.insert(0, "user@example.com")
em_ent.grid(row=2, column=1, columnspan=2)

pass_lab = Label(text="Password:", highlightthickness=0)
pass_lab.grid(row=3, column=0)
pass_ent = Entry(width=21, highlightthickness=0)
pass_ent.grid(row=3, column=1)

# Making Buttons, linking them to functions defined above.
gen_but = Button(text="Generate Password", width=10, borderwidth=0, command=generate)
gen_but.grid(row=3, column=2)

search_button = Button(text="Search", width=10, borderwidth=0, command=data_search)
search_button.grid(row=1, column=2)

add_but = Button(text="Add", width=34, borderwidth=0, command=save_entry)
add_but.grid(row=4, column=1, columnspan=2)

# ________________ File Structure Check/Setup _______________ #
try:
    with open('config.config', 'r') as master_file:  # looks for the master key file, with diversion name
        master_key = master_file.read()
except FileNotFoundError:  # if no master key file is found, that means this is the first time running the program, and
    # some setup is in order. We'll need to create a number of key files to encrypt and decrypt our data
    with open('gui.config', 'wb') as salt_file:  # the salt key file won't exist either, so we'll create one, and also
        # obscure the name a little, to be less obvious
        new_salt = secrets.token_urlsafe(16).encode()
        salt_file.write(new_salt)
    with open('username.default', 'w') as user_file:  # collect a username/email to display in the username text box.
        user_provided = simpledialog.askstring('Welcome :)', "Please enter the username/email that you use\nmost often "
                                                             "when signing up for services.\n\nThis can be changed for "
                                                             "individual logins\nif desired.\n\nThis username/email "
                                                             "will show up\nautomatically when this program opens.")
        user_file.write(user_provided)
    with open('config.config', 'wb') as master_file:  # we'll also need to create a master.key file here
        password_provided = simpledialog.askstring('Welcome :)', "Please enter a master password.\n"
                                                                 "This will be what you use to access\nall of your "
                                                                 "other passwords, so\ndon't forget it!")
        password_encoded = password_provided.encode()  # convert entered pass to bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=new_salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_encoded))  # can only use kdf once
        master_file.write(key)  # writes our key to the master.key file.

    with open('nerf.config', 'wb') as k_file:  # we'll also need to create a fernet key file to encrypt and decrypt data
        # the name is stupid to obscure the fact that it's an encryption key.
        key = Fernet.generate_key()
        k_file.write(key)

finally:  # executes after both the try and except above. We'll use this to gather and store our keys
    with open('gui.config', 'rb') as s:  # reads salt file
        salt = s.read()

    with open('nerf.config', 'rb') as f:  # reads fernet key
        key = f.read()
        fern = Fernet(key)

    with open('username.default', 'r') as username_file:
        username = username_file.read()
        em_ent.delete(0, END)
        em_ent.insert(0, username)

window.mainloop()  # keeps our window open until exited, so that we can successfully interact with our program
