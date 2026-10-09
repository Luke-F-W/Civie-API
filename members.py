"""This returns paginated member records matching the query, if provided."""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apimember():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON
        FROM Members
        WHERE (? = '' OR FullName LIKE ?)
        ORDER BY FullName ASC
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*)
        FROM Members
        WHERE (? = '' OR FullName LIKE ?)
    """

    sparams = [search, f"%{search}%"]

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
