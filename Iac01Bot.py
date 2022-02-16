import logging
from selenium.common.exceptions import NoSuchElementException


class Iac01Bot:
    def __init__(self, driver):
        self.driver = driver
        self.url = None
        self.logger = logging.getLogger(__name__)
        self.desired_time = None
        self.nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
        self.time_slot_text = None
        self.slot_id = None

    def login(self, un, pw):  # Returns True if successful, else returns False
        self.driver.get(self.url)
        un_field = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_UserName")
        pw_field = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_Password")
        login_btn = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_LoginButton")
        un_field.send_keys(un)
        pw_field.send_keys(pw)
        login_btn.click()

        status = self.login_status()
        if status:
            print("Logged in")
        else:
            self.logger.warning("Could not log in")
        return status

    def login_status(self):  # returns True if logged in, False if logged out
        status = self.driver.find_element('id', "ctl00_hyLogin")
        if status.text == "LOGOUT":
            return True
        if status.text == "LOGIN":
            return False

    def logout(self):
        logout_btn = self.driver.find_element('id', "ctl00_hyLogin")
        if not self.login_status():
            self.logger.warning("Already logged out")
        if self.login_status():
            logout_btn.click()
            print("Logged out")

    def check_slots(self):  # Returns True when timeslot is found
        slots_array = []
        for i in range(16):
            try:
                self.slot_id = f"ctl00_ContentPlaceHolder1_ctl00_repAvailFitness_ctl{self.nums[i]}_lnkBtnFitness"
                time_slot = self.driver.find_element('id', self.slot_id)
                text = time_slot.text
                slots_array.append(text)
                if self.desired_time in slots_array[i]:
                    self.time_slot_text = text
                    return True
            except NoSuchElementException:
                pass
        return False

    def book_slot(self):
        slot = self.driver.find_element('id', self.slot_id)
        slot.click()
        print(f"\nBooked {self.time_slot_text[5:24]}{' ' * 6}")
