"""
Property of Expert Thermal/XThermal
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

L_die = 0.0525 #Die length in m
W_die = 0.045 #Die Width in m
Thickness_die = 0.0022 #die Thickness in m


TDP = 150  # Thermal Design Power in Watts
T_ambient = 25  # Ambient temperature in Celsius
L = 90e-3  # Heat sink length in meters
W = 116e-3  # Heat sink width in meters
H = 27e-3  # Heat sink height in meters
Fin_Thickness = 0.8e-3  # Fin thickness in meters
N_fins = 60  # Number of fins
Base_Thickness = 2.5e-3  # Base thickness in meters
V_air = 1  # Air velocity in m/s
k_tim = 4.0  # Thermal conductivity of thermal interface material (TIM) in W/m.K
t_tim = 0.1e-3  # TIM thickness in meters
R_jc = 0.2  # Junction-to-case thermal resistance in °C/W

FEATURES = ["TDP_W", "V_air_m_s", "k_tim_W_mK"]
TARGETS = ["R_total_C_per_W", "T_j_C"]


def heat_sink_design(tdp: float = TDP, v_air: float = V_air, tim_conductivity: float = k_tim) -> dict[str, float]:
    """Calculate steady-state performance for the fixed heat-sink geometry."""
    if not 30.0 <= tdp <= 250.0:
        raise ValueError("TDP must be between 30 and 250 W.")
    if not 0.5 <= v_air <= 15.0:
        raise ValueError("Air velocity must be between 0.5 and 15 m/s.")
    if not 1.0 <= tim_conductivity <= 12.0:
        raise ValueError("TIM conductivity must be between 1 and 12 W/m.K.")

    # Given constants for air at 25 degree C
    k_air = 0.0262  # Thermal conductivity of air (W/m.K)
    nu_air = 1.57e-5  # Kinematic viscosity of air (m²/s)
    Pr_air = 0.71  # Prandtl number

    # Fin Spacing Calculation
    s_f = (W - (N_fins * Fin_Thickness)) / (N_fins - 1)

    # Reynolds Number Calculation
    Re = (v_air * s_f) / nu_air

    # Nusselt Number Calculation (Laminar & Turbulent cases)
    if Re < 2300:  # Laminar flow assumption
        Nu = 1.86 * ((Re * Pr_air * (2 * s_f) / L) ** (1/3))
    else:  # Turbulent flow
        Nu = 0.023 * (Re**0.8) * (Pr_air**0.3)

    # Convective Heat Transfer Coefficient
    h = (Nu * k_air) / (2 * s_f)

    #fin Height

    h_fin = H-Base_Thickness

    # Effective Surface Area Calculation
    A_fin = N_fins * (2 * h_fin * L)+ (s_f * L)
    A_Total_base = (L * W)

    A_base_convection = A_Total_base-(Fin_Thickness*N_fins*L) #only this area is exposed for convectionn

    A_total = A_fin + A_base_convection

    # Convective Thermal Resistance
    R_conv = 1 / (h * A_total)

    # TIM Thermal Resistance
    A_die = L_die*W_die # die area where thermal insulation is done
    R_tim = t_tim / (tim_conductivity * A_die)

    # Total Heat Sink Thermal Resistance
    R_hs = R_conv + R_tim

    # Total Thermal Resistance
    R_total = R_jc + R_hs

    # Junction Temperature Calculation
    T_j = T_ambient + (tdp * R_total)

    return {
        "Re": Re,
        "Nu": Nu,
        "h_W_m2K": h,
        "R_conv_C_per_W": R_conv,
        "R_tim_C_per_W": R_tim,
        "R_total_C_per_W": R_total,
        "T_j_C": T_j,
    }


def generate_dataset() -> pd.DataFrame:
    """Evaluate a full-factorial sweep including each requested range endpoint."""
    rows = []
    for tdp in np.linspace(30.0, 250.0, 20):
        for velocity in np.linspace(0.5, 15.0, 25):
            for conductivity in np.linspace(1.0, 12.0, 12):
                result = heat_sink_design(tdp, velocity, conductivity)
                rows.append({
                    "TDP_W": tdp,
                    "V_air_m_s": velocity,
                    "k_tim_W_mK": conductivity,
                    **result,
                })
    return pd.DataFrame(rows)


def evaluate_surrogates(dataset: pd.DataFrame) -> pd.DataFrame:
    """Fit two tree regressors and evaluate both requested outputs."""
    train_features, test_features, train_targets, test_targets = train_test_split(
        dataset[FEATURES], dataset[TARGETS], test_size=0.2, random_state=42
    )
    models = {
        "RandomForest": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=300, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
    }
    records = []
    for model_name, model in models.items():
        model.fit(train_features, train_targets)
        predictions = model.predict(test_features)
        for index, target in enumerate(TARGETS):
            actual = test_targets[target].to_numpy()
            predicted = predictions[:, index]
            records.append({
                "model": model_name,
                "target": target,
                "MAE": mean_absolute_error(actual, predicted),
                "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
                "R2": r2_score(actual, predicted),
            })
    return pd.DataFrame(records)


def analyze_sensitivity(dataset: pd.DataFrame) -> pd.DataFrame:
    """Calculate Pearson and Spearman input/output correlations."""
    records = []
    for feature in FEATURES:
        for target in TARGETS:
            records.append({
                "feature": feature,
                "target": target,
                "pearson_r": dataset[feature].corr(dataset[target], method="pearson"),
                "spearman_rho": dataset[feature].corr(dataset[target], method="spearman"),
            })
    return pd.DataFrame(records)


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    dataset = generate_dataset()
    dataset_path = output_dir / "heat_sink_sweep.csv"
    dataset.to_csv(dataset_path, index=False, float_format="%.17g")
    dataset = pd.read_csv(dataset_path)
    metrics = evaluate_surrogates(dataset)
    sensitivity = analyze_sensitivity(dataset)

    metrics.to_csv(output_dir / "surrogate_metrics.csv", index=False, float_format="%.17g")
    sensitivity.to_csv(output_dir / "sensitivity_analysis.csv", index=False, float_format="%.17g")
    print(f"Dataset: {len(dataset)} rows -> heat_sink_sweep.csv")
    print("Surrogate metrics (80/20 random holdout):")
    print(metrics.to_string(index=False, float_format=lambda value: f"{value:.6g}"))
    print("Input/output correlations:")
    print(sensitivity.to_string(index=False, float_format=lambda value: f"{value:.6g}"))


if __name__ == "__main__":
    main()