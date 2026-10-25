import json
import sqlite3
from flask import Response
from config import dbpath


def current_party(membership):
    for p in membership["parties"]:
        if not p["party"]["dateRange"].get("end"):
            return p["party"]["showAs"]
    return "Independent"


def apiconstituency():
    conn = sqlite3.connect(dbpath)
    rows = conn.execute("SELECT JSON FROM Members").fetchall()
    conn.close()

    out = {}
    for (blob,) in rows:
        member = json.loads(blob)
        member = member.get("member", member)
        for ms in member["memberships"]:
            ms = ms["membership"]
            # only TDs who are sitting in the Dail right now
            if ms["house"]["houseCode"] != "dail" or ms["dateRange"].get("end"):
                continue
            for r in ms["represents"]:
                out.setdefault(r["represent"]["showAs"], []).append({
                    "name": member["showAs"],
                    "party": current_party(ms),
                    "memberCode": member["uri"].split("/")[-1]
                })
            break

    return Response(json.dumps(out, ensure_ascii=False), mimetype="application/json")
