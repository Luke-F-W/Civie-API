"""This returns 30 debate records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apidebate():
    #queries
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    searchforname = request.args.get("name", "")
    searchdebatetitles = request.args.get("debatetitles", "")

    #debate type queries
    dail = request.args.get("dail", "true").lower() == "true"
    seanad = request.args.get("seanad", "true").lower() == "true"
    committee = request.args.get("committee", "true").lower() == "true"

    start = (page - 1) * pagesize

    query = """
        SELECT JSON FROM Debates
        WHERE ContextDate <= ?
        AND ContextDate >= ?
        AND (? = '' OR DebateTitles LIKE ? OR JSON LIKE ?)
        AND (? = '' OR NamesOfMembers LIKE ? OR MemberCodes LIKE ?)
        AND (? = '' OR DebateTitles LIKE ?)
        AND (? = 0 OR HouseCode != 'dail')
        AND (? = 0 OR HouseCode != 'seanad')
        AND (? = 0 OR (HouseCode = 'dail' OR HouseCode = 'seanad'))
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Debates
        WHERE ContextDate <= ?
        AND ContextDate >= ?
        AND (? = '' OR DebateTitles LIKE ? OR JSON LIKE ?)
        AND (? = '' OR NamesOfMembers LIKE ? OR MemberCodes LIKE ?)
        AND (? = '' OR DebateTitles LIKE ?)
        AND (? = 0 OR HouseCode != 'dail')
        AND (? = 0 OR HouseCode != 'seanad')
        AND (? = 0 OR (HouseCode = 'dail' OR HouseCode = 'seanad'))
    """

    sparams = [
        before, after,
        search, f"%{search}%", f"%{search}%",
        searchforname, f"%{searchforname}%", f"%{searchforname}%",
        searchdebatetitles, f"%{searchdebatetitles}%",
        int(not dail), int(not seanad), int(not committee),
    ]

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(countquery, sparams)
        records = cursor.fetchone()[0]

        cursor.execute(query, sparams + [pagesize, start])
        pagelist = [json.loads(row["JSON"]) for row in cursor.fetchall()]

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