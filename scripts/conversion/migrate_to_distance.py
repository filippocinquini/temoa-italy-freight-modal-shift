#!/usr/bin/env python3
"""
migrate_to_distance.py
======================
Sostituisce nel file TRA_MODAL_Italy.sql ogni riga che referenzia le tecnologie
TRA_ROA_LCV/MTR/HTR (senza suffisso _D1-D5) con le corrispondenti righe
distance-based estratte da TRA_MODAL.sql.

Strategia:
1. Identifica le righe in TRA_MODAL_Italy.sql che contengono nomi tecnologia
   senza _D1-D5 (es. TRA_ROA_HTR_DST_N).
2. Per ciascuna, estrae le righe D1-D5 da TRA_MODAL.sql (sia attive che commentate).
3. Gestione speciale per:
   - MaxActivity: distribuisce il valore con le quote proporzionali da ExistingCapacity
   - CurrencyTech: espande in 5 righe con lo stesso valore valuta
   - PLGHYB_N: non esistono D1-D5 → mantieni la riga originale (già commentata)
4. Le righe commodity (TRA_ROA_LCV/HTR/MTR senza suffisso tipo motore) e i
   riferimenti ai gruppi (_GRP) vengono lasciati intatti.
5. Allocation, Elasticity, MaxInputGroup usano nomi commodity/gruppo → intatti.
6. Salva il risultato in TRA_MODAL_Italy_migrated.sql.
"""

import re
import sys
from pathlib import Path

# ─── Configurazione ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
ITALY_FILE   = BASE_DIR / "TRA_MODAL_Italy.sql"
MODAL_FILE   = BASE_DIR / "TRA_MODAL.sql"
OUTPUT_FILE  = BASE_DIR / "TRA_MODAL_Italy_migrated.sql"

# Pattern per riconoscere un nome tecnologia LCV/MTR/HTR SENZA suffisso _D1-D5
# Il pattern cattura tutta la parte dopo TRA_ROA_ incluso il tipo motore
# Trova tecnologie CON suffisso _D1-D5 (per indicizzare MODAL)
TECH_D_RE = re.compile(
    r"'(TRA_ROA_(?:LCV|MTR|HTR)_[A-Z0-9]+_[A-Z]_D[1-5])'"
)
# Trova tecnologie SENZA suffisso _D1-D5 (per individuare le righe da sostituire in Italy)
TECH_IN_LINE_RE = re.compile(
    r"'(TRA_ROA_(?:LCV|MTR|HTR)_[A-Z0-9]+_[A-Z])(?!_D[1-5])'"
)

# Pattern per riconoscere se è già una versione _D1-D5
DISTANCE_SUFFIX = re.compile(r"_D[1-5]$")

# Nomi commodity/gruppo che vanno ignorati (non sono nomi tecnologia)
COMMODITY_NAMES = {"TRA_ROA_LCV", "TRA_ROA_HTR", "TRA_ROA_MTR"}
GROUP_NAMES_RE  = re.compile(r"TRA_ROA_(?:LCV|MTR|HTR)_GRP")

TABLE_RE = re.compile(r'INSERT INTO "([^"]+)"')

# ─── Quote D1-D5 da italy_freight_ROAD_MASTER.xlsx foglio 17_ExistingCap_Split ─
# Fonte: quota vkm (derivata da tkm con load factors per classe distanza)
# HTR_BIO_E usa le stesse quote MTR (nota Excel: "Da chiarire con prof: refuso label")
VKM_SHARES: dict[str, dict[int, float]] = {
    "TRA_ROA_LCV_DST_E": {1: 0.4081554008022293, 2: 0.3204641275542650, 3: 0.1828240086566736, 4: 0.0567687208276378, 5: 0.0317877421591944},
    "TRA_ROA_LCV_GSL_E": {1: 0.4081554008022293, 2: 0.3204641275542650, 3: 0.1828240086566736, 4: 0.0567687208276378, 5: 0.0317877421591944},
    "TRA_ROA_LCV_BIO_E": {1: 0.4081554008022293, 2: 0.3204641275542650, 3: 0.1828240086566736, 4: 0.0567687208276378, 5: 0.0317877421591944},
    "TRA_ROA_MTR_DST_E": {1: 0.1748793759113241, 2: 0.2605095365472568, 3: 0.2591031940658424, 4: 0.1615312819534907, 5: 0.1439766115220860},
    "TRA_ROA_HTR_DST_E": {1: 0.0670296172844788, 2: 0.1914941655742184, 3: 0.2679244272420917, 4: 0.1838383215918703, 5: 0.2897134683073408},
    "TRA_ROA_HTR_BIO_E": {1: 0.1748793759113241, 2: 0.2605095365472568, 3: 0.2591031940658424, 4: 0.1615312819534907, 5: 0.1439766115220860},  # usa quote MTR (vedi nota Excel)
}

