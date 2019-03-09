from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from collections import deque, defaultdict
from config import FACEBOOK_CONFIG
import time
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

class Scraper:
    #setup database connection
    def __init__(self):
        browser_options = Options()
        browser_options.add_argument("--disable-notifications")
        browser_options.add_argument("headless")
        self.driver = webdriver.Firefox(firefox_options = browser_options,
                                        firefox_binary=FirefoxBinary( firefox_path='/usr/bin/firefox'))
    def login(self):
        self.driver.get("https://www.facebook.com/")
        email_field = self.driver.find_element_by_id("email")
        pass_field = self.driver.find_element_by_id("pass")
        log_in = self.driver.find_elements_by_xpath("//input[@value='Log In']")
        email_field.send_keys(FACEBOOK_CONFIG["username"])
        pass_field.send_keys(FACEBOOK_CONFIG["password"])
        log_in[0].send_keys(Keys.ENTER)

    def get_friends(self, source):
        self.driver.get("https://www.facebook.com/%s/friends"%(source))
        profile_container = self.driver.find_element_by_id("pagelet_timeline_medley_friends")
        last_len = 0
        steps_unchanged = 0
        while(True):
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            print("size : ",profile_container.size)
            time.sleep(0.2)
            if(profile_container.size["height"] == last_len):
                steps_unchanged += 1
            else:
                steps_unchanged = 0
                last_len = profile_container.size["height"]
            if(steps_unchanged > 12):
                break
            if(steps_unchanged > 10):
                time.sleep(2)

        profile_blocks = self.driver.find_elements_by_xpath("//div[@class='uiProfileBlockContent']")
        people = []
        friends = dict()
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
                friends[username] = name
        return friends

    def get_locations(self,fbid):
        self.driver.get("https://www.facebook.com/%s/about?&section=living"%fbid)
        spans = self.driver.find_elements_by_xpath("//span[@class='_2iel _50f7']")
        locations =  [span.text for span in spans]
        return locations
