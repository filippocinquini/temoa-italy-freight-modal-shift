# Data sources

## `raw/`: statistics as downloaded

| File | Source | Content |
|---|---|---|
| `road_go_ta_dc.xlsx` | Eurostat, dataset `road_go_ta_dc` | Annual road freight transport by distance class |
| `rail_tf_trainmv.xlsx` | Eurostat, dataset `rail_tf_trainmv` | Train movements |
| `mar_go_am_it.xlsx` | Eurostat, dataset `mar_go_am_it` | Maritime transport of goods, Italy, annual data |
| `mar_sg_am_cw.xlsx` | Eurostat, dataset `mar_sg_am_cw` | Short sea shipping of goods, country level |
| `JRC_IDEES_IT_Transport_Freight_2006_2023.xlsx` | JRC-IDEES-2021, Joint Research Centre, [doi:10.2760/614599](https://doi.org/10.2760/614599) | Freight transport activity and energy use, Italy (extract prepared by the authors) |
| `istat_road_freight_by_distance_class.xlsx` | ISTAT, dataflow `121_329_DF_DCSC_TRAMERCIS2_1` | Road freight by type of transport and distance class, Italy |

The `Summary` sheet of each Eurostat file reports the dataset code, the extraction date and the
selected dimensions. Eurostat data can be reused with acknowledgement of the source; JRC-IDEES and
ISTAT data are published under Creative Commons Attribution licences.

## `processed/`: workbooks used to derive the model parameters

| File | Content |
|---|---|
| `road_freight_master.xlsx` | Road freight: methodology, load factors, distance factors by powertrain, tonne-kilometre shares, learning curves, validation, JRC baseline |
| `phev_trucks.xlsx` | Plug-in hybrid trucks: parameters, investment and fixed costs, input split, efficiency check |
| `modal_shift_parameters.xlsx` | Modal shift: unit conversions, rail and navigation efficiencies, load factors, aggregated demand `TRA_FRG`, SQL-ready values |
| `maritime_fuel_efficiency.xlsx` | Domestic navigation: load factor, specific fuel consumption from the literature, efficiency by fuel |
| `freight_master.xlsx` | Cross-modal overview: sources, heating values and emission factors, load factors, historical series for road, rail and maritime transport |

Sheet names and notes are partly in Italian. Each workbook has an index or README sheet.
