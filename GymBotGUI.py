import _tkinter
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
    def __init__(self, iac01bot, toaster, calendar, settings):
        super().__init__()
        self.iac01bot = iac01bot
        self.toaster = toaster
        self.calendar = calendar
        self.settings = settings
        self.icon_photo = None
        self.background_photo = None
        self.light_photo = None
        self.dark_photo = None
        self.logger = logging.getLogger(__name__)

        self.login_success = None
        self.backend_thread = None
        self.instance_loading_window = None
        self.instance_invalid_usr_win = None
        self.instance_settings_win = None
        self.invalid_usr_win = None
        self.settings_win = None
        self.bar = None
        self.time_available = False
        self.booking_successful = False
        self.window = tk.Tk()
        self.loading_window = None
        self.username_login = StringVar()
        self.password_login = StringVar()
        self.time_clicked = StringVar()
        self.time_entry = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
        self.time_menu = None
        self.cal_toggle_button = None
        self.fil_toggle_button = None
        self.add_to_cal = False
        self.auto_fill = False
        self.background_colour = None
        self.font_colour = None
        self.menu_colour = None
        self.entry_colour = None
        self.entry_font_colour = None
        self.gymbot_blue = '#245ec8'
        self.font_type20 = ("Bahnschrift Light", 20)
        self.font_type13 = ("Bahnschrift Light", 13)
        self.font_type10 = ("Bahnschrift Light", 10)
        self.option_menu_font = tk_font.Font(family='Bahnschrift Light', size=13)
        self.dropdown_font = tk_font.Font(family='Bahnschrift Light', size=13)
        self.retry = 0
        self.save_creds_on_login = False
        self.instance_auto_fill_prompt = None
        self.auto_fill_prompt = None
        self.cancel = False

    def create_main_window(self):
        self.window.iconphoto(True, self.icon_photo)  # Taskbar icon
        self.window.title("GymBot®")
        self.window.configure(bg=self.background_colour)

        # Background image
        canvas = Canvas(bd=10, bg=self.background_colour, width=self.background_photo.width(), height=self.background_photo.height(), highlightbackground=self.background_colour)
        canvas.place(x=0, y=420)
        canvas.create_image(0, 0, anchor=NW, image=self.background_photo)

        tk.Label(text="Welcome to GymBot®!", bg=self.background_colour, fg=self.font_colour, font=self.font_type20).pack()
        tk.Label(text="Ensure you do not currently have a booking. Appointments will be booked for today only.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(text="Select the hour of desired appointment start time (24 hour clock):", bg=self.background_colour,fg=self.font_colour, font=self.font_type13).pack()

        # no arrow?
        self.time_clicked.set("06")
        self.time_menu = tk.OptionMenu(self.window, self.time_clicked, *self.time_entry)
        self.time_menu.pack(pady=10)
        self.time_menu.config(font=self.option_menu_font, fg=self.font_colour, bg=self.menu_colour, activebackground=self.menu_colour, activeforeground=self.font_colour, highlightbackground=self.background_colour)  # set the button font
        menu = self.window.nametowidget(self.time_menu.menuname)
        menu.config(font=self.dropdown_font, fg=self.font_colour, bg=self.menu_colour, activebackground=self.gymbot_blue, activeforeground=self.font_colour)  # Set the dropdown menu's font

        tk.Label(text="Please enter U of C credentials below to login:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(self.window, text="Username:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Entry(self.window, textvariable=self.username_login, bg=self.entry_colour, fg=self.entry_font_colour, font=self.font_type13).pack()
        tk.Label(self.window, text="Password:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Entry(self.window, textvariable=self.password_login, show="*", bg=self.entry_colour, fg=self.entry_font_colour, font=self.font_type13).pack()
        tk.Button(self.window, text="Login", command=lambda: self.cred_thread(), bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5).pack(pady=10)

        tk.Label(self.window, text="Add to calendar:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        self.cal_toggle_button = tk.Button(self.window, text="OFF", command=self.cal_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        self.cal_toggle_button.pack(pady=10)

        tk.Label(self.window, text="Autofill:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        self.fil_toggle_button = tk.Button(self.window, text="OFF", command=self.fil_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        self.fil_toggle_button.pack(pady=10)

        tk.Button(self.window, text="Settings", command=lambda: self.open_settings(), bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

        tk.Label(text="Created with love, by Lukas Morrison and Nathan Tham", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).pack()
        self.window.mainloop()

    def cred_thread(self):
        self.backend_thread = threading.Thread(target=self.get_creds(), daemon=True).start()
        if self.login_success:
            self.loading_page()

    def get_creds(self):
        if not self.auto_fill:
            self.iac01bot.username = self.username_login.get()
            self.iac01bot.password = self.password_login.get()
        if self.auto_fill:
            creds = self.settings.get_settings()
            self.iac01bot.username = creds['user_profile']['username']
            self.iac01bot.password = creds['user_profile']['password']

        self.login_success = self.iac01bot.login()

        if self.save_creds_on_login:
            if self.login_success:
                print("Saving user configuration")
                self.settings.set_settings(username=self.username_login.get(), password=self.password_login.get())

        if self.login_success:
            if self.invalid_usr_win:
                self.destroy_invalid_usr_win()
            threading.Thread(target=self.get_gym_time, daemon=True).start()
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
        tk.Button(self.invalid_usr_win, text="Ok", command=self.destroy_invalid_usr_win, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

    def destroy_invalid_usr_win(self):
        self.invalid_usr_win = self.invalid_usr_win.destroy()
        self.instance_invalid_usr_win = self.instance_invalid_usr_win.destroy()

    def get_gym_time(self):
        wheel_index = 0
        if int(self.time_clicked.get()) < 10:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to 0{str(int(self.time_clicked.get()) + 1)}:00"
        else:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to {str(int(self.time_clicked.get()) + 1)}:00"
        print(f"Desired Time: {self.iac01bot.desired_time}")

        while not self.time_available or not self.booking_successful:  # main loop
            # Refresh / login if timed out
            if self.iac01bot.login_status():
                self.iac01bot.driver.refresh()
            else:
                self.iac01bot.login()

            # Get available slots / Check if desired slot is available
            self.time_available = self.iac01bot.check_slots()

            # Check for an existing booking - do later

            # Attempt booking
            if self.time_available:
                self.iac01bot.book_slot()
                # Check booking
                self.booking_successful = self.iac01bot.booking_successful()
                if not self.booking_successful:  # Upon unsuccessful booking
                    self.retry = self.retry + 1
                    self.logger.error(f"Retrying: {self.retry} of 3")
                if self.booking_successful:  # Upon successful booking
                    self.toaster.show_toast("GymBot®", "Your appointment has been booked!", duration=10, icon_path=self.toaster.icon, threaded=True)
                    self.exit_all()

            if self.retry >= 3:
                self.logger.error("Maximum number of retries reached, exiting program.")
                self.exit_all()
                break

            if self.cancel:
                self.logger.warning("\nCanceling")
                self.exit_all()
                break

            # Loading wheel
            if not self.time_available:
                loading_wheel = ['/', '─', "\\", '|']
                print(f'\rNot available - trying again   {loading_wheel[wheel_index]}', end="")
                wheel_index = wheel_index + 1
                if wheel_index == 4:
                    wheel_index = 0

    def loading_page(self):
        self.window = self.window.destroy()
        self.instance_loading_window = tk.Tk()
        self.instance_loading_window.withdraw()

        self.loading_window = tk.Toplevel(self.instance_loading_window)
        self.loading_window.title("GymBot®")
        self.loading_window.configure(bg=self.background_colour)

        tk.Label(self.loading_window, text="We are currently looking for your gym time.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()

        # Progress bar
        bar_style = Style()
        bar_style.theme_use('default')
        bar_style.configure("blue.Horizontal.TProgressbar", foreground=self.gymbot_blue, background=self.gymbot_blue)
        self.bar = Progressbar(self.loading_window, style="blue.Horizontal.TProgressbar", orient=HORIZONTAL, length=600, mode='indeterminate')
        self.bar.pack(pady=20)
        self.bar.start()

        tk.Button(self.loading_window, text="Cancel", command=self.cancel_search, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)
        tk.Label(self.loading_window, text="Feel free to close or minimize this window, we will notify you when your appointment is booked!", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()

        self.instance_loading_window.mainloop()

    def set_theme_mode(self):
        theme_config = self.settings.get_settings()
        theme = theme_config['settings']['theme']
        self.background_photo = self.light_photo

        if theme == "Auto":
            loc = LocationInfo(name='Calgary', region='AB, Canada', timezone='Canada/Mountain', latitude=51.048615, longitude=-114.070847)
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
                self.background_photo = self.dark_photo

        if theme == "Dark":
            self.background_colour = '#323437'
            self.font_colour = '#d1d0c5'
            self.entry_colour = '#f0f4fc'
            self.entry_font_colour = '#2b2c2f'
            self.menu_colour = "#302c34"
            self.background_photo = self.dark_photo

    def cal_toggle(self):
        if self.cal_toggle_button.config('text')[-1] == 'ON':
            self.cal_toggle_button.config(text='OFF')
            self.add_to_cal = False
        else:
            self.cal_toggle_button.config(text='ON')
            self.add_to_cal = True
            threading.Thread(target=self.calendar.authenticate(), daemon=True).start()

    def fil_toggle(self):
        if self.fil_toggle_button.config('text')[-1] == 'ON':
            self.fil_toggle_button.config(text='OFF')
            self.auto_fill = False
            if self.auto_fill_prompt:
                self.destroy_auto_fill_prompt()
        else:
            self.fil_toggle_button.config(text='ON')
            fill_creds = self.settings.get_settings()
            if fill_creds['user_profile']['username'] is None or fill_creds['user_profile']['password'] is None:
                self.auto_fill_prompt_user_interface()
            else:
                self.auto_fill = True

    def open_settings(self):
        if not self.settings_win:
            self.create_settings_win()
        else:
            self.destroy_settings_win()
            self.create_settings_win()

    def create_settings_win(self):
        self.instance_settings_win = tk.Tk()
        self.instance_settings_win.withdraw()
        self.settings_win = Toplevel(self.instance_settings_win)
        self.settings_win.title("Settings")
        self.settings_win.configure(bg=self.background_colour)

        tk.Label(self.settings_win, text="Settings", bg=self.background_colour, fg=self.font_colour, font=self.font_type20).grid(row=0, columnspan=8)

        tk.Label(self.settings_win, text="Select your default GymBot® theme (changes will take effect upon app restart):", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Button(self.settings_win, text="Auto", command=self.settings_win_auto, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)
        tk.Button(self.settings_win, text="Dark", command=self.settings_win_dark, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)
        tk.Button(self.settings_win, text="Light", command=self.settings_win_light, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

        tk.Label(self.settings_win, text="Remove saved username and password:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Button(self.settings_win, text="Remove", command=self.remove_creds, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

    def destroy_settings_win(self):
        self.settings_win = self.settings_win.destroy()
        self.instance_settings_win = self.instance_settings_win.destroy()

    def settings_win_auto(self):
        self.settings.set_settings(theme="Auto")
        self.destroy_settings_win()

    def settings_win_dark(self):
        self.settings.set_settings(theme="Dark")
        self.destroy_settings_win()

    def settings_win_light(self):
        self.settings.set_settings(theme="Light")
        self.destroy_settings_win()

    def auto_fill_prompt_user_interface(self):
        if not self.auto_fill_prompt:
            self.create_auto_fill_prompt()
        else:
            self.destroy_auto_fill_prompt()
            self.create_auto_fill_prompt()

    def create_auto_fill_prompt(self):
        self.instance_auto_fill_prompt = tk.Tk()
        self.instance_auto_fill_prompt.withdraw()
        self.auto_fill_prompt = Toplevel(self.instance_auto_fill_prompt)
        self.auto_fill_prompt.title("Autofill")
        self.auto_fill_prompt.configure(bg=self.background_colour)
        tk.Label(self.auto_fill_prompt, text="No user profile was found.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(self.auto_fill_prompt, text="Would you like to save your credentials on next login?", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Button(self.auto_fill_prompt, text="Yes", command=self.auto_fill_yes, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)
        tk.Button(self.auto_fill_prompt, text="No", command=self.auto_fill_no, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

    def auto_fill_yes(self):
        self.fil_toggle_button.config(text='OFF')
        self.auto_fill = False
        self.save_creds_on_login = True
        self.destroy_auto_fill_prompt()

    def auto_fill_no(self):
        self.fil_toggle_button.config(text='OFF')
        self.auto_fill = False
        self.save_creds_on_login = False
        self.destroy_auto_fill_prompt()

    def destroy_auto_fill_prompt(self):
        self.auto_fill_prompt = self.auto_fill_prompt.destroy()
        self.instance_auto_fill_prompt = self.instance_auto_fill_prompt.destroy()

    def remove_creds(self):
        creds = self.settings.get_settings()
        if creds['user_profile']['username'] is None and creds['user_profile']['password'] is None:
            self.logger.error("No username or password on file")
        if creds['user_profile']['username'] is not None:
            self.settings.set_settings(username=None)
            print("Removed: username")
        if creds['user_profile']['password'] is not None:
            self.settings.set_settings(password=None)
            print("Removed: password")
        self.destroy_settings_win()

    def cancel_search(self):
        self.cancel = True

    def exit_all(self):
        try:
            if self.window:
                self.window = self.window.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.invalid_usr_win:
                self.invalid_usr_win = self.invalid_usr_win.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.instance_invalid_usr_win:
                self.instance_invalid_usr_win = self.instance_invalid_usr_win.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.loading_window:
                self.loading_window = self.loading_window.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.instance_loading_window:
                self.instance_loading_window = self.instance_loading_window.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.auto_fill_prompt:
                self.auto_fill_prompt = self.auto_fill_prompt.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.instance_auto_fill_prompt:
                self.instance_auto_fill_prompt = self.instance_auto_fill_prompt.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.settings_win:
                self.settings_win = self.settings_win.destroy()
        except _tkinter.TclError:
            pass
        try:
            if self.instance_settings_win:
                self.instance_settings_win = self.instance_settings_win.destroy()
        except _tkinter.TclError:
            pass
