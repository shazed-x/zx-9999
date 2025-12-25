# ZX9999 Command Studio

ZX9999 is a Django-based web interface for building, editing, and staging CLI command presets.
It is designed for authorized, defensive use (labs, CTFs, approved assessments).

## Features
- Dark, operator-focused UI with automatic command generation.
- Multi-page console layout (Overview, Composer, Library, Manage, Import/Export).
- Tool and command template management from the browser.
- Placeholder-driven inputs (e.g. `{target}`, `{port}`, `{domain}`).
- Search and category filters for faster lookup.
- JSON import/export for sharing presets.
- Safe default presets for nmap, netcat, ngrok, curl, dig, whois, traceroute, ping,
  nslookup, host, wget, ipconfig, ifconfig, ip, netstat, ss, route, arp, and openssl.

## Requirements
- Python 3.11+

## One-command quick start
```bash
python scripts/run.py
```

## Local setup (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:9999
```

Open `http://127.0.0.1:9999`.

## Local setup (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:9999
```

## Docker (optional)
```bash
docker compose up --build
```

## Pages
- Overview: `/`
- Composer: `/composer/`
- Library: `/library/`
- Manage: `/manage/`
- Import/Export: `/import/`
- Export JSON: `/export/`

## Environment
Copy `.env.example` to `.env` if needed.

Optional variables:
- `DEBUG` (default `1`)
- `SECRET_KEY`
- `ALLOWED_HOSTS`

## Import JSON format
```json
{
  "tools": [
    {
      "name": "nmap",
      "description": "Network mapper",
      "commands": [
        {
          "name": "Ping scan",
          "description": "Discover hosts",
          "template": "nmap -sn {target}",
          "category": "Recon",
          "tags": ["safe", "discovery"]
        }
      ]
    }
  ]
}
```

## Notes
- ZX9999 never executes commands. It only generates and formats them.
- Keep usage limited to authorized targets and environments.
- Offensive or brute-force command presets are not preloaded.
