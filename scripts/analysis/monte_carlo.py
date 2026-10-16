import sys
import sqlite3
import os
from pathlib import Path
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Robust path handling (macOS / any OS): all paths are anchored to the project
# root, resolved from the location of THIS script, never from the shell cwd.
# The script may live in the project root or inside data_files/.
# ----------------------------------------------------------------------------
_here = Path(__file__).resolve().parent
ROOT = _here.parent if _here.name == 'data_files' else _here
if not (ROOT / 'temoa_model').is_dir():
    sys.exit(f"ERRORE: cartella 'temoa_model' non trovata in {ROOT}.\n"
             f"Sposta monte_carlo.py nella root del progetto TEMOA o in data_files/.")
os.chdir(ROOT)  # so that the TEMOA invocation below resolves its own relative paths

SEED = None  # set e.g. SEED = 42 for reproducible samplings
rng = np.random.default_rng(SEED)

now = 2030  # Used to select future time periods (MonteCarlo is only applied to them, not to past values)

std_dev_low = 0.50
std_dev_med = 0.50
std_dev_hig = 0.50
samplings = 10

file = 'TRA_MS_ON_BAU_0_SS.sqlite'
scenario_prefix = "BAU_MC_"

cc_item2group = {
}
cc_group2sd = {
}

cf_item2group = {
}
cf_group2sd = {
}

cost_item2group = {
    'TRA_MS_TRD5_RAIL': 'TRA_MS_TRD5_RAIL_COST',
    'TRA_MS_TRD5_NAV': 'TRA_MS_TRD5_NAV_COST',
}
cost_group2sd = {
    'TRA_MS_TRD5_RAIL_COST': 'std_dev_low',
    'TRA_MS_TRD5_NAV_COST': 'std_dev_low',
}

demand_item2group = {

}
demand_group2sd = {

}

efficiency_item2group = {

}
efficiency_group2sd = {

}

maxactcap_item2group = {
}
maxactcap_group2sd = {
}

cc_groups = list(cc_item2group.values())
cc_groups = list(dict.fromkeys(cc_groups))
cf_groups = list(cf_item2group.values())
cf_groups = list(dict.fromkeys(cf_groups))
cost_groups = list(cost_item2group.values())
cost_groups = list(dict.fromkeys(cost_groups))
demand_groups = list(demand_item2group.values())
demand_groups = list(dict.fromkeys(demand_groups))
efficiency_groups = list(efficiency_item2group.values())
efficiency_groups = list(dict.fromkeys(efficiency_groups))
maxactcap_groups = list(maxactcap_item2group.values())
maxactcap_groups = list(dict.fromkeys(maxactcap_groups))

scenario_cc = list()
regions_cc = list()
periods_cc = list()
tech_cc = list()
vintage_cc = list()
cc_cc = list()

scenario_cf = list()
regions_cf = list()
tech_cf = list()
vintage_cf = list()
cf_cf = list()

scenario_cft = list()
regions_cft = list()
season_name_cft = list()
time_of_day_name_cft = list()
tech_cft = list()
cft_cft = list()

scenario_cfp = list()
regions_cfp = list()
season_name_cfp = list()
time_of_day_name_cfp = list()
tech_cfp = list()
vintage_cfp = list()
cfp_cfp = list()

scenario_cost_invest = list()
regions_cost_invest = list()
tech_cost_invest = list()
vintage_cost_invest = list()
cost_invest_cost_invest = list()

scenario_cost_fixed = list()
regions_cost_fixed = list()
periods_cost_fixed = list()
tech_cost_fixed = list()
vintage_cost_fixed = list()
cost_fixed_cost_fixed = list()

scenario_cost_variable = list()
regions_cost_variable = list()
periods_cost_variable = list()
tech_cost_variable = list()
vintage_cost_variable = list()
cost_variable_cost_variable = list()

scenario_demand = list()
regions_demand = list()
demand_comm_demand = list()
periods_demand = list()
demand_demand = list()

scenario_efficiency = list()
regions_efficiency = list()
input_comm_efficiency = list()
tech_efficiency = list()
vintage_efficiency = list()
output_comm_efficiency = list()
efficiency_efficiency = list()

scenario_maxact = list()
regions_maxact = list()
periods_maxact = list()
tech_maxact = list()
maxact_maxact = list()

scenario_maxcap = list()
regions_maxcap = list()
periods_maxcap = list()
tech_maxcap = list()
maxcap_maxcap = list()

