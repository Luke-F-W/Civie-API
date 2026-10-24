"""
This scans the Oireachtas debates API and adds any debate not already in the
SQLite database to the debates table. For each new debate the xml is downloaded
and parsed into debatestuff (title, sections, speeches). The SQLite database has
many fields for just general data on the record, like membercodes, titles etc...
just to query by, then the last section is JSON of the object which will be
returned to the end client via my super cool API
"""
from lxml import etree
import os, re, unicodedata, json, requests, time, sqlite3

#paths
dbpath = "/var/www/flask_app/Database/civie.db"
conn = sqlite3.connect(dbpath)
cur = conn.cursor()
skip = 0

# the xml files use this "namespace" prefix
ns = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/CSD13"}


#either get normal text from xml, or just "" if nothing is there
def get_text(element):
    if element is None:
        return ""
    return etree.tostring(element, method="text", encoding="unicode").strip()


#normalises names, this function is used everywhere atp, makes Jamie O'Donoghue turn into jamieodonoghue
def normalisename(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ASCII', 'ignore')
    name = name.decode('utf-8')
    name = re.sub('[^a-zA-Z]', '', name)
    return name.lower()


#read all the people listed in the xml and store their info in a dict
def getpeople(xml_content):
    tree = etree.fromstring(xml_content)
    people = {}
    for person in tree.findall(".//akn:TLCPerson", ns):
        code = person.get("href").split("/")[-1]
        people[person.get("eId").lower()] = {
            "name": person.get("showAs"),
            "membercode": code,
            "imageURL": "https://data.oireachtas.ie/ie/oireachtas/member/" + code + "/image/large"
        }
    return people


#turn one <speech> tag into a dict with name + text, or "" if empty :D
def parse_speech(speech, people):
    #grab every paragraph's text and join it into one block of text
    paragraphs = []
    for p in speech.findall(".//akn:p", ns):
        p_text = get_text(p)
        if p_text:
            paragraphs.append(p_text)
    text = " ".join(paragraphs)

    if not text:
        return None

    #figure out who said it, using the people dict if we can
    by = normalisename(speech.get("by", ""))
    by = by.replace("#", "")
    person = people.get(by)

    if person:
        name = person["name"]
    else:
        from_tag = speech.find("akn:from", ns)
        name = get_text(from_tag) if from_tag is not None else None

    return {
        "name": name,
        "membercode": person["membercode"] if person else None,
        "imageurl": person["imageURL"] if person else None,
        "speechtext": text
    }


#turn a whole debate xml file into a dict with a title + list of sections
def parse_debate_xml(xml_content, people):
    tree = etree.fromstring(xml_content)

    #title is in one of either block
    title_block = tree.find(".//akn:block[@name='committee_en']", ns) or tree.find(".//akn:block[@name='proponent_en']", ns)
    title = get_text(title_block)

    #go through every section and collect its speeches
    sections = []
    for sec in tree.findall(".//akn:debateSection", ns):
        heading = sec.find("akn:heading", ns)

        speeches = []
        for speech in sec.findall("akn:speech", ns):
            parsed = parse_speech(speech, people)
            if parsed is not None:
                speeches.append(parsed)

        #only keep sections that actually have speeches in them
        if speeches:
            sections.append({
                "title": get_text(heading),
                "speeches": speeches
            })

    return {"title": title, "sections": sections}


#changes membercodes to names
def codestonames(codes):
    names = []
    for code in codes.split("|"):
        name = code.split(".")[0]
        name = name.replace("-", " ")
        names.append(name)
    return " | ".join(names)

#gets membercodes from an obj
def getmembercodes(obj):
    codes = []
    seen = set()
    debatestuff = obj.get("debatestuff", {})
    for section in debatestuff.get("sections", []):
        for speech in section.get("speeches", []):
            code = speech.get("membercode")
            if code and code not in seen:
                seen.add(code)
                codes.append(code)
    return "|".join(codes)

#gets titles from json
def getsectiontitles(obj):
    titles = []
    debatestuff = obj.get("debatestuff", {})
    for section in debatestuff.get("sections", []):
        title = section.get("title")
        if title:
            titles.append(title)
    return "|".join(titles)

#uris of the debates already in the table
existing = {row[0] for row in cur.execute("SELECT json_extract(JSON, '$.debateRecord.uri') FROM debates")}

recordno = 0

#looks for records not in the database already
while True:
    url = "https://api.oireachtas.ie/v1/debates?skip=" + str(skip) + "&limit=1000"
    response = requests.get(url)
    response = response.json().get("results")
    if not response:
        break

    for b in response:
        debate = b["debateRecord"]

        #skip if the debate is already in the table
        if debate["uri"] in existing:
            print("Skipped. DebateNo: " + str(recordno))
            recordno += 1
            continue

        #if this debate has an xml version available, download and parse it
        xml_entry = debate.get("formats", {}).get("xml")
        if xml_entry:
            try:
                r = requests.get(xml_entry["uri"], timeout=10)
                people = getpeople(r.content)
                b["debatestuff"] = parse_debate_xml(r.content, people)
            except Exception as e:
                print(f"failed {xml_entry['uri']}: {e}")
                continue
            del r, people  # free the raw xml + people dict as soon as parsing is done
            time.sleep(0.1)

        print("[SQL STATEMENT INSERTED]. DebateNo: " + str(recordno))
        recordno += 1
        contextdate = b["contextDate"]
        membercodes = getmembercodes(b)
        titles = getsectiontitles(b)
        housecode = debate["house"]["houseCode"]
        debatetype = debate["debateType"]
        jsondump = json.dumps(b, ensure_ascii=False)
        namesofmembers = codestonames(membercodes) if membercodes else ""

        #add data to SQLite database
        cur.execute("""
            INSERT INTO debates (
            ContextDate, MemberCodes, DebateTitles,
            HouseCode, DebateType, NamesOfMembers, JSON
            )
            VALUES (?,?,?,?,?,?,?)
        """, (
            contextdate,
            membercodes,
            titles,
            housecode,
            debatetype,
            namesofmembers,
            jsondump
        ))
        b.pop("debatestuff", None)
        del jsondump

    conn.commit()
    if len(response) < 1000:
        break
    skip += 1000
    time.sleep(0.1)

conn.close()

print("done")