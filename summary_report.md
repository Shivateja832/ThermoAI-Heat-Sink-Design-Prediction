# Heat-Sink Surrogate Assessment Summary

## Deliverables

- `Heat_Sink_calculation.py`: parameterized calculator, sweep, surrogate training, metrics, and sensitivity analysis.
- `app.py`: local Streamlit interface for design estimates, surrogate validation, sensitivity, and downloads.
- `heat_sink_sweep.csv`: 6,000 calculated cases.
- `surrogate_metrics.csv`: holdout accuracy for both models and targets.
- `sensitivity_analysis.csv`: Pearson and Spearman input/output correlations.
- `assessment_responses.md`: written assessment responses for Tasks 2–4.

Install dependencies with `python -m pip install -r requirements.txt`, generate the assessment outputs with `python Heat_Sink_calculation.py`, then launch the local app with `python -m streamlit run app.py`.

## Assumptions

- The supplied Python calculation is retained as the quantitative model: fixed heat-sink geometry, 25 °C ambient, fixed air properties, the supplied Reynolds/Nusselt correlations, `R_jc = 0.2 °C/W`, and the existing convection-area equation.
- Sweep bounds are TDP 30–250 W, air velocity 0.5–15 m/s, and TIM conductivity 1–12 W/m·K. The full-factorial grid has 20, 25, and 12 evenly spaced levels respectively.
- Only these three inputs vary. TIM thickness, die geometry, heat-sink dimensions, airflow properties, and ambient temperature remain fixed.
- The dataset labels are deterministic outputs of the engineering equations, not measured hardware data. This tests surrogate fidelity to the calculation, not agreement with physical experiments.

## Key Results

The 6,000-row sweep includes all requested endpoints. At the starter script's default operating point (150 W, 1 m/s, 4 W/m·K), the retained model gives `R_total = 0.369205 °C/W` and `T_j = 80.381 °C`.

The supplied `Thermal_Reference.pdf` reports 0.373043 °C/W and 80.95652 °C for its Excel result. The starter-code result is close, but not identical. The reference prose also specifies `R_jc = 0.1 °C/W` and adds aluminum-base conduction, while the starter code uses `R_jc = 0.2 °C/W` and omits that conduction term. This implementation preserves the code's equations as directed by the assessment and records this source inconsistency instead of silently combining incompatible assumptions.

## Surrogate Accuracy

Evaluation uses a reproducible 80/20 random holdout (`random_state=42`). MAE and RMSE use each target's native units; R² is unitless.

| Model | Target | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Random Forest | Total resistance (°C/W) | 0.000911436 | 0.00222688 | 0.995210 |
| Extra Trees | Total resistance (°C/W) | 0.000617054 | 0.00239506 | 0.994459 |
| Random Forest | Junction temperature (°C) | 0.123148 | 0.349755 | 0.999727 |
| Extra Trees | Junction temperature (°C) | 0.0827038 | 0.372856 | 0.999689 |

Both ensemble tree models suit the nonlinear tabular response and require little feature scaling. Random Forest has lower RMSE and slightly higher R² for both targets; Extra Trees has lower MAE for both. The preferred model therefore depends on whether large errors or average absolute error are more important. The holdout is a random split of a regular grid, so its scores may overstate performance on genuinely unseen geometries or conditions.

## Correlation / Sensitivity

Pearson correlations from the sweep:

| Input | Total resistance | Junction temperature |
|---|---:|---:|
| TDP | approximately 0.000 | 0.969 |
| Air velocity | -0.795 | -0.177 |
| TIM conductivity | -0.252 | -0.056 |

Air velocity has the strongest observed correlation with total resistance; greater velocity lowers resistance in this model. TDP has no effect on calculated resistance, but is the strongest correlate of junction temperature because `T_j = T_ambient + TDP × R_total`. TIM conductivity lowers TIM resistance, with a smaller overall effect than airflow across these selected ranges. Correlations depend on the chosen input ranges and are not causal estimates independent of the model assumptions.

## Limitations and Improvements

- The model is steady-state and uses simplified convection correlations and the starter code's surface-area approximation; it does not represent transient behavior, fan curves, contact resistance, fin efficiency, radiation, or geometric variation.
- No experimental or high-fidelity simulation data are used. Surrogate accuracy measures reproduction of this calculation only.
- The source documents disagree on junction-to-case resistance and base conduction. Resolve these against an authoritative design specification before using the outputs for design decisions.
- Improve confidence with measured or validated simulation data, grouped/structured holdouts, uncertainty estimates, out-of-range detection, and physical constraints such as positive resistance and monotonic trends where applicable.

## Model Choice

Random Forest averages bootstrap trees and is the current choice if minimizing RMSE is the priority. Extra Trees randomizes split thresholds more aggressively and has lower MAE here. Neither model should be trusted outside the sampled input ranges; a physics solver remains the authority for design acceptance.