# Model changes: endogenous freight modal shift in TEMOA-Italy

This folder contains only what we changed in the TEMOA-Italy database, as a patch
on top of the public model, instead of a full copy of it.

| File | Content |
|---|---|
| `modal_shift_additions.sql` | Everything we added (7,714 lines): D1–D5 distance-band disaggregation of LCV/MTR/HTR, plug-in hybrid trucks, charging-infrastructure costs, BAU `MaxActivity` path, aggregated freight demand `TRA_FRG`, linker and modal-shift technologies, rail/navigation shift-twins and their group constraints. |
| `base_edits.patch` | The rows of the original model that we disabled (commented out) or re-valued. Unified diff, 37 hunks. |
| `SCENARIOS.md` | The few rows to add or change in the base scenario to obtain each of the other scenarios, and what each edit does. |
| `scenarios/material_intensity_bev_fcev.sql` | Material intensity of electric and fuel-cell trucks, used by the material-shortage scenario. |
| `build_scenario.py` | Applies both to the base file and checks the result against a reference SHA-256. |

## Base model

[MAHTEP/TEMOA-Italy](https://github.com/MAHTEP/TEMOA-Italy), **release 3.3**
(commit `b22e800`, 2026-01-12), file `TEMOA-Italy/TEMOA_Italy.sql`.
The TEMOA-Italy database is distributed under CC BY 4.0 by Politecnico di Torino – MAHTEP Group.

## Rebuild the base scenario (`TRA_MS_ON_BAU_0`)

```sh
git clone --branch 3.3 --depth 1 https://github.com/MAHTEP/TEMOA-Italy.git
python build_scenario.py TEMOA-Italy/TEMOA-Italy/TEMOA_Italy.sql -o TRA_MS_ON_BAU_0.sql
```

The script prints `OK` when the output matches the reference build.

## Differences from the scenario used in the report

A database created from the output has the same rows as the `TRA_MS_ON_BAU_0` scenario of the
report in all 94 tables, except for four corrections:

- Material intensity of heavy trucks in the D5 band (38 rows) is expressed in t/Gtkm, the unit of
  that band, instead of t/Bvkm. Values are about 16.6 times lower.
- The dummy backstop `DMY_DEM_ANNUAL` for passenger rail demand has efficiency 1.00 again. A unit
  conversion meant for rail freight had set it to 392.836.
- The `TRA_HFO` input of `TRA_NAV_INT_DUAL_N` in 2025, dropped by mistake, is restored.
- Passenger rail and international navigation keep the original TEMOA-Italy numbers. A conversion
  script had introduced rounding noise, for example 24000 had become 24000.0012.

Superseded commented-out rows were removed from the additions; the dual-fuel shift-twin is kept
commented out on purpose, as explained in the report. Battery-electric and fuel-cell trucks carry no
material intensity in the base scenario: those rows are in
`scenarios/material_intensity_bev_fcev.sql` and are used by the material-shortage scenario only.

## What `base_edits.patch` does to the original model

**Disabled (433 rows commented out)**

- Aggregated road freight, replaced by the D1–D5 versions in the additions file:
  all rows of `TRA_ROA_LCV_*`, `TRA_ROA_MTR_*`, `TRA_ROA_HTR_*` in `technologies`, `tech_annual`,
  `tech_groups`, `TechGroupWeight`, `LifetimeTech`, `ExistingCapacity`, `MaxActivity`, `Efficiency`,
  `DiscountRate`, `CostInvest`, `CostFixed`, `CostVariable`, `CurrencyTech`; the three demand
  commodities with their `Demand`, `Elasticity`, `Allocation` and `DMY_DEM_ANNUAL` rows.
- Fuel-technology variable costs `TRA_FT_*` (15 rows), re-entered in the additions file.
- `CostFixed` of new rail freight technologies (3 rows), re-entered in M€/Gtkm.
- `EmissionLimit` on `TOT_CO2` for 2030/2040/2050 (3 rows) and `CostEmission`, the ETS price on
  `ELC_CO2`, `IND_CO2`, `UPS_CO2_PRC` (9 rows). The BAU scenario is meant to show what the system
  does with no emission policy at all, so both the cap and the carbon price are switched off.
- `TRA_ROA_CAR_FCELL_N`, fuel-cell cars, in every table (27 rows). We do not consider fuel cells a
  sensible option for private passenger transport, so the technology is excluded.

**Re-valued (51 rows)**

- `TRA_RAIL_FRG` and `TRA_NAV_DOM` change from demand commodities to physical commodities
  measured in Gtkm, so that they can receive shifted road freight. Efficiency, existing capacity,
  `MaxActivity` and costs of rail-freight and domestic-navigation technologies are converted
  accordingly (from Bvkm to Gtkm through the load factor).
- Efficiency of `TRA_NAV_DOM_LNG_N` and `TRA_NAV_DOM_H2L_ICE_N` corrected (anomalous values).

**Removed (45 rows)**

- `Demand`, `Elasticity`, `Allocation` and `DMY_DEM_ANNUAL` backstop of `TRA_RAIL_FRG` and `TRA_NAV_DOM`,
  now driven by `TRA_FRG`.

**Added (1 row)**: group `TRA_ROA_LCV_GRP`.
