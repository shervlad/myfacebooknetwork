import rq
from collections import defaultdict
from redis import Redis
from rq import Queue
from facebookworker import get_friends, get_locations
import time
import  pickle

class NetworkMapper:
    def __init__(self):
        self.q = Queue(connection=Redis())
        try:
            self.load()
        except:
            self.detected = set()
            self.graph = {}
            self.profiles = {}
        if len(self.detected) == 0:
            self.detected.add("vlad.seremet")
        self.active_jobs = []
        self.last_save = 0 #timestamp of last save

    def save(self):
        f = open("./files/graph","wb")
        pickle.dump(self.graph,f)
        f.close
        f = open("./files/detected","wb")
        pickle.dump(self.detected,f)
        f.close
        f = open("./files/profiles","wb")
        pickle.dump(self.profiles,f)
        f.close

    def load(self):
        f = open("./files/graph","rb")
        self.graph = pickle.load(f)
        f.close
        f = open("./files/detected","rb")
        self.detected = pickle.load(f)
        f.close
        f = open("./files/profiles","rb")
        self.profiles = pickle.load(f)
        f.close

    def explore(self):
        while True:
            if time.time()  - self.last_save > 60*5: #save every 5 minutes
                self.save()
            to_delete = []

            for i,(fbid,job) in enumerate(self.active_jobs):
                if job.result:
                    friends = job.result
                    self.profiles.update(friends)
                    friends = set(friends.keys())
                    to_delete.append(i)
                    self.detected.update(friends)
                    self.graph[fbid] = friends

            for i in to_delete:
                del self.active_jobs[i]

            if(len(self.q)<10 and len(self.detected) > 0):
                fbid = self.detected.pop()
                new_job = self.q.enqueue(get_friends,fbid)
                self.active_jobs.append((fbid,new_job))


if __name__ =="__main__":
    n = NetworkMapper()
    n.explore()
