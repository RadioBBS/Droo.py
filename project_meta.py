"""
Gemeinsame Projekt-Metadaten fuer Droo.py (Version, Lizenz, KI-Hinweis).

Projekt:     Droo.py
Modul:       project_meta.py
Version:     1.1.0
Stand:       2026-08-10
Lizenz:      BSD-3-Clause
Erstellt mit: Cursor KI Model Auto (Composer)
Bezug:       basiert auf stackp/Droopy (Pierre Duquesne)

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Sicherheit und Styleguide-Anpassungen
"""

from __future__ import annotations

__version__ = "1.1.0"
__date__ = "2026-08-10"
__license__ = "BSD-3-Clause"
__created_with__ = "Cursor KI Model Auto (Composer)"
__upstream__ = "https://github.com/stackp/Droopy"

ATTRIBUTION_LINES = (
    f"Lizenz: {__license__} – Ableitung von stackp/Droopy (Pierre Duquesne).",
    f"Upstream: {__upstream__}",
    f"Erstellt mit: {__created_with__}.",
    f"Droo.py v{__version__} ({__date__})",
)


def attribution_banner(prefix: str = "# ") -> str:
    """Mehrzeilige Attribution fuer Log-/Exportdateien.

    Parameter:
        prefix: Zeilenpraefix (Standard: ``# ``).

    Rueckgabe:
        Mehrzeiliger String.

    Fehlerfaelle:
        Keine.
    """
    return "\n".join(f"{prefix}{line}" for line in ATTRIBUTION_LINES)


def attribution_block() -> str:
    """Kurzblock fuer Modul-Docstrings.

    Rueckgabe:
        Formatierter Attributionsblock.

    Fehlerfaelle:
        Keine.
    """
    return (
        f"Lizenz:      {__license__}\n"
        f"Upstream:    {__upstream__}\n"
        f"Erstellt mit: {__created_with__}"
    )
