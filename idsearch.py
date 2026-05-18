"""This returns a dictionary of multiple jsons as a json, in my json database i have
6 folders with 1 json for each membercode, this script goes through all 6
and returns a json from each if it has the membercode in them, theres 1 for
lobbying, bills, votes, debates, questions and stats. i do not pageinate here
as the jsons are relatively small and do not really require pagination"""
from flask import request, Response
import json
from config import pagesize, dbpath
import sqlite3


def getmember(id):
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    offset = (page - 1) * pagesize

    tables = [
        ("bills",     "Legislation", "ContextDate", "NamesOfMembers LIKE ?"),
        ("votes",     "Votes",       "ContextDate", "ForVoters LIKE ? OR AgainstVoters LIKE ? OR AbstainVotes LIKE ?"),
        ("debates",   "Debates",     "ContextDate", "MemberCodes LIKE ?"),
        ("lobbying",  "Lobbying",    "contextDate", "Membercodes LIKE ?"),
        ("questions", "Questions",   "contextDate", "MembercodeBy LIKE ?"),
    ]

    result = {}
    like = f"%{id}%"
    slike = f"%{search}%"

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for name, table, datecol, condition in tables:
            likes = (like, like, like) if name == "votes" else (like,)
            base = f"FROM {table} WHERE {datecol} <= ? AND {datecol} >= ? AND ({condition}) AND (? = '' OR JSON LIKE ?)"

            cursor.execute(f"SELECT COUNT(*) {base}", (before, after, *likes, search, slike))
            records = cursor.fetchone()[0]

            cursor.execute(f"SELECT JSON {base} LIMIT ? OFFSET ?", (before, after, *likes, search, slike, pagesize, offset))
            result[name] = {
                "page": page, "pagesize": pagesize, "records": records,
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