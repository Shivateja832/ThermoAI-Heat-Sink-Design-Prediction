from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split

from Heat_Sink_calculation import (
    FEATURES,
    TARGETS,
    analyze_sensitivity,
    evaluate_surrogates,
    generate_dataset,
    heat_sink_design,
)

APP_DIR = Path(__file__).resolve().parent
def display_dataframe(data: pd.DataFrame, **kwargs: Any) -> None:
    streamlit_version = tuple(int(part) for part in st.__version__.split(".")[:2])
    if streamlit_version >= (1, 49):
        kwargs["width"] = "stretch"
    else:
        kwargs["use_container_width"] = True
    st.dataframe(data, **kwargs)


DATASET_PATH = APP_DIR / "heat_sink_sweep.csv"
METRICS_PATH = APP_DIR / "surrogate_metrics.csv"
SENSITIVITY_PATH = APP_DIR / "sensitivity_analysis.csv"
REPORT_PATH = APP_DIR / "summary_report.md"

st.set_page_config(page_title="Thermal Design Explorer", page_icon="T", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --ink: #17352f;
        --muted: #62726c;
        --surface: #f5f7f3;
        --line: #dce4dc;
        --accent: #087f70;
    }
    .stApp { background: var(--surface); }
    [data-testid="stHeader"] { background: rgba(245, 247, 243, 0.94); }
    h1, h2, h3 { color: var(--ink); }
    .eyebrow {
        color: var(--accent); font-size: 0.76rem; font-weight: 700;
        letter-spacing: 0.08em; text-transform: uppercase;
    }
    .subtle { color: var(--muted); }
    div[data-testid="stMetric"] {
        background: #ffffff; border: 1px solid var(--line);
        border-radius: 6px; padding: 14px 16px;
    }
    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 5px; border: 1px solid var(--accent);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading parameter sweep...")
def load_dataset() -> pd.DataFrame:
    if DATASET_PATH.exists():
        return pd.read_csv(DATASET_PATH)
    dataset = generate_dataset()
    dataset.to_csv(DATASET_PATH, index=False, float_format="%.17g")
    return dataset


@st.cache_data(show_spinner=False)
def load_metrics() -> pd.DataFrame:
    if METRICS_PATH.exists():
        return pd.read_csv(METRICS_PATH)
    metrics = evaluate_surrogates(load_dataset())
    metrics.to_csv(METRICS_PATH, index=False, float_format="%.10g")
    return metrics


@st.cache_data(show_spinner=False)
def load_sensitivity() -> pd.DataFrame:
    if SENSITIVITY_PATH.exists():
        return pd.read_csv(SENSITIVITY_PATH)
    sensitivity = analyze_sensitivity(load_dataset())
    sensitivity.to_csv(SENSITIVITY_PATH, index=False, float_format="%.10g")
    return sensitivity


@st.cache_resource(show_spinner="Preparing surrogate models...")
def train_models() -> dict[str, object]:
    dataset = load_dataset()
    train_features, _, train_targets, _ = train_test_split(
        dataset[FEATURES], dataset[TARGETS], test_size=0.2, random_state=42
    )
    models = {
        "Random Forest": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
        "Extra Trees": ExtraTreesRegressor(
            n_estimators=300, min_samples_leaf=1, random_state=42, n_jobs=-1
        ),
    }
    for model in models.values():
        model.fit(train_features, train_targets)
    return models


st.markdown('<p class="eyebrow">XThermal · Thermal engineering</p>', unsafe_allow_html=True)
st.title("Heat-sink design explorer")
st.markdown(
    '<p class="subtle">Physics calculation, ML surrogate comparison, and parameter-sweep results.</p>',
    unsafe_allow_html=True,
)

design_tab, validation_tab, data_tab = st.tabs(
    ["Design estimate", "Model validation", "Sensitivity and data"]
)

with design_tab:
    controls, results = st.columns([0.85, 1.65], gap="large")
    with controls:
        st.subheader("Operating point")
        tdp = st.slider("Thermal design power (W)", 30, 250, 150, 5)
        velocity = st.slider("Air velocity (m/s)", 0.5, 15.0, 1.0, 0.5)
        conductivity = st.slider("TIM conductivity (W/m·K)", 1.0, 12.0, 4.0, 0.5)
        model_name = st.radio("Surrogate", ["Random Forest", "Extra Trees"], horizontal=True)

    physics = heat_sink_design(float(tdp), float(velocity), float(conductivity))
    models = train_models()
    model_input = pd.DataFrame(
        [[float(tdp), float(velocity), float(conductivity)]], columns=FEATURES
    )
    estimate = models[model_name].predict(model_input)[0]
    with results:
        st.subheader("Predicted performance")
        physics_column, surrogate_column = st.columns(2)
        with physics_column:
            st.markdown("**Engineering model**")
            st.metric("Total thermal resistance", f"{physics['R_total_C_per_W']:.5f} °C/W")
            st.metric("Junction temperature", f"{physics['T_j_C']:.2f} °C")
        with surrogate_column:
            st.markdown(f"**{model_name} surrogate**")
            st.metric("Total thermal resistance", f"{estimate[0]:.5f} °C/W")
            st.metric("Junction temperature", f"{estimate[1]:.2f} °C")
        resistance_difference = estimate[0] - physics["R_total_C_per_W"]
        temperature_difference = estimate[1] - physics["T_j_C"]
        st.caption(
            "Surrogate minus engineering model: "
            f"{resistance_difference:+.5f} °C/W and {temperature_difference:+.3f} °C. "
            "Use the engineering model as the reference; the surrogate is valid only within the swept ranges."
        )
        display_dataframe(
            pd.DataFrame(
                {
                    "Quantity": ["Air Reynolds number", "Nusselt number", "Convection coefficient"],
                    "Value": [
                        f"{physics['Re']:.2f}",
                        f"{physics['Nu']:.3f}",
                        f"{physics['h_W_m2K']:.2f} W/m²·K",
                    ],
                }
            ),
            hide_index=True,
        )

with validation_tab:
    st.subheader("Holdout accuracy")
    st.caption("Reproducible 80/20 random split, seed 42. MAE and RMSE are in target units.")
    display_dataframe(load_metrics(), hide_index=True)

with data_tab:
    st.subheader("Parameter sensitivity")
    st.caption("Pearson and Spearman correlations over the generated sweep; correlation is not causal evidence.")
    display_dataframe(load_sensitivity(), hide_index=True)
    st.subheader("Sweep dataset")
    dataset = load_dataset()
    st.caption(f"{len(dataset):,} deterministic cases from the supplied engineering calculation.")
    display_dataframe(dataset.head(100), hide_index=True)
    st.download_button(
        "Download full sweep CSV",
        data=dataset.to_csv(index=False).encode("utf-8"),
        file_name="heat_sink_sweep.csv",
        mime="text/csv",
    )
    if REPORT_PATH.exists():
        st.download_button(
            "Download summary report",
            data=REPORT_PATH.read_bytes(),
            file_name="summary_report.md",
            mime="text/markdown",
        )