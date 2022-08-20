from tkinter import *
import secrets
from tkinter import messagebox, simpledialog
import pyperclip
import json

IMG = "logo.png"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
#   generates a 'true' random, url safe string to serve as our new password
def generate():
    generated_password = secrets.token_urlsafe(20)
    #   enters the generated password into the password input box for you so you don't have to copy and paste it in
    pass_ent.insert(0, generated_password)
    #   copies the generated password to your clipboard, so you can quickly and easily paste it into the app/web page
    #   that is requesting a new password input
    pyperclip.copy(generated_password)


# --------------------------- SEARCH FOR DATA ------------------------------ #
#   Searches our generated text file for json data, and handles exceptions...
def data_search():
    website = web_ent.get()
    #   catches an invalid website input
    if len(website) <= 1:
        messagebox.showerror(title="Whoops!", message="Please enter a website name and try again.")
    else:

        try:  # try to retrieve our previously saved password data
            open("data.json")
        #   if the saved password data CANNOT be found, the user is prompted to start saving some passwords
        except FileNotFoundError:
            messagebox.showerror(title="Whoops! File not found.", message="No data file exists yet! Start by saving "
                                                                          "some logins and passwords!")
        #   if the saved password file CAN be found, the program will open our data json file
        else:
            with open("data.json", mode="r") as data_file:
                data = json.load(data_file)
                try:  # the program will try to find saved username and password data for the given website input
                    website_data = data[website]

                except KeyError:  # if this data CANNOT be found. user is prompted to generate a new password instead.
                    messagebox.showerror(title="Whoops! Data not found.",
                                         message="No details for this website exists yet! \n"
                                                 "Try generating a new password for this site instead.")

                else:  # if this data IS found, the program will request a master password to authenticate the user
                    master_password = simpledialog.askstring('Input Master Password',
                                                             'Please enter your master password: ')
                    if master_password == saved_master_password:  # check password input against stored password
                        # if we pass this authentication step, the requested data will be displayed
                        email_data = website_data["email"]
                        password_data = website_data["password"]
                        messagebox.showinfo(title=website_data,
                                            message=f"Login: {email_data}\nPassword:{password_data}")
                        # now, we'll clear the website entry section of the window to "reset" the gui
                        web_ent.delete(0, END)

                    # ---------------------------- SAVE PASSWORD ------------------------------- #


# saves our user inputted website and user inputted password, OR the password we randomly generated, to our json file
def save_entry():
    website = web_ent.get()
    email = em_ent.get()
    password = pass_ent.get()
    new_data = {
        website: {
            "email": email,
            "password": password,
        }
    }
    #   catches an invalid website input
    if len(website) <= 1:
        messagebox.showerror(title="Whoops!", message="Please enter a website name and try again.")
    #   catches an invalid password input, prompts the user to try our "generate" button
    elif len(password) <= 1:
        messagebox.showerror(title="Whoops!", message="Please enter a password, or click 'generate' to generate a "
                                                      "random password, and try again.")
    #   if both username and password inputs ARE valid, we will store them in our json file.
    else:
        #   tries to open our data.json file
        try:
            open("data.json")
        #   if no file exists yet, we'll create a new one.
        except FileNotFoundError:
            with open("data.json", mode="w") as data_file:
                # saving new data into json dict
                json.dump(new_data, data_file, indent=4)
        #   if file DOES exist, we'll read the file, and then update the file with our newly inputted/generated data
        else:
            with open("data.json", mode="r") as data_file:
                # reading old data
                data = json.load(data_file)
                # updating old data with new data
                data.update(new_data)
            with open("data.json", mode="w") as data_file:
                # saving updated data into dictionary
                json.dump(data, data_file, indent=4)
        # finally, we will clear our input fields, and await a new password search or input.
        finally:
            web_ent.delete(0, END)
            pass_ent.delete(0, END)


# ---------------------------- UI SETUP ------------------------------- #
#   using a basic grid format to place our elements

#   General setup
window = Tk()
window.title("Offline Password Manager")
window.config(width=200, height=200, padx=50, pady=50)
canvas = Canvas(width=200, height=200, highlightthickness=0)

#   Pretty logo
image = PhotoImage(file=IMG)
canvas.create_image(100, 100, image=image)
canvas.grid(row=0, column=1)

#   Making Labels and Entry fields
web_lab = Label(text="Website:", highlightthickness=0)
web_lab.grid(row=1, column=0)
web_ent = Entry(width=21, highlightthickness=0)
web_ent.grid(row=1, column=1)
web_ent.focus()

em_lab = Label(text="E-Mail/Username:", highlightthickness=0)
em_lab.grid(row=2, column=0)
em_ent = Entry(width=36, highlightthickness=0)
#   Adds a default email to the email input. Swap this for your own email to make life easier!
em_ent.insert(0, "user@example.com")
em_ent.grid(row=2, column=1, columnspan=2)

pass_lab = Label(text="Password:", highlightthickness=0)
pass_lab.grid(row=3, column=0)
pass_ent = Entry(width=21, highlightthickness=0)
pass_ent.grid(row=3, column=1)

#   Making Buttons, linking them to functions defined above.
gen_but = Button(text="Generate Password", width=10, borderwidth=0, command=generate)
gen_but.grid(row=3, column=2)

search_button = Button(text="Search", width=10, borderwidth=0, command=data_search)
search_button.grid(row=1, column=2)

add_but = Button(text="Add", width=34, borderwidth=0, command=save_entry)
add_but.grid(row=4, column=1, columnspan=2)

# this is the master.key checking feature allowing us to hide our saved data behind a "master password" protective layer
try:  # tries to open the master.key file
    with open('master.key', 'r') as master_file:    # if successful, then the file exists.
        saved_master_password = master_file.read()  # the file's contents are assigned to saved_master_password var.
except FileNotFoundError:  # if unsuccessful, a new file is created and written using input from "Welcome" pop-up window
    with open('master.key', 'w') as master_file:
        master_password_provided = simpledialog.askstring('Welcome :)', "Please set a master password.\n"
                                                                        "This will be what you use to access all of "
                                                                        "your other passwords, so don't forget it!")
        saved_master_password = master_password_provided
        master_file.write(master_password_provided)

window.mainloop()  # keeps our window open until exited, so that we can successfully interact with our program
