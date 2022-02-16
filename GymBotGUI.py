import threading
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
import datetime
from astral import LocationInfo
from astral.sun import sun
from datetime import date
import logging
from tkinter import font as tk_font


class GymBotGUI:
    def __init__(self, iac01bot, toaster, calendar):
        super().__init__()
        self.iac01bot = iac01bot
        self.toaster = toaster
        self.calendar = calendar
        self.icon_photo = None
        self.logger = logging.getLogger(__name__)

        self.login_success = None
        self.backend_thread = None
        self.instance_loading_window = None
        self.instance_invalid_usr_win = None
        self.invalid_usr_win = None
        self.bar = None
        self.time_available = False
        self.window = tk.Tk()
        self.loading_window = None
        self.username_login = StringVar()
        self.password_login = StringVar()
        self.time_clicked = StringVar()
        self.time_entry = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
        self.username = None
        self.password = None
        self.time_menu = None
        self.toggle_button = None
        self.add_to_cal = False
        self.background_colour = None
        self.font_colour = None
        self.menu_colour = None
        self.entry_colour = None
        self.entry_font_colour = None
        self.font_type20 = ("Bahnschrift Light", 20)
        self.font_type13 = ("Bahnschrift Light", 13)
        self.font_type10 = ("Bahnschrift Light", 10)
        self.option_menu_font = tk_font.Font(family='Bahnschrift Light', size=13)
        self.dropdown_font = tk_font.Font(family='Bahnschrift Light', size=13)

    def create_main_window(self):
        self.window.iconphoto(False, self.icon_photo)  # Taskbar icon
        self.window.geometry("700x437")
        self.window.title("GymBot®")
        self.window.configure(bg=self.background_colour)
        tk.Label(text="Welcome to GymBot®!", bg=self.background_colour, fg=self.font_colour, font=self.font_type20).pack()
        tk.Label(text="Ensure you do not currently have a booking. Appointments will be booked for today only.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(text="Select the hour of desired appointment start time (24 hour clock):", bg=self.background_colour,fg=self.font_colour, font=self.font_type13).pack()

        # no arrow?
        self.time_clicked.set("06")
        self.time_menu = tk.OptionMenu(self.window, self.time_clicked, *self.time_entry)
        self.time_menu.pack(pady=10)
        self.time_menu.config(font=self.option_menu_font, fg=self.font_colour, bg=self.menu_colour)  # set the button font
        menu = self.window.nametowidget(self.time_menu.menuname)
        menu.config(font=self.dropdown_font, fg=self.font_colour, bg=self.menu_colour)  # Set the dropdown menu's font

        tk.Label(text="Please enter U of C credentials below to login:", bg=self.background_colour, fg=self.font_colour,font=self.font_type13).pack()
        tk.Label(self.window, text="Username *", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Entry(self.window, textvariable=self.username_login,bg=self.entry_colour, fg=self.entry_font_colour, font=self.font_type13).pack()
        tk.Label(self.window, text="Password *", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Entry(self.window, textvariable=self.password_login, show="*", bg=self.entry_colour, fg=self.entry_font_colour,font=self.font_type13).pack()
        tk.Button(self.window, text="Login", command=lambda: self.cred_thread(), bg=self.background_colour, fg=self.font_colour, font=self.font_type13, width=5).pack(pady=10)

        tk.Label(self.window, text="Add to calendar:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        self.toggle_button = tk.Button(self.window, text="OFF", command=self.toggle, bg=self.background_colour, fg=self.font_colour, font=self.font_type13, width=5)
        self.toggle_button.pack(pady=10)

        tk.Label(text="Created with love, by Lukas Morrison and Nathan Tham", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).pack()
        self.window.mainloop()

    def cred_thread(self):
        self.backend_thread = threading.Thread(target=self.get_creds()).start()
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
        self.logger.warning("Invalid User")
        if not self.invalid_usr_win:
            self.create_invalid_usr_win()
        else:
            self.destroy_invalid_usr_win()
            self.create_invalid_usr_win()

    def create_invalid_usr_win(self):
        self.instance_invalid_usr_win = tk.Tk()
        self.instance_invalid_usr_win.withdraw()
        self.invalid_usr_win = Toplevel(self.instance_invalid_usr_win)
        self.invalid_usr_win.title("Invalid User")
        self.invalid_usr_win.configure(bg=self.background_colour)
        tk.Label(self.invalid_usr_win, text="Invalid credentials, please try again.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Button(self.invalid_usr_win, text="Ok", command=self.destroy_invalid_usr_win, bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack(pady=10)

    def destroy_invalid_usr_win(self):
        self.invalid_usr_win.destroy()
        self.instance_invalid_usr_win.destroy()
        self.invalid_usr_win = None
        self.instance_invalid_usr_win = None

    def get_gym_time(self):
        wheel_index = 0
        if int(self.time_clicked.get()) < 10:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to 0{str(int(self.time_clicked.get()) + 1)}:00"
        else:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to {str(int(self.time_clicked.get()) + 1)}:00"
        print(f"Desired Time: {self.iac01bot.desired_time}")

        while not self.time_available:  # main loop
            # Refresh / login if timed out
            logged_in = self.iac01bot.login_status()
            if logged_in:
                self.iac01bot.driver.refresh()
            else:
                self.iac01bot.login(self.username, self.password)

            # Get available slots / Check if desired slot is available
            self.time_available = self.iac01bot.check_slots()

            # Loading wheel
            if not self.time_available:
                loading_wheel = ['/', '─', "\\", '|']
                print(f'\rNot available - trying again   {loading_wheel[wheel_index]}', end="")
                wheel_index = wheel_index + 1
                if wheel_index == 4:
                    wheel_index = 0

        # Check for an existing booking - do later

        # Book desired time slot
        if self.time_available:
            self.iac01bot.book_slot()
            self.loading_window.destroy()
            self.toaster.show_toast("GymBot®", "Your appointment has been booked!", icon_path=self.toaster.icon)
            self.instance_loading_window.destroy()

    def loading_page(self):

        self.window.destroy()
        self.instance_loading_window = tk.Tk()
        self.instance_loading_window.withdraw()

        self.loading_window = tk.Toplevel(self.instance_loading_window)
        self.loading_window.geometry("700x150")
        self.loading_window.title("GymBot®")
        self.loading_window.configure(bg=self.background_colour)

        # Progress bar
        self.bar = Progressbar(self.loading_window, orient=HORIZONTAL, length=600, mode='indeterminate')
        self.bar.pack(pady=20)
        self.bar.start()

        tk.Label(self.loading_window, text="We are currently looking for your gym time.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(self.loading_window, text="Feel free to minimize this window, we will notify you when your appointment is booked!", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()

        self.instance_loading_window.mainloop()

    def set_theme_mode(self):
        loc = LocationInfo(name='Calgary', region='AB, Canada', timezone='Canada/Mountain',
                           latitude=51.048615, longitude=-114.070847)
        s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
        sunrise = s["sunrise"].replace(tzinfo=None)
        sunset = s["sunset"].replace(tzinfo=None)
        current = datetime.datetime.now()
        if (sunrise < current) & (current < sunset):  # Light mode
            pass
        else:  # Dark mode
            self.background_colour = '#323437'
            self.font_colour = '#d1d0c5'
            self.entry_colour = '#f0f4fc'
            self.entry_font_colour = '#2b2c2f'
            self.menu_colour = "#302c34"

    def toggle(self):
        if self.toggle_button.config('text')[-1] == 'ON':
            self.toggle_button.config(text='OFF')
            self.add_to_cal = False
        else:
            self.toggle_button.config(text='ON')
            self.add_to_cal = True
            threading.Thread(target=self.calendar.authenticate()).start()
