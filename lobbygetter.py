"""This returns 30 lobbying records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apilobby():
    #queries
    page = request.args.get("page", 1, type=int)
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"
    lobbyistcode = request.args.get("lobbyistcode", "")
    q = request.args.get("q", "")
    lobbykey = request.args.get("lobbyingkey", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON, LobbyingPrimaryKey FROM Lobbying
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = '' OR LobbyistCode = ?)
        AND (? = '' OR LobbyistName LIKE ? OR MainLobbyist LIKE ? OR Membercodes LIKE ? OR RelevantMatter LIKE ? OR Details LIKE ? OR SubjectMatter LIKE ? OR LobbyingActivities LIKE ? OR IntendedResults LIKE ?)
        AND (? = '' OR LobbyingPrimaryKey = ?)
        ORDER BY contextDate DESC      
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Lobbying
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = '' OR LobbyistCode = ?)
        AND (? = '' OR LobbyistName LIKE ? OR MainLobbyist LIKE ? OR Membercodes LIKE ? OR RelevantMatter LIKE ? OR Details LIKE ? OR SubjectMatter LIKE ? OR LobbyingActivities LIKE ? OR IntendedResults LIKE ?)
        AND (? = '' OR LobbyingPrimaryKey = ?)
    """

    like = f"%{q}%"

    sparams = [
        before, after,
        lobbyistcode, lobbyistcode,
        q, like, like, like, like, like, like, like, like,
        lobbykey, lobbykey
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
            record["LobbyingPrimaryKey"] = row["LobbyingPrimaryKey"]
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