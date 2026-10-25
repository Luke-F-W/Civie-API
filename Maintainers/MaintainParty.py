"""
Makes table of parties.
"""
import requests, json, sqlite3

#path
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
cur.execute("DELETE FROM Party")

#labels that aren't parties, or are the same party under an older name (remove a name from here to keep it)
SKIP = {
    "Ceann Comhairle",
    "Republican",
    "Anti-Austerity Alliance - People Before Profit",
    "People Before Profit Alliance",
    "Sinn Féin the Workers Party",
    "Independent",
}

RENAME = {
    "Renua": "The Centre Party",
    "Socialist Party": "Solidarity"
}

#website for each party, the keys are the names the API uses
websites = {
    "100% RDR": "https://100percentredressparty.ie/",
    "Aontú": "https://aontu.ie/",
    "Business and Professional Group": "N/A",
    "Clann na Poblachta": "N/A",
    "Clann na Talmhan": "N/A",
    "Cumann na nGaedheal": "N/A",
    "Democratic Left": "N/A",
    "Democratic Socialist Party": "N/A",
    "Farmers Party": "N/A",
    "Fianna Fáil": "https://www.fiannafail.ie/",
    "Fine Gael": "https://www.finegael.ie/",
    "Green Party": "https://www.greenparty.ie/",
    "Independent Ireland": "https://www.independentireland.ie/",
    "Independents 4 Change": "N/A",
    "Irish Worker League": "N/A",
    "Labour Party": "https://www.labour.ie/",
    "National Centre Party": "N/A",
    "National Labour Party": "N/A",
    "National League Party": "N/A",
    "National Progressive Democrats": "N/A",
    "People Before Profit-Solidarity": "https://www.pbp.ie/",
    "Progressive Democrats": "N/A",
    "Renua": "https://centreparty.ie/",
    "Sinn Féin": "https://sinnfein.ie/",
    "Social Democrats": "https://www.socialdemocrats.ie/",
    "Socialist Labour Party": "N/A",
    "Socialist Party": "https://www.solidarity.ie/",
    "Workers Party": "https://workersparty.ie/",
    "Workers and Unemployed Action": "https://wuag.wordpress.com/",
}

#image for each party, same keys as above
images = {
    "100% RDR": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/redress.png",
    "Aontú": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/aontu.jpg",
    "Business and Professional Group": "N/A",
    "Clann na Poblachta": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/ClannNaPoblacla.jpg",
    "Clann na Talmhan": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/ClannNaTalman.jpg",
    "Cumann na nGaedheal": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/CummanNanGaedheal.jpg",
    "Democratic Left": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/DemocraticLeft.jpg",
    "Democratic Socialist Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/dsp.jpg",
    "Farmers Party": "N/A",
    "Fianna Fáil": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/fiannafail.png",
    "Fine Gael": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/finegael.jpg",
    "Green Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/greenparty.jpg",
    "Independent Ireland": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/IndepIreland.jpg",
    "Independents 4 Change": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/IndependentsForChange.jpg",
    "Irish Worker League": "N/A",
    "Labour Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/Labour.png",
    "National Centre Party": "N/A",
    "National Labour Party": "N/A",
    "National League Party": "N/A",
    "National Progressive Democrats": "N/A",
    "People Before Profit-Solidarity": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/pbp.png",
    "Progressive Democrats": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/ProgressiveDemocrats.jpg",
    "Renua": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/renua.jpg",
    "Sinn Féin": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/sinnfein.jpg",
    "Social Democrats": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/socialdems.webp",
    "Socialist Labour Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/SocialistLabourParty.jpg",
    "Socialist Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/Solidarity.png",
    "Workers Party": "https://raw.githubusercontent.com/Luke-F-W/Civie_Data_Getters/refs/heads/main/Images/WorkersParty.png",
    "Workers and Unemployed Action": "N/A",
}

