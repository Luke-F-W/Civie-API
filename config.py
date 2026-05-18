"""this is a seperate file to hold paths and pagesize, there is not much
of anything to talk about here, and since i moved from IJSON to SQLite
there is even less in here"""
from pathlib import Path
pagesize = 30
base = Path(__file__).resolve().parent
dbpath = base / "Database" / "civie.db"