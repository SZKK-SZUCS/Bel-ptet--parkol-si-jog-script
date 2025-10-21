import json
from dataclasses import dataclass
from typing import List

@dataclass
class PersonRecord:
    kartya: str
    permissions: List[str]
    plates: List[str]

path = "parkolas.json"

def load_records(path: str) -> List[PersonRecord]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    records = []
    for rec in raw:
        kartya = rec.get("kartya", "")
        permissions = [val for key, val in rec.items()
                       if key.startswith("jog") and val]
        plates = [val for key, val in rec.items()
                  if key.lower().startswith("rendszam") and val]
        records.append(PersonRecord(kartya, permissions, plates))
    return records

persons = load_records("parkolas.json")
