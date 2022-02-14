import threading
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import time
from selenium.common.exceptions import NoSuchElementException


class GymBotGUI:
    def __init__(self, iac01bot, toaster):
        super().__init__()
        self.print_time = StringVar
        self.login_success = None
        self.backend_thread = None
        self.instance_loading_window = None
        self.instance_invalid_usr_win = None
        self.invalid_usr_win = None
        self.bar = None
        self.time_available = False
        self.iac01bot = iac01bot
        self.toaster = toaster
        self.window = tk.Tk()
        self.loading_window = None
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
        self.time_clicked.set("06")  # For some reason doesn't get saved
        OptionMenu(self.window, self.time_clicked, *self.time_entry).pack()

        tk.Label(text="Please enter U of C credentials below to login:").pack()
        tk.Label(self.window, text="Username *").pack()
        self.username_entry = tk.Entry(self.window, textvariable=self.username_login)
        self.username_entry.pack()
        tk.Label(self.window, text="Password *").pack()
        self.password_entry = tk.Entry(self.window, textvariable=self.password_login, show="*")
        self.password_entry.pack()

        login_button = tk.Button(self.window, text="Login", command=lambda: self.threading())
        login_button.pack(pady=5)
        # self.window.bind('<Return>', self.get_creds())  # Allow us to use 'return' to submit
        self.window.mainloop()

    def threading(self):
        self.backend_thread = threading.Thread(target=self.get_creds())
        self.backend_thread.start()
        if self.login_success:
            self.loading_page()

    def get_creds(self):
        self.username = self.username_login.get()
        self.password = self.password_login.get()

        self.login_success = self.iac01bot.login(self.username, self.password)
        if self.login_success:
            threading.Thread(target=self.get_gym_time).start()
        else:
            self.invalid_user()

    def invalid_user(self):
        self.instance_invalid_usr_win = tk.Tk()
        self.instance_invalid_usr_win.withdraw()

        self.invalid_usr_win = Toplevel(self.instance_invalid_usr_win)
        self.invalid_usr_win.title("Invalid User")
        tk.Label(self.invalid_usr_win, text="Invalid credentials, please try again.").pack()
        tk.Button(self.invalid_usr_win, text="Retry", command=self.destroy_invalid_usr_win).pack()

    def destroy_invalid_usr_win(self):
        self.invalid_usr_win.destroy()
        self.instance_invalid_usr_win.destroy()

    def get_gym_time(self):
        wheel_index = 0

        desired_time = self.time_clicked.get() + ":00 to " + str(int(self.time_clicked.get()) + 1) + ":00"
        self.print_time = "Desired Time:" + desired_time
        print(self.print_time)
        nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']

        while not self.time_available:  # main loop
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
                        self.time_available = True
                        self.time_slot_text = text
                        break
                except NoSuchElementException:
                    pass
            if not self.time_available:
                loading_wheel = ['/', '─', "\\", '|']
                print(f'\rNot available - trying again   {loading_wheel[wheel_index]}', end="")
                wheel_index = wheel_index + 1
                if wheel_index == 4:
                    wheel_index = 0

        # Check for an existing booking - do later

        # Book desired time slot
        if self.time_available:
            slot = self.iac01bot.driver.find_element('id', slot_id)
            slot.click()
            print(f"\nBooked {self.time_slot_text[5:24]}{' ' * 6}")
            self.toaster.show_toast("GymBot®", "Your appointment has been booked!", icon_path=self.toaster.icon)
            self.window.destroy()

    def loading_page(self):

        self.window.destroy()
        self.instance_loading_window = tk.Tk()
        self.instance_loading_window.withdraw()

        self.loading_window = tk.Toplevel(self.instance_loading_window)
        self.loading_window.geometry("500x200")
        self.loading_window.title("GymBot®")
        # Progress bar
        self.bar = Progressbar(self.loading_window, orient=HORIZONTAL, length=400, mode='indeterminate')
        self.bar.pack(pady=20)
        self.bar.start()

        loading_wheel = 0

        tk.Label(self.loading_window, textvariable=self.print_time).pack()
        tk.Label(self.loading_window, text="We are currently looking for your gym time").pack()
        tk.Label(self.loading_window, textvariable=loading_wheel).pack()

        # while not self.time_available:
        #     print("TEST")
        #     #loading_wheel += 1
        #     self.loading_window.update_idletasks()

        self.instance_loading_window.mainloop()

