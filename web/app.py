"""Streamlit web UI driving all PIM Calculator flavours.

Engine selection (python/go/mojo), two data editors for TX/RX carriers,
results in tabs (IM3, IM5, RX Check, Charts). All compute state lives in
st.session_state so it survives widget-triggered reruns. Charting uses
Altair (bundled with streamlit) - declarative JSON rendered by the browser.
"""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

import pim_web

st.set_page_config(page_title="PIM Calculator", layout="wide")
st.title("PIM Calculator")

DEFAULT_TX = pd.DataFrame({"Frequency": [1980.0, 1940.0], "Bandwidth": [5.0, 5.0]})
DEFAULT_RX = pd.DataFrame({"Frequency": [1900.0, 1880.0], "Bandwidth": [5.0, 5.0]})

ENGINES = ["python", "go", "mojo", "mojo_py"]
available = {e: pim_web.engine_available(e) for e in ENGINES}

engine = st.radio(
    "Engine",
    ENGINES,
    format_func=lambda e: e if available[e] else f"{e} ({pim_web.ENGINE_HINTS[e]})",
    help="Unavailable engines show their missing prerequisite next to the name",
)

col_tx, col_rx = st.columns(2)
with col_tx:
    st.subheader("TX carriers")
    tx_df = st.data_editor(
        DEFAULT_TX,
        key="tx",
        num_rows="dynamic",
        column_config={
            "Frequency": st.column_config.NumberColumn(
                "Frequency [MHz]", min_value=0.0
            ),
            "Bandwidth": st.column_config.NumberColumn(
                "Bandwidth [MHz]", min_value=0.1
            ),
        },
    )
with col_rx:
    st.subheader("RX carriers")
    rx_df = st.data_editor(
        DEFAULT_RX,
        key="rx",
        num_rows="dynamic",
        column_config={
            "Frequency": st.column_config.NumberColumn(
                "Frequency [MHz]", min_value=0.0
            ),
            "Bandwidth": st.column_config.NumberColumn(
                "Bandwidth [MHz]", min_value=0.1
            ),
        },
    )

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("Calculate"):
    try:
        tx_freqs, tx_bws = pim_web.parse_rows(tx_df)
        rx_freqs, rx_bws = pim_web.parse_rows(rx_df)
        st.session_state.result = pim_web.compute(
            engine, tx_freqs, tx_bws, rx_freqs, rx_bws
        )
        st.session_state.calc_rx = (rx_freqs, rx_bws)
    except Exception as exc:  # noqa: BLE001 - surface any input/engine error in UI
        st.error(f"Calculation failed: {exc}")

result = st.session_state.result
if result is None:
    st.info("Set TX/RX carriers and press Calculate.")
else:
    rx_freqs, rx_bws = st.session_state.calc_rx

    tab_im3, tab_im5, tab_rx, tab_chart = st.tabs(["IM3", "IM5", "RX Check", "Charts"])

    for tab, order in ((tab_im3, "IM3"), (tab_im5, "IM5")):
        with tab:
            hits = result[f"{order}_rx_hits"]
            st.caption(
                f"engine: {result['engine']} - {len(result[order])} rows"
                f" ({len(hits)} RX hit{'s' if len(hits) != 1 else ''})"
            )
            st.dataframe(pim_web.order_table(result[order], hits))

    with tab_rx:
        all_hits = result["IM3_rx_hits"] + result["IM5_rx_hits"]
        if all_hits:
            for h in all_hits:
                st.warning(
                    f"{h['order']} cf={h['cf']} [{h['min']}, {h['max']}]"
                    f" overlaps RX {h['rx']}"
                )
            st.dataframe(pd.DataFrame(all_hits))
        else:
            st.success("No RX band is affected by any intermodulation product.")

    with tab_chart:
        frame = pim_web.chart_frame(result, rx_freqs, rx_bws)
        ink = "#9a9aa6"
        grid = "rgba(128,128,140,0.25)"
        chart = (
            alt.Chart(frame)
            .mark_area(opacity=0.35, line={"opacity": 1.0})
            .encode(
                x=alt.X("x", title="Frequency [MHz]"),
                y=alt.Y("y", title="Power (normalized)"),
                color="kind",
            )
            .configure_view(stroke=None)
            .configure_axis(
                labelColor=ink,
                titleColor=ink,
                gridColor=grid,
                domainColor=ink,
            )
            .configure_legend(labelColor=ink, titleColor=ink)
            .interactive()
        )
        st.altair_chart(chart, width="stretch")
