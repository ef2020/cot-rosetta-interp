# Corpus notes: UKLO puzzles with proper names, places, and dates

Scan of the full 347-PDF scrape (2026-10-16) for puzzles whose *data* (not
intro prose) contains personal names, place names, or dates — relevant to
the fact-layer decision in PROJECT.md (Blum-style entity/attribute frames).
Method: pdftotext over `gs://cot-rosetta-interp-data/raw/uklo_pdf/`,
heuristic scoring (name/place gazetteers, year/month/weekday patterns,
boilerplate filtering), manual verification of every listed hit.

## A. Personal names as arguments inside sentence data
(grammar applies to the names — closest to Blum-style fact frames)

| Puzzle | Names in data | Frame type |
|---|---|---|
| **2018 R2 P4 Mixtec** | Maria, Pedro, Juan | copular kinship facts: "Pedro is my child", "Juan is my husband" |
| **2024 R1 P5 Tariana** | Antônia, Cândido, Margarida, João, Maria, Emílio, Ismael | evidential statements about a named person ("Ismael drank manioc-flour" + evidence source) |
| **2018 P7 Icelandic** | Björk, Einar, Gunnar, Alda, Henrika, Gúðrun, Egill | family tree + kinship sentences with **names inflected** (gen. *Gúðrunur*, *Egills*) |
| **Manam (2026-03 upload)** | Sagido, 'Unwage, Bobong, ... | family tree; kinship possession, fill in names |

## B. Personal names as phonological material (script puzzles)

| Puzzle | Names |
|---|---|
| **2017 P2 Inuktitut** | Sarah, Sam, Anna, Tom, ... in syllabics |
| **2011 P7 English Braille / New York Point** | Ashley, Barb, Carl, Dave, Elena, Fred, Gerald, Heather, Ivan, Jack, Kathy, Lisa |
| 2015 P5 Runes | Thor, Odin (deity names; minor) |

## C. City / country names in data (script or matching tasks)

| Puzzle | Places |
|---|---|
| **2024 R1 P7 Kannada** | Paris, London, Budapest, Prague in Kannada script |
| **2025 R1 P5 Armenian** | Australia, America, Russia, Germany, Italy, Bulgaria in Armenian script |
| **2025 R1 P1 Devanagari** | IPL team names = Indian cities (Gujarat, Delhi, Mumbai, ...) |

## D. Dates and years: effectively ABSENT

No puzzle found with event dates/years inside the data. Closest: **2019 P2
Japanese** has weekday *lexemes* (kanji compounds: 月曜日 'Monday',
火曜日 'Tuesday'); number-system puzzles could *render* years as numerals
but none states dated facts. False positives everywhere else (competition
headers, reference lists, intro history).

## Implications for Project 5 / the Blum bridge

1. UKLO supplies **people and places, not dates**. A Blum-style
   birth-year/birth-city fact layer cannot be sourced from puzzles; it must
   be synthesized and verbalized *through* certified grammars (as PROJECT.md
   §3 already plans). The name-bearing puzzles above show this is
   naturalistic: UKLO authors themselves embed personal names in kinship /
   copular / evidential frames.
2. The four §A puzzles are the priority candidates for adding a *named-entity
   concept* column to the design matrix (how names inflect: Icelandic
   genitive on names is a certified rule target in its own right).
3. The §B/§C script puzzles are not Rosetta-format (no grammar to certify)
   but are ready-made **transliteration anchors** for entity sharing across
   scripts — useful for the extractability manipulation (same entity, Latin
   vs. Kannada vs. Armenian surface forms).
