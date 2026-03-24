"""This returns a dictionary of multiple jsons as a json, in my json database i have
6 folders with 1 json for each membercode, this script goes through all 6
and returns a json from each if it has the membercode in them, theres 1 for
lobbying, bills, votes, debates, questions and stats. i do not pageinate here
as the jsons are relatively small and do not really require pagination"""
from flask import request
import json
from mainargs import parsedate, extractdates, searchvalue
from config import idbillss, iddebatess, idlobbyingg, idquestionss, idstatss, idvotess
import os
import ijson

folders = { 
    "bills": idbillss,
    "votes": idvotess,
    "debates": iddebatess,
    "lobbying": idlobbyingg,
    "questions": idquestionss,
    "stats": idstatss
}
def getmember(id):
    search = request.args.get("q", "")
    before = request.args.get("before", "")
    after = request.args.get("after", "")

    if before:
        beforedate = parsedate(before)
    else:
        beforedate = None
    if after:
        afterdate = parsedate(after)
    else:
        afterdate = None

    result = {}
    for name, folder in folders.items():
        for filename in os.listdir(folder):
            if id.lower() in filename.lower():
                filepath = os.path.join(folder, filename)

                if name == "stats":
                    with open(filepath, "r", encoding="utf-8") as f:
                        result[name] = json.load(f)
                    break

                filtered = []
                with open(filepath, "r", encoding="utf-8") as f:
                    if name == "lobbying":
                        items = ijson.items(f, "item")
                    else:
                        items = ijson.items(f, "results.item")

                    for obj in items:
                        date = extractdates(obj)
                        if beforedate and date and date > beforedate:
                            continue
                        if afterdate and date and date < afterdate:
                            continue
                        if search and not searchvalue(obj, search):
                            continue
                        filtered.append(obj)

                if filtered:
                    result[name] = filtered
                break

    return result
