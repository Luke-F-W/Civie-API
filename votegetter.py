"""This returns 30 vote records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath

def apivote():
    #queries
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    votekey = request.args.get("votekey", "")

    #vote type queries
    dail = request.args.get("dail", "true").lower() == "true"
    seanad = request.args.get("seanad", "true").lower() == "true"
    committee = request.args.get("committee", "true").lower() == "true"

    OutcomeLost = request.args.get("lost", "true").lower() == "true"
    OutcomeCarried = request.args.get("carried", "true").lower() == "true"
    OutcomeNull = request.args.get("null", "true").lower() == "true"

    start = (page - 1) * pagesize

    query = """
        SELECT JSON, VotePrimaryKey FROM Votes
        WHERE ContextDate <= ?
        AND ContextDate >= ?
        AND (? = '' OR Vote LIKE ? OR ForNamesOfMembers LIKE ? OR AgainstNamesOfMembers LIKE ? OR AbstainNamesOfMembers LIKE ?)
        AND (? = 0 OR Chamber != 'Dáil Éireann')
        AND (? = 0 OR Chamber != 'Seanad Éireann')
        AND (? = 0 OR (Chamber = 'Dáil Éireann' OR Chamber = 'Seanad Éireann'))
        AND (? = 0 OR Outcome != 'Lost')
        AND (? = 0 OR Outcome != 'Carried')
        AND (? = 1 OR Outcome != '_')
        AND (? = '' OR VotePrimaryKey = ?)
        ORDER BY contextDate DESC
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Votes
        WHERE ContextDate <= ?
        AND ContextDate >= ?
        AND (? = '' OR Vote LIKE ? OR ForNamesOfMembers LIKE ? OR AgainstNamesOfMembers LIKE ? OR AbstainNamesOfMembers LIKE ?)
        AND (? = 0 OR Chamber != 'Dáil Éireann')
        AND (? = 0 OR Chamber != 'Seanad Éireann')
        AND (? = 0 OR (Chamber = 'Dáil Éireann' OR Chamber = 'Seanad Éireann'))
        AND (? = 0 OR Outcome != 'Lost')
        AND (? = 0 OR Outcome != 'Carried')
        AND (? = 1 OR Outcome != '_')
        AND (? = '' OR VotePrimaryKey = ?)
    """

    sparams = [
        before, after,
        search, f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%",
        int(not dail), int(not seanad), int(not committee),
        int(not OutcomeLost), int(not OutcomeCarried),
        int(OutcomeNull),
        votekey, votekey,
    ]

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(countquery, sparams)
        records = cursor.fetchone()[0]

        cursor.execute(query, sparams + [pagesize, start])
        pagelist = []
        for row in cursor.fetchall():
            record = json.loads(row["JSON"])
            record["VotePrimaryKey"] = row["VotePrimaryKey"]
            pagelist.append(record)

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