# myfacebooknetwork

This is a python project that allows you to create a database with all your facebook connections


### Prerequisites

You will need a mongo database were the data will be stored.
Either [download and install mongodb](https://www.mongodb.com/download-center#community) or use a mongo service such as [mlab](https://mlab.com)

After you have installed mongo, create database named facebook with two collections: people and bfs, and make sure that the link in the __init__() method of the Scraper class points to your database.


### Installing

Clone the repo
```
git clone https://github.com/shervlad/myfacebooknetwork
```

Install the python dependencies

```
pip install -r requirements.txt
```

## Running the scraper

Open a terminal window in the project directory and type:

```
python
```

All the following command should be executed in the python shell
Import the scraper:

```
from main import *
```

initialize a scraper object:

```
s = Scraper("<db_username>","<db_password>")
```

If this is the first time you are running the script, type:

```
s.add_person({"name" : "<your_facebook_name> ex: Jon Doe", "username": "<your_fb_username> ex: jon.doe", "friends": []})
s.db.bfs.insert_one({'queue':[],'visited':[]})
s.db.bfs.update_many({},{'$addToSet':{'queue':'<your_fb_username>}})
```

this will add you to the list of people and the bfs queue in the database. You will serve as the starting point for the search

Now log into your fb account:

```
s.login(<fb_email>,<fb_password>)
```

run bfs:

```
s.bfs(n)
```

where n is the number of people bfs will "explore" (works at about 20 people/hour)

You can also open multiple python shells and have several instances of scraper working in parallel.

## Contributing
If you have suggestions for how to make this faster and more robust, or want to work on implementing multithreading, contact me
