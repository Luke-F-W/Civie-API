"""This returns paginated member records matching the query, if provided."""
from flask import request, Response
import json
import sqlite3
from config import TDpagesize, dbpath


def apimember():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    membercode = request.args.get("membercode", "").strip()

    start = (page - 1) * TDpagesize

    query = """
        SELECT JSON
        FROM Members
        WHERE (? = '' OR FullName LIKE ?)
          AND (? = '' OR MemberCode = ?)
        ORDER BY FullName ASC
        LIMIT ? OFFSET ?
    """

    countquery = """
        SELECT COUNT(*)
        FROM Members
        WHERE (? = '' OR FullName LIKE ?)
          AND (? = '' OR MemberCode = ?)
    """

    sparams = [search, f"%{search}%", membercode, membercode]

    with sqlite3.connect(dbpath) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(countquery, sparams)
        records = cursor.fetchone()[0]

        cursor.execute(query, sparams + [TDpagesize, start])
        pagelist = [json.loads(row["JSON"]) for row in cursor.fetchall()]

    #exact lookup: return the one member object on its own
    if membercode:
        if not pagelist:
            return Response(
                json.dumps({"error": "member not found"}),
                status=404,
                mimetype="application/json"
            )
        return Response(
            json.dumps(pagelist[0], ensure_ascii=False),
            mimetype="application/json"
        )

    responsed = {
        "page": page,
        "pagesize": TDpagesize,
        "records": records,
        "data": pagelist
    }

    return Response(
        json.dumps(responsed, ensure_ascii=False),
        mimetype="application/json"
    )