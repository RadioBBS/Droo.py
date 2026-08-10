"""
Droo.py – optionales Datei-Logging (UTF-8 ohne BOM).

Projekt:     Droo.py
Modul:       droo/logutil.py
Version:     1.1.0
Stand:       2026-08-10
Lizenz:      BSD-3-Clause
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Schaltet ein ASCII-sicheres Logfile mit Zeitstempel
``YYYY-MM-DD HH:MM:SS`` ein oder aus. Dateiname ohne Umlaute.

Historie
--------
Version 1.1.0 – 2026-08-10 – Erstveroeffentlichung Logging-Hilfsmodul

Aufruf / Nutzung
----------------
  from droo.logutil import setup_logging, log_info, log_error

  setup_logging(enabled=True)
  log_info("Server gestartet")
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger("droo")
_CONFIGURED = False


class _StampFormatter(logging.Formatter):
    """Formatter mit festem Zeitformat YYYY-MM-DD HH:MM:SS."""

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        return datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")


def _ascii_log_name(when: Optional[datetime] = None) -> str:
    """ASCII-sicherer Logdateiname ohne Umlaute."""
    stamp = (when or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return f"droo_{stamp}.log"


def setup_logging(enabled: bool, directory: Optional[Path] = None) -> Optional[Path]:
    """Konfiguriert oder deaktiviert Datei-Logging.

    Parameter:
        enabled: True = Logdatei anlegen, False = nur Stub.
        directory: Zielordner (Standard: aktuelles Arbeitsverzeichnis).

    Rueckgabe:
        Pfad zur Logdatei oder None.

    Fehlerfaelle:
        OSError beim Anlegen der Datei wird nach stderr geschrieben.
    """
    global _CONFIGURED
    _LOGGER.handlers.clear()
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.propagate = False
    _CONFIGURED = True

    if not enabled:
        _LOGGER.addHandler(logging.NullHandler())
        return None

    log_dir = Path(directory) if directory is not None else Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / _ascii_log_name()
    try:
        handler = logging.FileHandler(path, encoding="utf-8", mode="w")
    except OSError as exc:
        print(f"Logging konnte nicht gestartet werden: {exc}", file=sys.stderr)
        _LOGGER.addHandler(logging.NullHandler())
        return None

    handler.setFormatter(_StampFormatter("%(asctime)s [%(levelname)s] %(message)s"))
    _LOGGER.addHandler(handler)
    _LOGGER.info("Logging gestartet: %s", path.name)
    return path


def log_info(message: str, *args: object) -> None:
    """Info-Eintrag ins Log (no-op ohne setup_logging)."""
    if _CONFIGURED:
        _LOGGER.info(message, *args)


def log_error(message: str, *args: object) -> None:
    """Fehler-Eintrag ins Log (no-op ohne setup_logging)."""
    if _CONFIGURED:
        _LOGGER.error(message, *args)


def log_debug(message: str, *args: object) -> None:
    """Debug-Eintrag ins Log (no-op ohne setup_logging)."""
    if _CONFIGURED:
        _LOGGER.debug(message, *args)
