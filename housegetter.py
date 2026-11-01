"""This returns Dail and Seanad pairs: party numbers, and each member with their constituency"""
from flask import request, Response
import json
import sqlite3
from config import dbpath, pagesize


def apihouse():
    #queries
    page = request.args.get("page", 1, type=int)
    name = request.args.get("name", "")
    key = request.args.get("housekey", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON, CompositionPrimaryKey FROM Composition
        WHERE (? = '' OR Name = ?)
        AND (? = '' OR CompositionPrimaryKey = ?)
        ORDER BY CompositionPrimaryKey
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*) FROM Composition
        WHERE (? = '' OR Name = ?)
        AND (? = '' OR CompositionPrimaryKey = ?)
    """

    sparams = [name, name, key, key]

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(countquery, sparams)
        records = cursor.fetchone()[0]

        cursor.execute(query, sparams + [pagesize, start])
        pagelist = []
        for row in cursor.fetchall():
            record = json.loads(row["JSON"])
            record["CompositionPrimaryKey"] = row["CompositionPrimaryKey"]
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