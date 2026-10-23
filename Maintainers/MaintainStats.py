"""
This builds the stats for every member in the SQLite database from the debates,
lobbying, legislation, questions and votes tables, and adds them to the Stats
table. The SQLite database has the MemberCode just to query by, then the last
section is JSON of the stats which will be returned to the end client via my
super cool API
"""
import json, sqlite3, os

#path
file = os.path.abspath(__file__)
filepath = os.path.dirname(file)
base = os.path.abspath(os.path.join(filepath, "..", "..", ".."))
dbpath = os.path.join(base, "CivieDatabase", "civie.db")
dbpath = os.path.normpath(dbpath)
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
cur.execute("DELETE FROM Stats")

def lobbyiststats(membercode):
    lobbyist_counts = {}
    lobbycount = 0
    lobbyyear_dict = {}
    like = "%" + membercode + "%"

    for (j,) in cur.execute("SELECT JSON FROM Lobbying WHERE Membercodes LIKE ?", (like,)):
        entry = json.loads(j)
        member_codes_field = entry.get("MemberCodes", "")

        if member_codes_field:
            membercodes_list = member_codes_field.split("|")

            if membercode in membercodes_list:
                lobbycount += 1
                lobbyist = entry.get("Lobbyist Name", "").strip().lower()

                if lobbyist in lobbyist_counts:
                    lobbyist_counts[lobbyist] += 1
                else:
                    lobbyist_counts[lobbyist] = 1

                date_published = entry.get("Date Published", "")
                year = date_published.split("/")[2].split()[0]
                if year in lobbyyear_dict:
                    lobbyyear_dict[year] += 1
                else:
                    lobbyyear_dict[year] = 1

    return lobbyist_counts, lobbycount, lobbyyear_dict

def questionstats(membercode):
    questionCount = 0
    questionYear_dict = {}
    questionType_dict = {}

    for (j,) in cur.execute("SELECT JSON FROM Questions WHERE MembercodeBy = ?", (membercode,)):
        entry = json.loads(j)
        questionCount += 1
        context_date = entry.get("contextDate", "")
        year = context_date.split("-")[0]

        if year in questionYear_dict:
            questionYear_dict[year] += 1
        else:
            questionYear_dict[year] = 1

        question_type = entry.get("question", {}).get("questionType", "")
        if question_type in questionType_dict:
            questionType_dict[question_type] += 1
        else:
            questionType_dict[question_type] = 1

    return questionCount, questionYear_dict, questionType_dict

def votestats(membercode):
    voteCount = 0
    votestally_dict = {}
    voteYear_dict = {}
    isVoted = False
    voteWithWinner = {}
    like = "%" + membercode + "%"

    for (j,) in cur.execute("SELECT JSON FROM votes WHERE ForVoters LIKE ? OR AgainstVoters LIKE ? OR AbstainVotes LIKE ?", (like, like, like)):
        entry = json.loads(j)
        voteoutcome = entry.get("division", {}).get("outcome", "").lower()
        isVoted = False
        tallies = entry.get("division", {}).get("tallies", {})

        # TA votes
        for m in (tallies.get("taVotes") or {}).get("members", []) or []:
            if m.get("member", {}).get("memberCode", "") == membercode:
                voteCount += 1
                votestally_dict["ta"] = votestally_dict.get("ta", 0) + 1
                isVoted = True

                if voteoutcome == "carried":
                    voteWithWinner["VotedWithWinner"] = (
                        voteWithWinner.get("VotedWithWinner", 0) + 1
                    )
                elif voteoutcome == "lost":
                    voteWithWinner["VotedAgainstWinner"] = (
                        voteWithWinner.get("VotedAgainstWinner", 0) + 1
                    )
                break

        # Nil votes
        for m in (tallies.get("nilVotes") or {}).get("members", []) or []:
            if m.get("member", {}).get("memberCode", "") == membercode:
                voteCount += 1
                votestally_dict["nil"] = votestally_dict.get("nil", 0) + 1
                isVoted = True

                if voteoutcome == "carried":
                    voteWithWinner["VotedAgainstWinner"] = (
                        voteWithWinner.get("VotedAgainstWinner", 0) + 1
                    )
                elif voteoutcome == "lost":
                    voteWithWinner["VotedWithWinner"] = (
                        voteWithWinner.get("VotedWithWinner", 0) + 1
                    )
                break

        # Staon votes
        for m in (tallies.get("staonVotes") or {}).get("members", []) or []:
            if m.get("member", {}).get("memberCode", "") == membercode:
                voteCount += 1
                votestally_dict["staon"] = votestally_dict.get("staon", 0) + 1
                isVoted = True
                break

        if isVoted:
            context_date = entry.get("contextDate", "")
            year = context_date.split("-")[0]

            if year in voteYear_dict:
                voteYear_dict[year] += 1
            else:
                voteYear_dict[year] = 1

    return voteCount, votestally_dict, voteYear_dict, voteWithWinner