CapacityCredit_Backup = pd.DataFrame()
CapacityFactor_Backup = pd.DataFrame()
CapacityFactorTech_Backup = pd.DataFrame()
CapacityFactorProcess_Backup = pd.DataFrame()
CostInvest_Backup = pd.DataFrame()
CostFixed_Backup = pd.DataFrame()
CostVariable_Backup = pd.DataFrame()
Demand_Backup = pd.DataFrame()
Efficiency_Backup = pd.DataFrame()
MaxActivity_Backup = pd.DataFrame()
MaxCapacity_Backup = pd.DataFrame()

config_sample = ROOT / 'temoa_model' / 'config_sample'
file_path = ROOT / 'data_files' / str(file)  # Path to the .sqlite database in data_files/

if not file_path.exists():
    available = '\n  '.join(p.name for p in (ROOT / 'data_files').glob('*.sqlite')) or '(nessun .sqlite)'
    sys.exit(f"ERRORE: database non trovato: {file_path}\n"
             f"File .sqlite disponibili in {ROOT / 'data_files'}:\n  {available}")
if not config_sample.exists():
    sys.exit(f"ERRORE: config non trovato: {config_sample}")

conn = sqlite3.connect(str(file_path))

time_periods = pd.read_sql("select * from time_periods", conn)
end = time_periods.t_periods[len(time_periods)-2]

