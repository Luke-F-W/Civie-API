"""This returns 30 question records matching the queries (if the user includes any)"""
from flask import request, Response
import json
import sqlite3
from config import pagesize, dbpath


def apiquestion():
    #queries
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    before = request.args.get("before", "2300-01-01") or "2300-01-01"
    after = request.args.get("after", "1900-01-01") or "1900-01-01"

    #type queries
    oral = request.args.get("oral", "true").lower() == "true"
    written = request.args.get("written", "true").lower() == "true"

    #search by Question
    questionText = request.args.get("questiontxt", "")
    answerText = request.args.get("answertxt", "")

    start = (page - 1) * pagesize

    query = """
        SELECT JSON FROM Questions
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = 0 OR QuestionType != 'Oral')
        AND (? = 0 OR QuestionType != 'Written')
        AND (? = '' OR Question LIKE ?)
        AND (? = '' OR answerText LIKE ?)
        AND (? = '' OR Question LIKE ? OR answerText LIKE ?)
        LIMIT ? OFFSET ?
        """

    countquery = """
        SELECT COUNT(*) FROM Questions
        WHERE contextDate <= ?
        AND contextDate >= ?
        AND (? = 0 OR QuestionType != 'Oral')
        AND (? = 0 OR QuestionType != 'Written')
        AND (? = '' OR Question LIKE ?)
        AND (? = '' OR answerText LIKE ?)
        AND (? = '' OR Question LIKE ? OR answerText LIKE ?)
    """

    sparams = [
        before, after,
        int(not oral), int(not written),
        questionText, f"%{questionText}%",
        answerText, f"%{answerText}%",
        search, f"%{search}%", f"%{search}%",
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