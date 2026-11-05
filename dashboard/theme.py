"""Visual theme: navy palette, Plotly template and chart helpers."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

COLORS = {
    "bg": "#0B1220",
    "bg_secondary": "#0E1728",
    "panel": "#111C2E",
    "panel_alt": "#16233A",
    "border": "rgba(96, 165, 250, 0.16)",
    "text": "#E7EEF9",
    "muted": "#8FA3BF",
    "blue": "#3B82F6",
    "cyan": "#22D3EE",
    "purple": "#A855F7",
    "indigo": "#818CF8",
    "sky": "#38BDF8",
    "pink": "#F472B6",
    "green": "#34D399",
    "amber": "#FBBF24",
    "red": "#FB7185",
    "grid": "rgba(148, 163, 184, 0.12)",
}

ACCENTS = {
    "blue": "#3B82F6",
    "cyan": "#22D3EE",
    "purple": "#A855F7",
    "indigo": "#818CF8",
    "green": "#34D399",
    "amber": "#FBBF24",
    "pink": "#F472B6",
    "red": "#FB7185",
}

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
    "scrollZoom": False,
}

_TEMPLATE_REGISTERED = False


def register_theme() -> None:
    """Register one consistent Plotly template for all pages."""
    global _TEMPLATE_REGISTERED
    if _TEMPLATE_REGISTERED:
        return

    template = go.layout.Template()
    template.layout = go.Layout(
        colorway=[COLORS["blue"], COLORS["cyan"], COLORS["purple"], COLORS["indigo"], COLORS["sky"], COLORS["pink"]],
        font=dict(family="Segoe UI, Inter, system-ui, sans-serif", color=COLORS["text"], size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(
            bgcolor=COLORS["panel_alt"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text"], size=12, family="Segoe UI, Inter, sans-serif"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["muted"], size=11),
        ),
        xaxis=dict(
            gridcolor=COLORS["grid"],
            zerolinecolor=COLORS["grid"],
            linecolor="rgba(148,163,184,0.20)",
            tickfont=dict(color=COLORS["muted"], size=11),
            title=dict(font=dict(color=COLORS["muted"], size=11)),
            automargin=True,
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"],
            zerolinecolor=COLORS["grid"],
            linecolor="rgba(148,163,184,0.20)",
            tickfont=dict(color=COLORS["muted"], size=11),
            title=dict(font=dict(color=COLORS["muted"], size=11)),
            automargin=True,
        ),
        margin=dict(l=16, r=16, t=48, b=16),
    )
    pio.templates["ecommerce_navy"] = template
    pio.templates.default = "ecommerce_navy"
    _TEMPLATE_REGISTERED = True


def style_figure(
    fig: go.Figure,
    *,
    height: int = 390,
    title: str | None = None,
    legend: bool = True,
    hovermode: str | None = "x unified",
) -> go.Figure:
    """Apply consistent sizing, spacing and legend placement."""
    layout = {
        "template": "ecommerce_navy",
        "height": height,
        "hovermode": hovermode,
        "margin": dict(l=16, r=16, t=56 if title else 22, b=16),
    }
    if title:
        layout["title"] = dict(
            text=title,
            x=0.01,
            xanchor="left",
            font=dict(size=14, color=COLORS["text"], family="Segoe UI, Inter, sans-serif"),
        )
    if legend:
        layout["legend"] = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["muted"], size=11),
        )
    fig.update_layout(**layout)
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def load_css() -> str:
    css_path = ASSETS_DIR / "styles.css"
    return css_path.read_text(encoding="utf-8") if css_path.exists() else ""
