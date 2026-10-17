Keep the past time series and background information the same, and change only the scenario. Compare the average forecast change from the **neutral forecast**, which is made without a scenario.

- **Direction — 24 comparisons:** Compare each scenario with neutral. P scenarios should raise the U.S. dollar index forecast, while M scenarios should lower it.
- **Contrast — 12 comparisons:** Compare each matched P and M pair. The P scenario should produce a higher average forecast than the M scenario.
- **Intensity — 16 comparisons:** Compare weaker and stronger conditions in the same direction. Stronger P conditions should raise the forecast more, while stronger M conditions should lower it more.

The table uses short IDs within each group. For example, P1 in the M-IR row means M-IR-P1. The arrow `→` points from the weaker condition to the stronger condition.

| Group | Contrast pairs | Intensity pairs |
|:---|:---|:---|
| **M-IR — Monetary policy and relative interest rates** | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3 | P1 → P2, P2 → P3; M1 → M2, M2 → M3 |
| **M-EC — Relative economic conditions** | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3 | P1 → P2, P2 → P3; M1 → M2, M2 → M3 |
| **M-RI — Global risk sentiment** | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3 | P1 → P2, P2 → P3; M1 → M2, M2 → M3 |
| **M-CF — Foreign developments and capital flows** | P1 ↔ M1, P2 ↔ M2, P3 ↔ M3 | P1 → P2, P2 → P3; M1 → M2, M2 → M3 |

Each Intensity comparison changes one attribute:

| Group and pairs | Change only | Keep fixed |
|:---|:---|:---|
| **M-IR:** P1 → P2, P2 → P3; M1 → M2, M2 → M3 | Magnitude of the change in the expected U.S. interest-rate path relative to major trading partners | Trading-partner reference, policy-path horizon, and timing |
| **M-EC:** P1 → P2, P2 → P3; M1 → M2, M2 → M3 | Magnitude of the change in U.S. real household-consumption growth relative to major trading partners | Real-consumption definition, goods-and-services coverage, trading-partner reference, and period |
| **M-RI:** P1 → P2, P2 → P3; M1 → M2, M2 → M3 | Magnitude of the change in total investor demand for liquid short-term U.S. Treasury securities | Funding-stress mechanism, investor population, security definition, and period |
| **M-CF:** P1 → P2, P2 → P3; M1 → M2, M2 → M3 | Magnitude of the net portfolio reallocation between foreign-currency sovereign bonds and U.S. Treasuries | Investor population, source and destination assets, currency-basket composition, and period |

For all four groups, levels **1, 2, and 3** represent small, moderate, and large changes in the specified attribute. Use adjacent levels only; exclude **1 → 3**.

For M-RI, the strength attribute is the Treasury-demand response. Do not introduce an additional strength dimension for funding stress or risk aversion.

For M-CF, keep the reallocation direction unchanged within each sequence: foreign bonds to U.S. Treasuries for P, and the reverse for M. The associated currency sales and purchases follow the reallocation.

Apply the fixed conditions within each comparison. Allow downstream economic activity, yields, capital flows, and exchange rates to respond; do not hold these consequences fixed or introduce separate offsetting shocks.