def billstats(membercode):
    billCount = 0
    billCountPerYear_dict = {}
    billSource_dict = {}
    like = "%" + membercode + "%"

    for (j,) in cur.execute("SELECT JSON FROM Legislation WHERE Membercodes LIKE ?", (like,)):
        entry = json.loads(j)
        uri = (entry.get("bill", {}).get("sponsors") or [{}])[0].get("sponsor", {}).get("by", {}).get("uri") or ""
        if not uri:
            continue
        billMembercode = uri.split("/")[-1]

        if billMembercode == membercode:
            billCount += 1
            context_date = entry.get("contextDate", "")
            year = context_date.split("-")[0]

            if year in billCountPerYear_dict:
                billCountPerYear_dict[year] += 1
            else:
                billCountPerYear_dict[year] = 1

            source = entry.get("bill", {}).get("source", "")
            if source in billSource_dict:
                billSource_dict[source] += 1
            else:
                billSource_dict[source] = 1

    return billCount, billCountPerYear_dict, billSource_dict

def debatestats(membercode):
    speechCount = 0
    wordCount = 0
    speechYear_dict = {}
    speechChamber_dict = {}
    speechSection_dict = {}
    debateDays = set()  # unique (chamber, date) pairs the member spoke in
    like = "%" + membercode + "%"

    for (j,) in cur.execute("SELECT JSON FROM debates WHERE MemberCodes LIKE ?", (like,)):
        entry = json.loads(j)
        context_date = entry.get("contextDate", "")
        year = context_date.split("-")[0]
        chamber = entry.get("debateRecord", {}).get("house", {}).get("houseCode", "")
        sections = entry.get("debatestuff", {}).get("sections", []) or []

        for section in sections:
            title = section.get("title", "")

            for speech in section.get("speeches", []) or []:
                # speakers like "Deputy Michael Collins" have a null membercode, so they are skipped
                if speech.get("membercode", "") != membercode:
                    continue

                speechCount += 1
                wordCount += len((speech.get("speechtext") or "").split())
                debateDays.add((chamber, context_date))

                if year in speechYear_dict:
                    speechYear_dict[year] += 1
                else:
                    speechYear_dict[year] = 1

                if chamber in speechChamber_dict:
                    speechChamber_dict[chamber] += 1
                else:
                    speechChamber_dict[chamber] = 1

                if title in speechSection_dict:
                    speechSection_dict[title] += 1
                else:
                    speechSection_dict[title] = 1

    return speechCount, wordCount, len(debateDays), speechYear_dict, speechChamber_dict, speechSection_dict

