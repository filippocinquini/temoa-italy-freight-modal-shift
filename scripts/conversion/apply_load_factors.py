import re
import os

factors = {
    'TRA_ROA_HTR_D5': 16.59600,
    'TRA_RAIL_FRG': 392.8367,
    'TRA_NAV_DOM': 2119.3604
}

techs = {
    'TRA_ROA_HTR_BIO_E_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_DST_E_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_DST_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_ELC_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_FCELL_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_FULHYB_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_LPG_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_NGA_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_ROA_HTR_PHEV_N_D5': factors['TRA_ROA_HTR_D5'],
    'TRA_RAIL_FRG_E': factors['TRA_RAIL_FRG'],
    'TRA_RAIL_FRG_DST_N': factors['TRA_RAIL_FRG'],
    'TRA_RAIL_FRG_ELC_N': factors['TRA_RAIL_FRG'],
    'TRA_RAIL_FRG_H2G_MNL_N': factors['TRA_RAIL_FRG'],
    'TRA_NAV_DOM_E': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_DST_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_HFO_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_LNG_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_DUAL_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_AMM_ICE_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_MET_ICE_N': factors['TRA_NAV_DOM'],
    'TRA_NAV_DOM_H2L_ICE_N': factors['TRA_NAV_DOM']
}

def parse_val(s):
    try:
        return float(s)
    except:
        return s

def format_val(f):
    if isinstance(f, float):
        if abs(f) > 1000 or abs(f) < 0.001:
            return "{:.4e}".format(f)
        return "{:.5g}".format(f)
    return str(f)

