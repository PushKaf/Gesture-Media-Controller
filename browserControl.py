from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

 
class Browser():
    def __init__(self, show=True) -> None:
        self.URL = "https://www.youtube.com/watch?v=HB76Ydx8msk&list=PLN_DIJJJ8men451hJpo4MhO7Sxgk_yS4Y&index=1&ab_channel=SteezyTracks"

        options = Options()
        options.add_experimental_option("detach", True)
        options.add_extension("adblock.crx")
        options.add_extension("adblock2.crx")
        
        if not show:
            options.add_argument("--headless")

        #basically get the chromedriver
        serv=Service(ChromeDriverManager().install())

        self.chrome = webdriver.Chrome(service=serv, options=options)

        self.chrome.get(self.URL)
        self.chrome.implicitly_wait(10)

        self.startTime = time.time()

        #waits 1 second in between play and pause
        self.timeToPause = 1


    def next(self):
        CLASS = "ytp-next-button"

        nextBtn = self.chrome.find_element(By.CLASS_NAME, CLASS)
        
        try:
            self.chrome.execute_script("arguments[0].click();", nextBtn)
        except: 
            print("\nERROR\n")

    def play(self):
        endTime = time.time()

        if (endTime - self.startTime) > self.timeToPause:
            CLASS = "ytp-play-button"

            playBtn = self.chrome.find_element(By.CLASS_NAME, CLASS)

            try:
                # self.chrome.execute_script("arguments[0].click();", playBtn)
                playBtn.send_keys(Keys.RETURN)
            except:
                print("ERROR 2")

            self.startTime = time.time()
        
        else:
            pass
        

# x = Browser()
# time.sleep(10)
# x.next()