"""
Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.

Projekt:     Droo.py
Modul:       droo.py
Version:     1.0.0
Stand:       2026-07-25
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
2026-07-25  1.0.0  Erstveroeffentlichung Droo.py (Modernisierung von Droopy)

Aufruf / Nutzung
----------------
  python droo.py
  python droo.py -m "Bitte Datei hochladen" -d uploads -p avatar.png
  python droo.py --dl -a user:geheim 9000
  python droo.py --ssl cert.pem --chmod 644
  python droo.py --save-config -d uploads -m "Hallo"
  python droo.py --delete-config
  .\droo.py --ssl droo.pem --chmod 644 -d uploads -m "Feeeeed meeeee" -p pimping.png --dl --save-config

Im Browser: http://localhost:8000  (bzw. gewaehlter Port)

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
from droo.server import run_server
from project_meta import __date__, __license__, __upstream__, __version__

BANNER = r"""
 _____
|  __ \               
| |  | |_ __ ___   ___ 
| |  | | '__/ _ \ / _ \
| |__| | | | (_) | (_) |
|_____/|_|  \___/ \___/
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
    }


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstieg. Gibt Exit-Code zurueck."""
    if argv is not None:
        sys.argv = [sys.argv[0], *argv]

    # CLI-Overrides (ohne Defaults), dann Config-Datei, dann volle Defaults
    # (--help beendet hier bereits via argparse, ohne Banner)
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

    if cfg.save_config:
        save_options(cfg.config_file, sys.argv[1:])
        print(f"Optionen gespeichert in {cfg.config_file}")

    print(f"Uploads nach: {cfg.directory}\n")
    proto = "https" if cfg.ssl else "http"
    print(f"HTTP-Server startet … {proto}://localhost:{cfg.port}")
    print("Beenden mit Ctrl+C\n")

    try:
        run_server(cfg)
    except KeyboardInterrupt:
        print("\n^C – beende verbleibende Threads …")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
