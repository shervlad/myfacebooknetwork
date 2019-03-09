import rq
from collections import defaultdict
from redis import Redis
from rq import Queue
from facebookworker import get_friends, get_locations
import time
q = Queue(connection=Redis())

detected = set()
detected.add("vlad.seremet")

graph = defaultdict(lambda: set())
profiles = {}
active_jobs = []

while True:
    to_delete = []
    for i,(fbid,job) in enumerate(active_jobs):
        if job.result:
            friends = job.result
            profiles.update(friends)
            friends = set(friends.keys())
            to_delete.append(i)
            detected.update(friends)
            graph[fbid] = friends

    for i in to_delete:
        del active_jobs[i]

    if(len(q)<60 and len(detected) > 0):
        fbid = detected.pop()
        new_job = q.enqueue(get_friends,fbid)
        active_jobs.append((fbid,new_job))
