# pyinstaller --onefile --add-binary "GymBot.ico;files" --add-binary "chromedriver.exe;files" -i GymBot.ico GymBot.py
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from win10toast import ToastNotifier
from iac01bot import iac01bot
import signal
import sys


# TODO logging levels

def signal_handler(sig, frame):
    print('\nExiting')
    driver.quit()


if getattr(sys, 'frozen', False): # Running as compiled
    running_dir = sys._MEIPASS + "/files/" # Same path name than pyinstaller option
else:
    running_dir = "./" # Path name when run with Python interpreter

iconFileName = running_dir + "GymBot.ico"
driverFileName = running_dir + "chromedriver.exe"


if __name__ == "__main__":

    login_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"
    default_url = "https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx"

    print("GymBot v0.8")
    print("Ensure you do not currently have a booking. Appointments will be booked day-of only.")

    # Define objects
    ser = Service(driverFileName)
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument('--log-level=3')
    op.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=ser, options=op)  # webdriver
    toaster = ToastNotifier()                           # notifier
    iac01bot = iac01bot(driver)                         # iac01bot
    signal.signal(signal.SIGINT, signal_handler)        # signal handler

    # Check validity of input time
    valid_time = False
    while not valid_time:
        time_input = input("Input 2-digit 24hr number of desired appointment start time (i.e., 09, 13, 18):")
        if time_input not in ['06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']:
            print("Invalid input (hint: use 2 digits, i.e., 09)")
            print()
        else:
            valid_time = True

    desired_time = time_input + ":00 to " + str(int(time_input) + 1) + ":00"
    # desired_date = input("Input desired date (i.e., January 28):")
    nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
    time_available = False
    wheel_index = 0

    creds_good = False
    while not creds_good:  # check credentials
        username = input("Input your username:")
        password = input("Input your password:")
        driver.get(login_url)
        iac01bot.login(username, password)
        if iac01bot.login_status():
            creds_good = True
        else:
            print("Invalid credentials try again")
            print()

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
                slots_array.append(text)
                if desired_time in slots_array[i]:
                    time_available = True
                    print(text)
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
        print(f"\nBooked{' '*26}")
        toaster.show_toast("GymBot", "Your appointment has been booked!", icon_path=iconFileName)

    driver.quit()