for i in range(0, samplings):
    scenario = scenario_prefix + str(i+1)

    for group in cc_groups:
        if cc_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif cc_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif cc_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for CapacityCredit of ' + group)
        cc_sampling = rng.normal(0, std_dev)

        for item in cc_item2group.keys():
            if cc_item2group[item] == group:
                CapacityCredit = pd.read_sql("select * from CapacityCredit where tech = '" + str(item) + "' and periods > " + str(now), conn)
                CapacityCredit = CapacityCredit.sort_values(by=['periods'], ignore_index=True)
                CapacityCredit_Backup = pd.concat([CapacityCredit_Backup, CapacityCredit], ignore_index=True)
                for j in range(0, len(CapacityCredit)):
                    cc_mc = (1 + cc_sampling * (CapacityCredit.periods[j] - now) / (end - now)) * CapacityCredit.cf_tech[j]
                    if  cc_mc < 0.5 * CapacityCredit.cf_tech[j]:
                        cc_mc = 0.5 * CapacityCredit.cf_tech[j]
                    elif cc_mc > 1.0:
                        cc_mc = 1.0
                    
                    cursor = conn.cursor()
                    conn.execute("update CapacityCredit set cf_tech =" + str(cc_mc) +
                                    " where regions = '" + str(CapacityCredit.regions[j]) +
                                    "' and vintage = " + str(CapacityCredit.vintage[j]) +
                                    " and tech = '" + str(CapacityCredit.tech[j]) +
                                    "' and periods = " + str(CapacityCredit.periods[j]))
                    conn.commit()

                    scenario_cc.append(scenario)
                    regions_cc.append(CapacityCredit.regions[j])
                    periods_cc.append(CapacityCredit.periods[j])
                    tech_cc.append(CapacityCredit.tech[j])
                    vintage_cc.append(CapacityCredit.vintage[j])
                    cc_cc.append(cc_mc)

    for group in cf_groups:
        if cf_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif cf_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif cf_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for CapacityFactor of ' + group)
        cf_sampling = rng.normal(0, std_dev)

        for item in cf_item2group.keys():
            if cf_item2group[item] == group:
                CapacityFactor = pd.read_sql("select * from CapacityFactor where tech = '" + str(item) + "' and vintage > " + str(now), conn)
                CapacityFactor = CapacityFactor.sort_values(by=['vintage'], ignore_index=True)
                CapacityFactor_Backup = pd.concat([CapacityFactor_Backup, CapacityFactor], ignore_index=True)
                for j in range(0, len(CapacityFactor)):
                    cf_mc = (1 + cf_sampling * (CapacityFactor.vintage[j] - now) / (end - now)) * CapacityFactor.cf[j]
                    if cf_mc < 0.5 * CapacityFactor.cf[j]:
                        cf_mc = 0.5 * CapacityFactor.cf[j]
                    elif cf_mc > 1.0:
                        cf_mc = 1.0
                    cursor = conn.cursor()
                    conn.execute("update CapacityFactor set cf =" + str(cf_mc) +
                                    " where regions = '" + str(CapacityFactor.regions[j]) +
                                    "' and tech = '" + str(CapacityFactor.tech[j]) +
                                    "' and vintage = " + str(CapacityFactor.vintage[j]))
                    conn.commit()

                    scenario_cf.append(scenario)
                    regions_cf.append(CapacityFactor.regions[j])
                    tech_cf.append(CapacityFactor.tech[j])
                    vintage_cf.append(CapacityFactor.vintage[j])
                    cf_cf.append(cf_mc)
                
                CapacityFactorTech = pd.read_sql("select * from CapacityFactorTech where tech = '" + str(item) + "'", conn)
                CapacityFactorTech_Backup = pd.concat([CapacityFactorTech_Backup, CapacityFactorTech], ignore_index=True)
                for j in range(0, len(CapacityFactorTech)):
                    cft_mc = (1 + cf_sampling) * CapacityFactorTech.cf_tech[j]  # No indexes for the milestone year in this case!
                    if cft_mc < 0.5 * CapacityFactorTech.cf_tech[j]:
                        cft_mc = 0.5 * CapacityFactorTech.cf_tech[j]
                    elif cft_mc > 1.0:
                        cft_mc = 1.0
                    cursor = conn.cursor()
                    conn.execute("update CapacityFactorTech set cf_tech =" + str(cft_mc) +
                                    " where regions = '" + str(CapacityFactorTech.regions[j]) +
                                    "' and season_name = '" + str(CapacityFactorTech.season_name[j]) +
                                    "' and time_of_day_name = '" + str(CapacityFactorTech.time_of_day_name[j]) +
                                    "' and tech = '" + str(CapacityFactorTech.tech[j]) + "'")
                    conn.commit()

                    scenario_cft.append(scenario)
                    regions_cft.append(CapacityFactorTech.regions[j])
                    season_name_cft.append(CapacityFactorTech.season_name[j])
                    time_of_day_name_cft.append(CapacityFactorTech.time_of_day_name[j])
                    tech_cft.append(CapacityFactorTech.tech[j])
                    cft_cft.append(cft_mc)

                CapacityFactorProcess = pd.read_sql("select * from CapacityFactorProcess where tech = '" + str(item) + "' and vintage > " + str(now), conn)
                CapacityFactorProcess = CapacityFactorProcess.sort_values(by=['vintage'], ignore_index=True)
                CapacityFactorProcess_Backup = pd.concat([CapacityFactorProcess_Backup, CapacityFactorProcess], ignore_index=True)
                for j in range(0, len(CapacityFactorProcess)):
                    cfp_mc = (1 + cf_sampling * (CapacityFactorProcess.vintage[j] - now) / (end - now)) * CapacityFactorProcess.cf_process[j]
                    if cfp_mc < 0.5 * CapacityFactorProcess.cf_process[j]:
                        cfp_mc = 0.5 * CapacityFactorProcess.cf_process[j]
                    elif cfp_mc > 1.0:
                        cfp_mc = 1.0
                    cursor = conn.cursor()
                    conn.execute("update CapacityFactorProcess set cf_process =" + str(cfp_mc) +
                                    " where regions = '" + str(CapacityFactorProcess.regions[j]) +
                                    "' and season_name = '" + str(CapacityFactorProcess.season_name[j]) +
                                    "' and time_of_day_name = '" + str(CapacityFactorProcess.time_of_day_name[j]) +
                                    "' and tech = '" + str(CapacityFactorProcess.tech[j]) +
                                    "' and vintage = " + str(CapacityFactorProcess.vintage[j]))
                    conn.commit()

                    scenario_cfp.append(scenario)
                    regions_cfp.append(CapacityFactorProcess.regions[j])
                    season_name_cfp.append(CapacityFactorProcess.season_name[j])
                    time_of_day_name_cfp.append(CapacityFactorProcess.time_of_day_name[j])
                    tech_cfp.append(CapacityFactorProcess.tech[j])
                    vintage_cfp.append(CapacityFactorProcess.vintage[j])
                    cfp_cfp.append(cfp_mc)

    for group in cost_groups:
        if cost_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif cost_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif cost_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for CostInvest of ' + group)
        cost_sampling = rng.normal(0, std_dev)

        for item in cost_item2group.keys():
            if cost_item2group[item] == group:
                CostInvest = pd.read_sql("select * from CostInvest where tech = '" + str(item) + "' and vintage > " + str(now), conn)
                CostInvest = CostInvest.sort_values(by=['vintage'], ignore_index=True)
                CostInvest_Backup = pd.concat([CostInvest_Backup, CostInvest], ignore_index=True)
                for j in range(0, len(CostInvest)):
                    cost_invest_mc = (1 + cost_sampling * (CostInvest.vintage[j] - now) / (end - now)) * CostInvest.cost_invest[j]

                    cursor = conn.cursor()
                    conn.execute("update CostInvest set cost_invest =" + str(cost_invest_mc) +
                                    " where regions = '" + str(CostInvest.regions[j]) +
                                    "' and tech = '" + str(CostInvest.tech[j]) +
                                    "' and vintage = " + str(CostInvest.vintage[j]))
                    conn.commit()

                    scenario_cost_invest.append(scenario)
                    regions_cost_invest.append(CostInvest.regions[j])
                    tech_cost_invest.append(CostInvest.tech[j])
                    vintage_cost_invest.append(CostInvest.vintage[j])
                    cost_invest_cost_invest.append(cost_invest_mc)

                CostFixed = pd.read_sql("select * from CostFixed where tech = '" + str(item) + "' and periods > " + str(now), conn)
                CostFixed = CostFixed.sort_values(by=['vintage', 'periods'], ignore_index=True)
                CostFixed_Backup = pd.concat([CostFixed_Backup, CostFixed], ignore_index=True)
                for j in range(0, len(CostFixed)):
                    cost_fixed_mc = (1 + cost_sampling * (CostFixed.periods[j] - now) / (end - now)) * CostFixed.cost_fixed[j]
                    
                    cursor = conn.cursor()
                    conn.execute("update CostFixed set cost_fixed =" + str(cost_fixed_mc) +
                                    " where regions = '" + str(CostFixed.regions[j]) +
                                    "' and tech = '" + str(CostFixed.tech[j]) +
                                    "' and vintage = " + str(CostFixed.vintage[j]) +
                                    " and periods = " + str(CostFixed.periods[j]))
                    conn.commit()

                    scenario_cost_fixed.append(scenario)
                    regions_cost_fixed.append(CostFixed.regions[j])
                    periods_cost_fixed.append(CostFixed.periods[j])
                    tech_cost_fixed.append(CostFixed.tech[j])
                    vintage_cost_fixed.append(CostFixed.vintage[j])
                    cost_fixed_cost_fixed.append(cost_fixed_mc)

                CostVariable = pd.read_sql("select * from CostVariable where tech = '" + str(item) + "' and periods > " + str(now), conn)
                CostVariable = CostVariable.sort_values(by=['vintage', 'periods'], ignore_index=True)
                CostVariable_Backup = pd.concat([CostVariable_Backup, CostVariable], ignore_index=True)
                for j in range(0, len(CostVariable)):
                    cost_variable_mc = (1 + cost_sampling * (CostVariable.periods[j] - now) / (end - now)) * CostVariable.cost_variable[j]
                    
                    cursor = conn.cursor()
                    conn.execute("update CostVariable set cost_variable =" + str(cost_variable_mc) +
                                    " where regions = '" + str(CostVariable.regions[j]) +
                                    "' and tech = '" + str(CostVariable.tech[j]) +
                                    "' and vintage = " + str(CostVariable.vintage[j]) +
                                    " and periods = " + str(CostVariable.periods[j]))
                    conn.commit()

                    scenario_cost_variable.append(scenario)
                    regions_cost_variable.append(CostVariable.regions[j])
                    periods_cost_variable.append(CostVariable.periods[j])
                    tech_cost_variable.append(CostVariable.tech[j])
                    vintage_cost_variable.append(CostVariable.vintage[j])
                    cost_variable_cost_variable.append(cost_variable_mc)

    for group in demand_groups:
        if demand_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif demand_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif demand_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for Demand of ' + group)
        demand_sampling = rng.normal(0, std_dev)

        for item in demand_item2group.keys():
            if demand_item2group[item] == group:
                Demand = pd.read_sql("select * from Demand where demand_comm = '" + str(item) + "' and periods > " + str(now), conn)
                Demand = Demand.sort_values(by=['periods'], ignore_index=True)
                Demand_Backup = pd.concat([Demand_Backup, Demand], ignore_index=True)
                for j in range(0, len(Demand)):
                    demand_mc = (1 + demand_sampling * (Demand.periods[j] - now) / (end - now)) * Demand.demand[j]
                    if demand_mc <= 0.0:
                        demand_mc = Demand.demand[j]
                    
                    cursor = conn.cursor()
                    conn.execute("update Demand set demand =" + str(demand_mc) +
                                    " where regions = '" + str(Demand.regions[j]) +
                                    "' and demand_comm = '" + str(Demand.demand_comm[j]) +
                                    "' and periods = " + str(Demand.periods[j]))
                    conn.commit()

                    scenario_demand.append(scenario)
                    regions_demand.append(Demand.regions[j])
                    periods_demand.append(Demand.periods[j])
                    demand_comm_demand.append(Demand.demand_comm[j])
                    demand_demand.append(demand_mc)

    for group in efficiency_groups:
        if efficiency_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif efficiency_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif efficiency_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for Efficiency of ' + group)
        efficiency_sampling = rng.normal(0, std_dev)

        for item in efficiency_item2group.keys():
            if efficiency_item2group[item] == group:
                Efficiency = pd.read_sql("select * from Efficiency where tech = '" + str(item) + "' and vintage > " + str(now), conn)
                Efficiency = Efficiency.sort_values(by=['vintage'], ignore_index=True)
                Efficiency_Backup = pd.concat([Efficiency_Backup, Efficiency], ignore_index=True)
                for j in range(0, len(Efficiency)):
                    efficiency_mc = (1 + efficiency_sampling * (Efficiency.vintage[j] - now) / (end - now)) * Efficiency.efficiency[j]
                    if efficiency_mc <= 0.0:
                        efficiency_mc = Efficiency.efficiency[j]
                    
                    cursor = conn.cursor()
                    conn.execute("update Efficiency set efficiency =" + str(efficiency_mc) +
                                    " where regions = '" + str(Efficiency.regions[j]) +
                                    "' and input_comm = '" + str(Efficiency.input_comm[j]) +
                                    "' and tech = '" + str(Efficiency.tech[j]) +
                                    "' and output_comm = '" + str(Efficiency.output_comm[j]) +
                                    "' and vintage = " + str(Efficiency.vintage[j]))
                    conn.commit()

                    scenario_efficiency.append(scenario)
                    regions_efficiency.append(Efficiency.regions[j])
                    input_comm_efficiency.append(Efficiency.input_comm[j])
                    tech_efficiency.append(Efficiency.tech[j])
                    vintage_efficiency.append(Efficiency.vintage[j])
                    output_comm_efficiency.append(Efficiency.output_comm[j])
                    efficiency_efficiency.append(efficiency_mc)

    for group in maxactcap_groups:
        if maxactcap_group2sd[group] == 'std_dev_low':
            std_dev = std_dev_low
        elif maxactcap_group2sd[group] == 'std_dev_med':
            std_dev = std_dev_med
        elif maxactcap_group2sd[group] == 'std_dev_hig':
            std_dev = std_dev_hig
        else:
            print('Error: Standar deviation non specified for MaxActivity/MaxCapacity of ' + group)
        maxactcap_sampling = rng.normal(0, std_dev)

        for item in maxactcap_item2group.keys():
            if maxactcap_item2group[item] == group:
                MaxActivity = pd.read_sql("select * from MaxActivity where tech = '" + str(item) + "' and periods > " + str(now), conn)
                MaxActivity = MaxActivity.sort_values(by=['periods'], ignore_index=True)
                MaxActivity_Backup = pd.concat([MaxActivity_Backup, MaxActivity], ignore_index=True)
                for j in range(0, len(MaxActivity)):
                    maxact_mc = (1 + maxactcap_sampling * (MaxActivity.periods[j] - now) / (end - now)) * MaxActivity.maxact[j]
                    if maxact_mc <= 0.0:
                        maxact_mc = MaxActivity.maxact[j]

                    cursor = conn.cursor()
                    conn.execute("update MaxActivity set maxact =" + str(maxact_mc) +
                                    " where regions = '" + str(MaxActivity.regions[j]) +
                                    "' and tech = '" + str(MaxActivity.tech[j]) +
                                    "' and periods = " + str(MaxActivity.periods[j]))
                    conn.commit()

                    scenario_maxact.append(scenario)
                    regions_maxact.append(MaxActivity.regions[j])
                    periods_maxact.append(MaxActivity.periods[j])
                    tech_maxact.append(MaxActivity.tech[j])
                    maxact_maxact.append(maxact_mc)

                MaxCapacity = pd.read_sql("select * from MaxCapacity where tech = '" + str(item) + "' and periods > " + str(now), conn)
                MaxCapacity = MaxCapacity.sort_values(by=['periods'], ignore_index=True)
                MaxCapacity_Backup = pd.concat([MaxCapacity_Backup, MaxCapacity], ignore_index=True)
                for j in range(0, len(MaxCapacity)):
                    maxcap_mc = (1 + maxactcap_sampling * (MaxCapacity.periods[j] - now) / (end - now)) * MaxCapacity.maxcap[j]
                    if maxcap_mc <= 0.0:
                        maxcap_mc = MaxCapacity.maxcap[j]

                    cursor = conn.cursor()
                    conn.execute("update MaxCapacity set maxcap =" + str(maxcap_mc) +
                                    " where regions = '" + str(MaxCapacity.regions[j]) +
                                    "' and tech = '" + str(MaxCapacity.tech[j]) +
                                    "' and periods = " + str(MaxCapacity.periods[j]))
                    conn.commit()

                    scenario_maxcap.append(scenario)
                    regions_maxcap.append(MaxCapacity.regions[j])
                    periods_maxcap.append(MaxCapacity.periods[j])
                    tech_maxcap.append(MaxCapacity.tech[j])
                    maxcap_maxcap.append(maxcap_mc)

    # Update the scenario name in config_sample (search the line, no fixed index)
    with open(config_sample, 'r', encoding='utf-8') as fh:
        data = fh.readlines()
    idx = [k for k, ln in enumerate(data) if ln.lstrip().startswith('--scenario')]
    if not idx:
        sys.exit(f"ERRORE: nessuna riga '--scenario' trovata in {config_sample}")
    data[idx[0]] = '--scenario=' + scenario + '\n'
    with open(config_sample, 'w', encoding='utf-8') as fh:
        fh.writelines(data)

    # Run TEMOA with 573-578 rows of temoa_run.py commented
    rc = os.system(f'"{sys.executable}" temoa_model/ --config=temoa_model/config_sample')
    if rc != 0:
        print(f'ATTENZIONE: run TEMOA {scenario} terminata con codice {rc}')

    # Restoring the original values
    cursor = conn.cursor()
    for j in range(0, len(CapacityCredit_Backup)):
        conn.execute("update CapacityCredit set cf_tech =" + str(CapacityCredit_Backup.cf_tech[j]) +
                        " where regions = '" + str(CapacityCredit_Backup.regions[j]) +
                        "' and periods = " + str(CapacityCredit_Backup.periods[j]) +
                        " and tech = '" + str(CapacityCredit_Backup.tech[j]) +
                        "' and vintage = " + str(CapacityCredit_Backup.vintage[j]))
    for j in range(0, len(CapacityFactor_Backup)):
        conn.execute("update CapacityFactor set cf =" + str(CapacityFactor_Backup.cf[j]) +
                        " where regions = '" + str(CapacityFactor_Backup.regions[j]) +
                        "' and tech = '" + str(CapacityFactor_Backup.tech[j]) +
                        "' and vintage = " + str(CapacityFactor_Backup.vintage[j]))
    for j in range(0, len(CapacityFactorTech_Backup)):
        conn.execute("update CapacityFactorTech set cf_tech =" + str(CapacityFactorTech_Backup.cf_tech[j]) +
                        " where regions = '" + str(CapacityFactorTech_Backup.regions[j]) +
                        "' and season_name = '" + str(CapacityFactorTech_Backup.season_name[j]) +
                        "' and time_of_day_name = '" + str(CapacityFactorTech_Backup.time_of_day_name[j]) +
                        "' and tech = '" + str(CapacityFactorTech_Backup.tech[j]) + "'")
    for j in range(0, len(CapacityFactorProcess_Backup)):
        conn.execute("update CapacityFactorProcess set cf_process =" + str(CapacityFactorProcess_Backup.cf_process[j]) +
                        " where regions = '" + str(CapacityFactorProcess_Backup.regions[j]) +
                        "' and season_name = '" + str(CapacityFactorProcess_Backup.season_name[j]) +
                        "' and time_of_day_name = '" + str(CapacityFactorProcess_Backup.time_of_day_name[j]) +
                        "' and tech = '" + str(CapacityFactorProcess_Backup.tech[j]) +
                        "' and vintage = " + str(CapacityFactorProcess_Backup.vintage[j]))
    for j in range(0, len(CostInvest_Backup)):
        conn.execute("update CostInvest set cost_invest =" + str(CostInvest_Backup.cost_invest[j]) +
                        " where regions = '" + str(CostInvest_Backup.regions[j]) +
                        "' and tech = '" + str(CostInvest_Backup.tech[j]) +
                        "' and vintage = " + str(CostInvest_Backup.vintage[j]))
    for j in range(0, len(CostFixed_Backup)):
        conn.execute("update CostFixed set cost_fixed =" + str(CostFixed_Backup.cost_fixed[j]) +
                        " where regions = '" + str(CostFixed_Backup.regions[j]) +
                        "' and periods = " + str(CostFixed_Backup.periods[j]) +
                        " and tech = '" + str(CostFixed_Backup.tech[j]) +
                        "' and vintage = " + str(CostFixed_Backup.vintage[j]))
    for j in range(0, len(CostVariable_Backup)):
        conn.execute("update CostVariable set cost_variable =" + str(CostVariable_Backup.cost_variable[j]) +
                        " where regions = '" + str(CostVariable_Backup.regions[j]) +
                        "' and periods = " + str(CostVariable_Backup.periods[j]) +
                        " and tech = '" + str(CostVariable_Backup.tech[j]) +
                        "' and vintage = " + str(CostVariable_Backup.vintage[j]))
    for j in range(0, len(Demand_Backup)):
        conn.execute("update Demand set demand =" + str(Demand_Backup.demand[j]) +
                        " where regions = '" + str(Demand_Backup.regions[j]) +
                        "' and demand_comm = '" + str(Demand_Backup.demand_comm[j]) +
                        "' and periods = " + str(Demand_Backup.periods[j]))
    for j in range(0, len(Efficiency_Backup)):
        conn.execute("update Efficiency set efficiency =" + str(Efficiency_Backup.efficiency[j]) +
                        " where regions = '" + str(Efficiency_Backup.regions[j]) +
                        "' and input_comm = '" + str(Efficiency_Backup.input_comm[j]) +
                        "' and tech = '" + str(Efficiency_Backup.tech[j]) +
                        "' and output_comm = '" + str(Efficiency_Backup.output_comm[j]) +
                        "' and vintage = " + str(Efficiency_Backup.vintage[j]))
    for j in range(0, len(MaxActivity_Backup)):
        conn.execute("update MaxActivity set maxact =" + str(MaxActivity_Backup.maxact[j]) +
                        " where regions = '" + str(MaxActivity_Backup.regions[j]) +
                        "' and tech = '" + str(MaxActivity_Backup.tech[j]) +
                        "' and periods = " + str(MaxActivity_Backup.periods[j]))
    for j in range(0, len(MaxCapacity_Backup)):
        conn.execute("update MaxCapacity set maxcap =" + str(MaxCapacity_Backup.maxcap[j]) +
                        " where regions = '" + str(MaxCapacity_Backup.regions[j]) +
                        "' and tech = '" + str(MaxCapacity_Backup.tech[j]) +
                        "' and periods = " + str(MaxCapacity_Backup.periods[j]))
    conn.commit()

