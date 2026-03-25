"""This returns 30 question records matching the queries (if the user includes any)
it gets them from the question json, i use ijson as it doesnt load the entire json
into memory, its not as important here as the question json is like 35mb, but it's
done anyways"""
from flask import request, Response
import json
from mainargs import parsedate, extractdates, searchvalue
import ijson
from config import pagesize, questionss

def apiquestion():
    #queries
    page = request.args.get("page", 1, type=int)
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

    start = (page - 1) * pagesize
    end = start + pagesize

    pagelist = []
    records = 0
    #prepare response
    with open(questionss, "r", encoding="utf-8") as f:
        for obj in ijson.items(f, "item"):
            date = extractdates(obj)

            if beforedate and date and date > beforedate:
                continue
            if afterdate and date and date < afterdate:
                continue
            if search and not searchvalue(obj, search):
                continue

            records += 1
            if start <= records <= end:
                pagelist.append(obj)

            

    responsed = {
        "page": page,
        "pagesize": pagesize,
        "records": records,
        "data": pagelist
    }

    return Response(
        json.dumps(responsed, ensure_ascii=False),
        mimetype="application/json"
    )
