"""
This scans the Oireachtas legislation API and adds any bill not already in the
SQLite database to the Legislation table. The SQLite database has many fields for
just general data on the record, like membercodes, tallies, dates etc... just to
query by, then the last section is JSON of the object which will be returned to
the end client via my super cool API
"""
import json, sqlite3, os, requests, time
from bs4 import BeautifulSoup

#paths
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
skip = 0

#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

def clean(x):
    return BeautifulSoup(x, "html.parser").get_text() if x else None

recordno = 0

#looks for records not in the database already
while True:
    url = "https://api.oireachtas.ie/v1/legislation?bill_status=&skip=" + str(skip) + "&limit=1000&lang=en"
    response = requests.get(url)
    response = response.json().get("results")
    if not response:
        break

    for b in response:
        bill = b["bill"]
        bill_no = bill["billNo"] #bill number
        billYear = bill["billYear"]

        #skip if the bill is already in the table
        cur.execute("SELECT 1 FROM Legislation WHERE BillNo = ? AND BillYear = ?", (bill_no, billYear))
        if cur.fetchone():
            print("Skipped. BillNo:  " + str(recordno))
            recordno += 1
            continue

        print("[SQL STATEMENT INSERTED]. BillNo: " + str(recordno))
        recordno += 1
        longTitleEn = bill["longTitleEn"] #long title en
        shortTitleEn = bill["shortTitleEn"] #short title en
        longTitleGa = bill["longTitleGa"] #long title ga
        shortTitleGa = bill["shortTitleGa"] #short title ga

        #json has HTML in these, must be cleaned
        longTitleEn = clean(longTitleEn)
        longTitleGa = clean(longTitleGa)
        shortTitleEn = clean(shortTitleEn)
        shortTitleGa = clean(shortTitleGa)
        status = bill["status"]
        context_date = b["contextDate"]
        source = bill["source"]
        billType = bill["billType"]

        #membercodes, which are annoying
        sponsors = bill.get("sponsors", [])
        membercodes_list = []
        for s in sponsors:
            uri = (
                s.get("sponsor", {})
                .get("by", {})
                .get("uri")
            )
            if uri:
                membercode = uri.split("/")[-1]
                membercodes_list.append(membercode)
        membercodes = "|".join(membercodes_list)

        namesofmembers = codestonames(membercodes) if membercodes else ""

        #insert cool data into cool SQLite table
        cur.execute("""
            INSERT INTO Legislation (
                BillNo, BillType, BillYear,
                LongTitleEn, LongTitleGa,
                ShortTitleEn, ShortTitleGa,
                Source, Status,
                contextDate, Membercodes, NamesOfMembers, JSON
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            bill_no,
            billType,
            billYear,

            longTitleEn,
            longTitleGa,
            shortTitleEn,
            shortTitleGa,

            source,
            status,
            context_date,

            membercodes,
            namesofmembers,
            json.dumps(b)
        ))

    conn.commit()
    if len(response) < 1000:
        break
    skip += 1000

conn.close()

print("done")