# Saving the MonteCarlo samplings in the .sqlite database

CapacityCredit_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cc, dtype='str'),
        "regions": pd.Series(regions_cc, dtype='str'),
        "periods": pd.Series(periods_cc, dtype='int'),
        "tech": pd.Series(tech_cc, dtype='str'),
        "vintage": pd.Series(vintage_cc, dtype='int'),
        "cf_tech": pd.Series(cc_cc, dtype='float'),
    }
)
CapacityCredit_MonteCarlo.to_sql('CapacityCredit_MonteCarlo', conn, index=False, if_exists='replace')

CapacityFactor_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cf, dtype='str'),
        "regions": pd.Series(regions_cf, dtype='str'),
        "tech": pd.Series(tech_cf, dtype='str'),
        "vintage": pd.Series(vintage_cf, dtype='int'),
        "cf": pd.Series(cf_cf, dtype='float'),
    }
)
CapacityFactor_MonteCarlo.to_sql('CapacityFactor_MonteCarlo', conn, index=False, if_exists='replace')

CapacityFactorTech_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cft, dtype='str'),
        "regions": pd.Series(regions_cft, dtype='str'),
        "season_name": pd.Series(season_name_cft, dtype='str'),
        "time_of_day_name": pd.Series(time_of_day_name_cft, dtype='str'),
        "tech": pd.Series(tech_cft, dtype='str'),
        "cf_tech": pd.Series(cft_cft, dtype='float'),
    }
)
CapacityFactorTech_MonteCarlo.to_sql('CapacityFactorTech_MonteCarlo', conn, index=False, if_exists='replace')

