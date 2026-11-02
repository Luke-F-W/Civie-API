"""
Goes through the Lobbying table, finds every lobbyist and counts how many returns
each one has. Each name is turned into a lobbyistcode (letters only, lowercase,
no accents) so "Edwards" and "edwards" count as the same lobbyist.
Lobbyists already in the Lobbyist table keep their key and just get a new tally.
New lobbyists are added at the end with the next key.
"""

import json, sqlite3, os, re, unicodedata

#path
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()

#used everywhere atp
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()

#lobbyistcode
#ORDER BY rowid keeps the order the same every run, so new lobbyists are
#numbered in the order they first appear
lobbyists = {}
for (name,) in cur.execute("SELECT LobbyistName FROM Lobbying ORDER BY rowid").fetchall():
    code = normalisename(name) if name else ""
    if not code:
        continue
    if code not in lobbyists:
        lobbyists[code] = {"name": name, "tally": 0}
    lobbyists[code]["tally"] += 1

#makes finding a lobbyist by code quick, and stops the same code being added twice
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lobbyist_code ON Lobbyist(LobbyistCode)")

updated = 0
added = 0
for code, l in lobbyists.items():
    info = json.dumps({"name": l["name"], "lobbyistcode": code, "tally": l["tally"]})

    #try to rewrite the tally of a lobbyist we already have
    cur.execute("UPDATE Lobbyist SET Tally = ?, JSON = ? WHERE LobbyistCode = ?",
                (l["tally"], info, code))

    if cur.rowcount > 0:
        updated += 1
    else:
        #no row was changed, so this lobbyist is new: add them at the end
        cur.execute("INSERT INTO Lobbyist (LobbyistCode, Name, Tally, JSON) VALUES (?,?,?,?)",
                    (code, l["name"], l["tally"], info))
        added += 1

conn.commit()
conn.close()

print(added, "new lobbyists,", updated, "updated")
print("done")