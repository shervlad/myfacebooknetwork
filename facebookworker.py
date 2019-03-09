from main import Scraper


def get_friends(fbid):
    s = Scraper()
    s.login()
    locations = s.get_locations(fbid)
    from_chisinau = False
    for location in locations:
        from_chisinau = from_chisinau or "chisinau" in location.lower()
    if from_chisinau:
        return s.get_friends(fbid)
    else:
        return {}

def get_locations(fbid):
    s = Scraper()
    s.login()
    return s.get_locations(fbid)
