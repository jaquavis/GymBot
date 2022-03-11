import threading
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import datetime
from astral import LocationInfo
from astral.sun import sun
from datetime import date
from tkinter import font as tk_font
import time
from Redirect import Redirect
import sys


class GymBotGUI:
    def __init__(self, iac01bot, calendar, settings, toaster=None):
        super().__init__()
        self.iac01bot = iac01bot
        self.toaster = toaster
        self.calendar = calendar
        self.settings = settings
        self.icon_photo = None
        self.background_photo = None
        self.light_photo = None
        self.dark_photo = None
        self.today = datetime.datetime.now()
        self.old_stdout = sys.stdout

        # Windows
        self.window = tk.Tk()
        self.invalid_usr_win = None
        self.settings_win = None
        self.terminal_win = None
        self.auto_fill_prompt = None
        self.loading_window = None

        # Toggle buttons
        self.show_pass_toggle_button = None
        self.cal_toggle_button = None
        self.terminal_toggle_button = None
        self.fil_toggle_button = None

        # Styles
        self.gymbot_gold = '#d8b824'
        self.hover_bgcolour = '#d1d0c6'
        self.hover_fgcolour = '#000000'
        self.background_colour = None
        self.font_colour = None
        self.entry_colour = None
        self.entry_font_colour = None
        self.font_type20 = ("Bahnschrift Light", 20)
        self.font_type13 = ("Bahnschrift Light", 13)
        self.font_type10 = ("Bahnschrift Light", 10)
        self.option_menu_font = tk_font.Font(family='Bahnschrift Light', size=13)
        self.dropdown_font = tk_font.Font(family='Bahnschrift Light', size=13)
        self.selected_button_text_colour = '#000000'
        self.cal_button_colour = None
        self.cal_font_colour = None
        self.fil_button_colour = None
        self.fil_font_colour = None

        # Variables
        self.login_success = None
        self.time_available = False
        self.booking_successful = False
        self.save_creds_on_login = False
        self.cancel = False
        self.retry = 0
        self.username_login = StringVar()
        self.password_login = StringVar()
        self.time_clicked = StringVar()
        self.date_clicked = StringVar()
        self.time_entry = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
        self.date_entry = [datetime.datetime.strftime(self.today, "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=1), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=2), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=3), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=4), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=5), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=6), "%A, %B %d, %Y"),
                           datetime.datetime.strftime(self.today + datetime.timedelta(days=7), "%A, %B %d, %Y")]

    def create_main_window(self):
        def main_on_click(arg):
            cred_thread()

        def cred_thread():
            threading.Thread(target=self.get_creds(), daemon=True).start()
            if self.login_success:
                self.loading_page()

        # Set theme
        self.set_theme_mode()

        # Start terminal process
        self.start_terminal()
        print(f"GymBot® {self.settings.version}")

        # Version check for local data
        self.settings.version_check()

        # Authenticate calendar
        #if self.settings.get_settings()['settings']['add_to_cal']:
            #self.calendar.authenticate()

        # Configure main window
        self.window.iconphoto(True, self.icon_photo)  # Taskbar icon
        self.window.title("GymBot®")
        self.window.configure(bg=self.background_colour)

        self.window.bind('<Return>', main_on_click)  # Allows use of enter button to login

        # Background image
        canvas = Canvas(bd=10, bg=self.background_colour, width=self.background_photo.width(), height=self.background_photo.height(), highlightbackground=self.background_colour)
        canvas.place(x=0, y=320)
        canvas.create_image(0, 0, anchor=NW, image=self.background_photo)

        tk.Label(text="Welcome to GymBot®!", bg=self.background_colour, fg=self.font_colour, font=self.font_type20).pack()
        tk.Label(text="Ensure you do not currently have a booking.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(text="Select the date and hour of desired appointment start time (24 hour clock):", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()

        self.date_clicked.set(self.date_entry[0])
        date_menu = tk.OptionMenu(self.window, self.date_clicked, *self.date_entry)
        date_menu.pack(pady=10)
        date_menu.config(font=self.option_menu_font, fg=self.font_colour, bg=self.background_colour, activebackground=self.background_colour, activeforeground=self.font_colour, highlightbackground=self.background_colour)  # set the button font
        menu2 = self.window.nametowidget(date_menu.menuname)
        menu2.config(font=self.dropdown_font, fg=self.font_colour, bg=self.background_colour, activebackground=self.gymbot_gold, activeforeground=self.hover_fgcolour)  # Set the dropdown menu's font

        # no arrow?
        self.time_clicked.set(self.time_entry[0])
        time_menu = tk.OptionMenu(self.window, self.time_clicked, *self.time_entry)
        time_menu.pack(pady=10)
        time_menu.config(font=self.option_menu_font, fg=self.font_colour, bg=self.background_colour, activebackground=self.background_colour, activeforeground=self.font_colour, highlightbackground=self.background_colour)  # set the button font
        menu = self.window.nametowidget(time_menu.menuname)
        menu.config(font=self.dropdown_font, fg=self.font_colour, bg=self.background_colour, activebackground=self.gymbot_gold, activeforeground=self.hover_fgcolour)  # Set the dropdown menu's font

        settings = self.settings.get_settings()
        tk.Label(text="Please enter U of C credentials below to login:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(self.window, text="Username:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        username_entry = tk.Entry(self.window, textvariable=self.username_login, bg=self.entry_colour, fg=self.entry_font_colour, font=self.font_type13)
        if settings['settings']['autofill']:
            username_entry.insert(0, settings['user_profile']['username'])
        username_entry.pack()
        tk.Label(self.window, text="Password:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        password_entry = tk.Entry(self.window, textvariable=self.password_login, show="*", bg=self.entry_colour, fg=self.entry_font_colour, font=self.font_type13)
        if settings['settings']['autofill']:
            password_entry.insert(0, settings['user_profile']['password'])
        password_entry.pack()
        login_button = tk.Button(self.window, text="Login", command=lambda: cred_thread(), bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        login_button.pack(pady=10)

        settings_button = tk.Button(self.window, text="Settings", command=lambda: self.open_settings_win(), bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        settings_button.pack(pady=10)

        self.terminal_toggle_button = tk.Button(self.window, text="Show Terminal", command=self.terminal_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        self.terminal_toggle_button.pack(pady=10)

        tk.Label(self.window, text="Created with love, by Lukas Morrison and Nathan Tham", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).pack()
        tk.Label(self.window, text=f"GymBot® {self.settings.version}", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).place(x=480, y=509)

        # Highlight buttons on hover
        login_button.bind("<Enter>", lambda arg: self.hover(arg, button=login_button, use="over"))
        login_button.bind("<Leave>", lambda arg: self.hover(arg, button=login_button, use="leave"))

        settings_button.bind("<Enter>", lambda arg: self.hover(arg, button=settings_button, use="over"))
        settings_button.bind("<Leave>", lambda arg: self.hover(arg, button=settings_button, use="leave"))

        self.terminal_toggle_button.bind("<Enter>", lambda arg: self.hover(arg, button=self.terminal_toggle_button, use="over"))
        self.terminal_toggle_button.bind("<Leave>", lambda arg: self.hover(arg, button=self.terminal_toggle_button, use="leave"))

        # Start main window instance
        self.window.mainloop()

    def hover(self, arg, button, use, bg=None, fg=None, menu=False):
        if menu:
            if use == "over":
                button.config(bg=self.hover_bgcolour, fg=self.hover_fgcolour)
            if use == "leave":
                button.config(bg=self.background_colour, fg=self.font_colour)
        if bg == None:
            if use == "over":
                button["bg"] = self.hover_bgcolour
                button["fg"] = self.hover_fgcolour
            if use == "leave":
                button["bg"] = self.background_colour
                button["fg"] = self.font_colour
        if fg == None:
            if use == "over":
                button["bg"] = self.hover_bgcolour
                button["fg"] = self.hover_fgcolour
            if use == "leave":
                button["bg"] = self.background_colour
                button["fg"] = self.font_colour
        if use == "over":
            button["bg"] = self.hover_bgcolour
            button["fg"] = self.hover_fgcolour
        if use == "leave":
            button["bg"] = bg
            button["fg"] = fg

    def get_creds(self):
        settings = self.settings.get_settings()
        if not settings['settings']['autofill']:
            self.iac01bot.username = self.username_login.get()
            self.iac01bot.password = self.password_login.get()
        if settings['settings']['autofill']:
            if settings['user_profile']['username'] is not None and settings['user_profile']['password'] is not None:
                self.iac01bot.username = settings['user_profile']['username']
                self.iac01bot.password = settings['user_profile']['password']
            else:
                self.iac01bot.username = self.username_login.get()
                self.iac01bot.password = self.password_login.get()
                print("Autofill failed")
                self.settings.set_settings(autofill=False)

        self.login_success = self.login()

        if self.save_creds_on_login:
            if self.login_success:
                print("Saving user configuration")
                self.settings.set_settings(username=self.username_login.get(), password=self.password_login.get())
                self.settings.set_settings(autofill=True)

        if self.login_success:
            if self.invalid_usr_win:
                self.destroy_invalid_usr_win()
            threading.Thread(target=self.get_gym_time, daemon=True).start()
        else:
            self.open_invalid_user_win()

    def open_invalid_user_win(self):
        print("Invalid User")
        if not self.invalid_usr_win:
            self.create_invalid_usr_win()
        else:
            self.destroy_invalid_usr_win()
            self.create_invalid_usr_win()

    def create_invalid_usr_win(self):
        self.invalid_usr_win = Toplevel(self.window)
        self.invalid_usr_win.title("Invalid User")
        self.invalid_usr_win.configure(bg=self.background_colour)

        tk.Label(self.invalid_usr_win, text="Invalid credentials, please try again.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        exit_inv_usr_win = tk.Button(self.invalid_usr_win, text="Close", command=self.destroy_invalid_usr_win, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        exit_inv_usr_win.pack(pady=10)

        # Highlight button on hover
        exit_inv_usr_win.bind("<Enter>", lambda arg: self.hover(arg, button=exit_inv_usr_win, use="over"))
        exit_inv_usr_win.bind("<Leave>", lambda arg: self.hover(arg, button=exit_inv_usr_win, use="leave"))

    def destroy_invalid_usr_win(self):
        self.invalid_usr_win = self.invalid_usr_win.destroy()

    def login(self):  # Returns True if successful, else returns False; Will wait and retry if site is down
        while True:  # Check if site is down
            state = self.iac01bot.login()
            if state == 'unavail':
                print("Retrying in 1 minute")
                time.sleep(60)
            elif state == 'success':
                return True
            elif state == 'invalid':
                return False

    def get_gym_time(self):
        wheel_index = 0
        if int(self.time_clicked.get()) < 9:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to 0{str(int(self.time_clicked.get()) + 1)}:00"
        else:
            self.iac01bot.desired_time = f"{self.time_clicked.get()}:00 to {str(int(self.time_clicked.get()) + 1)}:00"
        print(f"Desired date: {self.date_clicked.get()}")
        print(f"Desired time: {self.iac01bot.desired_time}")
        print("Starting search...")
        print("Searching")

        while not self.time_available or not self.booking_successful:  # main loop
            # Refresh / login if timed out
            if self.iac01bot.login_status():
                self.iac01bot.driver.refresh()
                if 'error' in self.iac01bot.driver.current_url:
                    self.login()
            else:
                self.login()

            self.iac01bot.goto_date(datetime.datetime.strptime(self.date_clicked.get(), "%A, %B %d, %Y"))

            # Get available slots / Check if desired slot is available
            self.time_available = self.iac01bot.check_slots()

            # Attempt booking
            if self.time_available:
                self.iac01bot.book_slot()
                # Check booking
                self.booking_successful = self.iac01bot.booking_successful(self.date_clicked.get())
                if not self.booking_successful:  # Upon unsuccessful booking
                    self.retry = self.retry + 1
                    print(f"Retrying: {self.retry} of 3")
                if self.booking_successful:  # Upon successful booking
                    if self.toaster is not None:
                        self.toaster.show_toast("GymBot®", "Your appointment has been booked!", duration=10, icon_path=self.toaster.icon, threaded=True)
                    else:
                        messagebox.showinfo("Information", "Your appointment has been booked!")
                    self.book_event()
                    print('\nExiting: This window will now close')
                    self.exit_all()

            if self.retry >= 3:
                print("Maximum number of retries reached, exiting program.")
                self.exit_all()
                break

            if self.cancel:
                self.exit_all()
                break

            # Loading wheel
            if not self.time_available:
                loading_wheel = ['/', '─', "\\", '|']
                sys.stdout = self.old_stdout  # Avoid printing this in the terminal
                print(f'\rNot available - trying again   {loading_wheel[wheel_index]}', end="")
                wheel_index = wheel_index + 1
                if wheel_index == 4:
                    wheel_index = 0

    def book_event(self):
        try:
            booking_date = datetime.datetime.strftime(datetime.datetime.strptime(self.date_clicked.get(), "%A, %B %d, %Y"), "%Y-%m-%d")+"T"
            start_time = f"{booking_date}{self.iac01bot.time_slot_text[10:15]}:00.000"
            end_time = f"{booking_date}{self.iac01bot.time_slot_text[19:24]}:00.000"
            if self.settings.get_settings()['settings']['add_to_cal']:
                self.calendar.book_event(start_time, end_time)
        except TypeError:
            print("Could not find event times")

    def loading_page(self):
        def cancel_search():
            print("\nCancelling...")
            self.cancel = True

        self.window.withdraw()
        self.loading_window = tk.Toplevel(self.window)
        self.loading_window.title("GymBot®")
        self.loading_window.configure(bg=self.background_colour)

        if int(self.time_clicked.get()) < 9:
            desired_time_str = f"{self.time_clicked.get()}:00 to 0{str(int(self.time_clicked.get()) + 1)}:00"
        else:
            desired_time_str = f"{self.time_clicked.get()}:00 to {str(int(self.time_clicked.get()) + 1)}:00"
        tk.Label(self.loading_window, text="We are currently looking for your gym time:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(row=0, column=0, columnspan=2)
        display_time_clicked = tk.Label(self.loading_window, bg=self.background_colour, fg=self.font_colour, font=self.font_type13)
        display_time_clicked.config(text=f"{self.date_clicked.get()} from {desired_time_str}")
        display_time_clicked.grid(row=1, column=0, columnspan=2)

        # Progress bar
        progress_bar_style = Style()
        progress_bar_style.theme_use('default')
        progress_bar_style.configure("blue.Horizontal.TProgressbar", foreground=self.gymbot_gold, background=self.gymbot_gold)
        progress_bar = Progressbar(self.loading_window, style="blue.Horizontal.TProgressbar", orient=HORIZONTAL, length=600, mode='indeterminate')
        progress_bar.grid(pady=10, row=2, column=0, columnspan=2)
        progress_bar.start()

        exit_loading_win = tk.Button(self.loading_window, text="Cancel", command=cancel_search, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        exit_loading_win.grid(row=4, column=0, columnspan=1, sticky=E, padx=10)

        if self.terminal_toggle_button["text"] == "Hide Terminal":
            self.terminal_toggle_button = tk.Button(self.loading_window, text="Hide Terminal", command=self.terminal_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        else:
            self.terminal_toggle_button = tk.Button(self.loading_window, text="Show Terminal", command=self.terminal_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        self.terminal_toggle_button.grid(row=4, column=1, columnspan=1, sticky=W, padx=10)

        tk.Label(self.loading_window, text="Feel free to minimize this window, we will notify you when your appointment is booked!", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(row=5, column=0, columnspan=2)
        tk.Label(self.loading_window, text="Created with love, by Lukas Morrison and Nathan Tham", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).grid(row=6, column=0, columnspan=2)
        tk.Label(self.loading_window, text=f"GymBot® {self.settings.version}", bg=self.background_colour, fg=self.font_colour, font=self.font_type10).grid(row=6,column=1, sticky='SE')

        # Highlight buttons on hover
        exit_loading_win.bind("<Enter>", lambda arg: self.hover(arg, button=exit_loading_win, use="over"))
        exit_loading_win.bind("<Leave>", lambda arg: self.hover(arg, button=exit_loading_win, use="leave"))
        self.terminal_toggle_button.bind("<Enter>", lambda arg: self.hover(arg, button=self.terminal_toggle_button, use="over"))
        self.terminal_toggle_button.bind("<Leave>", lambda arg: self.hover(arg, button=self.terminal_toggle_button, use="leave"))

    def set_theme_mode(self):
        settings = self.settings.get_settings()
        self.background_photo = self.light_photo

        def light_mode():
            self.background_colour = '#F0F0F0'
            self.font_colour = '#000000'
            self.entry_colour = '#f0f4fc'
            self.entry_font_colour = '#2b2c2f'
            self.background_photo = self.light_photo

        def dark_mode():
            self.background_colour = '#323437'
            self.font_colour = '#d1d0c5'
            self.entry_colour = '#f0f4fc'
            self.entry_font_colour = '#2b2c2f'
            self.background_photo = self.dark_photo

        if settings['settings']['theme'] == "Auto":
            loc = LocationInfo(name='Calgary', region='AB, Canada', timezone='Canada/Mountain', latitude=51.048615, longitude=-114.070847)
            s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
            sunrise = s["sunrise"].replace(tzinfo=None)
            sunset = s["sunset"].replace(tzinfo=None)
            current = datetime.datetime.now()
            if (sunrise < current) & (current < sunset):
                light_mode()
            else:
                dark_mode()

        if settings['settings']['theme'] == "Dark":
            dark_mode()

        if settings['settings']['theme'] == "Light":
            light_mode()

    def open_settings_win(self):
        if not self.settings_win:
            self.create_settings_win()
        else:
            self.destroy_settings_win()
            self.create_settings_win()

    def create_settings_win(self):
        def settings_win_auto():
            self.settings.set_settings(theme="Auto")
            self.destroy_settings_win()

        def settings_win_dark():
            self.settings.set_settings(theme="Dark")
            self.destroy_settings_win()

        def settings_win_light():
            self.settings.set_settings(theme="Light")
            self.destroy_settings_win()

        def show_pass_toggle():
            if self.show_pass_toggle_button.config('text')[-1] == 'Show password':
                self.show_pass_toggle_button.config(text='Hide password', bg=self.background_colour, fg=self.font_colour)
                show_password()
            else:
                self.show_pass_toggle_button.config(text='Show password', bg=self.background_colour, fg=self.font_colour)
                hide_password()

        def show_password():
            if settings['user_profile']['password'] is not None:
                saved_password.config(text=settings['user_profile']['password'])
            else:
                saved_password.config(text='No saved password found')

        def hide_password():
            stars = ''
            if settings['user_profile']['password'] is not None:
                for _ in settings['user_profile']['username']:
                    stars += '*'
                saved_password.config(text=stars)

        def cal_toggle():
            if self.cal_toggle_button.config('text')[-1] == 'ON':
                self.cal_button_colour = self.background_colour
                self.cal_font_colour = self.font_colour
                self.cal_toggle_button.config(text='OFF', bg=self.cal_button_colour, fg=self.cal_font_colour)
                self.settings.set_settings(add_to_cal=False)
            else:
                self.cal_button_colour = self.gymbot_gold
                self.cal_font_colour = self.selected_button_text_colour
                self.cal_toggle_button.config(text='ON', bg=self.cal_button_colour, fg=self.cal_font_colour)
                self.settings.set_settings(add_to_cal=True)
                threading.Thread(target=self.calendar.authenticate(), daemon=True).start()

        def fil_toggle():
            if self.fil_toggle_button.config('text')[-1] == 'ON':
                self.fil_button_colour = self.background_colour
                self.fil_font_colour = self.font_colour
                self.fil_toggle_button.config(text='OFF', bg=self.fil_button_colour, fg=self.fil_font_colour)
                self.settings.set_settings(autofill=False)
                if self.auto_fill_prompt:
                    self.destroy_auto_fill_prompt()
            else:
                if settings['user_profile']['username'] is None or settings['user_profile']['password'] is None:
                    self.open_auto_fill_prompt()
                else:
                    self.fil_button_colour = self.gymbot_gold
                    self.fil_font_colour = self.selected_button_text_colour
                    self.fil_toggle_button.config(text='ON', bg=self.fil_button_colour, fg=self.fil_font_colour)
                    self.settings.set_settings(autofill=True)

        settings = self.settings.get_settings()
        self.settings_win = Toplevel(self.window)
        self.settings_win.title("Settings")
        self.settings_win.configure(bg=self.background_colour)
        tk.Label(self.settings_win, text="Settings", bg=self.background_colour, fg=self.font_colour, font=self.font_type20).grid(row=0, columnspan=2)
        tk.Label(self.settings_win, text="Select your default GymBot® settings (theme changes will be applied after app restart):", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(pady=10, row=1, column=0, columnspan=2)

        # Add to calendar control
        if settings['settings']['add_to_cal']:
            self.cal_button_colour = self.gymbot_gold
            self.cal_font_colour = self.selected_button_text_colour
            cal_text = "ON"
        else:
            self.cal_button_colour = self.background_colour
            self.cal_font_colour = self.font_colour
            cal_text = "OFF"

        tk.Label(self.settings_win, text="Add to calendar:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(pady=10, row=2, column=0)
        self.cal_toggle_button = tk.Button(self.settings_win, text=cal_text, command=cal_toggle, bg=self.cal_button_colour, activebackground=self.background_colour, fg=self.cal_font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        self.cal_toggle_button.grid(row=3, column=0)

        # Autofill control
        if settings['settings']['autofill']:
            self.fil_button_colour = self.gymbot_gold
            self.fil_font_colour = self.selected_button_text_colour
            autofill_text = "ON"
        else:
            self.fil_button_colour = self.background_colour
            self.fil_font_colour = self.font_colour
            autofill_text = "OFF"
            
        tk.Label(self.settings_win, text="Autofill:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(pady=10, row=4, column=0)
        self.fil_toggle_button = tk.Button(self.settings_win, text=autofill_text, command=fil_toggle, bg=self.fil_button_colour, activebackground=self.background_colour, fg=self.fil_font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        self.fil_toggle_button.grid(row=5, column=0)

        # Theme control
        tk.Label(self.settings_win, text="Select your preferred theme:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(pady=10, row=2, column=1)
        if settings['settings']['theme'] == "Auto":
            auto_colour = self.gymbot_gold
            dark_colour = self.background_colour
            light_colour = self.background_colour
            auto_font_colour = self.selected_button_text_colour
            dark_font_colour = self.font_colour
            light_font_colour = self.font_colour
        elif settings['settings']['theme'] == "Dark":
            auto_colour = self.background_colour
            dark_colour = self.gymbot_gold
            light_colour = self.background_colour
            auto_font_colour = self.font_colour
            dark_font_colour = self.selected_button_text_colour
            light_font_colour = self.font_colour
        else:  # Light
            auto_colour = self.background_colour
            dark_colour = self.background_colour
            light_colour = self.gymbot_gold
            auto_font_colour = self.font_colour
            dark_font_colour = self.font_colour
            light_font_colour = self.selected_button_text_colour

        auto_button = tk.Button(self.settings_win, text="AUTO", command=settings_win_auto, bg=auto_colour, activebackground=self.background_colour, fg=auto_font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        auto_button.grid(row=3, column=1)
        dark_button = tk.Button(self.settings_win, text="Dark", command=settings_win_dark, bg=dark_colour, activebackground=self.background_colour, fg=dark_font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        dark_button.grid(row=4, column=1)
        light_button = tk.Button(self.settings_win, text="Light", command=settings_win_light, bg=light_colour, activebackground=self.background_colour, fg=light_font_colour, font=self.font_type13, activeforeground=self.font_colour, width=5)
        light_button.grid(row=5, column=1)

        # Account removal
        settings = self.settings.get_settings()
        tk.Label(self.settings_win, text="Remove saved username and password:", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).grid(pady=10, row=6, column=0)
        saved_username = tk.Label(self.settings_win, bg=self.background_colour, fg=self.font_colour, font=self.font_type13)
        saved_password = tk.Label(self.settings_win, bg=self.background_colour, fg=self.font_colour, font=self.font_type13)

        if settings['user_profile']['username'] is None and settings['user_profile']['password'] is None:
            saved_username.config(text='No saved username found')
            saved_password.config(text='No saved password found')
        else:
            saved_username.config(text=settings['user_profile']['username'])
            hide_password()
            self.show_pass_toggle_button = tk.Button(self.settings_win, text="Show password", command=show_pass_toggle, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
            self.show_pass_toggle_button.grid(row=9, column=0, rowspan=2)

        saved_username.grid(row=7, column=0)
        saved_password.grid(row=8, column=0)
        remove_button = tk.Button(self.settings_win, text="Remove", command=self.remove_creds, bg=self.background_colour, activebackground="#FF7F7F", fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        remove_button.grid(row=7, column=1, rowspan=2)

        # Close settings window button
        close_settings_button = tk.Button(self.settings_win, text="Close", command=self.destroy_settings_win, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour)
        close_settings_button.grid(pady=10, row=11, column=0, columnspan=2)

        # Highlight buttons on hover
        self.cal_toggle_button.bind("<Enter>", lambda arg: self.hover(arg, button=self.cal_toggle_button, use="over"))
        self.cal_toggle_button.bind("<Leave>", lambda arg: self.hover(arg, button=self.cal_toggle_button, use="leave", bg=self.cal_button_colour, fg=self.cal_font_colour))
        self.fil_toggle_button.bind("<Enter>", lambda arg: self.hover(arg, button=self.fil_toggle_button, use="over"))
        self.fil_toggle_button.bind("<Leave>", lambda arg: self.hover(arg, button=self.fil_toggle_button, use="leave", bg=self.fil_button_colour, fg=self.fil_font_colour))
        if self.show_pass_toggle_button is not None:
            self.show_pass_toggle_button.bind("<Enter>", lambda arg: self.hover(arg, button=self.show_pass_toggle_button, use="over"))
            self.show_pass_toggle_button.bind("<Leave>", lambda arg: self.hover(arg, button=self.show_pass_toggle_button, use="leave"))

        auto_button.bind("<Enter>", lambda arg: self.hover(arg, button=auto_button, use="over"))
        auto_button.bind("<Leave>", lambda arg: self.hover(arg, button=auto_button, use="leave", bg=auto_colour, fg=auto_font_colour))
        dark_button.bind("<Enter>", lambda arg: self.hover(arg, button=dark_button, use="over"))
        dark_button.bind("<Leave>", lambda arg: self.hover(arg, button=dark_button, use="leave", bg=dark_colour, fg=dark_font_colour))
        light_button.bind("<Enter>", lambda arg: self.hover(arg, button=light_button, use="over"))
        light_button.bind("<Leave>", lambda arg: self.hover(arg, button=light_button, use="leave", bg=light_colour, fg=light_font_colour))
        remove_button.bind("<Enter>", lambda arg: self.hover(arg, button=remove_button, use="over"))
        remove_button.bind("<Leave>", lambda arg: self.hover(arg, button=remove_button, use="leave"))
        close_settings_button.bind("<Enter>", lambda arg: self.hover(arg, button=close_settings_button, use="over"))
        close_settings_button.bind("<Leave>", lambda arg: self.hover(arg, button=close_settings_button, use="leave"))

    def destroy_settings_win(self):
        self.settings_win = self.settings_win.destroy()
        if self.auto_fill_prompt:
            self.destroy_auto_fill_prompt()

    def open_auto_fill_prompt(self):
        if not self.auto_fill_prompt:
            self.create_auto_fill_prompt()
        else:
            self.destroy_auto_fill_prompt()
            self.create_auto_fill_prompt()

    def create_auto_fill_prompt(self):
        def auto_fill_yes():
            self.save_creds_on_login = True
            self.destroy_auto_fill_prompt()

        def auto_fill_no():
            self.save_creds_on_login = False
            self.destroy_auto_fill_prompt()

        self.auto_fill_prompt = Toplevel(self.window)
        self.auto_fill_prompt.title("Autofill")
        self.auto_fill_prompt.configure(bg=self.background_colour)
        tk.Label(self.auto_fill_prompt, text="No user profile was found.", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Label(self.auto_fill_prompt, text="Would you like to save your credentials on next login?", bg=self.background_colour, fg=self.font_colour, font=self.font_type13).pack()
        tk.Button(self.auto_fill_prompt, text="Yes", command=auto_fill_yes, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)
        tk.Button(self.auto_fill_prompt, text="No", command=auto_fill_no, bg=self.background_colour, activebackground=self.background_colour, fg=self.font_colour, font=self.font_type13, activeforeground=self.font_colour).pack(pady=10)

    def destroy_auto_fill_prompt(self):
        self.auto_fill_prompt = self.auto_fill_prompt.destroy()

    def terminal_toggle(self):
        try:
            if self.terminal_toggle_button.config('text')[-1] == 'Show Terminal':
                self.terminal_toggle_button.config(text='Hide Terminal', bg=self.background_colour, fg=self.font_colour)
                self.terminal_win.deiconify()
            else:
                self.terminal_toggle_button.config(text='Show Terminal', bg=self.background_colour, fg=self.font_colour)
                self.terminal_win.withdraw()
        except TclError:
            self.start_terminal()  # Restart terminal if down

    def start_terminal(self):
        try:
            if not self.terminal_win.winfo_exists():
                self.create_terminal_instance()
        except AttributeError:
            self.create_terminal_instance()

    def create_terminal_instance(self):
        self.terminal_win = Toplevel(self.window)
        # self.terminal_win.overrideredirect(True)
        self.terminal_win.withdraw()
        self.terminal_win.title("Terminal")
        self.terminal_win.configure(bg=self.background_colour)

        frame = tk.Frame(self.terminal_win, bg=self.background_colour)
        frame.pack(expand=True, fill='both')

        text = tk.Text(frame, bg=self.background_colour, fg=self.font_colour)
        text.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')

        text['yscrollcommand'] = scrollbar.set
        scrollbar['command'] = text.yview

        redirect = Redirect(text)
        sys.stdout = redirect

    def remove_creds(self):
        self.settings.set_settings(autofill=False)
        settings = self.settings.get_settings()
        if settings['user_profile']['username'] is None and settings['user_profile']['password'] is None:
            print("No username or password on file")
        if settings['user_profile']['username'] is not None:
            self.settings.set_settings(username=None)
            print("Removed: username")
        if settings['user_profile']['password'] is not None:
            self.settings.set_settings(password=None)
            print("Removed: password")
        self.destroy_settings_win()

    def exit_all(self):
        sys.stdout = self.old_stdout

        try:
            if self.invalid_usr_win:
                self.invalid_usr_win = self.invalid_usr_win.destroy()
        except TclError:
            pass
        try:
            if self.loading_window:
                self.loading_window = self.loading_window.destroy()
        except TclError:
            pass
        try:
            if self.auto_fill_prompt:
                self.auto_fill_prompt = self.auto_fill_prompt.destroy()
        except TclError:
            pass
        try:
            if self.settings_win:
                self.settings_win = self.settings_win.destroy()
        except TclError:
            pass
        try:
            if self.terminal_win:
                if self.terminal_win.winfo_viewable():
                    time.sleep(10)
                self.terminal_win = self.terminal_win.destroy()
        except TclError:
            pass
        try:
            if self.window:
                self.window = self.window.destroy()
        except TclError:
            pass