CapacityFactorProcess_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cfp, dtype='str'),
        "regions": pd.Series(regions_cfp, dtype='str'),
        "season_name": pd.Series(season_name_cfp, dtype='str'),
        "time_of_day_name": pd.Series(time_of_day_name_cfp, dtype='str'),
        "tech": pd.Series(tech_cfp, dtype='str'),
        "vintage": pd.Series(vintage_cfp, dtype='int'),
        "cf_process": pd.Series(cfp_cfp, dtype='float'),
    }
)
CapacityFactorProcess_MonteCarlo.to_sql('CapacityFactorProcess_MonteCarlo', conn, index=False, if_exists='replace')

CostInvest_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cost_invest, dtype='str'),
        "regions": pd.Series(regions_cost_invest, dtype='str'),
        "tech": pd.Series(tech_cost_invest, dtype='str'),
        "vintage": pd.Series(vintage_cost_invest, dtype='int'),
        "cost_invest": pd.Series(cost_invest_cost_invest, dtype='float'),
    }
)
CostInvest_MonteCarlo.to_sql('CostInvest_MonteCarlo', conn, index=False, if_exists='replace')

CostFixed_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cost_fixed, dtype='str'),
        "regions": pd.Series(regions_cost_fixed, dtype='str'),
        "periods": pd.Series(periods_cost_fixed, dtype='int'),
        "tech": pd.Series(tech_cost_fixed, dtype='str'),
        "vintage": pd.Series(vintage_cost_fixed, dtype='int'),
        "cost_fixed": pd.Series(cost_fixed_cost_fixed, dtype='float'),
    }
)
CostFixed_MonteCarlo.to_sql('CostFixed_MonteCarlo', conn, index=False, if_exists='replace')

