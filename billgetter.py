"""
This returns 30 bill records matching the queries (if the user includes any)
it gets them from the SQLite database instead of the large bills JSON
"""

from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath

def apibill():
    #Main Queries
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    searchforname = request.args.get("name", "")
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    before = request.args.get("before", "2300-01-01") or "2300-01-01"

    #Status Queries
    StatusCurrent = request.args.get("current", "true").lower() == "true"
    StatusWithdrawn = request.args.get("withdrawn", "true").lower() == "true"
    StatusEnacted = request.args.get("enacted", "true").lower() == "true"
    StatusRejected = request.args.get("rejected", "true").lower() == "true"
    StatusDefeated = request.args.get("defeated", "true").lower() == "true"
    StatusLapsed = request.args.get("lapsed", "true").lower() == "true"
    StatusRepugnant = request.args.get("repugnant", "true").lower() == "true"

    #Source Queries
    SourcePrivate = request.args.get("SourcePrivate", "true") == "true"
    SourceGovernment = request.args.get("SourceGovernment", "true") == "true"
    SourcePrivateMember = request.args.get("SourcePrivateMember", "true") == "true"

    #BillType Queries
    BillTypePublic = request.args.get("BillTypePublic", "true") == "true"
    BillTypePrivate = request.args.get("BillTypePrivate", "true") == "true"
    BillTypeHybrid = request.args.get("BillTypeHybrid", "true") == "true"

    start = (page - 1) * pagesize

    query = """
        SELECT JSON FROM Legislation
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = 0 OR Status != 'Current')
        AND (? = 0 OR Status != 'Withdrawn')
        AND (? = 0 OR Status != 'Enacted')
        AND (? = 0 OR Status != 'Rejected')
        AND (? = 0 OR Status != 'Defeated')
        AND (? = 0 OR Status != 'Lapsed')
        AND (? = 0 OR Status != 'Repugnant')
        AND (? = 0 OR Source != 'Private')
        AND (? = 0 OR Source != 'Government')
        AND (? = 0 OR Source != 'Private Member')
        AND (? = 0 OR BillType != 'Public')
        AND (? = 0 OR BillType != 'Private')
        AND (? = 0 OR BillType != 'Hybrid')
        AND (ShortTitleEn LIKE ? OR LongTitleEn LIKE ? OR ShortTitleGa LIKE ?)
        AND (? = '' OR NamesOfMembers LIKE ?)
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Legislation
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = 0 OR Status != 'Current')
        AND (? = 0 OR Status != 'Withdrawn')
        AND (? = 0 OR Status != 'Enacted')
        AND (? = 0 OR Status != 'Rejected')
        AND (? = 0 OR Status != 'Defeated')
        AND (? = 0 OR Status != 'Lapsed')
        AND (? = 0 OR Status != 'Repugnant')
        AND (? = 0 OR Source != 'Private')
        AND (? = 0 OR Source != 'Government')
        AND (? = 0 OR Source != 'Private Member')
        AND (? = 0 OR BillType != 'Public')
        AND (? = 0 OR BillType != 'Private')
        AND (? = 0 OR BillType != 'Hybrid')
        AND (ShortTitleEn LIKE ? OR LongTitleEn LIKE ? OR ShortTitleGa LIKE ?)
        AND (? = '' OR NamesOfMembers LIKE ?)
    """

    sparams = [
        before, after,
        int(not StatusCurrent), int(not StatusWithdrawn), int(not StatusEnacted),
        int(not StatusRejected), int(not StatusDefeated), int(not StatusLapsed), int(not StatusRepugnant),
        int(not SourcePrivate), int(not SourceGovernment), int(not SourcePrivateMember),
        int(not BillTypePublic), int(not BillTypePrivate), int(not BillTypeHybrid),
        f"%{search}%", f"%{search}%", f"%{search}%",
        searchforname, f"%{searchforname}%"
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