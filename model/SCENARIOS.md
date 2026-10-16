# Scenarios

The contribution of this repository is the modal-shift structure in the base file. The scenarios
below are the ones we ran on it and are meant as examples: each is `TRA_MS_ON_BAU_0.sql` (built
with `build_scenario.py`) plus a few edits, and other designs are equally possible. Find the rows
by searching for the technology or table name, because line numbers depend on the build.

| Scenario | Starts from | Edit | Purpose |
|---|---|---|---|
| `BAU_0` | – | – | Modal shift available, no emission policy |
| `NT0_0` | `BAU_0` | A | Same model under the net-zero CO₂ cap and carbon prices |
| `BAU_INC` | `BAU_0` | B1 | Incentive on shifted navigation, no emission policy |
| `NT0_INC` | `NT0_0` | B2 | Incentive on low-carbon shifted navigation and terminals, net zero |
| `BAU_FRZ`, `NT0_FRZ` | `BAU_0`, `NT0_0` | C | Navigation shift forced to the EU ceiling |
| `…_FRZ25/50/75` | `BAU_0`, `NT0_0` | C with a factor | Navigation shift forced to 25/50/75 % of the ceiling |
| `NT0_FRZ_ELC_1`, `_2` | `NT0_FRZ` | D | As above, with diesel traction forbidden on shifted trains (1) or on all new trains (2) |
| `NT0_MAT` | `NT0_0` | E | Platinum and graphite shortage |
| `MS_OFF_BAU`, `MS_OFF_NT0` | – | see the last section | Reference without modal shift |

## A. Net zero (`NT0`)

Remove the leading `--` from 18 rows that are commented out in `BAU_0`:

```sql
INSERT INTO "EmissionLimit" VALUES ('IT',2030,'TOT_CO2',194208,'kt','');
INSERT INTO "EmissionLimit" VALUES ('IT',2040,'TOT_CO2',111475,'kt','');
INSERT INTO "EmissionLimit" VALUES ('IT',2050,'TOT_CO2',28742,'kt','');
```

and all 15 `INSERT INTO "CostEmission"` rows: the ETS price on `ELC_CO2`, `IND_CO2`, `UPS_CO2_PRC`
(9 rows) and the ETS2 price on `TRA_CO2`, `RES_CO2`, `COM_CO2` (6 rows).

Effect: total CO₂ is capped at 194 Mt in 2030, 111 Mt in 2040 and 29 Mt in 2050, and emissions are
priced at 80 €/t in 2030 rising to 150 €/t in 2050. The ETS2 rows are commented out in the public
TEMOA-Italy too, so this scenario prices transport and buildings on top of the original model.

## B. Incentives (`INC`)

**B1, `BAU_INC`.** Multiply the cost of the navigation shift-twins `TRA_NAV_DOM_*_SHIFT_N`:

- `CostInvest` × 0.35, for example `0.35*166.0872`, on vintages from 2030 (HFO also 2010 and 2020);
- `CostFixed` × 0.86 on periods from 2030, for HFO, LNG, AMM, MET and H2L (the diesel twin keeps its
  fixed cost).

Effect: a 65 % investment subsidy and a 14 % cut of fixed costs on ships carrying shifted freight,
which makes the road-to-sea shift competitive without any emission policy.

**B2, `NT0_INC`.** The incentive is restricted to low-carbon ships. In the database solved for
the report:

- `CostInvest` × 0.35 on the ammonia, methanol and liquid-hydrogen twins (AMM, MET, H2L);
- `CostFixed` × 0.86 on the ammonia and liquid-hydrogen twins;
- `CostInvest` and `CostFixed` of the terminals `TRA_MS_TRD5_RAIL` and `TRA_MS_TRD5_NAV` × 0.5.

Effect: the same 65 % and 14 % discounts as B1, but only where they do not favour fossil-fuelled
ships, plus intermodal terminals at half cost.