#wikipedia page for each party, same keys as above
wikipedia = {
    "100% RDR": "https://en.wikipedia.org/wiki/100%25_Redress",
    "Aontú": "https://en.wikipedia.org/wiki/Aont%C3%BA",
    "Business and Professional Group": "https://en.wikipedia.org/wiki/Business_and_Professional_Group",
    "Clann na Poblachta": "https://en.wikipedia.org/wiki/Clann_na_Poblachta",
    "Clann na Talmhan": "https://en.wikipedia.org/wiki/Clann_na_Talmhan",
    "Cumann na nGaedheal": "https://en.wikipedia.org/wiki/Cumann_na_nGaedheal",
    "Democratic Left": "https://en.wikipedia.org/wiki/Democratic_Left_(Ireland)",
    "Democratic Socialist Party": "https://en.wikipedia.org/wiki/Democratic_Socialist_Party_(Ireland)",
    "Farmers Party": "https://en.wikipedia.org/wiki/Farmers%27_Party_(Ireland)",
    "Fianna Fáil": "https://en.wikipedia.org/wiki/Fianna_F%C3%A1il",
    "Fine Gael": "https://en.wikipedia.org/wiki/Fine_Gael",
    "Green Party": "https://en.wikipedia.org/wiki/Green_Party_(Ireland)",
    "Independent Ireland": "https://en.wikipedia.org/wiki/Independent_Ireland",
    "Independents 4 Change": "https://en.wikipedia.org/wiki/Independents_4_Change",
    "Irish Worker League": "https://en.wikipedia.org/wiki/Irish_Worker_League",
    "Labour Party": "https://en.wikipedia.org/wiki/Labour_Party_(Ireland)",
    "National Centre Party": "https://en.wikipedia.org/wiki/National_Centre_Party_(Ireland)",
    "National Labour Party": "https://en.wikipedia.org/wiki/National_Labour_Party_(Ireland)",
    "National League Party": "https://en.wikipedia.org/wiki/National_League_Party",
    "National Progressive Democrats": "https://en.wikipedia.org/wiki/National_Progressive_Democrats",
    "People Before Profit-Solidarity": "https://en.wikipedia.org/wiki/People_Before_Profit",
    "Progressive Democrats": "https://en.wikipedia.org/wiki/Progressive_Democrats",
    "Renua": "https://en.wikipedia.org/wiki/Renua",
    "Sinn Féin": "https://en.wikipedia.org/wiki/Sinn_F%C3%A9in",
    "Social Democrats": "https://en.wikipedia.org/wiki/Social_Democrats_(Ireland)",
    "Socialist Labour Party": "https://en.wikipedia.org/wiki/Socialist_Labour_Party_(Ireland)",
    "Socialist Party": "https://en.wikipedia.org/wiki/Socialist_Party_(Ireland)",
    "Workers Party": "https://en.wikipedia.org/wiki/Workers%27_Party_(Ireland)",
    "Workers and Unemployed Action": "https://en.wikipedia.org/wiki/Workers_and_Unemployed_Action",
}

#D for disbanded, P for in power, O for out of power.
power = {
    "100% RDR": "P",
    "Aontú": "P",
    "Business and Professional Group": "D",
    "Clann na Poblachta": "D",
    "Clann na Talmhan": "D",
    "Cumann na nGaedheal": "D",
    "Democratic Left": "D",
    "Democratic Socialist Party": "D",
    "Farmers Party": "D",
    "Fianna Fáil": "P",
    "Fine Gael": "P",
    "Green Party": "P",
    "Independent Ireland": "P",
    "Independents 4 Change": "D",
    "Irish Worker League": "D",
    "Labour Party": "P",
    "National Centre Party": "D",
    "National Labour Party": "D",
    "National League Party": "D",
    "National Progressive Democrats": "D",
    "People Before Profit-Solidarity": "P",
    "Progressive Democrats": "D",
    "Renua": "O",
    "Sinn Féin": "P",
    "Social Democrats": "P",
    "Socialist Labour Party": "D",
    "Socialist Party": "O",
    "Workers Party": "O",
    "Workers and Unemployed Action": "O",
}

#every party that has had a member in any Dail or Seanad term
parties = {}
houses = [("dail", n) for n in range(1, 35)] + [("seanad", n) for n in range(1, 28)]
for chamber, house_no in houses:
    url = ("https://api.oireachtas.ie/v1/parties?chamber=" + chamber
           + "&house_no=" + str(house_no) + "&limit=1000")
    for r in requests.get(url, timeout=30).json().get("results", []):
        parties[r["party"]["partyCode"]] = r["party"]["showAs"]


for code, name in parties.items():
    if name in SKIP:
        continue
    stats = {
        "showAs": RENAME.get(name, name),
        "partyCode": code,
        "website": websites[name],
        "image": images[name],
        "wikipedia": wikipedia[name],
        "status": power[name],
    }

    cur.execute("""
        INSERT INTO Party (
        PartyCode, JSON
        )
        VALUES (?,?)
    """, (
        code,
        json.dumps(stats, ensure_ascii=False),
    ))

conn.commit()
conn.close()

print("done")
