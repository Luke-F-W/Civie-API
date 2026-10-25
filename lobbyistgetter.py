"""This returns paginated lobbyist records matching the query, if provided."""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apilobbyist():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON
        FROM Lobbyist
        WHERE (? = '' OR Name LIKE ? OR LobbyistCode LIKE ?)
        ORDER BY Name ASC
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*)
        FROM Lobbyist
        WHERE (? = '' OR Name LIKE ? OR LobbyistCode LIKE ?)
    """

    sparams = [search, f"%{search}%", f"%{search}%"]

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