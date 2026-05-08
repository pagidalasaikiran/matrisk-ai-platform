"""
MatRisk AI - Chart Components
Altair charts with defensive encoding and Plotly fallbacks.
All charts use explicit dtypes and reset_index to prevent schema errors.
"""

import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
from utils.constants import COLORS, CHART_COLORS


def _safe_chart_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for Altair by resetting index and ensuring no IntervalIndex."""
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.reset_index(drop=True)
    # Convert any Interval or Category columns to strings to prevent serialization errors
    for col in df.columns:
        dtype_str = str(df[col].dtype).lower()
        if 'interval' in dtype_str or 'category' in dtype_str:
            df[col] = df[col].astype(str)
        elif pd.api.types.is_object_dtype(df[col]):
            # Ensure everything in object columns is stringable
            df[col] = df[col].fillna("N/A").astype(str)
    return df


def line_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
               title: str = "", height: int = 350, x_title: str = "", y_title: str = ""):
    """Create an Altair line chart with defensive encoding."""
    df = _safe_chart_df(df)
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No data available for chart.")
        return None

    # Ensure x column is proper type for Altair
    x_type = ":T" if pd.api.types.is_datetime64_any_dtype(df[x]) else ":Q"
    y_type = ":Q"

    encoding = {
        "x": alt.X(f"{x}{x_type}", title=x_title or x),
        "y": alt.Y(f"{y}{y_type}", title=y_title or y),
    }

    if color and color in df.columns:
        df[color] = df[color].astype(str)
        encoding["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=CHART_COLORS), legend=alt.Legend(title=color))

    chart = (
        alt.Chart(df, title=title)
        .mark_line(strokeWidth=2, opacity=0.9)
        .encode(**encoding)
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
            gridColor="#334155",
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
              title: str = "", height: int = 350, horizontal: bool = False,
              x_title: str = "", y_title: str = ""):
    """Create an Altair bar chart."""
    df = _safe_chart_df(df)
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No data available for chart.")
        return None

    df[x] = df[x].astype(str)

    if horizontal:
        encoding = {
            "y": alt.Y(f"{x}:N", title=x_title or x, sort="-x"),
            "x": alt.X(f"{y}:Q", title=y_title or y),
        }
    else:
        encoding = {
            "x": alt.X(f"{x}:N", title=x_title or x, sort="-y"),
            "y": alt.Y(f"{y}:Q", title=y_title or y),
        }

    if color and color in df.columns:
        df[color] = df[color].astype(str)
        encoding["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=CHART_COLORS))
    else:
        encoding["color"] = alt.value(COLORS["primary"])

    chart = (
        alt.Chart(df, title=title)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, opacity=0.85)
        .encode(**encoding)
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
            gridColor="#334155",
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
                  size: str = None, title: str = "", height: int = 350,
                  x_title: str = "", y_title: str = ""):
    """Create an Altair scatter plot."""
    df = _safe_chart_df(df)
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No data available for chart.")
        return None

    encoding = {
        "x": alt.X(f"{x}:Q", title=x_title or x),
        "y": alt.Y(f"{y}:Q", title=y_title or y),
        "tooltip": [x, y],
    }

    if color and color in df.columns:
        df[color] = df[color].astype(str)
        encoding["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=CHART_COLORS))

    if size and size in df.columns:
        encoding["size"] = alt.Size(f"{size}:Q")

    chart = (
        alt.Chart(df, title=title)
        .mark_circle(opacity=0.7)
        .encode(**encoding)
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
            gridColor="#334155",
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def area_chart(df: pd.DataFrame, x: str, y: str, color: str = None,
               title: str = "", height: int = 350):
    """Create an Altair area chart."""
    df = _safe_chart_df(df)
    if df.empty or x not in df.columns or y not in df.columns:
        st.info("No data available for chart.")
        return None

    x_type = ":T" if pd.api.types.is_datetime64_any_dtype(df[x]) else ":Q"

    encoding = {
        "x": alt.X(f"{x}{x_type}", title=x),
        "y": alt.Y(f"{y}:Q", title=y),
    }

    if color and color in df.columns:
        df[color] = df[color].astype(str)
        encoding["color"] = alt.Color(f"{color}:N", scale=alt.Scale(range=CHART_COLORS))

    chart = (
        alt.Chart(df, title=title)
        .mark_area(opacity=0.5, line=True)
        .encode(**encoding)
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
            gridColor="#334155",
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def heatmap_chart(df: pd.DataFrame, x: str, y: str, color_field: str,
                  title: str = "", height: int = 350):
    """Create an Altair heatmap."""
    df = _safe_chart_df(df)
    if df.empty or x not in df.columns or y not in df.columns or color_field not in df.columns:
        st.info("No data available for heatmap.")
        return None

    df[x] = df[x].astype(str)
    df[y] = df[y].astype(str)

    chart = (
        alt.Chart(df, title=title)
        .mark_rect(cornerRadius=4)
        .encode(
            x=alt.X(f"{x}:N", title=x),
            y=alt.Y(f"{y}:N", title=y),
            color=alt.Color(f"{color_field}:Q", scale=alt.Scale(scheme="turbo")),
            tooltip=[x, y, color_field],
        )
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def histogram_chart(df: pd.DataFrame, field: str, bins: int = 30,
                    title: str = "", height: int = 300):
    """Create an Altair histogram."""
    df = _safe_chart_df(df)
    if df.empty or field not in df.columns:
        st.info("No data available for histogram.")
        return None

    chart = (
        alt.Chart(df, title=title)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color=COLORS["primary"], opacity=0.8)
        .encode(
            x=alt.X(f"{field}:Q", bin=alt.Bin(maxbins=bins), title=field),
            y=alt.Y("count():Q", title="Count"),
        )
        .properties(height=height)
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=COLORS["text_muted"],
            titleColor=COLORS["text"],
            gridColor="#334155",
        )
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart


def donut_chart(df: pd.DataFrame, category: str, value: str,
                title: str = "", height: int = 300):
    """Create an Altair donut chart."""
    df = _safe_chart_df(df)
    if df.empty or category not in df.columns or value not in df.columns:
        st.info("No data available for chart.")
        return None

    df[category] = df[category].astype(str)

    chart = (
        alt.Chart(df, title=title)
        .mark_arc(innerRadius=50, cornerRadius=4, opacity=0.85)
        .encode(
            theta=alt.Theta(f"{value}:Q"),
            color=alt.Color(f"{category}:N", scale=alt.Scale(range=CHART_COLORS)),
            tooltip=[category, value],
        )
        .properties(height=height)
        .configure_title(color=COLORS["primary"])
    )
    st.altair_chart(chart, use_container_width=True)
    return chart
