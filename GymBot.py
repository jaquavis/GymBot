# pyinstaller --onefile --add-binary "GymBot.ico;files" --add-binary "chromedriver.exe;files" -i GymBot.ico GymBot.py
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from win10toast import ToastNotifier
from iac01bot import iac01bot
import tkinter as tk
from tkinter import *
import signal
import sys


# TODO logging levels
# TODO calendar linking

def signal_handler(sig, frame):
    print('\nExiting')
    driver.quit()


def delete2():
    window2.destroy()


def onclick(self):  # Allow us to use 'return' to submit (Return key requires positional argument)
    login()


def invaliduser():
    global window2
    window2 = Toplevel(window)
    window2.title("Invalid User")
    Label(window2, text="Invalid credentials, please try again").pack()
    Button(window2, text="Retry", command=delete2).pack()


def getgymtime():
    time_available = False
    wheel_index = 0

    desired_time = time_clicked.get() + ":00 to " + str(int(time_clicked.get()) + 1) + ":00"
    print("Desired Time:", desired_time)
    nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']

    while not time_available:  # main loop
        # Refresh / login if timed out
        logged_in = iac01bot.login_status()
        if logged_in:
            driver.refresh()
        else:
            driver.get(login_url)
            iac01bot.login(username, password)

        # Get available slots / Check if desired slot is available
        slots_array = []
        for i in range(16):
            try:
                slot_id = f"ctl00_ContentPlaceHolder1_ctl00_repAvailFitness_ctl{nums[i]}_lnkBtnFitness"
                time_slot = driver.find_element('id', slot_id)
                text = time_slot.text
                # print("Available times:")
                # print(text)
                slots_array.append(text)
                if desired_time in slots_array[i]:
                    time_available = True
                    print(time_available)
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
        slot = driver.find_element('id', slot_id)
        slot.click()
        print(f"\nBooked{' ' * 26}")
        toaster.show_toast("GymBot", "Your appointment has been booked!", icon_path=iconFileName)


def login():
    username = username_login.get()
    password = password_login.get()  # Mask??????
    username_entry.delete(0, END)

    password_entry.delete(0, END)

    # while not creds_good:  # check credentials
    driver.get(login_url)
    iac01bot.login(username, password)
    if iac01bot.login_status():
        #tk.Label(window, text="Logged in").pack()<-------------------------------------------------------------------------------
        getgymtime()
    else:
        invaliduser()


def window():
    global window
    window = tk.Tk()
    window.geometry("500x250")

    global username_login
    global password_login
    global time_clicked
    # global desired_time

    username_login = StringVar()
    password_login = StringVar()
    time_clicked = StringVar()

    global username_entry
    global password_entry
    global time_entry

    window.title("JimBot")
    tk.Label(text="Welcome to JimBot!").pack()
    tk.Label(text="Ensure you do not currently have a booking. Appointments will be booked for today only.").pack()

    tk.Label(text="Select the hour of desired appointment start time (24 hour clock):").pack()
    time_entry = ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
    time_clicked = StringVar()
    time_clicked.set("06")
    OptionMenu(window, time_clicked, *time_entry).pack()

    tk.Label(window, text="Please enter U of C credentials below to login").pack()
    tk.Label(window, text="Username *").pack()
    username_entry = tk.Entry(window, textvariable=username_login)
    username_entry.pack()
    tk.Label(window, text="Password *").pack()
    password_entry = tk.Entry(window, textvariable=password_login, show="*")
    password_entry.pack()

    tk.Label(window, text="").pack()
    button1 = tk.Button(window, text="Next", command=login)
    button1.pack()
    window.bind('<Return>', onclick)  # Allow us to use 'return' to submit

    window.mainloop()


if getattr(sys, 'frozen', False):  # Running as compiled
    running_dir = sys._MEIPASS + "/files/"  # Same path name than pyinstaller option
else:
    running_dir = "./"  # Path name when run with Python interpreter

iconFileName = running_dir + "GymBot.ico"
driverFileName = running_dir + "chromedriver.exe"

if __name__ == "__main__":
    login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
    default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"

    # Define objects
    global ser
    global op
    global driver
    global toaster
    global iac01bot

    ser = Service(driverFileName)
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument('--log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=ser, options=op)  # webdriver
    toaster = ToastNotifier()  # notifier
    iac01bot = iac01bot(driver)  # iac01bot
    signal.signal(signal.SIGINT, signal_handler)  # signal handler

    window()

    driver.quit()
