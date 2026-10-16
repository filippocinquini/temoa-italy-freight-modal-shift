#!/usr/bin/env python3
"""
Divide per 16.596 tutti i valori numerici di CostInvest e CostFixed
per le righe attive (non commentate) che contengono HTR.*D5 come tech.

Logica:
  - Riga attiva:  inizia con "INSERT INTO"
  - Tabella:      "CostInvest" o "CostFixed"
  - Tech (campo): contiene 'HTR' e 'D5'
  - Per CostFixed: divide SEMPRE il valore numerico
  - Per CostInvest: divide SEMPRE il valore numerico
  
Il valore da dividere è il 4° campo per CostInvest  (region, tech, vintage, cost, unit, note)
                          il 5° campo per CostFixed  (region, period, tech, vintage, cost, unit, note)

Lo script fa backup del file originale come .bak, poi sovrascrive in-place.
"""

import re
import shutil
from pathlib import Path

SQL_FILE = Path(__file__).parent / "TRA_MS_ON_BAU.sql"
DIVISOR = 16.596

# Pattern per estrarre il contenuto VALUES (...) di una INSERT
# Cattura il nome della tabella e i valori tra parentesi
INSERT_RE = re.compile(
    r'^(INSERT\s+INTO\s+"(CostInvest|CostFixed)"\s+VALUES\s*\()(.+)(\);.*)$',
    re.IGNORECASE
)

def parse_values(values_str: str) -> list[str]:
    """Divide la stringa di valori SQL rispettando le virgole dentro stringhe."""
    tokens = []
    current = []
    in_string = False
    for ch in values_str:
        if ch == "'" and not in_string:
            in_string = True
            current.append(ch)
        elif ch == "'" and in_string:
            in_string = False
            current.append(ch)
        elif ch == ',' and not in_string:
            tokens.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        tokens.append(''.join(current).strip())
    return tokens

def format_number(value: float) -> str:
    """Formatta il numero mantenendo una precisione ragionevole."""
    # Usa repr per evitare notazione scientifica inutile,
    # poi tronca a max 6 cifre significative
    formatted = f"{value:.6g}"
    return formatted

def process_line(line: str) -> tuple[str, bool]:
    """
    Restituisce (nuova_riga, modificata).
    Se la riga non deve essere modificata, restituisce (line, False).
    """
    # Salta commenti
    stripped = line.strip()
    if stripped.startswith('--'):
        return line, False

    m = INSERT_RE.match(stripped)
    if not m:
        return line, False

    prefix   = m.group(1)   # INSERT INTO "CostXxx" VALUES (
    table    = m.group(2)   # CostInvest | CostFixed
    vals_str = m.group(3)   # i valori separati da virgola
    suffix   = m.group(4)   # );

    tokens = parse_values(vals_str)

    # Verifica che il tech contenga HTR e D5
    # CostInvest: (region, tech, vintage, cost, unit, notes)  -> tech = token[1]
    # CostFixed:  (region, period, tech, vintage, cost, unit, notes) -> tech = token[2]
    if table.lower() == 'costinvest':
        tech_idx  = 1
        cost_idx  = 3
    else:  # costfixed
        tech_idx  = 2
        cost_idx  = 4

    if len(tokens) <= cost_idx:
        return line, False

    tech_token = tokens[tech_idx].strip("'")
    if 'HTR' not in tech_token or 'D5' not in tech_token:
        return line, False

    # Dividi il valore
    cost_str = tokens[cost_idx]
    try:
        cost_val = float(cost_str)
    except ValueError:
        return line, False

    new_cost = cost_val / DIVISOR
    tokens[cost_idx] = format_number(new_cost)

    new_vals = ','.join(tokens)
    # Ricostruisci la riga originale (con la stessa indentazione)
    indent = line[: len(line) - len(line.lstrip())]
    new_line = f"{indent}{prefix}{new_vals}{suffix}\n"
    return new_line, True

def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"File non trovato: {SQL_FILE}")

    # Backup
    backup = SQL_FILE.with_suffix('.sql.bak')
    shutil.copy2(SQL_FILE, backup)
    print(f"Backup creato: {backup}")

    lines = SQL_FILE.read_text(encoding='utf-8').splitlines(keepends=True)

    modified_count = 0
    new_lines = []
    for i, line in enumerate(lines, start=1):
        new_line, changed = process_line(line)
        new_lines.append(new_line)
        if changed:
            modified_count += 1
            # Log per verifica
            orig_val = line.strip()
            new_val  = new_line.strip()
            print(f"  L{i}: {orig_val}")
            print(f"    → {new_val}")

    SQL_FILE.write_text(''.join(new_lines), encoding='utf-8')
    print(f"\nTotale righe modificate: {modified_count}")
    print(f"File aggiornato: {SQL_FILE}")

if __name__ == '__main__':
    main()
