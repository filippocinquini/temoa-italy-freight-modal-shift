# Scripts

## `temoa_italy/`: database creation and post-processing

Modified copies of the scripts distributed with TEMOA-Italy release 3.3 (MAHTEP Group, MIT
License). They must run from the `data_files` folder of TEMOA, next to the scenario `.sql` file.

| File | Change with respect to TEMOA-Italy |
|---|---|
| `database_creator.py` | File names set to `TRA_MS_ON_BAU_0` |
| `database_preprocessing.py` | File name; three `DataFrame.append` calls replaced by `pd.concat` for pandas 2 |
| `database_check.py` | File name |
| `database_postprocessing.py` | Technology list replaced by the freight technologies of this work (D1–D5 trucks and modal-shift technologies); `append` replaced by `pd.concat` |
| `database_simplifier.sql` | Copy of the version used for the runs of the report |

To process another scenario, change the file name at the top of each script.

## `conversion/`: how the units were converted

One-off scripts that edited the working `.sql` files while the patch was being built. They are
kept as a record of the method and are not needed to use the patch. File names inside them refer
to working files that are not part of this repository.

| File | Purpose |
|---|---|
| `migrate_to_distance.py` | Replaces the aggregated truck rows with the D1–D5 rows |
| `apply_load_factors.py` | Converts heavy trucks D5, rail freight and domestic navigation from Bvkm to Gtkm with the load factors |
| `fix_htr_d5_costs.py` | Divides investment and fixed costs of heavy trucks D5 by the load factor 16.596 |
| `update_htr_d5.py` | Converts `MaxActivity` and `ExistingCapacity` of heavy trucks D5 |

## `analysis/`

| File | Purpose |
|---|---|
| `batch_db_creator.py` | Runs the creation pipeline on a list of `.sql` files |
| `generate_excel.py` | Exports truck costs by powertrain and distance class to Excel |
| `monte_carlo.py` | Monte Carlo on the costs of the two intermodal terminals (10 samples, σ = 50 % in the report) |