CostVariable_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_cost_variable, dtype='str'),
        "regions": pd.Series(regions_cost_variable, dtype='str'),
        "periods": pd.Series(periods_cost_variable, dtype='int'),
        "tech": pd.Series(tech_cost_variable, dtype='str'),
        "vintage": pd.Series(vintage_cost_variable, dtype='int'),
        "cost_variable": pd.Series(cost_variable_cost_variable, dtype='float'),
    }
)
CostVariable_MonteCarlo.to_sql('CostVariable_MonteCarlo', conn, index=False, if_exists='replace')

Demand_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_demand, dtype='str'),
        "regions": pd.Series(regions_demand, dtype='str'),
        "periods": pd.Series(periods_demand, dtype='int'),
        "demand_comm": pd.Series(demand_comm_demand, dtype='str'),
        "demand": pd.Series(demand_demand, dtype='float'),
    }
)
Demand_MonteCarlo.to_sql('Demand_MonteCarlo', conn, index=False, if_exists='replace')

Efficiency_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_efficiency, dtype='str'),
        "regions": pd.Series(regions_efficiency, dtype='str'),
        "input_comm": pd.Series(input_comm_efficiency, dtype='str'),
        "tech": pd.Series(tech_efficiency, dtype='str'),
        "vintage": pd.Series(vintage_efficiency, dtype='int'),
        "output_comm": pd.Series(output_comm_efficiency, dtype='str'),
        "efficiency": pd.Series(efficiency_efficiency, dtype='float'),
    }
)
Efficiency_MonteCarlo.to_sql('Efficiency_MonteCarlo', conn, index=False, if_exists='replace')

