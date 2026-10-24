"""
Makes table of parties.
"""
import requests, json, sqlite3, os

#path
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
cur.execute("DELETE FROM Party")

#website for each party
websites = {
    "100% RDR": "https://100percentredressparty.ie/",
    "Aontú": "https://aontu.ie/",
    "Fianna Fáil": "https://www.fiannafail.ie/",
    "Fine Gael": "https://www.finegael.ie/",
    "Green Party": "https://www.greenparty.ie/",
    "Independent": "N/A",
    "Independent Ireland": "https://www.independentireland.ie/",
    "Labour Party": "https://www.labour.ie/",
    "People Before Profit-Solidarity": "https://www.pbp.ie/",
    "Sinn Féin": "https://sinnfein.ie/",
    "Social Democrats": "https://www.socialdemocrats.ie/",
}

#image for each party
images = {
    "100% RDR": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/redress.png",
    "Aontú": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/aontu.jpg",
    "Fianna Fáil": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/fiannafail.png",
    "Fine Gael": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/finegael.jpg",
    "Green Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/greenparty.jpg",
    "Independent": "N/A",
    "Independent Ireland": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/IndepIreland.jpg",
    "Labour Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/Labour.png",
    "People Before Profit-Solidarity": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/pbp.png",
    "Sinn Féin": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/sinnfein.jpg",
    "Social Democrats": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/socialdems.webp",
}

#wikipedia page for each party
wikipedia = {
    "100% RDR": "https://en.wikipedia.org/wiki/100%25_Redress",
    "Aontú": "https://en.wikipedia.org/wiki/Aont%C3%BA",
    "Fianna Fáil": "https://en.wikipedia.org/wiki/Fianna_F%C3%A1il",
    "Fine Gael": "https://en.wikipedia.org/wiki/Fine_Gael",
    "Green Party": "https://en.wikipedia.org/wiki/Green_Party_(Ireland)",
    "Independent": "N/A",
    "Independent Ireland": "https://en.wikipedia.org/wiki/Independent_Ireland",
    "Labour Party": "https://en.wikipedia.org/wiki/Labour_Party_(Ireland)",
    "People Before Profit-Solidarity": "https://en.wikipedia.org/wiki/People_Before_Profit",
    "Sinn Féin": "https://en.wikipedia.org/wiki/Sinn_F%C3%A9in",
    "Social Democrats": "https://en.wikipedia.org/wiki/Social_Democrats_(Ireland)",
}

url = "https://api.oireachtas.ie/v1/parties?chamber=dail&house_no=34&limit=1000"
response = requests.get(url).json().get("results")

for r in response:
    party = r["party"]
    stats = {
        "showAs": party["showAs"],
        "partyCode": party["partyCode"],
        "website": websites[party["showAs"]],
        "image": images[party["showAs"]],
        "wikipedia": wikipedia[party["showAs"]],
    }

    #add data to SQLite database
    cur.execute("""
        INSERT INTO Party (
        PartyCode, JSON
        )
        VALUES (?,?)
    """, (
        party["partyCode"],
        json.dumps(stats, ensure_ascii=False),
    ))

conn.commit()
conn.close()

print("done")
