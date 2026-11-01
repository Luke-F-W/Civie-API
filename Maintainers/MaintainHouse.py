import requests
import json
import sqlite3
import os
import time

dbpath = "/var/www/flask_app/Database/civie.db"

# Each pair is a Dail and the Seanads that sat during it.
# The names must match the API's showAs exactly. Newest first.
PAIRS = [
    ("34th Dáil", ["27th Seanad"]),
    ("33rd Dáil", ["26th Seanad"]),
    ("32nd Dáil", ["25th Seanad"]),
    ("31st Dáil", ["24th Seanad"]),
    ("30th Dáil", ["23rd Seanad"]),
    ("29th Dáil", ["22nd Seanad"]),
    ("28th Dáil", ["21st Seanad"]),
    ("27th Dáil", ["20th Seanad"]),
    ("26th Dáil", ["19th Seanad"]),
    ("25th Dáil", ["18th Seanad"]),
    ("24th Dáil", ["17th Seanad"]),
    ("23rd Dáil", ["16th Seanad"]),
    ("22nd Dáil", ["15th Seanad"]),
    ("21st Dáil", ["14th Seanad"]),
    ("20th Dáil", ["13th Seanad"]),
    ("19th Dáil", ["12th Seanad"]),
    ("18th Dáil", ["11th Seanad"]),
    ("17th Dáil", ["10th Seanad"]),
    ("16th Dáil", ["9th Seanad"]),
    ("15th Dáil", ["8th Seanad"]),
    ("14th Dáil", ["7th Seanad"]),
    ("13th Dáil", ["6th Seanad"]),
    ("12th Dáil", ["5th Seanad"]),
    ("11th Dáil", ["4th Seanad"]),
    ("10th Dáil", ["3rd Seanad"]),
    ("9th Dáil", ["2nd Seanad"]),
    ("8th Dáil", ["1931 Seanad", "1934 Seanad"]),
    ("7th Dáil", ["1931 Seanad"]),
    ("6th Dáil", ["1925 Seanad", "1928 Seanad", "1931 Seanad"]),
    ("5th Dáil", ["1925 Seanad"]),
    ("4th Dáil", ["1922 Seanad", "1925 Seanad"]),
    ("3rd Dáil", ["1922 Seanad"]),
    ("2nd Dáil", []),
    ("1st Dáil", []),
]

# Ask the API for every house, so we know each one's code, number and dates
response = requests.get("https://api.oireachtas.ie/v1/houses?limit=200", timeout=30)
houses = {}
for result in response.json()["results"]:
    house = result["house"]
    houses[house["showAs"]] = house


def get_house(house_name):
    house = houses.get(house_name)
    if house is None:
        print("House not found:", house_name)
        return None

    house_code = house["houseCode"]
    house_number = house["houseNo"]

    # A house with no end date is the current one
    is_current = house["dateRange"]["end"] is None

    print("Getting", house_name)
    url = "https://api.oireachtas.ie/v1/members?chamber=" + house_code + "&house_no=" + str(house_number) + "&limit=1000"
    results = requests.get(url, timeout=30).json()["results"]
    time.sleep(1)

    members = []
    party_counts = {}

    for result in results:
        person = result["member"]

        for item in person["memberships"]:
            membership = item["membership"]

            # Skip memberships from other houses
            if membership["house"]["houseCode"] != house_code:
                continue
            if str(membership["house"]["houseNo"]) != str(house_number):
                continue

            # For the current house, skip people who have already left
            if is_current and membership["dateRange"].get("end"):
                continue

            # Their party: the one they joined last
            party_list = []
            for p in membership["parties"]:
                party_list.append(p["party"])
            party_list.sort(key=lambda p: p["dateRange"].get("start") or "")

            party = "Independent"
            if party_list:
                party = party_list[-1]["showAs"]

            # Constituency (or panel, for the Seanad)
            constituency = None
            if membership["represents"]:
                constituency = membership["represents"][0]["represent"]["showAs"]

            members.append({
                "name": person["showAs"],
                "memberCode": person["uri"].split("/")[-1],
                "party": party,
                "constituency": constituency,
            })

            if party in party_counts:
                party_counts[party] = party_counts[party] + 1
            else:
                party_counts[party] = 1

            break  # each person is only counted once

    # Turn the counts into a list, biggest party first
    parties = []
    for party, count in party_counts.items():
        parties.append({"party": party, "count": count})
    parties.sort(key=lambda x: x["count"], reverse=True)

    return {
        "house": house_name,
        "start": house["dateRange"]["start"],
        "end": house["dateRange"]["end"],
        "total": len(members),
        "parties": parties,
        "members": members,
    }


# Build every row first. Nothing is written until all of them worked.
rows = []
cache = {}   # a Free State Seanad is in several pairs, only fetch it once

for dail_name, seanad_names in PAIRS:
    if dail_name not in cache:
        cache[dail_name] = get_house(dail_name)

    seanads = []
    for seanad_name in seanad_names:
        if seanad_name not in cache:
            cache[seanad_name] = get_house(seanad_name)
        seanads.append(cache[seanad_name])

    name = " & ".join([dail_name] + seanad_names)
    data = {"dail": cache[dail_name], "seanad": seanads}
    rows.append((name, json.dumps(data, ensure_ascii=False)))

# Stop if the current Dail or Seanad came back empty, so we never wipe good data
current = json.loads(rows[0][1])
if not current["dail"] or current["dail"]["total"] == 0 or current["seanad"][0]["total"] == 0:
    print("The current houses came back empty, table left unchanged")
    raise SystemExit

# Clear the table, then save every row
conn = sqlite3.connect(dbpath)
conn.execute("DELETE FROM Composition")
conn.executemany("INSERT INTO Composition (Name, JSON) VALUES (?, ?)", rows)
conn.commit()
conn.close()

print("Done:", len(rows), "rows saved")