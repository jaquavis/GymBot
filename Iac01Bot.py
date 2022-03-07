import logging
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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

    def login(self):  # Returns 'success' if successful; returns 'invalid' if invalid credentials; returns 'unavail' if site down
        self.driver.get(self.login_url)
        if 'error' in self.driver.current_url:
            self.logger.error("Site is down")
            return 'unavail'

        un_field = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_logCamRec_UserName")))
        pw_field = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_logCamRec_Password")))
        un_field.send_keys(self.username)
        pw_field.send_keys(self.password)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_logCamRec_LoginButton"))).click()

        if self.login_status():
            print("Logged in")
            return 'success'
        else:
            self.logger.warning("Could not log in")
            return 'invalid'

    def login_status(self):  # returns True if logged in, False if logged out
        try:
            status = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_hyLogin")))
            if status.text == "LOGOUT":
                return True
            if status.text == "LOGIN":
                return False
        except NoSuchElementException:
            self.logger.warning("Could not determine login status!")
            return False  # Assume logged out
            pass

    def logout(self):
        if not self.login_status():
            self.logger.warning("Already logged out")
        if self.login_status():
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_logCamRec_LoginButton"))).click()
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
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, self.slot_id))).click()
        print(f"\nAttempting to book {self.time_slot_text[5:24]}")

    def booking_successful(self, date):  # Returns True if the booking was successful
        index = 2
        self.driver.get(self.login_url)
        self.login()

        if self.time_slot_text is not None:
            booking_msg = f"{date} from {self.time_slot_text[10:15]} to {self.time_slot_text[19:24]}, Fitness Centre"
            while True:
                try:
                    if index < 10:
                        booking_id = f"ctl00_ContentPlaceHolder1_ctl00_gvClientFitnessBookings_ctl0{index}_lblFCBooking"
                    else:
                        booking_id = f"ctl00_ContentPlaceHolder1_ctl00_gvClientFitnessBookings_ctl{index}_lblFCBooking"
                    booking = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, f"//span[contains(@id,'{booking_id}')]")))
                    booking_text = booking.text
                    if booking_msg == booking_text:
                        print("Booking successful")
                        return True
                    index = index + 1
                except TimeoutException:
                    self.logger.error("Booking unsuccessful")
                    return False

    def next_page(self):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lnkBtnNext"))).click()

    def previous_page(self):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lnkBtnPrev"))).click()

    def get_page_date(self):  # Returns a datetime object
        page_date_obj = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_ctl00_lblAvailableFitness")))
        page_date = datetime.datetime.strptime(page_date_obj.text[12:].strip(), "%A, %B %d, %Y.")
        return page_date

    def goto_date(self, date):
        while True:
            page_date = self.get_page_date()
            if page_date.day == date.day:
                return
            self.next_page()
