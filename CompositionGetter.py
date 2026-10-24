"""This returns the party breakdown of the sitting members of the Dail and the Seanad"""
from flask import Response
import json
import sqlite3
from config import dbpath
 
 
def apicomposition():
    responsed = {"dail": [], "seanad": []}
 
    with sqlite3.connect(dbpath) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MemberCode, JSON FROM Stats WHERE MemberCode IN ('dail', 'seanad')")
        for code, j in cursor.fetchall():
            responsed[code] = json.loads(j)
 
    return Response(
        json.dumps(responsed, ensure_ascii=False),
        mimetype="application/json"
    )
