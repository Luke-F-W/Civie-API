"""
Goes through the Lobbying table, finds every lobbyist and counts how many returns
each one has. Each name is turned into a lobbyistcode (letters only, lowercase,
no accents) so "Edwards" and "edwards" count as the same lobbyist. The results
go into the Lobbyist table as lobbyistcode, name and tally.
"""

import json, sqlite3, os, re, unicodedata

#path
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
cur.execute("DELETE FROM Lobbyist")

#used everywhere atp
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()

#lobbyistcode
lobbyists = {}
for (name,) in cur.execute("SELECT LobbyistName FROM Lobbying").fetchall():
    code = normalisename(name) if name else ""
    if not code:
        continue
    if code not in lobbyists:
        lobbyists[code] = {"name": name, "tally": 0}
    lobbyists[code]["tally"] += 1

#clears table to add brand new data :D
cur.execute("DELETE FROM Lobbyist")

cur.executemany(
    "INSERT INTO Lobbyist (LobbyistCode, Name, Tally, JSON) VALUES (?,?,?,?)",
    [
        (code, l["name"], l["tally"],
         json.dumps({"name": l["name"], "lobbyistcode": code, "tally": l["tally"]}))
        for code, l in lobbyists.items()
    ]
)

conn.commit()
conn.close()

print(len(lobbyists), "lobbyists")
print("done")
