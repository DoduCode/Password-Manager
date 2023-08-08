import customtkinter
from cryptography.fernet import Fernet

import secrets
import string
import json
import os

class SliderFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.slider = customtkinter.CTkSlider(self, from_= 8, to=50, orientation="vertical", height = 110, width = 10, command = self.update)
        self.slider.grid(row = 0, column = 0, padx=(40, 10), pady=0, sticky="e")

        self.label = customtkinter.CTkLabel(self, text = str(int(self.slider.get())))
        self.label.grid(row = 0, column = 1, padx=0, pady=0, sticky="w")

    def update(self, value):
        self.label.configure(text = str(int(value)))

    def get(self):
        return self.slider.get()

class OptionsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.checkbox_1 = customtkinter.CTkCheckBox(self, text = "Mixed Alphabets")
        self.checkbox_1.grid(row=0, column=0, padx=10, pady=(10, 0), sticky = "w")
        self.checkbox_2 = customtkinter.CTkCheckBox(self, text = "Special Characters")
        self.checkbox_2.grid(row=1, column=0, padx=10, pady = (10, 0), sticky = "w")
        self.checkbox_3 = customtkinter.CTkCheckBox(self, text = "Numbers")
        self.checkbox_3.grid(row = 2, column = 0, padx = (10, 265), pady = (10, 10), sticky = "w")

        self.checkbox_1.select()
        self.checkbox_2.select()
        self.checkbox_3.select()
        
    def get(self):
        checked_checkboxes = []
        if self.checkbox_1.get() == 1:
            checked_checkboxes.append(self.checkbox_1.cget("text"))
        if self.checkbox_2.get() == 1:
            checked_checkboxes.append(self.checkbox_2.cget("text"))
        if self.checkbox_3.get() == 1:
            checked_checkboxes.append(self.checkbox_3.cget("text"))

        return checked_checkboxes

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Password Manager")
        self.geometry("390x240")
        self.minsize(385, 240)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        if os.path.isfile("key.json"):
            self.key = open("key.json", "rb").read()
            self.fernet = Fernet(self.key)

        else:
            self.key = Fernet.generate_key()
            with open("key.json", "wb") as key_file:
                key_file.write(self.key)
            self.fernet = Fernet(self.key)

        self.entry = customtkinter.CTkEntry(self, placeholder_text="Password", width=300, state = 'normal')
        self.entry.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="nsw")

        self.copy = customtkinter.CTkButton(self, text = "Copy", command=self.copy, width = 40, height=48)
        self.copy.grid(row=0, column=0, padx=(315, 10), pady=(5, 0), sticky="new")

        self.options = OptionsFrame(self)
        self.options.grid(row=2, column=0, padx=(10, 10), pady=(10, 0), sticky="nsw")

        self.sliders = SliderFrame(self)
        self.sliders.grid(row=2, column=0, padx=(250, 0), pady=(10, 0), sticky="nsw")

        self.gen_button = customtkinter.CTkButton(self, text="Generate", command=self.gen_password, width = 115, height = 48)
        self.gen_button.grid(row=3, column=0, padx=(10, 10), pady=10, sticky = "w")

        self.save_button = customtkinter.CTkButton(self, text="Save", command=self.save_pass, width = 115, height = 48)
        self.save_button.grid(row=3, column=0, padx=(10, 10), pady=10)

        self.search_button = customtkinter.CTkButton(self, text="Search", command=self.search_pass, width = 115, height = 48)
        self.search_button.grid(row=3, column=0, padx=(10, 10), pady=10, sticky = "e")

    def gen_password(self):
        if not self.options.get():
            self.entry.delete(0, len(self.entry.get()))
            self.focus()
            self.entry.configure(placeholder_text = "Choose an option")

        else:
            pool = ""

            if 'Mixed Alphabets' in self.options.get(): pool += string.ascii_letters
            if 'Special Characters' in self.options.get(): pool += string.punctuation
            if 'Numbers' in self.options.get(): pool += string.digits

            # Generate a random password of the given length
            self.password = ''.join (secrets.choice (pool) for _ in range(int(self.sliders.get())))
            self.entry.delete(0, len(self.entry.get()))
            self.entry.insert(0, self.password)

            self.save_button.configure(state = 'normal')

    def copy(self):
        if self.entry.get():
            self.clipboard_clear()
            self.clipboard_append(self.entry.get())

    def save_pass(self):
        try:
            with open("pass.json", "rb") as f:
                # Load the dictionary from the JSON file
                passwords_bytes = f.read()

            passwords_bytes = self.fernet.decrypt(passwords_bytes)
            passwords_json = passwords_bytes.decode("utf-8")
            self.passwords = json.loads(passwords_json)

        except:
            self.passwords = {}

        if not self.entry.get():
            self.focus()
            self.entry.configure(placeholder_text = "Please Generate Password")

        else:
            self.save_password_txt = self.entry.get()

            self.entry.delete(0, len(self.entry.get()))
            self.focus()
            self.entry.configure(placeholder_text = "Name to Save (Press Enter)")

            self.entry.bind("<Return>", self.save_password)

            self.save_button.configure(state = 'disabled')

        # with open('pass.txt', 'a') as f:
        #     f.write(self.fernet.encrypt(b''))

    def save_password(self, e):
        if self.entry.get() != "GetAll":
            self.entry.unbind("<Return>")
            self.passwords[str(self.entry.get())] = self.save_password_txt
            self.json_passwords = json.dumps(self.passwords)
            self.passwords_bytes = self.json_passwords.encode("utf-8")

            with open('pass.json', 'wb') as f:
                self.key = Fernet.generate_key()
                with open("key.json", "wb") as key_file:
                    key_file.write(self.key)
                self.fernet = Fernet(self.key)
                f.write(self.fernet.encrypt(self.passwords_bytes))
                f.write(b'\n\n')

            self.save_button.configure(state = 'normal')
            self.entry.delete(0, len(self.entry.get()))
            self.focus()
            self.entry.configure(placeholder_text = "Saved")
        
        else:
            self.entry.delete(0, len(self.entry.get()))
            self.focus()
            self.entry.configure(placeholder_text = "You cannot use this word")

    def search_pass(self):
        self.entry.delete(0, len(self.entry.get()))

        try:
            with open("pass.json", "rb") as f:
                # Load the dictionary from the JSON file
                passwords_bytes = f.read()

            passwords_bytes = self.fernet.decrypt(passwords_bytes)
            passwords_json = passwords_bytes.decode("utf-8")
            self.passwords = json.loads(passwords_json)

            self.focus()
            self.entry.configure(placeholder_text = "Enter name of website (Press Enter)")

            self.entry.bind("<Return>", self.search_password)

        except:
            self.focus()
            self.entry.configure(placeholder_text = "No Passwords Saved")

    def search_password(self, e):
        word = self.entry.get()
        try:
            self.entry.delete(0, len(self.entry.get()))
            self.entry.insert(0, self.passwords[word])

        except:
            if word == "GetAll":
                self.entry.delete(0, len(self.entry.get()))
                self.entry.insert(0, self.passwords)

            else:
                self.focus()
                self.entry.configure(placeholder_text = f"Cound not find {word}")

        self.entry.unbind("<Return>")

app = App()
app.mainloop()