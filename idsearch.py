"""This returns a dictionary of multiple jsons as a json, in my json database i have
6 folders with 1 json for each membercode, this script goes through all 6
and returns a json from each if it has the membercode in them, theres 1 for
lobbying, bills, votes, debates, questions and stats. i do not pageinate here
as the jsons are relatively small and do not really require pagination"""
from flask import request, Response
import json
from config import TDpagesize, dbpath
import sqlite3


def getmember(id):
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    offset = (page - 1) * TDpagesize

    tables = [
        ("bills",     "Legislation", "contextDate", "Membercodes LIKE ?",                                          1),
        ("votes",     "Votes",       "ContextDate", "ForVoters LIKE ? OR AgainstVoters LIKE ? OR AbstainVotes LIKE ?", 3),
        ("debates",   "Debates",     "ContextDate", "MemberCodes LIKE ?",                                          1),
        ("lobbying",  "Lobbying",    "contextDate", "Membercodes LIKE ?",                                          1),
        ("questions", "Questions",   "contextDate", "MembercodeBy LIKE ?",                                         1),
    ]

    result = {}
    exact = f"%{id}%"

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT JSON FROM Members WHERE MemberCode = ?", (id,))
        row = cursor.fetchone()
        if row:
            result["member"] = json.loads(row["JSON"])

        for name, table, datecol, condition, likecount in tables:
            likes = tuple([exact] * likecount)
            base = f"FROM {table} WHERE {datecol} <= ? AND {datecol} >= ? AND ({condition}) AND (? = '' OR JSON LIKE ?)"

            cursor.execute(f"SELECT COUNT(*) {base}", (before, after, *likes, search, f"%{search}%"))
            records = cursor.fetchone()[0]

            cursor.execute(f"SELECT JSON {base} LIMIT ? OFFSET ?", (before, after, *likes, search, f"%{search}%", TDpagesize, offset))
            result[name] = {
                "page": page, "pagesize": TDpagesize, "records": records,
                "data": [json.loads(row["JSON"]) for row in cursor.fetchall()]
            }

        cursor.execute("SELECT JSON FROM Stats WHERE Membercode = ?", (id,))
        row = cursor.fetchone()
        if row:
            result["stats"] = json.loads(row["JSON"])

    return Response(
        json.dumps(result, ensure_ascii=False),
        mimetype="application/json"
    )