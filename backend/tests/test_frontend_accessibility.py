from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
JAVASCRIPT = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")


class ElementCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.elements.append((tag, dict(attrs)))


parser = ElementCollector()
parser.feed(HTML)
ELEMENTS = parser.elements


def elements_with_class(tag: str, class_name: str) -> list[dict[str, str | None]]:
    return [
        attrs
        for element_tag, attrs in ELEMENTS
        if element_tag == tag and class_name in (attrs.get("class") or "").split()
    ]


def element_by_id(element_id: str) -> dict[str, str | None]:
    matches = [
        attrs
        for _, attrs in ELEMENTS
        if attrs.get("id") == element_id
    ]
    assert len(matches) == 1
    return matches[0]


def test_navigation_exposes_names_and_active_state() -> None:
    navigation = elements_with_class("button", "nav-item")

    assert len(navigation) == 2
    assert {item["aria-label"] for item in navigation} == {
        "New analysis",
        "Case history",
    }
    assert [item["aria-pressed"] for item in navigation].count("true") == 1


def test_tabs_have_complete_aria_relationships() -> None:
    tabs = elements_with_class("button", "tab")

    assert len(tabs) == 3
    assert [tab["aria-selected"] for tab in tabs].count("true") == 1
    assert [tab["tabindex"] for tab in tabs].count("0") == 1

    for tab in tabs:
        panel = element_by_id(str(tab["aria-controls"]))
        assert panel["role"] == "tabpanel"
        assert panel["aria-labelledby"] == tab["id"]
        assert panel["tabindex"] == "0"


def test_focus_targets_and_table_headers_are_defined() -> None:
    for heading_id in ("analysisHeading", "resultHeading", "historyHeading"):
        assert element_by_id(heading_id)["tabindex"] == "-1"

    headers = [attrs for tag, attrs in ELEMENTS if tag == "th"]
    assert headers
    assert all(header.get("scope") == "col" for header in headers)


def test_keyboard_behavior_and_focus_updates_are_present() -> None:
    expected_javascript = (
        'event.key === "ArrowRight"',
        'event.key === "ArrowLeft"',
        'event.key === "Home"',
        'event.key === "End"',
        "panel.hidden = !active;",
        'byId("resultHeading").focus();',
        'item.setAttribute("aria-pressed", String(active));',
    )

    for expected in expected_javascript:
        assert expected in JAVASCRIPT


def test_visible_focus_styles_are_present() -> None:
    assert ":focus-visible" in CSS
    assert ".drop-zone:focus-within" in CSS