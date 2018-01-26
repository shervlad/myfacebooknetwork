from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4 as bs
import time
import pymongo
from pymongo import MongoClient
from pymongo.collection import ObjectId
from collections import deque

class Scraper:
    #setup database connection
    def __init__(self,dbusername,dbpass):
        self.client = MongoClient('mongodb://%s:%s@localhost:27017/facebook'%(dbusername,dbpass))
        self.db = self.client.facebook
        self.driver = webdriver.Firefox()

    def login(self,fbemail,fbpassword):
        self.driver.get("https://www.facebook.com/")
        email_field = self.driver.find_element_by_id("email")
        pass_field = self.driver.find_element_by_id("pass")
        log_in = self.driver.find_elements_by_xpath("//input[@value='Log In']")
        email_field.send_keys(fbemail)
        pass_field.send_keys(fbpassword)
        log_in[0].send_keys(Keys.ENTER)
        time.sleep(5)
        try:
            not_now = self.driver.find_element_by_class_name("layerCancel")
            not_now.click()
        except e:
            print(e)

    def get_friends_from_fb(self, source):
        self.driver.get("https://www.facebook.com/%s/friends"%(source))
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        soup = bs.BeautifulSoup(html, 'html.parser')
        n_friends = 99999999
        print("Looking at %s\'s friends"%(source))
        try:
            f = soup.find_all(attrs={"name":"All friends"})
            n_friends = int(f[0].find_all("span")[1].text)
        except:
            f = soup.find_all(attrs={"name":"Mutual friends"})
            n_friends = int(f[0].find_all("span")[1].text)
        print("He/she has %s friends"%(n_friends))
        friends_on_page = len(soup.find_all("div","uiProfileBlockContent"))
        fop = list(range(50))
        footer = self.driver.find_element_by_id("pageFooter")

        while(fop[-1] != fop[-7]):
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            self.driver.execute_script("window.scrollBy(0,500)","")
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            soup = bs.BeautifulSoup(html, 'html.parser')
            friends_on_page = len(soup.find_all("div", "uiProfileBlockContent"))
            print("%s friends on the page. Scrolling..."%(friends_on_page))
            fop.append(friends_on_page)

        profile_blocks = soup.find_all("div","uiProfileBlockContent")

        people = []
        friends = []
        for div in profile_blocks:
            link = div.find_all("a")[0]
            name = link.text
            href = link.get("href")
            username = ""
            if "profile.php" in href:
                username =  href.replace("https://www.facebook.com/profile.php?id=","").replace("&fref=pb&hc_location=friends_tab","")
            else:
                username = link.get("href").replace("https://www.facebook.com/","").replace("?fref=pb&hc_location=friends_tab","")
            # db.people.insert_one({'name':name,'username':username})
            if username!="#":
                friends.append({'name':name,'username':username, 'friends':[source]})
        return friends
        # db.people.update_one({'username':'vlad.seremet'}, {'$set':{'friends':friends}})

    def get_friends_from_db(self, username):
        return [friend.str for friend in self.db.people.find_one({'username': username})['friends']]

    def add_person(self,person):
        if self.db.people.find({'username': person['username']}).count() > 0:
            return
        self.db.people.insert_one({'username':person['username'],
                                   'name':person['name'],
                                   'friends' : [friend for friend in person['friends']]
                                   })

    def add_friends(self,username,friends):
        old_friends = self.db.people.find_one({'username' : username})['friends']
        new_friends = [friend['username'] for friend in friends]
        all_friends = list(set(old_friends + new_friends))
        self.db.people.update_one({'username': username},{'$set':{'friends':all_friends}})

    def add_people(self,people):
        for p in people:
            self.add_person(p)

    def bfs(self,n):
        q = deque()
        visited = self.db.bfs.find()[0]['visited']

        count = 0
        while(count <= n):
            f = self.db.bfs.aggregate([{ '$project' : {'elem' : {'$arrayElemAt' : ['$queue',0]}}}])
            current = f.next()['elem']
            self.db.bfs.update_many({},{'$pop':{'queue':-1}})
            friends = self.get_friends_from_fb(current)
            self.add_friends(current, friends)
            self.add_people(friends)
            for friend in friends:
                friend_username = friend['username']
                if friend_username not in visited:
                    q.append(friend_username)
                    visited.append(friend_username)
                    self.db.bfs.update_many({},{'$addToSet':{'queue':friend_username}})
                    self.db.bfs.update_many({},{'$addToSet':{'visited':friend_username}})
            count += 1
    def get_db_client(self):
        return self.client

