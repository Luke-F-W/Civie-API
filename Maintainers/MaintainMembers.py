"""
This scans the Oireachtas members API and adds any member not already in the
SQLite database to the Members table. The SQLite database has a few fields for
just general data on the record, to query by, then the last section is JSON of
the object which will be returned to the end client via my super cool API
"""
import requests, json, sqlite3, os, time

#path
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
skip = 0

recordno = 0
#goes through all records for members
while True:
    url = "https://api.oireachtas.ie/v1/members?date_start=2015-01-01&skip=" + str(skip) + "&limit=1000"
    response = requests.get(url)
    response = response.json().get("results")
    if not response:
        break

    for b in response:
        member = b["member"]
        membercode = member["memberCode"]

        #skip if the member is already in the table
        cur.execute("SELECT 1 FROM Members WHERE MemberCode = ?", (membercode,))
        if cur.fetchone():
            print("Skipped. MemberNo: " + str(recordno))
            recordno += 1
            continue

        print("[SQL STATEMENT INSERTED]. MemberNo: " + str(recordno))
        recordno += 1
        fullname = member["fullName"]
        fname = member["firstName"]
        lname = member["lastName"]

        #get image
        image = "https://data.oireachtas.ie/ie/oireachtas/member/id/" + membercode + "/image/large"
        member["image"] = image

        #add data to SQLite database
        cur.execute("""
            INSERT INTO Members (
            FullName, FirstName, LastName,
            Image, MemberCode, JSON
            )
            VALUES (?,?,?,?,?,?)
        """, (
            fullname,
            fname,
            lname,
            image,
            membercode,
            json.dumps(b),
        ))

    conn.commit()
    if len(response) < 1000:
        break
    skip += 1000
    print("got 1000 records, we are now at:" + str(skip))

conn.close()

print("done")