def process_file(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out_lines = []
    for line in lines:
        if not line.startswith("INSERT INTO"):
            out_lines.append(line)
            continue
            
        match = re.match(r'(INSERT INTO "[^"]+" VALUES \()(.+)(\);)', line)
        if not match:
            out_lines.append(line)
            continue
            
        prefix, content, suffix = match.groups()
        # Splitting keeping string quotes intact
        parts = []
        in_quote = False
        curr = ""
        for c in content:
            if c == "'":
                in_quote = not in_quote
                curr += c
            elif c == ',' and not in_quote:
                parts.append(curr)
                curr = ""
            else:
                curr += c
        if curr:
            parts.append(curr)
            
        table_match = re.search(r'INSERT INTO "([^"]+)"', line)
        table = table_match.group(1)
        
        modified = False
        
        # Clean quotes for comparison
        clean_parts = [p.strip("'") for p in parts]
        
        if table == "Demand":
            comm = clean_parts[2]
            if comm in factors:
                val = float(clean_parts[3]) * factors[comm]
                parts[3] = str(round(val, 6))
                if 'Bvkm' in clean_parts[4]: parts[4] = parts[4].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table == "Efficiency":
            out_comm = clean_parts[4]
            if out_comm in factors:
                val = float(clean_parts[5]) * factors[out_comm]
                parts[5] = str(round(val, 6))
                if 'Bvkm' in clean_parts[6]: parts[6] = parts[6].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table in ["ExistingCapacity", "MaxCapacity", "MinCapacity"]:
            tech = clean_parts[1]
            if tech in techs:
                val = float(clean_parts[3]) * techs[tech]
                parts[3] = str(round(val, 6))
                if 'Bvkm' in clean_parts[4]: parts[4] = parts[4].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table in ["MaxActivity", "MinActivity"]:
            # MaxActivity = (regions, periods, tech, activity, activity_notes)
            tech = clean_parts[2]
            if tech in techs:
                val = float(clean_parts[3]) * techs[tech]
                parts[3] = str(round(val, 6))
                if len(clean_parts) > 4 and 'Bvkm' in clean_parts[4]: 
                    parts[4] = parts[4].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table == "CostInvest":
            # ('IT','TRA_RAIL_FRG_DST_N',2007,22999.9978,'M€/Bvkm','Assumption')
            tech = clean_parts[1]
            if tech in techs:
                val = float(clean_parts[3]) / techs[tech]
                parts[3] = str(round(val, 6))
                if 'Bvkm' in clean_parts[4]: parts[4] = parts[4].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table == "CostFixed":
            # ('IT',2007,'TRA_MS_TRD5_RAIL',2007,0.4762,'M€/Gtkm','10% O&M')
            tech = clean_parts[2]
            if tech in techs:
                val = float(clean_parts[4]) / techs[tech]
                parts[4] = str(round(val, 6))
                if 'Bvkm' in clean_parts[5]: parts[5] = parts[5].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table == "CostVariable":
            # ('IT',2007,'TRA_MS_TRD5_RAIL',2007,0.0,'M€/Gtkm','')
            tech = clean_parts[2]
            if tech in techs:
                val = float(clean_parts[4]) / techs[tech]
                parts[4] = str(round(val, 6))
                if 'Bvkm' in clean_parts[5]: parts[5] = parts[5].replace('Bvkm', 'Gtkm')
                modified = True
                
        elif table == "EmissionActivity":
            # ('IT','CO2','TRA_ROA_HTR_DST_N_D5',2007,178.6015,'kt/Bvkm','...')
            # Notice the actual columns: regions, emis_comm, input_comm, tech, vintage, emis_act, emis_units
            tech = clean_parts[3]
            if tech in techs:
                val = float(clean_parts[5]) / techs[tech]
                parts[5] = str(round(val, 6))
                if 'Bvkm' in clean_parts[6]: parts[6] = parts[6].replace('Bvkm', 'Gtkm')
                modified = True
        
        if modified:
            out_lines.append(f"{prefix}{','.join(parts)}{suffix}\n")
        else:
            out_lines.append(line)
            
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
    print(f"Processed {in_path} -> {out_path}")

process_file("TRA_MS_OFF_BAU.sql", "TRA_MS_ON_BAU.sql")
process_file("TRA_MS_OFF_NT0.sql", "TRA_MS_ON_NT0.sql")

# Manual steps:
def apply_modal_shift_changes(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update commodities to 'p'
    content = content.replace("INSERT INTO \"commodities\" VALUES ('TRA_ROA_HTR_D5','d'", "INSERT INTO \"commodities\" VALUES ('TRA_ROA_HTR_D5','p'")
    content = content.replace("INSERT INTO \"commodities\" VALUES ('TRA_RAIL_FRG','d'", "INSERT INTO \"commodities\" VALUES ('TRA_RAIL_FRG','p'")
    content = content.replace("INSERT INTO \"commodities\" VALUES ('TRA_NAV_DOM','d'", "INSERT INTO \"commodities\" VALUES ('TRA_NAV_DOM','p'")
    
    # 2. Comment out Demands
    content = re.sub(r'(INSERT INTO "Demand" VALUES \(\'IT\',[0-9]+,\'TRA_ROA_HTR_D5\')', r'--\1', content)
    content = re.sub(r'(INSERT INTO "Demand" VALUES \(\'IT\',[0-9]+,\'TRA_RAIL_FRG\')', r'--\1', content)
    content = re.sub(r'(INSERT INTO "Demand" VALUES \(\'IT\',[0-9]+,\'TRA_NAV_DOM\')', r'--\1', content)
    
    # 3. Comment out DMY_DEM_ANNUAL
    content = re.sub(r'(INSERT INTO "Efficiency" VALUES \(\'IT\',\'ethos\',\'DMY_DEM_ANNUAL\',[0-9]+,\'TRA_ROA_HTR_D5\')', r'--\1', content)
    content = re.sub(r'(INSERT INTO "Efficiency" VALUES \(\'IT\',\'ethos\',\'DMY_DEM_ANNUAL\',[0-9]+,\'TRA_RAIL_FRG\')', r'--\1', content)
    content = re.sub(r'(INSERT INTO "Efficiency" VALUES \(\'IT\',\'ethos\',\'DMY_DEM_ANNUAL\',[0-9]+,\'TRA_NAV_DOM\')', r'--\1', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    # 4. Append Modal Shift
    with open('../../../Desktop/database progetto/Modal_shift/TRA_MODAL_SHIFT_FINAL.sql', 'r') as m:
        modal_shift = m.read()
        
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n\n-- ==========================================\n")
        f.write("-- MODAL SHIFT IMPLEMENTATION\n")
        f.write("-- ==========================================\n")
        f.write(modal_shift)
        
apply_modal_shift_changes("TRA_MS_ON_BAU.sql")
apply_modal_shift_changes("TRA_MS_ON_NT0.sql")
print("Modal shift changes appended.")
