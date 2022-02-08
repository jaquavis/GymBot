#pyinstaller .\GymBot.py -F
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import numpy as np

def login(username, password):
    #TODO detect login errors
    un_field = driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_UserName")
    pw_field = driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_Password")
    login_btn = driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_LoginButton")
    un_field.send_keys(username)
    pw_field.send_keys(password)
    login_btn.click()
    print("Logged in")
    return

def logout():
    logout_btn = driver.find_element('id', "ctl00_hyLogin")
    if logout_btn.text == "LOGOUT":
        logout_btn.click()
        print("Logged out")

print("Ensure you do not currently have a booking. Apointments will be booked day-of only.")
username = input("Input your username:")
password = input("Input your password:")
time_temp = input("Input 2-digit 24hr number of desired appointment start time (i.e., 09, 13, 18):")
desired_time = time_temp + ":00 to " + str(int(time_temp)+1) + ":00"
#desired_date = input("Input desired date (i.e., January 28):")
nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
time_available = False

#Define webdriver
ser = Service("C:/Users/Lukas Morrison/OneDrive - University of Calgary/chromedriver.exe")
op = webdriver.ChromeOptions()
op.add_argument("--headless")
driver = webdriver.Chrome(service=ser, options=op)

while time_available == False:
    #Login
    #TODO refresh only (check login status everytime)
    time.sleep(0.1)
    driver.get("https://iac01.ucalgary.ca/CamRecWebBooking/Login.aspx")
    time.sleep(0.1)
    login(username, password)
    time.sleep(0.3)

    #Get available slots / Check if desired slot is available
    slots_array = []
    for i in range(16):
        try:
            slot_id = "ctl00_ContentPlaceHolder1_ctl00_repAvailFitness_ctl" + nums[i] + "_lnkBtnFitness"
            time_slot = driver.find_element('id', slot_id)
            text = time_slot.text
            slots_array.append(text)
            if desired_time in slots_array[i]:
                time_available = True
                print(text)
                break
        except:
            pass
    if time_available == False:
        print('not available - trying again')

#Check for an existing booking - do later

#Book desired time slot
if time_available == True:
    slot = driver.find_element('id', slot_id)
    slot.click()
    print("Booked")

time.sleep(10)
driver.quit()