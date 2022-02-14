import threading
import tkinter as tk
from tkinter import *
from selenium.common.exceptions import NoSuchElementException


class GymBotGUI:
    def __init__(self, iac01bot, toaster):
        super().__init__()
        self.iac01bot = iac01bot
        self.toaster = toaster
        self.window = tk.Tk()
        self.username_login = StringVar()
        self.password_login = StringVar()
        self.time_clicked = StringVar()
        self.time_entry = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                           '21']
        self.username_entry = None
        self.password_entry = None
        self.username = None
        self.password = None
        self.time_slot_text = None

    def create_main_window(self):
        self.window.geometry("500x250")
        self.window.title("GymBot®")
        tk.Label(text="Welcome to GymBot®!").pack()
        tk.Label(text="Ensure you do not currently have a booking. Appointments will be booked for today only.").pack()
        tk.Label(text="Select the hour of desired appointment start time (24 hour clock):").pack()
        self.time_clicked.set("06")
        OptionMenu(self.window, self.time_clicked, *self.time_entry).pack()

        tk.Label(text="Please enter U of C credentials below to login:").pack()
        tk.Label(self.window, text="Username *").pack()
        self.username_entry = tk.Entry(self.window, textvariable=self.username_login)
        self.username_entry.pack()
        tk.Label(self.window, text="Password *").pack()
        self.password_entry = tk.Entry(self.window, textvariable=self.password_login, show="*")
        self.password_entry.pack()
        tk.Label(self.window, text="").pack()
        login_button = tk.Button(self.window, text="Login", command=self.get_creds)
        login_button.pack()
        #self.window.bind('<Return>', self.get_creds())  # Allow us to use 'return' to submit
        self.window.mainloop()

    def get_creds(self):
        self.username = self.username_login.get()
        self.password = self.password_login.get()  # Mask??????
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)

        login_success = self.iac01bot.login(self.username, self.password)
        if login_success:
            threading.Thread(target=self.get_gym_time).start()
            # threading.Thread(target=self.get_gym_time, daemon=True).start()
        else:
            self.invalid_user()

    def invalid_user(self):
        invalid_usr_win = Toplevel(self.window)
        invalid_usr_win.title("Invalid User")
        Label(invalid_usr_win, text="Invalid credentials, please try again.").pack()
        Button(invalid_usr_win, text="Retry", command=invalid_usr_win.destroy).pack()

    def get_gym_time(self):
        time_available = False
        wheel_index = 0

        desired_time = self.time_clicked.get() + ":00 to " + str(int(self.time_clicked.get()) + 1) + ":00"
        print("Desired Time:", desired_time)
        nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']

        while not time_available:  # main loop
            # Refresh / login if timed out
            logged_in = self.iac01bot.login_status()
            if logged_in:
                self.iac01bot.driver.refresh()
            else:
                self.iac01bot.login(self.username, self.password)

            # Get available slots / Check if desired slot is available
            slots_array = []
            for i in range(16):
                try:
                    slot_id = f"ctl00_ContentPlaceHolder1_ctl00_repAvailFitness_ctl{nums[i]}_lnkBtnFitness"
                    time_slot = self.iac01bot.driver.find_element('id', slot_id)
                    text = time_slot.text
                    slots_array.append(text)
                    if desired_time in slots_array[i]:
                        time_available = True
                        self.time_slot_text = text
                        break
                except NoSuchElementException:
                    pass
            if not time_available:
                loading_wheel = ['/', '─', "\\", '|']
                print(f'\rNot available - trying again   {loading_wheel[wheel_index]}', end="")
                wheel_index = wheel_index + 1
                if wheel_index == 4:
                    wheel_index = 0

        # Check for an existing booking - do later

        # Book desired time slot
        if time_available:
            slot = self.iac01bot.driver.find_element('id', slot_id)
            slot.click()
            print(f"\nBooked {self.time_slot_text[5:24]}{' ' * 6}")
            self.toaster.show_toast("GymBot®", "Your appointment has been booked!", icon_path=self.toaster.icon)
            self.window.destroy()
