"""
This scans the Oireachtas questions API and adds any question not already in the
SQLite database to the Questions table. The SQLite database has many fields for
just general data on the record, like membercodes, dates etc... just to query by,
then the last section is JSON of the object which will be returned to the end
client via my super cool API
"""
import requests, json, sqlite3, os, time

#paths
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
skip = 0

recordno = 0
#looks for records not in the database already
while True:
    url = "https://api.oireachtas.ie/v1/questions?skip=" + str(skip) + "&limit=1000&qtype=&show_answers=true"
    response = requests.get(url)
    response = response.json().get("results")
    if not response:
        break

    for b in response:
        quest = b["question"]
        questionno = quest["questionNumber"]
        questiontype = quest["questionType"]
        contextDate = b["contextDate"]

        #skip if the question is already in the table
        cur.execute("SELECT 1 FROM Questions WHERE QuestionNumber = ? AND QuestionType = ? AND contextDate = ?", (questionno, questiontype, contextDate))
        if cur.fetchone():
            print("Skipped. QuestionNo: " + str(recordno))
            recordno += 1
            continue

        print("[SQL STATEMENT INSERTED]. QuestionNo: " + str(recordno))
        recordno += 1
        question = quest["showAs"]
        answertext = quest["answerText"]
        questionTo = quest["to"]["showAs"]
        questionBy = quest["by"]["showAs"]
        membercodeBy = quest["by"]["memberCode"]

        #add data to SQLite database
        cur.execute("""
            INSERT INTO Questions (
            QuestionNumber, QuestionType, Question, answerText, contextDate, QuestionTo,
            QuestionBy, MembercodeBy, JSON
            )
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            questionno,
            questiontype,
            question,
            answertext,
            contextDate,
            questionTo,
            questionBy,
            membercodeBy,
            json.dumps(b),
        ))

    conn.commit()
    if len(response) < 1000:
        break
    skip += 1000

conn.close()

print("done")