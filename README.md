# Droo.py

```
Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.

Projekt:     Droo.py
Modul:       README.md
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)
```

## Idee

Manchmal braucht man nur eins: jemandem schnell eine Datei schicken lassen –
ohne Cloud, ohne Account, ohne E-Mail-Anhang-Limit. **Droo.py** ist ein
Mini-Webserver, der auf dem eigenen Rechner laeuft und im Browser eine
Upload-Seite anbietet. Fertig.

Modernisierte Neuimplementierung von [stackp/Droopy](https://github.com/stackp/Droopy)
(Pierre Duquesne). Erzeugt mit Cursor (Composer).

**Version:** 1.2.0 · **Stand:** 2026-08-16 · **Lizenz:** BSD-3-Clause · **Python:** ≥ 3.10

## Features

- Einfache **Upload-Seite** (Mehrfachauswahl, HTML5)
- Optional **Download-Links** der Dateien im Upload-Ordner (`--dl`)
- **Nachricht** und **Bild** auf der Seite (Nachricht standardmaessig escaped)
- **HTTP Basic Auth** und optional **HTTPS** (PEM, TLS ≥ 1.2)
- **Upload-Limit** (Standard 512M) und Pflicht-`Content-Length`
- Dateinamen-Nummerierung statt Ueberschreiben (`foto.png`, `foto-1.png`, …)
- Mehrsprachige UI (Accept-Language, u. a. Deutsch/Englisch)
- Config speichern/laden (`%APPDATA%\droo` unter Windows)
- Optional **Datei-Logging** (`--log`), Pause am Ende (`-E` / `--Ende`)
- **Ohne** `cgi` / Python-2-Ballast – lauffaehig unter Python 3.13+

## Voraussetzungen

- Windows, Linux oder macOS
- Python ≥ 3.10
- Keine Drittanbieter-Pakete (nur Standardbibliothek)

Erwartete Abhaengigkeiten installieren (reproduzierbarer Weg, auch wenn
`requirements.txt` derzeit nur Kommentare enthaelt):

```bash
python -m pip install -r requirements.txt
```

Virtuelle Umgebung (empfohlen):

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Schnellstart

```bash
cd GIT-Projects\Droo.py
python droo.py
python droo.py -m "Bitte Datei hier hochladen" -d uploads
python droo.py -m "Hallo" -p avatar.png --dl 9000
python droo.py -a user:geheim -d uploads
python droo.py --version
python droo.py --log -E -d uploads --max-upload 100M
```

HTTPS (self-signed PEM im Startverzeichnis):

```bash
python make_pem.py
python make_pem.py -o droo.pem --days 365 --cn localhost
python droo.py --ssl droo.pem -a user:geheim
.\droo.py --ssl droo.pem --chmod 644 -d uploads -m "Feeeeed meeeee" -p pimping.png --dl --save-config
```

`make_pem.py` prueft zuerst, ob `openssl` im PATH liegt; Ausgabe immer ins
aktuelle Arbeitsverzeichnis.

Im Browser: `http://localhost:8000` (bzw. gewaehlter Port). Freunden die
LAN-IP mit Port nennen; Firewall ggf. oeffnen.

### Wichtige Parameter (`droo.py`)

| Parameter | Typ | Standard | Bedeutung |
|-----------|-----|----------|-----------|
| `PORT` | int | `8000` | Port (Positionsargument) |
| `-d DIR`, `--directory DIR` | str | `.` | Upload-Verzeichnis |
| `-m TEXT`, `--message TEXT` | str | leer | Nachricht (escaped; HTML nur mit Flag) |
| `--allow-html-message` | flag | aus | HTML in `--message` erlauben |
| `-p FILE`, `--picture FILE` | str | leer | Bild auf der Upload-Seite |
| `--dl`, `--publish-files` | flag | aus | Download-Links anzeigen |
| `-a USER:PASS`, `--auth` | str | leer | HTTP Basic Auth |
| `--ssl PEMFILE` | str | leer | HTTPS mit PEM-Zertifikat (+Key) |
| `--chmod MODE` | oktal | – | Dateirechte (z. B. `644`) |
| `--max-upload SIZE` | str | `512M` | Max. Request-Body (`100M`, `1G`, …) |
| `--log` / `--no-log` | flag | aus | Datei-Logging ein/aus |
| `-E`, `--Ende` | flag | aus | Am Ende auf Enter warten |
| `-V`, `--version` | flag | – | Version, Datum, Beschreibung |
| `--save-config` | flag | aus | Optionen in Config-Datei speichern |
| `--delete-config` | flag | aus | Config loeschen und beenden |
| `--config-file PATH` | str | plattformtypisch | Anderer Config-Pfad |

## Module

| Datei | Rolle |
|-------|--------|
| `droo.py` | CLI-Einstieg, Banner, Config-Merge, Server-Start |
| `make_pem.py` | Self-Signed-PEM via OpenSSL (fuer `--ssl`) |
| `droo/server.py` | Threaded HTTP(S)-Handler, Auth, Seiten |
| `droo/upload.py` | Multipart-Streaming ohne `cgi` |
| `droo/config.py` | argparse, Config speichern/laden |
| `droo/logutil.py` | Optionales UTF-8-Datei-Logging |
| `droo/templates.py` | HTML/CSS (Layout aus Droopy) |
| `droo/i18n.py` | UI-Uebersetzungen |
| `project_meta.py` | Version, Lizenz, Attribution; gemeinsame Quelle der Dateikopf-Felder |

## Hinweise

- Uploads landen im aktuellen Verzeichnis bzw. unter `-d`.
- `--message` wird standardmaessig HTML-escaped; mit `--allow-html-message` nur vertrauenswuerdige Texte.
- Dateinamen in der Download-Liste (`--dl`) werden immer escaped.
- Mit `--dl` sind alle Dateien im Upload-Ordner per Link erreichbar.
- Ohne `-a` erscheint eine Warnung: der Server lauscht auf allen Interfaces.
- Auth und TLS schuetzen den Zugang; fuer oeffentliche Netze beides nutzen.
- Requests ohne `Content-Length` oder ueber `--max-upload` werden mit 411/413 abgelehnt.
- Original-Referenz liegt lokal unter `_reference/Droopy/` (nicht versioniert).

## Lizenz

BSD-3-Clause – siehe [LICENSE](LICENSE). Copyright urspruenglich Pierre Duquesne;
Droo.py ist eine modernisierte Ableitung.

Erstellt mit Cursor (Composer).
