from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#-----------------------------------------
# Main Broswer class for all actions 
# performed within the browser.
#-----------------------------------------
class Browser():
    def __init__(self, url, show=True) -> None:
        self.URL = url

        options = Options()

        # Setting the browser to headless ensures it dosent open a window, but runs without one
        if not show:
            options.add_argument("--headless")

        #get the geckodriver used for firefox 
        serv=Service(GeckoDriverManager().install())

        #Adding the options & installing the adblocker addon
        self.firefox = webdriver.Firefox(service=serv, options=options)
        self.firefox.implicitly_wait(10)
        self.firefox.install_addon("adblockULT.xpi")

        self.firefox.get(self.URL) 

        #closes the tab opened by the adblocker
        self.switchToTab(-1)
        self.firefox.close()
        self.switchToTab(0)

        self.startTime = time.time()

        #waits 1 second in between play and pause
        self.timeToPause = 1

    #-----------------------------------------
    # Using a js script, it presses the
    # "Next Video" button on the video
    #-----------------------------------------
    def next(self):
        CLASS = "ytp-next-button"

        nextBtn = self.firefox.find_element(By.CLASS_NAME, CLASS)
        
        try:
            self.firefox.execute_script("arguments[0].click();", nextBtn)

        except Exception: 
            print(f"Couldnt click the next button, class: {CLASS}")

    #-----------------------------------------
    # Uses a js script to press the 
    # Next Video button
    #-----------------------------------------
    def previous(self):
        CLASS = "ytp-prev-button"

        prevBtn = self.firefox.find_element(By.CLASS_NAME, CLASS)

        try:
            self.firefox.execute_script("arguments[0].click();", prevBtn)

        except Exception:
            print(f"Couldnt click the previous button, class: {CLASS}")

    #-----------------------------------------
    # Presses the Enter key to play or pause
    # the video depending on the cur state
    #-----------------------------------------
    def play(self):
        endTime = time.time()

        if (endTime - self.startTime) > self.timeToPause:
            CLASS = "ytp-play-button"

            playBtn = self.firefox.find_element(By.CLASS_NAME, CLASS)

            try:
                # self.firefox.execute_script("arguments[0].click();", playBtn)
                playBtn.send_keys(Keys.RETURN)

            except Exception:
                print(f"Couldnt click the play button, class: {CLASS}")

            self.startTime = time.time()

    #-----------------------------------------
    # Switches to the given tab
    #-----------------------------------------
    def switchToTab(self, tabNum):
        self.firefox.switch_to.window(self.firefox.window_handles[tabNum])

    #-----------------------------------------
    # Closes the current active tab
    #-----------------------------------------
    def closeTab(self):
        self.firefox.close()