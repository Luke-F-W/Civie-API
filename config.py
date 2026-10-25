"""this is a seperate file to hold paths and pagesize, there is not much
of anything to talk about here, and since i moved from IJSON to SQLite
there is even less in here"""
from pathlib import Path
pagesize = 30
TDpagesize = 15 # td jsons are large, so im giving them less
base = Path(__file__).resolve().parent
dbpath = base / "Database" / "civie.db"
RATE_LIMIT = "360 per hour"