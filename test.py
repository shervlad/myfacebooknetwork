from main import Scraper
from pprint import pprint

s = Scraper()
s.login()

pprint(s.get_friends("vlad.seremet"))
