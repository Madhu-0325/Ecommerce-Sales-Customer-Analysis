"""Reusable UI components for the Streamlit dashboard."""

from __future__ import annotations

from html import escape

import streamlit as st

from theme import ACCENTS

_SVG_ATTRS = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'

ICONS = {
    "revenue": f'<svg {_SVG_ATTRS}><path d="M12 2v20"/><path d="M17 5.5c-.8-1-2.1-1.5-3.7-1.5H10a3.5 3.5 0 0 0 0 7h4a3.5 3.5 0 0 1 0 7h-3.3c-1.6 0-2.9-.5-3.7-1.5"/></svg>',
    "purchases": f'<svg {_SVG_ATTRS}><path d="M6 7h12l1.5 13h-15L6 7Z"/><path d="M9 7a3 3 0 0 1 6 0"/></svg>',
    "sessions": f'<svg {_SVG_ATTRS}><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></svg>',
    "conversion": f'<svg {_SVG_ATTRS}><path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/></svg>',
    "aov": f'<svg {_SVG_ATTRS}><path d="M5 3h14v18l-2.5-1.5L14 21l-2-1.5L10 21l-2.5-1.5L5 21V3Z"/><path d="M9 8h6M9 12h6"/></svg>',
    "customers": f'<svg {_SVG_ATTRS}><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "repeat": f'<svg {_SVG_ATTRS}><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M3 21v-5h5M21 3v5h-5"/></svg>',
    "cart": f'<svg {_SVG_ATTRS}><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M3 3h2l2.5 12h11l2-8H6"/></svg>',
    "abandon": f'<svg {_SVG_ATTRS}><circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/></svg>',
    "time": f'<svg {_SVG_ATTRS}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "pages": f'<svg {_SVG_ATTRS}><path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/></svg>',
    "rating": f'<svg {_SVG_ATTRS}><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
    "channel": f'<svg {_SVG_ATTRS}><path d="M3 11v2a1 1 0 0 0 1 1h2l4 4V6L6 10H4a1 1 0 0 0-1 1Z"/><path d="M14 8a5 5 0 0 1 0 8M17 5a9 9 0 0 1 0 14"/></svg>',
    "discount": f'<svg {_SVG_ATTRS}><path d="M20.6 13.6 13.6 20.6a2 2 0 0 1-2.8 0l-7.4-7.4a2 2 0 0 1-.6-1.4V4a1 1 0 0 1 1-1h7.8a2 2 0 0 1 1.4.6l7.6 7.6a2 2 0 0 1 0 2.4Z"/><circle cx="7.5" cy="7.5" r="1.2"/></svg>',
    "units": f'<svg {_SVG_ATTRS}><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>',
    "calendar": f'<svg {_SVG_ATTRS}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></svg>',
    "star": f'<svg {_SVG_ATTRS}><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg>',
}


def _accent(name: str) -> str:
    return ACCENTS.get(name, ACCENTS["blue"])


def kpi_card(label: str, value: str, helper: str, icon: str = "revenue", accent: str = "blue") -> str:
    icon_markup = ICONS.get(icon, ICONS["revenue"])
    return f"""
    <div class="kpi-card" style="--accent:{_accent(accent)}">
        <div class="kpi-card-top">
            <span class="kpi-label">{escape(label)}</span>
            <span class="kpi-icon">{icon_markup}</span>
        </div>
        <div class="kpi-value">{escape(value)}</div>
        <div class="kpi-helper">{escape(helper)}</div>
        <div class="kpi-glow"></div>
    </div>
    """


def render_kpi_row(items: list[dict]) -> None:
    columns = st.columns(len(items) if items else 1, gap="medium")
    for column, item in zip(columns, items):
        with column:
            st.markdown(kpi_card(**item), unsafe_allow_html=True)


def page_header(page_number: str, title: str, subtitle: str, context: str | None = None) -> None:
    context_html = f'<span class="page-context">{escape(context)}</span>' if context else ""
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <div class="page-eyebrow">PAGE {escape(page_number)} <span class="dot"></span> E-COMMERCE ANALYTICS</div>
                <h1>{escape(title)}</h1>
                <p>{escape(subtitle)}</p>
            </div>
            {context_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-mark"></div>
            <div><h3>{escape(title)}</h3>{subtitle_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(text: str, label: str = "Key insight") -> None:
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-label">{escape(label)}</div>
            <div class="insight-text">{escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    st.markdown(f'<div class="chart-note">{escape(text)}</div>', unsafe_allow_html=True)


def sidebar_brand() -> None:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">EA</div>
            <div>
                <div class="brand-title">E-Commerce Analytics</div>
                <div class="brand-subtitle">Sales &amp; Customer Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(title: str) -> None:
    st.markdown(f'<div class="sidebar-section-title">{escape(title)}</div>', unsafe_allow_html=True)
