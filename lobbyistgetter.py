"""This returns 30 lobbyist records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apilobby():
    #queries
    page = request.args.get("page", 1, type=int)
    lobbyistcode = request.args.get("lobbyistcode", "")
    q = request.args.get("q", "")
    lobbyistkey = request.args.get("lobbyistkey", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON, LobbyistPrimaryKey FROM Lobbyist
        WHERE (? = '' OR LobbyistCode = ?)
        AND (? = '' OR Name LIKE ? OR LobbyistCode LIKE ?)
        AND (? = '' OR LobbyistPrimaryKey = ?)
        ORDER BY Tally DESC
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Lobbyist
        WHERE (? = '' OR LobbyistCode = ?)
        AND (? = '' OR Name LIKE ? OR LobbyistCode LIKE ?)
        AND (? = '' OR LobbyistPrimaryKey = ?)
    """

    like = f"%{q}%"

    sparams = [
        lobbyistcode, lobbyistcode,
        q, like, like,
        lobbyistkey, lobbyistkey
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
            record["lobbyistkey"] = row["LobbyistPrimaryKey"]
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