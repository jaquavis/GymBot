class Iac01Bot:
    def __init__(self, driver):
        self.driver = driver

    def login(self, un, pw):  # Returns True if successful, else returns False
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
            print("Could not log in")
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
            print("Already logged out")
        if self.login_status():
            logout_btn.click()
            print("Logged out")