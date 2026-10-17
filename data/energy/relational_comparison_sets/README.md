Keep the past time series and background information the same, and change only the scenario. Compare the average forecast change from the **neutral forecast**, which is made without a scenario.

- **Direction — 30 comparisons:** Compare each scenario with neutral. P scenarios should raise the natural gas price forecast, while M scenarios should lower it.
- **Contrast — 15 comparisons:** Compare each matched P and M pair. The P scenario should produce a higher average forecast than the M scenario.
- **Intensity — 20 comparisons:** Compare weaker and stronger conditions in the same direction. Stronger P conditions should raise the forecast more, while stronger M conditions should lower it more.

The table uses short IDs within each group. For example, P1 in the E-W row means E-W-P1. The arrow `→` points from the weaker condition to the stronger condition.

| Group | Contrast pairs | Intensity pairs |
|:---|:---|:---|
| **E-W — Weather demand**  | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3 | P1 → P2, P2 → P3; M1 → M2, M2 → M3 |
| **E-PR — Production** | Pa ↔ Ma, Pb ↔ Mb | Pa → Pb; Ma → Mb |
| **E-PI — Pipelines** | P1 ↔ M1, P2 ↔ M2 | P1 → P2; M1 → M2 |
| **E-ST — Storage** | P1 ↔ M1, P2 ↔ M2 | P1 → P2; M1 → M2 |
| **E-LN — LNG and trade** | P1 ↔ M1, P2 ↔ M2 | P1 → P2; M1 → M2 |
| **E-FS — Industry and fuel substitution** | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3, P4 ↔ M4 | P1 → P2, P3 → P4, P1 → P3, P2 → P4; M1 → M2, M3 → M4, M1 → M3, M2 → M4 |

Each Intensity comparison changes one attribute:

| Group and pairs | Change only | Keep fixed |
|:---|:---|:---|
| **E-W:** P1 → P2, P2 → P3; M1 → M2, M2 → M3 | Magnitude of the weather-driven change in natural gas consumption | Affected area, equipment, duration, and heating/cooling mix |
| **E-PR:** Pa → Pb; Ma → Mb | Magnitude of the realized output change per affected facility | Affected facilities, region, market connections, and duration |
| **E-PI:** P1 → P2; M1 → M2 | Magnitude of the change in gas actually delivered to Henry Hub | Supply route, upstream gas availability, alternative supply conditions, and duration |
| **E-ST:** P1 → P2; M1 → M2 | Magnitude of the withdrawable working-gas inventory deviation | Storage facilities, comparison time, and seasonal benchmark |
| **E-LN:** P1 → P2; M1 → M2 | Magnitude of the change in gas withdrawn from the domestic network for LNG production | Export facilities, pipeline connections, and duration |
| **E-FS:** 1 → 2 and 3 → 4, for both P and M | Magnitude of the industrial-output change | Change in the gas-supplied share of process heat |
| **E-FS:** 1 → 3 and 2 → 4, for both P and M | Magnitude of the change in the gas-supplied share of process heat | Industrial-output change |

For E-W, keep the heating/cooling pathway unchanged across intensity levels. Weather scenarios do not introduce production freeze-offs or transportation disruptions. Use adjacent levels only; exclude **1 → 3**.

For E-ST, compare working gas available for withdrawal, excluding base gas. Allow subsequent injections, withdrawals, and ending inventories to adjust.

For E-FS, exclude **1 → 4** and **2 ↔ 3** because both attributes differ. Each row or column forms a separate two-level sequence; there is no single ordering of 1, 2, 3, and 4.

Keep facilities, product mix, equipment efficiencies, and periods fixed within the relevant comparisons. For E-FS, fix process-heat requirements **per unit of output**. Total process heat may change with industrial output, while gas and fuel-oil heat shares adjust in opposite directions.

All stated changes affect markets connected to Henry Hub. The capacity needed to realize each stated change is available, and no separate offsetting shocks occur.