# DevDesk

A lightweight, open-source project, task, and notes dashboard built with Flask and SQLite.

## Features
- English by default, with Persian (Farsi) language switching
- No account registration or login
- Projects, tasks, and notes
- SQLite persistence
- Responsive RTL/LTR interface
- Windows-friendly startup script

## Run on Windows
1. Install Python 3.10 or newer.
2. Double-click `run_windows.bat`.
3. Open http://127.0.0.1:5000

## Data
The application creates `devdesk_public.db` beside `app.py`.
This database is ignored by Git so personal data is not committed.

## Security
This app has no authentication. Keep it local or use it only on a trusted network.
Do not expose it directly to the public internet without adding authentication and security protections.

## License
MIT