"""Offline tests for the HTTP layer: no request leaves the process."""

import json

import httpx
import pytest

from mcp_server_fxmacrodata import server

KEY = "test-key-123"


@pytest.fixture
def api(monkeypatch):
    """Route every request to a handler; record what was sent."""
    sent = []
    state = {"handler": lambda request: httpx.Response(200, json={"data": []})}

    def transport(request):
        sent.append(request)
        return state["handler"](request)

    monkeypatch.setattr(server, "API_KEY", KEY)
    monkeypatch.setattr(
        server,
        "_http",
        httpx.Client(transport=httpx.MockTransport(transport), follow_redirects=False),
    )

    def use(handler):
        state["handler"] = handler
        return sent

    return use


def test_currency_list_matches_public_catalogue():
    assert len(server.SUPPORTED_CURRENCIES) == 22
    assert "PLN" not in server.SUPPORTED_CURRENCIES
    assert "SGD" not in server.SUPPORTED_CURRENCIES
    assert "22 currencies" in server.mcp.instructions
    for code in server.SUPPORTED_CURRENCIES:
        assert code in server.mcp.instructions
    desc = {t.name: t.description for t in server.mcp._tool_manager.list_tools()}
    assert server._CURRENCY_LIST in desc["data_catalogue"]
    assert "PLN" not in desc["data_catalogue"]


def test_success_returns_json_and_sends_header(api):
    sent = api(lambda r: httpx.Response(200, json={"data": [{"val": 1}]}))
    out = json.loads(server.indicator_query(" AUD ", "Inflation", start_date="2025-01-01"))
    assert out == {"data": [{"val": 1}]}
    req = sent[0]
    assert req.url.path == "/v1/announcements/aud/inflation"
    assert req.url.params["start_date"] == "2025-01-01"
    assert "end_date" not in req.url.params
    assert req.headers["X-API-Key"] == KEY
    assert KEY not in str(req.url)


def test_path_segments_are_escaped(api):
    sent = api(lambda r: httpx.Response(200, json={"data": []}))
    server.data_catalogue("../ping")
    assert sent[0].url.raw_path.startswith(b"/v1/data_catalogue/..%2Fping")


def test_redirect_is_not_followed(api):
    sent = api(lambda r: httpx.Response(302, headers={"Location": "https://evil.example/x"}))
    out = json.loads(server.ping())
    assert "redirect" in out["error"]
    assert len(sent) == 1
    assert sent[0].url.host != "evil.example"


def test_401_gives_subscribe_help_without_key(api):
    api(lambda r: httpx.Response(401, json={"detail": f"bad key {KEY}"}))
    raw = server.forex("eur", "usd")
    out = json.loads(raw)
    assert "requires an API key" in out["error"]
    assert "api-management" in out["help"]
    assert KEY not in raw


def test_error_text_never_contains_key(api):
    api(lambda r: httpx.Response(500, text=f"boom {KEY}"))
    raw = server.cot_data("eur")
    assert KEY not in raw
    assert json.loads(raw)["error"].startswith("500")


def test_200_with_error_body_is_an_error(api):
    api(lambda r: httpx.Response(200, json={"error": "upstream unavailable"}))
    assert json.loads(server.commodities("gold")) == {"error": "upstream unavailable"}


def test_200_non_json_is_an_error(api):
    api(lambda r: httpx.Response(200, text="<html>maintenance</html>"))
    assert "non-JSON" in json.loads(server.market_sessions())["error"]


def test_timeout_is_reported(api):
    def raise_timeout(request):
        raise httpx.ReadTimeout("slow", request=request)

    api(raise_timeout)
    assert "timed out" in json.loads(server.release_calendar("usd"))["error"]


def test_transport_error_hides_details(api):
    def raise_connect(request):
        raise httpx.ConnectError(f"cannot reach {request.url} {KEY}", request=request)

    api(raise_connect)
    raw = server.ping()
    assert KEY not in raw
    assert "ConnectError" in json.loads(raw)["error"]


def test_comm_routes_to_commodities(api):
    sent = api(lambda r: httpx.Response(200, json={"data": []}))
    server.indicator_query("comm", "gold")
    assert sent[0].url.path == "/v1/commodities/gold"


def test_client_has_timeout_and_no_redirects():
    assert server._http.follow_redirects is False
    assert server._http.timeout.read is not None


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, "https://api.fxmacrodata.com"),
        ("https://example.test/", "https://example.test"),
        ("http://localhost:8080", "http://localhost:8080"),
        ("http://127.0.0.1:8000/", "http://127.0.0.1:8000"),
    ],
)
def test_base_url_accepted(raw, expected):
    assert server._resolve_base_url(raw) == expected


@pytest.mark.parametrize("raw", ["http://api.example.com", "ftp://x", "api.fxmacrodata.com"])
def test_base_url_rejected(raw):
    with pytest.raises(ValueError):
        server._resolve_base_url(raw)


@pytest.mark.parametrize(
    "bad_key",
    [f"{KEY} x", f"{KEY}\tx", f"{KEY}\x00", f"{KEY}\r\nX-Injected: 1", f"{KEY}é"],
)
def test_malformed_key_is_rejected_before_sending(api, monkeypatch, bad_key):
    sent = api(lambda r: httpx.Response(200, json={"status": "ok"}))
    monkeypatch.setattr(server, "API_KEY", bad_key)
    raw = server.ping()
    assert "FXMACRODATA_API_KEY" in json.loads(raw)["error"]
    assert KEY not in raw
    assert sent == []


@pytest.mark.parametrize(
    "raw,expected",
    [(None, 30.0), ("", 30.0), ("12", 12.0), ("2.5", 2.5), ("abc", 30.0), ("0", 30.0), ("-5", 30.0)],
)
def test_env_timeout(raw, expected):
    assert server._env_timeout(raw) == expected
