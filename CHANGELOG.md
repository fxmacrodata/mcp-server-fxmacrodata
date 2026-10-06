# Changelog

## 0.1.3 - 2026-10-06

### Changed

- The currency list in the server instructions and tool descriptions now
  matches the public catalogue: 22 currencies, driven by one
  `SUPPORTED_CURRENCIES` constant.
- The server calls the API directly with one `httpx` client instead of going
  through the `fxmacrodata` SDK.

### Security

- Redirects are never followed, so the API key cannot be re-sent to another
  host.
- `FXMACRODATA_BASE_URL` must be `https://`, except for `localhost`,
  `127.0.0.1` and `::1`.
- The API key never appears in tool output. A key with spaces, control
  characters or non-ASCII characters is rejected before any request is made.
- The configured API key is sent on USD requests too, so subscribers get
  real-time USD data instead of the free tier.

### Added

- `FXMACRODATA_TIMEOUT` environment variable (seconds, default 30).

### Fixed

- HTTP errors, timeouts, non-JSON bodies and HTTP 200 responses carrying an
  error message are returned as a JSON `{"error": ...}` result instead of
  raising.
- Path segments (currency, indicator, pair) are URL-escaped.
- Surrounding whitespace in `FXMACRODATA_API_KEY` is stripped.
