"""This returns 30 lobbying records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apilobby():
    #Main Queries
    page = request.args.get("page", 1, type=int)
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    searchforname = request.args.get("name", "")

    #Searchable Queries
    searchLobbyistName = request.args.get("LobbyistName", "")
    searchLobbyistGroup = request.args.get("LobbyistGroup", "")
    searchMatters = request.args.get("Matters", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON FROM Lobbying
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = '' OR LobbyistName LIKE ?)
        AND (? = '' OR MainLobbyist LIKE ?)
        AND (? = '' OR RelevantMatter LIKE ? OR Details LIKE ? OR SubjectMatter LIKE ? OR LobbyingActivities LIKE ? OR IntendedResults LIKE ?)
        AND (? = '' OR Membercodes LIKE ?)
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Lobbying
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = '' OR LobbyistName LIKE ?)
        AND (? = '' OR MainLobbyist LIKE ?)
        AND (? = '' OR RelevantMatter LIKE ? OR Details LIKE ? OR SubjectMatter LIKE ? OR LobbyingActivities LIKE ? OR IntendedResults LIKE ?)
        AND (? = '' OR Membercodes LIKE ?)
    """

    sparams = [
        before, after,
        searchLobbyistName, f"%{searchLobbyistName}%",
        searchLobbyistGroup, f"%{searchLobbyistGroup}%",
        searchMatters, f"%{searchMatters}%", f"%{searchMatters}%", f"%{searchMatters}%", f"%{searchMatters}%", f"%{searchMatters}%",
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