"""this is a seperate file to hold paths and pagesize, there is not much
of anything to talk about here"""
from pathlib import Path
import os

pagesize = 30

database = Path(
    os.getenv("CIVIE_DATA_FOLDER", Path(__file__).resolve().parent / "Database")
)
base = Path(__file__).resolve().parent

alldir = base / "Database" / "json-all"

#for the getters
billss = alldir / "bills.json"
votess= alldir / "votes.json"
debatess = alldir / "debates.json"
lobbyingg = alldir / "lobbying.json"
questionss = alldir / "questions.json"
mainstatss = database / "json-stats" / "overall_statistics.json"
memberss = database / "json-members" / "members.json"

#for idsearch
idbillss = base / "Database" / "json-bills"
idvotess = base / "Database" / "json-votes"
iddebatess = base / "Database" / "json-debates"
idlobbyingg = base / "Database" / "json-lobbying"
idquestionss = base / "Database" / "json-questions"
idstatss = base / "Database" / "json-stats"
