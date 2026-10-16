# Results

Excel exports produced with `scripts/temoa_italy/database_postprocessing.py` from the solved
databases of the report. Each workbook has the sheets `Output_V_Capacity`, `Output_CostInvest`,
`Output_CostFixed`, `Output_CostVariable`, `Output_VFlow_In`, `Output_VFlow_Out`,
`Output_VMat_Cons` and `Output_Emissions`, restricted to the freight technologies.

| Folder | Runs |
|---|---|
| `free/` | Modal shift available: `BAU_0`, `NT0_0` and the incentive runs `BAU_INC`, `NT0_INC` |
| `forced_bau/` | Navigation shift forced to 25, 50, 75 and 100 % (`FRZ`) of the EU ceiling, no emission policy |
| `forced_nt0/` | The same under net zero, plus the two electric-rail variants `FRZ_ELC_1` and `FRZ_ELC_2` |
| `off/` | Reference runs without the modal-shift structure |
| `materials/` | The two runs of the material-shortage analysis, `MAT_BASE` and `MAT_MAX` |

These runs were solved before the four corrections listed in `model/README.md`, and the `off/`
runs with an earlier version of the model. The solved databases (37 MB to 750 MB each) and the
MGA and Monte Carlo exports are not included.
