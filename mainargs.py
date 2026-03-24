"""small collection of important functions used throughout the API,
parsedate takes both "Date Published":"21\/01\/2016 09:34 (this comes
from lobbying) and"contextDate": "2026-03-05 (which comes from bills,
votes, debates and questions) and cleans it into 1 YYYY-MM-DD format.
extractdate just finds the date in the json, and searchvalue just takes
the record as a string and searches for a string in it"""

from datetime import datetime

def parsedate(date):
    if not date:
        return None
    #these 2 below are needed for lobbying date, they make no difference to other dates
    date = date.split(" ")[0]
    date = date.replace("\\/", "/")

    if "-" in date:
        return datetime.strptime(date, "%Y-%m-%d")
    #this is for lobbying records which store dates very differently
    if "/" in date:
        d = date.split("/")[0]
        m = date.split("/")[1]
        y = date.split("/")[2]
        date = y + "-" + m + "-" + d
        return datetime.strptime(date, "%Y-%m-%d")

def extractdates(obj):
    date = obj.get("contextDate") or obj.get("Date Published")
    date= parsedate(date)
    return date

def searchvalue(value, query):
    text = str(value)
    text = text.lower()
    query = query.lower()
    return query in text
