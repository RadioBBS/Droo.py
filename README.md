# Droo.py

## Idee

Manchmal braucht man nur eins: jemandem schnell eine Datei schicken lassen –
ohne Cloud, ohne Account, ohne E-Mail-Anhang-Limit. **Droo.py** ist ein
Mini-Webserver, der auf dem eigenen Rechner laeuft und im Browser eine
Upload-Seite anbietet. Fertig.

Modernisierte Neuimplementierung von [stackp/Droopy](https://github.com/stackp/Droopy)
(Pierre Duquesne). Erzeugt mit Cursor (Composer).

**Version:** 1.0.0 · **Lizenz:** BSD-3-Clause · **Python:** ≥ 3.10

## Features

- Einfache **Upload-Seite** (Mehrfachauswahl, HTML5)
- Optional **Download-Links** der Dateien im Upload-Ordner (`--dl`)
- **Nachricht** und **Bild** auf der Seite
- **HTTP Basic Auth** und optional **HTTPS** (PEM)
- Dateinamen-Nummerierung statt Ueberschreiben (`foto.png`, `foto-1.png`, …)
- Mehrsprachige UI (Accept-Language, u. a. Deutsch/Englisch)
- Config speichern/laden (`%APPDATA%\droo` unter Windows)
- **Ohne** `cgi` / Python-2-Ballast – lauffaehig unter Python 3.13+

## Voraussetzungen

- Windows, Linux oder macOS
- Python ≥ 3.10
- Keine Drittanbieter-Pakete (nur Standardbibliothek)

```bash
# optional, falls spaeter Abhaengigkeiten dazukommen:
pip install -r requirements.txt
```

## Schnellstart

```bash
cd Projects\Droo.py
python droo.py
python droo.py -m "Bitte Datei hier hochladen" -d uploads
python droo.py -m "Hallo" -p avatar.png --dl 9000
python droo.py -a user:geheim -d uploads
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

| Parameter | Bedeutung |
|-----------|-----------|
| `PORT` | Port (Position, Standard `8000`) |
| `-d DIR`, `--directory DIR` | Upload-Verzeichnis |
| `-m TEXT`, `--message TEXT` | Nachricht auf der Seite (HTML erlaubt) |
| `-p FILE`, `--picture FILE` | Bild auf der Upload-Seite |
| `--dl`, `--publish-files` | Download-Links anzeigen |
| `-a USER:PASS`, `--auth` | HTTP Basic Auth |
| `--ssl PEMFILE` | HTTPS mit PEM-Zertifikat (+Key) |
| `--chmod MODE` | Dateirechte oktal (z. B. `644`) |
| `--save-config` | Optionen in Config-Datei speichern |
| `--delete-config` | Config loeschen und beenden |
| `--config-file PATH` | Anderer Config-Pfad |

## Module

| Datei | Rolle |
|-------|--------|
| `droo.py` | CLI-Einstieg, Banner, Config-Merge, Server-Start |
| `make_pem.py` | Self-Signed-PEM via OpenSSL (fuer `--ssl`) |
| `droo/server.py` | Threaded HTTP(S)-Handler, Auth, Seiten |
| `droo/upload.py` | Multipart-Streaming ohne `cgi` |
| `droo/config.py` | argparse, Config speichern/laden |
| `droo/templates.py` | HTML/CSS (Layout aus Droopy) |
| `droo/i18n.py` | UI-Uebersetzungen |
| `project_meta.py` | Version, Lizenz, Attribution |

## Hinweise

- Uploads landen im aktuellen Verzeichnis bzw. unter `-d`.
- `--message` darf HTML enthalten (wie im Original) – nur vertrauenswuerdige Texte.
- Mit `--dl` sind alle Dateien im Upload-Ordner per Link erreichbar.
- Auth und TLS schuetzen den Zugang; fuer oeffentliche Netze beides nutzen.
- Original-Referenz liegt lokal unter `_reference/Droopy/` (nicht versioniert).

## Lizenz

BSD-3-Clause – siehe [LICENSE](LICENSE). Copyright urspruenglich Pierre Duquesne;
Droo.py ist eine modernisierte Ableitung.

Erstellt mit Cursor (Composer).
