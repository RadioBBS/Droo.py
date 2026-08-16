"""
Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.

Projekt:     Droo.py
Modul:       project_meta.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Gemeinsame Projekt-Metadaten (Version, Lizenz, KI-Hinweis, Upstream).
Einzelne Quelle fuer Angaben, die in Dateikoepfen, CLI und Attribution
wiederverwendet werden.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Sicherheit und Styleguide-Anpassungen
Version 1.2.0 – 2026-08-16 – Vollstaendiger Metadaten-Block, alle Pflichtfelder

Aufruf / Nutzung
----------------
  from project_meta import __version__, metadata_block
  print(metadata_block("droo.py"))
"""

from __future__ import annotations

PROJECT_NAME = "Droo.py"
PROJECT_DESCRIPTION = "Mini-Webserver zum Empfangen von Datei-Uploads."
PYTHON_REQUIRES = ">=3.10"

__version__ = "1.2.0"
__date__ = "2026-08-16"
__license__ = "BSD-3-Clause"
__created_with__ = "Cursor KI Model Auto (Composer)"
__upstream__ = "https://github.com/stackp/Droopy"
__upstream_credit__ = "Pierre Duquesne"
__requires__ = "nur Python-Standardbibliothek (Python ≥ 3.10)"
__requirements_ref__ = "requirements.txt (leer – Stdlib only)"

ATTRIBUTION_LINES = (
    f"Lizenz: {__license__} – Ableitung von stackp/Droopy ({__upstream_credit__}).",
    f"Upstream: {__upstream__}",
    f"Erstellt mit: {__created_with__}.",
    f"{PROJECT_NAME} v{__version__} ({__date__})",
)


def metadata_block(module: str) -> str:
    """Erzeugt den standardisierten Dateikopf-Block (Pflichtfelder).

    Parameter:
        module: Relativer Modul-/Dateiname im Projekt (z. B. ``droo.py``).

    Rueckgabe:
        Mehrzeiliger String mit allen Pflichtfeldern in fester Reihenfolge.

    Fehlerfaelle:
        Keine.

    Beispiel:
        >>> "Version:" in metadata_block("droo.py")
        True
    """
    return (
        f"Projekt:     {PROJECT_NAME}\n"
        f"Modul:       {module}\n"
        f"Version:     {__version__}\n"
        f"Stand:       {__date__}\n"
        f"Abhaengig:   {__requires__}\n"
        f"Bezug:       {__requirements_ref__}\n"
        f"Lizenz:      {__license__}\n"
        f"Upstream:    {__upstream__} ({__upstream_credit__})\n"
        f"Erstellt mit: {__created_with__}"
    )


def attribution_banner(prefix: str = "# ") -> str:
    """Mehrzeilige Attribution fuer Log-/Exportdateien.

    Parameter:
        prefix: Zeilenpraefix (Standard: ``# ``).

    Rueckgabe:
        Mehrzeiliger String.

    Fehlerfaelle:
        Keine.

    Beispiel:
        >>> attribution_banner("# ").startswith("# Lizenz:")
        True
    """
    return "\n".join(f"{prefix}{line}" for line in ATTRIBUTION_LINES)


def attribution_block() -> str:
    """Kurzblock fuer Modul-Docstrings (Lizenz, Upstream, Erstellt mit).

    Rueckgabe:
        Formatierter Attributionsblock.

    Fehlerfaelle:
        Keine.

    Beispiel:
        >>> "BSD-3-Clause" in attribution_block()
        True
    """
    return (
        f"Lizenz:      {__license__}\n"
        f"Upstream:    {__upstream__} ({__upstream_credit__})\n"
        f"Erstellt mit: {__created_with__}"
    )
