import os
import re
import sqlite3
import shutil
import time

# =============================================================================
#  BATCH DATABASE CREATOR
#  Uso: aggiungi i file .sql nella lista qui sotto, il resto è automatico.
#  Il nome del .sqlite viene derivato automaticamente dal nome del .sql.
# =============================================================================

sql_files = ['TRA_ITALY']

# Flags — disattiva singole fasi se necessario (normalmente tutti True)
Deleting      = True
Reading       = True
Preprocessing = True
Simplifying   = True

# Cartella di destinazione finale (dove legge runs_manager.py)
# Imposta None per disabilitare la copia automatica
OUTPUT_DIR = None  # es. "../data_files" oppure None

# =============================================================================

PREPROCESSING_SCRIPT = "database_preprocessing.py"
SIMPLIFIER_SCRIPT    = "database_simplifier.sql"

def separator(label):
    print()
    print("=" * 70)
    print(f"  {label}")
    print("=" * 70)

def run_pipeline(sql_file):
    """Esegue il pipeline completo per un singolo file .sql."""

    sqlite_database = sql_file.replace('.sql', '.sqlite')
    separator(f"Processing: {sql_file}  →  {sqlite_database}")
    start = time.time()

    # 1. Cancella il database esistente
    if Deleting:
        if os.path.exists(sqlite_database):
            os.remove(sqlite_database)
            print(f"  [DEL]  Database esistente cancellato.")

    # 2. Legge il .sql e crea il database
    if Reading:
        if not os.path.exists(sql_file):
            print(f"  [ERR]  File non trovato: {sql_file} — salto questo database.")
            return
        conn = sqlite3.connect(sqlite_database)
        with open(sql_file, mode='r', encoding='utf-8-sig') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print(f"  [OK ]  Database creato ed SQL eseguito.")

    # 3. Preprocessing — inietta il nome corretto del database dinamicamente
    if Preprocessing:
        if not os.path.exists(PREPROCESSING_SCRIPT):
            print(f"  [WARN] {PREPROCESSING_SCRIPT} non trovato — preprocessing saltato.")
        else:
            with open(PREPROCESSING_SCRIPT) as f:
                code = f.read()
            # Sostituisce il primo sqlite3.connect(...) con il database corretto,
            # qualunque nome sia hardcodato nello script originale.
            code = re.sub(
                r'sqlite3\.connect\(["\'][^"\']*["\']\)',
                f'sqlite3.connect("{sqlite_database}")',
                code,
                count=1
            )
            exec(code, {"__name__": "__preprocessing__"})
            print(f"  [OK ]  Preprocessing completato.")

    # 4. Simplifier
    if Simplifying:
        if not os.path.exists(SIMPLIFIER_SCRIPT):
            print(f"  [WARN] {SIMPLIFIER_SCRIPT} non trovato — simplifier saltato.")
        else:
            conn = sqlite3.connect(sqlite_database)
            with open(SIMPLIFIER_SCRIPT, mode='r', encoding='utf-8-sig') as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()
            print(f"  [OK ]  Database semplificato.")

    # 5. VACUUM finale
    conn = sqlite3.connect(sqlite_database)
    conn.execute("VACUUM")
    conn.close()

    # 6. Copia nella cartella di output (es. dove legge runs_manager.py)
    if OUTPUT_DIR is not None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        dest = os.path.join(OUTPUT_DIR, sqlite_database)
        shutil.copy(sqlite_database, dest)
        print(f"  [COPY] {sqlite_database} → {dest}")

    elapsed = time.time() - start
    print(f"  [DONE] {sqlite_database} completato in {elapsed:.1f}s")

# =============================================================================

if __name__ == "__main__":

    total_start = time.time()
    success, failed = [], []

    for sql in sql_files:
        try:
            run_pipeline(sql)
            success.append(sql)
        except Exception as e:
            print(f"\n  [ERR]  Errore su {sql}: {e}")
            failed.append(sql)

    # Riepilogo finale
    separator("RIEPILOGO")
    print(f"  Completati con successo : {len(success)}/{len(sql_files)}")
    for s in success:
        print(f"    ✓  {s.replace('.sql', '.sqlite')}")
    if failed:
        print(f"\n  Falliti ({len(failed)}):")
        for f in failed:
            print(f"    ✗  {f}")
    print(f"\n  Tempo totale: {time.time() - total_start:.1f}s")
    print()