# ─── Lettura file ──────────────────────────────────────────────────────────────
print(f"Lettura {ITALY_FILE} ...")
with open(ITALY_FILE, "r", encoding="utf-8") as f:
    italy_lines = f.readlines()

print(f"Lettura {MODAL_FILE} ...")
with open(MODAL_FILE, "r", encoding="utf-8") as f:
    modal_lines = f.readlines()

# ─── Indicizzazione TRA_MODAL.sql ──────────────────────────────────────────────
# Costruisce: table_name -> { base_tech_name -> [riga_d1, riga_d2, ...] }
# Include anche le righe COMMENTATE (per es. CostVariable ELC_N)
print("Indicizzazione righe distance-based da TRA_MODAL.sql ...")

modal_index: dict[str, dict[str, list[str]]] = {}

for line in modal_lines:
    stripped = line.strip()
    
    # Considera sia righe INSERT attive che commentate (--INSERT)
    active_part = stripped
    if stripped.startswith("--"):
        active_part = stripped.lstrip("--").strip()
    
    if not active_part.startswith("INSERT"):
        continue

    table_match = TABLE_RE.search(active_part)
    if not table_match:
        continue
    table = table_match.group(1)

    # Usa TECH_D_RE per trovare tecnologie con suffisso _D[1-5]
    techs_in_line = TECH_D_RE.findall(active_part)
    for tech in techs_in_line:
        # Ricaviamo il nome base rimuovendo _D[1-5]
        base = DISTANCE_SUFFIX.sub("", tech)

        if table not in modal_index:
            modal_index[table] = {}
        if base not in modal_index[table]:
            modal_index[table][base] = []
        modal_index[table][base].append(line)

print(f"  Trovate {sum(len(v) for vv in modal_index.values() for v in vv.values())} righe distance-based")
print(f"  Tabelle indicizzate: {sorted(modal_index.keys())}")

# ─── Funzione: la riga contiene una tecnologia da migrare? ────────────────────
def get_tech_to_replace(line: str) -> str | None:
    """
    Ritorna il nome base della tecnologia (es. TRA_ROA_HTR_DST_N)
    se la riga contiene un riferimento a una tecnologia LCV/MTR/HTR
    senza suffisso _D1-D5; altrimenti None.
    """
    techs = TECH_IN_LINE_RE.findall(line)
    for tech in techs:
        # Salta se è già distance-based
        if DISTANCE_SUFFIX.search(tech):
            return None
        # Salta commodity pure
        if tech in COMMODITY_NAMES:
            return None
        # Salta nomi gruppo
        if GROUP_NAMES_RE.search(tech):
            return None
        # È una tecnologia base senza _D1-D5
        return tech
    return None

def get_table_from_line(line: str) -> str | None:
    m = TABLE_RE.search(line)
    return m.group(1) if m else None

# ─── Generazione righe MaxActivity D1-D5 ─────────────────────────────────────
# Pattern per estrarre i valori dalla riga MaxActivity
MAXACT_RE = re.compile(
    r"INSERT INTO \"MaxActivity\" VALUES \('([^']+)',(\d+),'([^']+)',([^,]+),'([^']+)','([^']*)'\);"
)

def generate_maxactivity_rows(line: str, tech: str) -> list[str] | None:
    """
    Genera 5 righe MaxActivity D1-D5 dalla riga originale.
    Per valore = 0.0 → tutte le D a 0.0
    Per valore ≠ 0 → distribuisce con le quote VKM_SHARES
    """
    m = MAXACT_RE.search(line.strip())
    if not m:
        return None
    
    region, period, orig_tech, value_str, units, notes = m.groups()
    
    try:
        value = float(value_str)
    except ValueError:
        return None
    
    result_lines = []
    eol = "\r\n" if "\r\n" in line else "\n"
    
    if value == 0.0:
        # Tutte le classi a zero
        for d in range(1, 6):
            new_tech = f"{tech}_D{d}"
            row = f"INSERT INTO \"MaxActivity\" VALUES ('{region}',{period},'{new_tech}',0.0,'{units}','');{eol}"
            result_lines.append(row)
    else:
        # Distribuisci con le quote VKM_SHARES
        if tech not in VKM_SHARES:
            # Fallback: quota uniforme
            shares = {d: 0.2 for d in range(1, 6)}
        else:
            shares = VKM_SHARES[tech]
        
        for d in range(1, 6):
            new_tech = f"{tech}_D{d}"
            new_val = value * shares[d]
            row = f"INSERT INTO \"MaxActivity\" VALUES ('{region}',{period},'{new_tech}',{new_val:.4E},'{units}','split via vkm shares from {tech}');{eol}"
            result_lines.append(row)
    
    return result_lines

# ─── Generazione righe CurrencyTech D1-D5 ─────────────────────────────────────
CURRENCY_RE = re.compile(
    r"INSERT INTO \"CurrencyTech\" VALUES \('([^']+)','([^']+)'\);"
)

