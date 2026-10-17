Keep the past time series and background information the same, and change only the scenario. Compare the average forecast change from the **neutral forecast**, which is made without a scenario.

- **Direction — 27 comparisons:** Compare each scenario with neutral. P scenarios should raise the party-support forecast, while M scenarios should lower it.
- **Contrast — 12 comparisons:** Compare each matched P and M pair. The P scenario should produce a higher average forecast than the M scenario.
- **Intensity — 18 comparisons:** Compare weaker and stronger conditions in the same direction. Stronger P conditions should raise the forecast more, while stronger M conditions should lower it more.

The table uses short IDs within each group. For example, Pa in the P-EC row means P-EC-Pa. The arrow `→` points from the weaker condition to the stronger condition.

| Group | Contrast pairs | Intensity pairs |
|:---|:---|:---|
| **P-EC — Economic conditions** | Pa ↔ Ma, Pb ↔ Mb, Pc ↔ Mc, Pd ↔ Md | Pa → Pb, Pc → Pd, Pa → Pc, Pb → Pd; Ma → Mb, Mc → Md, Ma → Mc, Mb → Md |
| **P-GV — Government performance and policy delivery** | Pa ↔ Ma, Pb ↔ Mb, Pc ↔ Mc, Pd ↔ Md | Pa → Pb, Pc → Pd, Pa → Pc, Pb → Pd; Ma → Mb, Mc → Md, Ma → Mc, Mb → Md |
| **P-LD — Leadership and party dynamics** | PU ↔ MU, PA ↔ MA | None |
| **P-PO — Policy positions and issue salience** | P1 ↔ M1, P2 ↔ M2 | P1 → P2; M1 → M2 |
| **P-CO — Political competition** | None | None |

Each Intensity comparison changes one attribute:

| Group and pairs | Change only | Keep fixed |
|:---|:---|:---|
| **P-EC:** a → b, c → d, for both P and M | Magnitude of the pay change relative to essential living costs | Layoffs change |
| **P-EC:** a → c, b → d, for both P and M | Magnitude of the layoffs change | Pay change relative to essential living costs |
| **P-GV:** a → b, c → d, for both P and M | Magnitude of the income-tax change | Pension-payment change |
| **P-GV:** a → c, b → d, for both P and M | Magnitude of the pension-payment change | Income-tax change |
| **P-PO:** P1 → P2, M1 → M2 | Magnitude of the proposed border-control shift | Public demand, initial policy position, and requested enforcement level |

For P-EC and P-GV, exclude **a → d** and **b ↔ c** because both attributes differ. Each row or column forms a separate two-level sequence; there is no single ordering of a, b, c, and d.

Keep populations, measurement definitions, and periods fixed. For P-GV, also fix the tax base, gross wages, pension eligibility, and recipient composition. Tax revenue and pension spending may change as consequences; do not impose a fixed government budget.

For P-PO, stronger P shifts must remain within the requested enforcement level. P-LD and P-CO contain different political events, so no Intensity ordering is assigned.