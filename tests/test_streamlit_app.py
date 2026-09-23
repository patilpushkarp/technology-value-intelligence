"""Unit and integration tests for the interactive Streamlit application."""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

VIEWS = [
    "Executive Spend & Variance",
    "Business Capability Costing",
    "Application TCO & Unit Economics",
    "Consumption Quadrants",
    "Application Rationalization",
    "Graph Dependencies & Blast Radius",
    "Investment & Benefit Realization (TVR)",
    "AI Knowledge Graph Analyst",
    "Board Executive Report"
]


def test_streamlit_app_default_view():
    """Verify default executive view renders without unhandled exceptions."""
    app_file = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"
    at = AppTest.from_file(str(app_file))
    at.run(timeout=20)
    assert not at.exception, f"App threw exception: {at.exception}"


@pytest.mark.parametrize("view_name", VIEWS)
def test_streamlit_all_views(view_name):
    """Verify that every single view in the application renders without exceptions."""
    app_file = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"
    at = AppTest.from_file(str(app_file))
    at.run(timeout=20)
    assert not at.exception

    if at.sidebar.radio:
        radio = at.sidebar.radio[0]
        radio.set_value(view_name)
        at.run(timeout=20)
        assert not at.exception, f"View {view_name} failed with exception: {at.exception}"


@pytest.mark.parametrize("query_text", [
    "Why did spend increase in August?",
    "Which business units depend on technology supplied by TechNova?",
    "What is the capital of France?"
])
def test_streamlit_ai_analyst_interaction(query_text):
    """Verify AI Knowledge Graph Analyst interaction does not raise KeyError or exception."""
    app_file = Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py"
    at = AppTest.from_file(str(app_file))
    at.run(timeout=20)
    assert not at.exception

    radio = at.sidebar.radio[0]
    radio.set_value("AI Knowledge Graph Analyst")
    at.run(timeout=20)
    assert not at.exception

    if at.button and at.text_input:
        at.text_input[0].set_value(query_text)
        at.button[0].click()
        at.run(timeout=20)
        assert not at.exception, f"Query '{query_text}' raised: {at.exception}"
