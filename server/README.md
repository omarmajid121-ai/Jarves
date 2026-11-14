# Musaed call server

Places a phone call through Twilio and lets the assistant speak on the owner's behalf with the same voice as the app.

Run on Render as a Web Service: root directory `server`, build `npm install`, start `npm start`.

Environment variables (set them in the host, never in code):

- `GEMINI_KEY` – Google AI key
- `TWILIO_SID`, `TWILIO_TOKEN` – Twilio account
- `TWILIO_FROM` – the Twilio number, e.g. `+17372508034`
- `APP_SECRET` – passphrase (12+ characters) typed into the app's settings
- `OWNER_NAME` – the name she calls on behalf of
- Optional: `MAX_CALL_SECONDS` (300), `MAX_CALLS_PER_DAY` (20), `ALLOWED_ORIGINS`, `GEMINI_MODEL`
