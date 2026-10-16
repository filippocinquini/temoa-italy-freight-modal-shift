import re

file_path = "TRA_MS_ON_BAU.sql"

with open(file_path, "r") as f:
    lines = f.readlines()

new_lines = []
modified_maxactivity = 0
modified_existcap = 0

for line in lines:
    if line.startswith('INSERT INTO "MaxActivity"'):
        # INSERT INTO "MaxActivity" VALUES ('IT',2007,'TRA_ROA_HTR_BIO_E_D5',1.3980E-04,'Bvkm','92.86%...');
        # The regex:
        # group(1): INSERT INTO "MaxActivity" VALUES ('IT',2007,'TRA_ROA_HTR_BIO_E_D5',
        # group(2): TRA_ROA_HTR_BIO_E_D5
        # group(3): 1.3980E-04
        # group(4): Bvkm
        # group(5): ,'92.86%...');
        
        match = re.match(r'(INSERT INTO "MaxActivity" VALUES \([^,]+,[^,]+,\'([^\']+)\',)([^,]+),\'([^\']+)\'(.*);', line)
        if match:
            prefix = match.group(1)
            tech = match.group(2)
            val_str = match.group(3)
            unit_str = match.group(4)
            suffix = match.group(5)
            
            if tech.startswith('TRA_ROA_HTR_') and tech.endswith('_D5'):
                val = float(val_str)
                if val != 0.0:
                    new_val = val * 16.596
                    if 'e' in val_str.lower():
                        new_val_str = f"{new_val:.4e}"
                    else:
                        new_val_str = f"{new_val:.5f}".rstrip('0').rstrip('.')
                        if new_val_str == '': new_val_str = '0.0'
                    new_unit_str = unit_str.replace('Bvkm', 'Gtkm')
                    new_line = f"{prefix}{new_val_str},'{new_unit_str}'{suffix};\n"
                    new_lines.append(new_line)
                    modified_maxactivity += 1
                    continue
                else:
                    new_unit_str = unit_str.replace('Bvkm', 'Gtkm')
                    new_line = f"{prefix}0.0,'{new_unit_str}'{suffix};\n"
                    new_lines.append(new_line)
                    modified_maxactivity += 1
                    continue
                    
    elif line.startswith('INSERT INTO "ExistingCapacity"'):
        # INSERT INTO "ExistingCapacity" VALUES ('IT','TRA_ROA_HTR_DST_E_D5',2006,2.153,'Bvkm','notes');
        match = re.match(r'(INSERT INTO "ExistingCapacity" VALUES \([^,]+,\'([^\']+)\',[^,]+,)([^,]+),\'([^\']+)\'(.*);', line)
        if match:
            prefix = match.group(1)
            tech = match.group(2)
            val_str = match.group(3)
            unit_str = match.group(4)
            suffix = match.group(5)
            
            if tech.startswith('TRA_ROA_HTR_') and tech.endswith('_D5'):
                val = float(val_str)
                if val != 0.0:
                    new_val = val * 16.596
                    if 'e' in val_str.lower():
                        new_val_str = f"{new_val:.4e}"
                    else:
                        new_val_str = f"{new_val:.5f}".rstrip('0').rstrip('.')
                        if new_val_str == '': new_val_str = '0.0'
                    new_unit_str = unit_str.replace('Bvkm', 'Gtkm')
                    new_line = f"{prefix}{new_val_str},'{new_unit_str}'{suffix};\n"
                    new_lines.append(new_line)
                    modified_existcap += 1
                    continue
                else:
                    new_unit_str = unit_str.replace('Bvkm', 'Gtkm')
                    new_line = f"{prefix}0.0,'{new_unit_str}'{suffix};\n"
                    new_lines.append(new_line)
                    modified_existcap += 1
                    continue

    new_lines.append(line)

with open(file_path, "w") as f:
    f.writelines(new_lines)

print(f"Modifications complete:")
print(f"MaxActivity rows modified: {modified_maxactivity}")
print(f"ExistingCapacity rows modified: {modified_existcap}")

