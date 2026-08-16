"""
Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.

Projekt:     Droo.py
Modul:       droo/__init__.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Paket-API: Config, Server-Start, Upload-Helfer.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Sicherheit und Styleguide
Version 1.2.0 – 2026-08-16 – Vollstaendiger Dateikopf (Projekt-Metadaten)

Aufruf / Nutzung
----------------
  from droo import DrooConfig, run_server, parse_args
"""

from __future__ import annotations

from droo.config import DrooConfig, default_configfile, parse_args
from droo.server import run_server

__all__ = [
    "DrooConfig",
    "default_configfile",
    "parse_args",
    "run_server",
]
