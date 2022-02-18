import logging
from selenium.common.exceptions import NoSuchElementException
import datetime


class Iac01Bot:
    def __init__(self, driver):
        self.driver = driver
        self.login_url = None
        self.default_url = None
        self.logger = logging.getLogger(__name__)
        self.desired_time = None
        self.nums = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']
        self.time_slot_text = None
        self.slot_id = None
        self.username = None
        self.password = None

    def login(self):  # Returns True if successful, else returns False
        self.driver.get(self.login_url)
        un_field = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_UserName")
        pw_field = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_Password")
        login_btn = self.driver.find_element('id', "ctl00_ContentPlaceHolder1_logCamRec_LoginButton")
        un_field.send_keys(self.username)
        pw_field.send_keys(self.password)
        login_btn.click()

        status = self.login_status()
        if status:
            print("Logged in")
        else:
            self.logger.warning("Could not log in")
        return status

    def login_status(self):  # returns True if logged in, False if logged out
        try:
            status = self.driver.find_element('id', "ctl00_hyLogin")
            if status.text == "LOGOUT":
                return True
            if status.text == "LOGIN":
                return False
        except NoSuchElementException:
            self.logger.warning("Could not determine login status!")
            return False  # Assume logged out
            pass

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
                slot = self.driver.find_element('id', self.slot_id)
                slot_text = slot.text
                slots_array.append(slot_text)
                if self.desired_time in slots_array[i]:
                    self.time_slot_text = slot_text
                    return True
            except NoSuchElementException:
                pass
        return False

    def book_slot(self):
        slot = self.driver.find_element('id', self.slot_id)
        slot.click()
        print(f"\nBooked {self.time_slot_text[5:24]}{' '*6}")
        #print(f"\nAttempting to book {self.time_slot_text[5:24]}")

    def booking_successful(self):  # Returns True if the booking was successful
        index = 102
        self.driver.get(self.login_url)
        self.login()

        if self.time_slot_text is not None:
            booking_msg = f"{datetime.datetime.now().strftime('%A, %d, %B, %Y')} from {self.time_slot_text[10:15]} to {self.time_slot_text[19:24]}, Fitness Centre"
            print("booking msg")
            print(booking_msg)

            while True:
                try:
                    booking_id = f"ctl00_ContentPlaceHolder1_ctl00_gvClientFitnessBookings_ct{index}_lblFCBooking"
                    print(booking_id)
                    index = index + 1
                    booking = self.driver.find_element('id', booking_id)
                    booking_text = booking.text
                    print("booking text")
                    print(booking.text)
                    if booking_msg == booking_text:
                        print("Booking successful")
                        return True
                except NoSuchElementException:
                    self.logger.error("Booking unsuccessful")
                    return False
