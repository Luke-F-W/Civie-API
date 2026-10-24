"""
Keeps two rows in the Stats table up to date with how many sitting members
"""
import requests, json, sqlite3, os

#path
dbpath = "/var/www/flask_app/Database/civie.db"

HOUSES = {
    "dail": 34,
    "seanad": 27,
}

def fetch_members(house_code, house_no):
    members = []
    skip = 0
    while True:
        url = ("https://api.oireachtas.ie/v1/members?chamber=" + house_code
               + "&house_no=" + str(house_no) + "&skip=" + str(skip) + "&limit=1000")
        response = requests.get(url, timeout=30)
        print(results)
        response.raise_for_status()
        results = response.json().get("results")
        if not results:
            break
        members.extend(r["member"] for r in results)
        if len(results) < 1000:
            break
        skip += 1000
    return members

def current_party(membership):
    parties = [p["party"] for p in (membership.get("parties") or [])]
    current = [p for p in parties if not (p.get("dateRange") or {}).get("end")]
    if not current:
        return "Independent"
    return current[-1]["showAs"]

def tally(members, house_code, house_no):
    counts = {}
    for m in members:
        for ms in m["memberships"]:
            ms = ms["membership"]
            house = ms["house"]
            if house["houseCode"] != house_code or str(house["houseNo"]) != str(house_no):
                continue
            if (ms.get("dateRange") or {}).get("end"):
                continue
            party = current_party(ms)
            counts[party] = counts.get(party, 0) + 1
            break  #count each member once
    ordered = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return [{"party": p, "count": c} for p, c in ordered]


def main():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for house_code, house_no in HOUSES.items():
        members = fetch_members(house_code, house_no)
        result = tally(members, house_code, house_no)

        #don't wipe the table if the API returned nothing
        if not result:
            print(house_code + ": no sitting members found, left unchanged")
            continue

        total = sum(r["count"] for r in result)
        print(house_code + ": " + str(total) + " sitting members")
        for r in result:
            print("   " + r["party"] + ": " + str(r["count"]))

        cur.execute(
            "INSERT OR REPLACE INTO Stats (MemberCode, JSON) VALUES (?,?)",
            (house_code, json.dumps(result, ensure_ascii=False)),
        )

    conn.commit()
    conn.close()
    print("done")

if __name__ == "__main__":
    main()
