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

 
class Browser():
    def __init__(self, url, show=True) -> None:
        # self.URL = "https://www.youtube.com/watch?v=f6aLOYb8HAE&list=PLN_DIJJJ8men451hJpo4MhO7Sxgk_yS4Y&index=2&ab_channel=Akintoye-Topic"
        self.URL = url

        options = Options()

        if not show:
            options.add_argument("--headless")

        #get the geckodriver used for firefox 
        serv=Service(GeckoDriverManager().install())

        self.firefox = webdriver.Firefox(service=serv, options=options)
        self.firefox.implicitly_wait(10)
        self.firefox.install_addon("adblockULT.xpi")

        self.firefox.get(self.URL) 

        self.switchToTab(-1)
        self.firefox.close()
        self.switchToTab(0)

        self.startTime = time.time()
        #waits 1 second in between play and pause
        self.timeToPause = 1

    def next(self):
        CLASS = "ytp-next-button"

        nextBtn = self.firefox.find_element(By.CLASS_NAME, CLASS)
        
        try:
            self.firefox.execute_script("arguments[0].click();", nextBtn)

        except Exception: 
            print(f"Couldnt click the next button, class: {CLASS}")

    def previous(self):
        CLASS = "ytp-prev-button"

        prevBtn = self.firefox.find_element(By.CLASS_NAME, CLASS)

        try:
            self.firefox.execute_script("arguments[0].click();", prevBtn)

        except Exception:
            print(f"Couldnt click the previous button, class: {CLASS}")

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

    def scrub(self, sTime):
        #WIP, i cant get it to work at all

        # BAR_CLASS = "ytp-progress-bar"
        # SCRUB_CLASS = "ytp-scrubber-container"

        # pgrsSlider = self.firefox.find_element(By.CLASS_NAME, BAR_CLASS)
        # print(pgrsSlider.size)

        # time.sleep(20)

        # scrubCnt = self.firefox.find_element(By.CLASS_NAME, SCRUB_CLASS)

        # print(scrubCnt.get_attribute("style"))


        # ActionChains(self.firefox).click_and_hold(scrubCnt).move_by_offset(30, 0)
        # time.sleep(10)
        # print(scrubCnt.get_attribute("style"))
        pass
    def switchToTab(self, tabNum):
        self.firefox.switch_to.window(self.firefox.window_handles[tabNum])

    def closeTab(self):
        self.firefox.close()

if __name__ == '__main__':
    x = Browser()
    x.scrub(20)