def generate_currencytech_rows(line: str, tech: str) -> list[str] | None:
    """
    Genera 5 righe CurrencyTech _D1-D5 dalla riga originale.
    Il codice valuta è lo stesso per tutte le classi.
    """
    m = CURRENCY_RE.search(line.strip())
    if not m:
        return None
    
    orig_tech, currency = m.groups()
    eol = "\r\n" if "\r\n" in line else "\n"
    
    result_lines = []
    for d in range(1, 6):
        new_tech = f"{tech}_D{d}"
        row = f"INSERT INTO \"CurrencyTech\" VALUES ('{new_tech}','{currency}');{eol}"
        result_lines.append(row)
    
    return result_lines

# ─── Sostituzione ─────────────────────────────────────────────────────────────
print("Elaborazione righe TRA_MODAL_Italy.sql ...")

output_lines: list[str] = []
replaced_count = 0
not_found_count = 0
not_found_list: list[tuple[str, str, int]] = []
special_handled: list[tuple[str, str, int]] = []

i = 0
while i < len(italy_lines):
    line = italy_lines[i]
    stripped = line.strip()

    # Determina se la riga è commentata
    is_commented = stripped.startswith("--")
    active_line = stripped.lstrip("--").strip() if is_commented else stripped

    # Cerca tecnologie da migrare nella riga attiva
    tech = get_tech_to_replace(active_line)

    if tech is None:
        output_lines.append(line)
        i += 1
        continue

    # Troviamo la tabella
    table = get_table_from_line(active_line)

    # ─── Gestione speciale MaxActivity ───────────────────────────────────────
    if table == "MaxActivity" and not is_commented:
        new_rows = generate_maxactivity_rows(line, tech)
        if new_rows:
            output_lines.extend(new_rows)
            replaced_count += 1
            special_handled.append((table, tech, i + 1))
            i += 1
            continue

    # ─── Gestione speciale CurrencyTech ──────────────────────────────────────
    if table == "CurrencyTech" and not is_commented:
        new_rows = generate_currencytech_rows(line, tech)
        if new_rows:
            output_lines.extend(new_rows)
            replaced_count += 1
            special_handled.append((table, tech, i + 1))
            i += 1
            continue

    # ─── Ricerca in modal_index (include righe commentate in MODAL) ──────────
    replacement_lines = None
    if table and table in modal_index and tech in modal_index[table]:
        replacement_lines = modal_index[table][tech]

    if replacement_lines is None:
        # Non trovato → mantieni la riga originale con avviso
        not_found_count += 1
        not_found_list.append((table or "?", tech, i + 1))
        output_lines.append(line)
        i += 1
        continue

    # Sostituiamo la riga con le righe D1-D5
    # Se la riga originale era commentata, commentiamo anche le nuove
    if is_commented:
        for r in replacement_lines:
            r_stripped = r.strip()
            if r_stripped.startswith("--"):
                output_lines.append(r)
            else:
                eol = "\r\n" if "\r\n" in r else "\n"
                output_lines.append("--" + r.rstrip() + eol)
    else:
        # Le righe provenienti da MODAL possono essere commentate (es. CostVariable ELC_N)
        # Se la riga in Italy era ATTIVA ma in MODAL era commentata → rendiamo ATTIVE
        for r in replacement_lines:
            r_stripped = r.strip()
            if r_stripped.startswith("--"):
                # Rimuoviamo il commento
                uncommented = r_stripped.lstrip("--").strip()
                eol = "\r\n" if "\r\n" in r else "\n"
                output_lines.append(uncommented + eol)
            else:
                output_lines.append(r)

    replaced_count += 1
    i += 1

# ─── Scrittura output ─────────────────────────────────────────────────────────
print(f"\nScrittura {OUTPUT_FILE} ...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output_lines)

# ─── Report ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"REPORT MIGRAZIONE")
print(f"{'='*60}")
print(f"  Righe nel file originale  : {len(italy_lines)}")
print(f"  Righe nel file output     : {len(output_lines)}")
print(f"  Sostituzioni totali       : {replaced_count}")
print(f"  - di cui speciali         : {len(special_handled)}  (MaxActivity/CurrencyTech)")
print(f"  Righe non trovate (warn)  : {not_found_count}")

if special_handled:
    from collections import Counter
    cnt = Counter(t for t, _, _ in special_handled)
    print(f"\n  Gestioni speciali per tabella:")
    for tbl, c in sorted(cnt.items()):
        print(f"    {tbl:30s}: {c} righe")

if not_found_list:
    print(f"\n  Dettaglio righe NON trovate in TRA_MODAL.sql:")
    from collections import Counter
    cnt = Counter(t for t, _, _ in not_found_list)
    for tbl, c in sorted(cnt.items()):
        print(f"    {tbl:30s}: {c} righe")
    print()
    for table, tech, lineno in not_found_list:
        print(f"    Riga {lineno:5d}  tabella={table:30s}  tech={tech}")

print(f"\nFile salvato in: {OUTPUT_FILE}")
print("FATTO!")
