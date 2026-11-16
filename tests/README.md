# Tests

Browser tests for the app with a stand-in voice connection and stand-in services.

Run from the repository root, for example:

    python3 tests/t19.py
    python3 tests/audit.py s

Needs Python with Playwright and Chrome. Screenshots go to `tests/out/`.

The app needs an account. Run older tests through `tests/run.py`, which signs in a test account first:

    python3 tests/run.py tests/t21.py
