from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from collections import deque, defaultdict
from config import FACEBOOK_CONFIG
import time
class Scraper:
    #setup database connection
    def __init__(self):
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get("https://www.facebook.com/")
        email_field = self.driver.find_element_by_id("email")
        pass_field = self.driver.find_element_by_id("pass")
        log_in = self.driver.find_elements_by_xpath("//input[@value='Log In']")
        email_field.send_keys(FACEBOOK_CONFIG["username"])
        pass_field.send_keys(FACEBOOK_CONFIG["password"])
        log_in[0].send_keys(Keys.ENTER)
        time.sleep(5)

    def get_friends(self, source):
        self.driver.get("https://www.facebook.com/%s/friends"%(source))
        profile_blocks = self.driver.find_elements_by_xpath("//div[@class='uiProfileBlockContent']")
        last_len = 0
        steps_unchanged = 0
        while(True):
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            time.sleep(1)
            profile_blocks = self.driver.find_elements_by_xpath("//div[@class='uiProfileBlockContent']")
            if(len(profile_blocks) == last_len):
                steps_unchanged += 1
            else:
                steps_unchanged = 0
                last_len = len(profile_blocks)

            if(steps_unchanged > 5):
                break
        people = []
        friends = defaultdict(lambda: set())
        for div in profile_blocks:
            link = div.find_element_by_tag_name("a")
            name = link.text
            href = link.get_attribute("href")
            username = ""
            if "profile.php" in href:
                username =  href.replace("https://www.facebook.com/profile.php?id=","").replace("&fref=pb&hc_location=friends_tab","")
            else:
                username = href.replace("https://www.facebook.com/","").replace("?fref=pb&hc_location=friends_tab","")
            if username!="#":
                friends[source].add(username)
        return friends
