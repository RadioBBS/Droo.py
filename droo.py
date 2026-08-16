"""
Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.

Projekt:     Droo.py
Modul:       droo.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Startet einen lokalen HTTP(S)-Server, der anderen erlaubt, Dateien per
Browser hochzuladen. Optional: Download-Links, Basic-Auth, TLS, Bild und
Nachricht auf der Seite. Modernisierte Neuimplementierung von Droopy:
ohne Python 2, ohne ``cgi`` (Python 3.13+), SSLContext, sichere Auth.
Fuer https://localhost:8000 muss ein SSL-Zertifikat erstellt werden.
Mit dem Script make_pem.py wird openssl gesucht und droo.pem erstellt.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung Droo.py (Modernisierung von Droopy)
Version 1.1.0 – 2026-08-10 – Sicherheit (XSS, Upload-Limit) und Styleguide
Version 1.2.0 – 2026-08-16 – Projekt-Metadaten in allen Projektdateien vereinheitlicht

Aufruf / Nutzung
----------------
  python droo.py
  python droo.py -m "Bitte Datei hochladen" -d uploads -p avatar.png
  python droo.py --dl -a user:geheim 9000
  python droo.py --ssl cert.pem --chmod 644
  python droo.py --save-config -d uploads -m "Hallo"
  python droo.py --delete-config
  python droo.py --version
  python droo.py --log -E -d uploads --max-upload 100M
  .\\droo.py --ssl droo.pem --chmod 644 -d uploads -m "Feeeeed meeeee" -p pimping.png --dl --save-config

Im Browser: http://localhost:8000  (bzw. https & gewaehlter Port)

Oeffentliche Einstiege
----------------------
  main                 CLI-Einstieg
  droo.run_server      Server starten (programmatisch)
"""

from __future__ import annotations

import sys
from pathlib import Path

from droo.config import (
    DrooConfig,
    default_configfile,
    load_options,
    merge_config,
    parse_args,
    save_options,
)
from droo.logutil import log_error, log_info, setup_logging
from droo.server import run_server
from project_meta import __date__, __license__, __upstream__, __version__

BANNER = r"""
 _____                
|  __ \               
| |  | |_ __ ___   ___ 
| |  | | '__/ _ \ / _ \
| |__| | | | (_) | (_) |
|_____/|_|  \___/ \___/ .py
"""


def _config_to_dict(cfg: DrooConfig) -> dict:
    return {
        "port": cfg.port,
        "directory": cfg.directory,
        "message": cfg.message,
        "picture": cfg.picture,
        "publish_files": cfg.publish_files,
        "auth": cfg.auth,
        "ssl": cfg.ssl,
        "chmod": cfg.chmod,
        "save_config": cfg.save_config,
        "config_file": cfg.config_file,
        "max_upload": cfg.max_upload,
        "allow_html_message": cfg.allow_html_message,
        "logging_enabled": cfg.logging_enabled,
        "wait_at_end": cfg.wait_at_end,
    }


def _wait_at_end() -> None:
    """Pausiert bis Enter gemaess Styleguide --Ende / -E."""
    try:
        input('Programmende: Hit any Key or Enter')
    except EOFError:
        pass


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstieg. Gibt Exit-Code zurueck.

    Parameter:
        argv: Optionale Argumente ohne Programmname.

    Rueckgabe:
        Prozess-Exitcode (0 = ok).

    Fehlerfaelle:
        argparse beendet bei --help/--version; sonst Exceptions nach stderr.
    """
    if argv is not None:
        sys.argv = [sys.argv[0], *argv]

    # CLI-Overrides (ohne Defaults), dann Config-Datei, dann volle Defaults
    # (--help / --version beenden hier bereits via argparse, ohne Banner)
    term = parse_args(ignore_defaults=True)
    assert isinstance(term, dict)
    cfg_path = Path(term.get("config_file", default_configfile()))
    file_cfg = load_options(cfg_path)

    print(BANNER)
    print(f"Droo.py v{__version__} ({__date__}) · {__license__}")
    print(f"Basiert auf: {__upstream__}\n")

    if file_cfg:
        print(f"Konfiguration geladen: {cfg_path}")
        base = file_cfg
    else:
        print("Keine Konfigurationsdatei gefunden")
        full = parse_args(ignore_defaults=False)
        assert isinstance(full, DrooConfig)
        base = _config_to_dict(full)

    cfg = merge_config(base, term)

    log_path = setup_logging(cfg.logging_enabled)
    if log_path:
        print(f"Logging aktiv: {log_path}")
        log_info("Droo.py v%s gestartet", __version__)

    if cfg.save_config:
        save_options(cfg.config_file, sys.argv[1:])
        print(f"Optionen gespeichert in {cfg.config_file}")

    if not cfg.auth:
        print(
            "Warnung: Keine Basic-Auth (-a USER:PASS). "
            "Der Server lauscht auf allen Interfaces – "
            "fuer LAN/Internet Auth (und idealerweise --ssl) setzen.",
            file=sys.stderr,
        )
        log_info("Start ohne Basic-Auth")

    print(f"Uploads nach: {cfg.directory}")
    print(f"Max. Upload:  {cfg.max_upload} Bytes")
    proto = "https" if cfg.ssl else "http"
    print(f"HTTP-Server startet … {proto}://localhost:{cfg.port}")
    print("Beenden mit Ctrl+C\n")

    exit_code = 0
    try:
        run_server(cfg)
    except KeyboardInterrupt:
        print("\n^C – beende verbleibende Threads …")
        log_info("Beendet durch KeyboardInterrupt")
    except Exception as exc:  # noqa: BLE001
        print(f"Fehler: {exc}", file=sys.stderr)
        log_error("Server-Abbruch: %r", exc)
        exit_code = 1

    if cfg.wait_at_end:
        _wait_at_end()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
