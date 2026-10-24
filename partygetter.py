"""This returns every party in the Party table in one go"""
from flask import Response
import json
import sqlite3
from config import dbpath


def apiparty():
    with sqlite3.connect(dbpath) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT JSON FROM Party ORDER BY PartyCode")
        pagelist = [json.loads(row[0]) for row in cursor.fetchall()]

    responsed = {
        "records": len(pagelist),
        "data": pagelist
    }

    return Response(
        json.dumps(responsed, ensure_ascii=False),
        mimetype="application/json"
    )
