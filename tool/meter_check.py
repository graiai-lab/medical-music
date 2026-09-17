"""Check a lyrics/*.md against the locked meter: 8-6-8-6 syllables per verse.

    python3 tool/meter_check.py lyrics/gut_liver.md

Counts syllables per line with a rule-based counter plus an override table
for drug names and respellings (the counter is a heuristic; the override
table is the record of what we intend Suno to sing). Prints every line
with its count and flags any that miss 8 or 6. Stress is not checked here;
that stays a by-ear job.
"""
import re
import sys
from pathlib import Path

# case-insensitive lookup; keys lower-case. Counts are how the word is SUNG.
OVERRIDE = {
    "doxorubicin": 5, "two-fifty": 3, "decades": 2, "modern": 2, "e.f.": 2,
    "trastuzumab": 4, "deruxtecan": 4, "carfilzomib": 4, "ibrutinib": 4,
    "capecitabine": 5, "five-f.u.": 3, "nilotinib": 4, "osimertinib": 5,
    "ondansetron": 4, "sunitinib": 4, "sorafenib": 4, "lenvatinib": 4,
    "bevacizumab": 5, "ponatinib": 4, "dasatinib": 4, "ipi-nivo": 4,
    "e.k.g.": 3, "q.t.": 2, "b.n.p.": 3, "m.i.": 2, "tor-sahds": 2,
    "blee-oh-my-sin": 4, "ev-er-oh-li-mus": 5, "tem-sir-oh-li-mus": 5, "em-tor": 2,
    "gem-site-uh-bean": 4, "methotrexate": 4, "pembro": 2, "nivo": 2, "ipi": 2,
    "ah-tez-oh": 3, "durva": 2, "r.t.": 2, "i.l.d.": 3, "her2": 2, "byoo-sul-fan": 3,
    "p.f.t.": 3, "hypersensitivity": 6, "eosinophils": 5, "fluid": 2, "lasix": 2,
    "irinotecan": 5, "vedolizumab": 5, "infliximab": 4, "loperamide": 4, "atropine": 3,
    "defibrotide": 4, "inotuzumab": 5, "gemtuzumab": 4, "asparaginase": 5,
    "c. diff": 2, "c.diff": 2, "cmv": 3, "c.m.v.": 3, "d.p.d.": 3, "colitis": 3,
    "hepatitis": 4, "pancreatitis": 5, "typhlitis": 3, "bilirubin": 4, "cytarabine": 4,
    "mucositis": 4, "neutropenic": 4, "cyclophosphamide": 5, "busulfan": 3,
    "olfactory": 4, "cribriform": 3, "cribriform's": 3, "optic": 2, "canal's": 2, "canal": 2,
    "pupil": 2, "oculomotor": 5, "fissure": 2, "pupils": 2, "trochlear": 3, "trigeminal": 4,
    "rotundum": 3, "ovale": 3, "abducens": 3, "stylomastoid's": 4, "stylomastoid": 4,
    "forehead": 2, "forehead's": 2, "meatus": 3, "glossopharyngeal": 6, "jugular": 3,
    "vagus": 2, "uvula": 3, "accessory": 4, "eleven": 3, "trapezius": 4, "hypoglossal": 4,
    "lesion": 2, "toward": 2, "seventh": 2, "facial": 2, "eye": 1, "eyed": 1,
    "comes": 1, "the": 1, "every": 3, "fire": 1, "hour": 1, "our": 1, "spasm": 2, "rhythm": 2,
    "arsenic": 3, "myeloma": 4, "hundred": 2, "prior": 2, "cultures": 2, "hypersensitivity": 7,
    "ipilimumab": 5, "nivolumab": 4, "mycophenolate": 5, "uridine": 3, "triacetate": 4,
    "antidote": 3, "colonoscope": 4, "antibiotics": 5, "pancreas": 3, "thrombosis": 3,
    "typhlitis": 3, "neutrophils": 3, "sagittal": 3, "diarrhea": 4, "lipase": 2,
    "bili": 2, "steroids": 2, "steroid": 2, "biopsy": 3, "fever": 2, "atropine": 3,
    "sinus": 2, "headache's": 2, "imaged": 2, "given": 2, "liver's": 2, "jaundice": 2,
}


def syllables(word):
    w = word.lower().strip(",;:!?—\"'()")
    if re.fullmatch(r"(?:[a-z]\.)+'?s?", w):       # spelled abbreviation E.F. / D.P.D.'s
        return len(re.findall(r"[a-z]\.", w))
    w = w.strip(".")
    if w in OVERRIDE:
        return OVERRIDE[w]
    if "-" in w:
        return sum(syllables(p) for p in w.split("-"))
    groups = len(re.findall(r"[aeiouy]+", w))
    # silent final e, except consonant+le (table) and ee/ye; vowel+le (rule) is silent
    if w.endswith("e") and not (re.search(r"[^aeiou]le$", w) or w.endswith(("ee", "ye"))) and groups > 1:
        groups -= 1
    if w.endswith("ed") and not w.endswith(("ted", "ded", "red")) and groups > 1:
        groups -= 1
    return max(1, groups)


path = Path(sys.argv[1])
in_verse, verse, li, bad = False, 0, 0, 0
for raw in path.read_text().splitlines():
    s = raw.strip()
    if s.startswith("[Verse"):
        in_verse, li = True, 0; verse += 1; print(s, flush=True); continue
    if not s:
        in_verse = False; continue
    if not in_verse:
        continue
    want = 8 if li % 2 == 0 else 6
    n = sum(syllables(w) for w in s.split() if w != "—")
    flag = "" if n == want else f"   <-- want {want}"
    if flag: bad += 1
    print(f"  {n}  {s}{flag}", flush=True)
    li += 1
print(f"{verse} verses, {bad} lines off meter", flush=True)