# speechCount_int is an int with the amount of speeches (individual contributions) by the member
# wordCount_int is an int with the total words spoken by the member
# debateDayCount_int is an int with the number of sitting days the member spoke on
# speechYear_dict is a dict with each year and the number of speeches that year
# speechChamber_dict is a dict with each chamber (dail, seanad) and the number of speeches in it
# speechSection_dict is a dict with each debate section title and the number of speeches in it
# ---
# speechCount_int, wordCount_int, debateDayCount_int, speechYear_dict, speechChamber_dict, speechSection_dict = debatestats("Brendan-Howlin.S.1983-02-23")

# lobbyistcount_dict is a dict with each lobbyist and a counter
# lobbycount_int is an int with the amount of records
# lobbyyear_dict is a dict with each year and a count of the amount of lobbying records
# ---
# lobbyistcount_dict, lobbycount_int, lobbyyear_dict = lobbyiststats("Brendan-Howlin.S.1983-02-23")

# billCount_int is an int with the amount of records
# billCountPerYear_dict is a dict with each year a bill was sponsored and teh number of times that year
# billSource_dict shows the source of the bill and a number of how many
# ---
# billCount_int, billCountPerYear_dict, billSource_dict = billstats("Brendan-Howlin.S.1983-02-23")

# questionCount_int is an int with the amount of records
# questionYear_dict is a dict with each year a question was asked and the number of times that year
# questionType_dict shows the type of the question and a number of how many
# ---
# questionCount_int, questionYear_dict, questionType_dict = questionstats("Carol-Nolan.D.2016-10-03")

# voteCount_int is an int with the amount of votes cast by the member
# votestally_dict is a dict with each vote type (ta, nil, staon) and a count
# voteYear_dict is a dict with each year and the number of votes cast that year
# voteWithWinner_dict shows how many times the member voted with or against the winning outcome
# ---
# voteCount_int, votestally_dict, voteYear_dict, voteWithWinner_dict = votestats("Brendan-Howlin.S.1983-02-23")

#every member in the database
members = [row[0] for row in cur.execute("SELECT MemberCode FROM Members")]

for membercode in members:
    print("========================================")
    print("Starting: " + membercode)
    speechCount_int, wordCount_int, debateDayCount_int, speechYear_dict, speechChamber_dict, speechSection_dict = debatestats(membercode)
    print("debates is done for: " + membercode)

    lobbyistcount_dict, lobbycount_int, lobbyyear_dict = lobbyiststats(membercode)
    print("lobbying is done for: " + membercode)

    billCount_int, billCountPerYear_dict, billSource_dict = billstats(membercode)
    print("bills is done for: " + membercode)

    questionCount_int, questionYear_dict, questionType_dict = questionstats(membercode)
    print("questions is done for: " + membercode)

    voteCount_int, votestally_dict, voteYear_dict, voteWithWinner_dict = votestats(membercode)
    print("votes is done for: " + membercode)
    print("========================================")

    stats = {
        "member": {
            "memberCode": membercode,
            "debates": {
                "speechCount": speechCount_int,
                "wordCount": wordCount_int,
                "debateDayCount": debateDayCount_int,
                "speechesPerYear": speechYear_dict,
                "speechesPerChamber": speechChamber_dict,
            },
            "lobbying": {
                "lobbyCount": lobbycount_int,
                "lobbyistCounts": lobbyistcount_dict,
                "lobbyPerYear": lobbyyear_dict
            },
            "bills": {
                "billCount": billCount_int,
                "billsPerYear": billCountPerYear_dict,
                "billSources": billSource_dict
            },
            "questions": {
                "questionCount": questionCount_int,
                "questionsPerYear": questionYear_dict,
                "questionTypes": questionType_dict
            },
            "votes": {
                "voteCount": voteCount_int,
                "voteTally": votestally_dict,
                "votesPerYear": voteYear_dict,
                "voteWithWinner": voteWithWinner_dict
            }
        }
    }

    #add data to SQLite database
    cur.execute("""
        INSERT OR REPLACE INTO Stats (
        MemberCode, JSON
        )
        VALUES (?,?)
    """, (
        membercode,
        json.dumps(stats),
    ))
    conn.commit()

conn.close()

print("done")