## C. Forced shift (`FRZ`)

Append before the `Output_*` tables:

```sql
INSERT INTO MinActivityGroup (regions, periods, group_name, min_act_g, notes) VALUES
('IT', 2030, 'NAV_SHIFT_GRP', 2.167, 'MS_FORCED: pin to EU ceiling -> read dual'),
('IT', 2035, 'NAV_SHIFT_GRP', 2.462, 'MS_FORCED: pin to EU ceiling -> read dual'),
('IT', 2040, 'NAV_SHIFT_GRP', 2.756, 'MS_FORCED: pin to EU ceiling -> read dual'),
('IT', 2045, 'NAV_SHIFT_GRP', 3.086, 'MS_FORCED: pin to EU ceiling -> read dual'),
('IT', 2050, 'NAV_SHIFT_GRP', 3.415, 'MS_FORCED: pin to EU ceiling -> read dual');
```

Effect: the minimum equals the existing `MaxActivityGroup`, so shifted navigation is pinned to the
EU ceiling in Gtkm. The dual of this constraint is the marginal subsidy needed to obtain the shift.
The solver still chooses the fuel of the ships.

For `FRZ25`, `FRZ50` and `FRZ75` multiply each value by 0.25, 0.5 or 0.75, for example `2.167*0.25`.
Effect: traces how the marginal subsidy grows with the amount of forced shift.

## D. Electric rail (`NT0_FRZ_ELC_1`, `NT0_FRZ_ELC_2`)

On top of C, append the first four rows for variant 1, all eight for variant 2:

```sql
INSERT INTO "MaxActivity" VALUES ('IT',2020,'TRA_RAIL_FRG_DST_SHIFT_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2030,'TRA_RAIL_FRG_DST_SHIFT_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2040,'TRA_RAIL_FRG_DST_SHIFT_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2050,'TRA_RAIL_FRG_DST_SHIFT_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2020,'TRA_RAIL_FRG_DST_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2030,'TRA_RAIL_FRG_DST_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2040,'TRA_RAIL_FRG_DST_N',0.0,'Gtkm','forcing electricity shift installation');
INSERT INTO "MaxActivity" VALUES ('IT',2050,'TRA_RAIL_FRG_DST_N',0.0,'Gtkm','forcing electricity shift installation');
```

Effect: in variant 1 the trains that carry shifted freight cannot be diesel; in variant 2 no new
diesel train can operate, shifted or not, so rail freight growth has to be electric or hydrogen.

## E. Material shortage (`NT0_MAT`)

On top of A, append:

1. the whole file [`scenarios/material_intensity_bev_fcev.sql`](scenarios/material_intensity_bev_fcev.sql) (570 rows);
2. the two reserve limits:

```sql
INSERT INTO "MaxMaterialReserve" VALUES ('IT','MAT_SUP_PLA',47.6*0.75,'t','Platinum shortage: -25% vs base run (47.6 t)');
INSERT INTO "MaxMaterialReserve" VALUES ('IT','MAT_SUP_GRA',4914695*0.80,'t','Graphite shortage: -20% vs base run (4914695 t)');
```

Effect of 1: battery-electric and fuel-cell trucks get their critical-raw-material intensity, which
the other scenarios leave out. Run the model once with step 1 only to obtain the unconstrained
consumption (the base run).
Effect of 2: cumulative platinum and graphite supply is capped at 75 % and 80 % of that
consumption, which shows how the truck fleet and the modal split react to a shortage.

## Scenarios without modal shift (`MS_OFF`)

`TRA_MS_OFF_BAU` and `TRA_MS_OFF_NT0` are not a small edit of `BAU_0`. They contain the D1–D5
disaggregation but none of the modal-shift structure (no `TRA_FRG` demand, terminal technologies,
shift-twins or shift groups), so road freight cannot move to rail or sea. They were built from an
earlier version of the model, before the last corrections to the structure, and are not
included here.
