# What-If TSF(WIT): A Benchmark for Scenario-Guided Multimodal Time Series Forecasting

We provide a scenario-guided multimodal time-series forecasting benchmark in the Energy, Economy, and Politics domains. It connects numerical histories, domain knowledge, source-supported scenarios, controlled relations, and empirical matched cases through **Factual**, **Relational**, and **Grounded Comparison**. The neutral case uses the same historical time series and domain background without a future scenario and serves as the common baseline for all three comparisons.

## Benchmark configuration

<table>
  <thead>
    <tr>
      <th rowspan="2">Domain</th>
      <th rowspan="2">Factual scenarios</th>
      <th colspan="4">Relational Comparison (per anchor)</th>
      <th rowspan="2">Grounded sets</th>
    </tr>
    <tr>
      <th>Direction</th>
      <th>Contrast</th>
      <th>Intensity</th>
      <th>Restraint</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Energy</td>
      <td align="center">38</td>
      <td align="center">30</td>
      <td align="center">15</td>
      <td align="center">20</td>
      <td align="center">3</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td>Economy</td>
      <td align="center">38</td>
      <td align="center">24</td>
      <td align="center">12</td>
      <td align="center">16</td>
      <td align="center">3</td>
      <td align="center">11</td>
    </tr>
    <tr>
      <td>Politics</td>
      <td align="center">38</td>
      <td align="center">27</td>
      <td align="center">12</td>
      <td align="center">18</td>
      <td align="center">3</td>
      <td align="center">6</td>
    </tr>
  </tbody>
</table>

- **Factual Comparison:** Checks whether factual scenario information improves prediction of the observed future compared with the neutral case.
- **Relational Comparison:** Checks whether scenario-induced revisions from the neutral forecast respect scenario meaning and relationships. An anchor is one forecasting case with a fixed historical window and forecast origin.

    - **Direction:** Checks whether the mean forecast shifts in the expected direction from neutral.
    - **Contrast:** Checks whether the mean revision from neutral is higher for an upward scenario than for its paired downward scenario.
    - **Intensity:** Checks whether a stronger scenario yields a higher mean revision from neutral than its weaker counterpart for an upward effect, or a lower one for a downward effect.
    - **Restraint:** Checks whether an irrelevant scenario leaves the forecast close to neutral.

- **Grounded Comparison:** Checks whether scenario-induced revisions from the neutral forecast resemble how actual outcomes differ from each matched case's own neutral forecast. Each set contains 3 or 4 matched cases.

## Model inference and evaluation

See `evaluation/` for inference and evaluation code for **Directly prompted LLMs and Context-aware forecasting systems**.

## Data construction for other domains

- Users provide the numerical series, relevant textual sources, and a target definition with units. WIT's reusable construction pipeline drafts the domain background and mechanism map from those sources, then supports scenario construction and relation labeling. The generated outputs should be reviewed before use.
- See the `construction/` folder for the related code.