MaxActivity_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_maxact, dtype='str'),
        "regions": pd.Series(regions_maxact, dtype='str'),
        "periods": pd.Series(periods_maxact, dtype='int'),
        "tech": pd.Series(tech_maxact, dtype='str'),
        "maxact": pd.Series(maxact_maxact, dtype='float'),
    }
)
MaxActivity_MonteCarlo.to_sql('MaxActivity_MonteCarlo', conn, index=False, if_exists='replace')

MaxCapacity_MonteCarlo = pd.DataFrame(
    {
        "scenario": pd.Series(scenario_maxcap, dtype='str'),
        "regions": pd.Series(regions_maxcap, dtype='str'),
        "periods": pd.Series(periods_maxcap, dtype='int'),
        "tech": pd.Series(tech_maxcap, dtype='str'),
        "maxcap": pd.Series(maxcap_maxcap, dtype='float'),
    }
)
MaxCapacity_MonteCarlo.to_sql('MaxCapacity_MonteCarlo', conn, index=False, if_exists='replace')

# Restore a neutral scenario name in config_sample
with open(config_sample, 'r', encoding='utf-8') as fh:
    data = fh.readlines()
idx = [k for k, ln in enumerate(data) if ln.lstrip().startswith('--scenario')]
if idx:
    data[idx[0]] = '--scenario=test_run' + '\n'
    with open(config_sample, 'w', encoding='utf-8') as fh:
        fh.writelines(data)

conn.close()
