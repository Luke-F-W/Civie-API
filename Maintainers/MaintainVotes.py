"""
This scans the Oireachtas votes API and adds any vote not already in the
SQLite database to the votes table. The SQLite database has many fields for just
general data on the record, like membercodes, tallies, dates etc... just to query
by, then the last section is JSON of the object which will be returned to the end
client via my super cool API
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

#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

#uris of the votes already in the table
existing = {row[0] for row in cur.execute("SELECT json_extract(JSON, '$.division.uri') FROM votes")}

recordno = 0

#looks for records not in the database already
while True:
    url = "https://api.oireachtas.ie/v1/votes?skip=" + str(skip) + "&limit=1000&outcome="
    response = requests.get(url)
    response = response.json().get("results")
    if not response:
        break

    for b in response:
        division = b["division"]

        #skip if the vote is already in the table
        if division["uri"] in existing:
            print("Skipped. VoteNo: " + str(recordno))
            recordno += 1
            continue

        print("[SQL STATEMENT INSERTED]. VoteNo: " + str(recordno))
        recordno += 1
        isbill = division["isBill"]
        vote = division["debate"]["showAs"]

        ta_votes = division.get("tallies", {}).get("taVotes", {})
        ta_members = ta_votes.get("members", []) if ta_votes else []
        ta_codes = []
        for m in ta_members:
            code = m.get("member", {}).get("memberCode")
            if code:
                ta_codes.append(code)
        ta_membercodes = "|".join(ta_codes)
        ta_tally = ta_votes.get("tally") if ta_votes else 0

        nil_votes = division.get("tallies", {}).get("nilVotes", {})
        nil_members = nil_votes.get("members", []) if nil_votes else []
        nil_codes = []
        for m in nil_members:
            code = m.get("member", {}).get("memberCode")
            if code:
                nil_codes.append(code)
        nil_membercodes = "|".join(nil_codes)
        nil_tally = nil_votes.get("tally") if nil_votes else 0

        staon_votes = division.get("tallies", {}).get("staonVotes", {})
        staon_members = staon_votes.get("members", []) if staon_votes else []
        staon_codes = []
        for m in staon_members:
            code = m.get("member", {}).get("memberCode")
            if code:
                staon_codes.append(code)
        staon_membercodes = "|".join(staon_codes)
        staon_tally = staon_votes.get("tally") if staon_votes else 0

        outcome = division["outcome"]
        contextdate = b["contextDate"]
        chamber = division["chamber"]["showAs"]

        formembersnames = codestonames(ta_membercodes) if ta_members else ""
        againstmembersnames = codestonames(nil_membercodes) if nil_members else ""
        abstainmembersnames = codestonames(staon_membercodes) if staon_members else ""

        #add data to SQLite database
        cur.execute("""
            INSERT INTO votes (
            isBill, Chamber, Vote, ForVoters, ForTally, ForNamesOfMembers, AgainstVoters,
            AgainstTally, AgainstNamesOfMembers, AbstainVotes, AbstainTally, AbstainNamesOfMembers, Outcome,
            ContextDate, JSON
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            isbill,
            chamber,
            vote,
            ta_membercodes,
            ta_tally,
            formembersnames,
            nil_membercodes,
            nil_tally,
            againstmembersnames,
            staon_membercodes,
            staon_tally,
            abstainmembersnames,
            outcome,
            contextdate,
            json.dumps(b),
        ))

    conn.commit()
    if len(response) < 1000:
        break
    skip += 1000

conn.close()

print("done")