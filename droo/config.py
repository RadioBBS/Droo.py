"""
Droo.py – Konfiguration und CLI-Argumente.

Projekt:     Droo.py
Modul:       droo/config.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Argumentparser, Default-Config-Pfad (%APPDATA%\\droo bzw. ~/.droo), Speichern
und Laden der Optionen. Unterstuetzt --version, Logging, Upload-Limit und -E.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Styleguide (--version, -E, --log), Sicherheit
Version 1.2.0 – 2026-08-16 – Vollstaendiger Dateikopf (Projekt-Metadaten)

Aufruf / Nutzung
----------------
  from droo.config import parse_args, default_configfile, load_options

  args = parse_args()
  cfg = load_options(default_configfile())
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from project_meta import __date__, __version__

# 512 MiB Standard-Maximum pro Request-Body
DEFAULT_MAX_UPLOAD = 512 * 1024 * 1024

_SIZE_RE = re.compile(r"^(\d+)([KMG]?)$", re.IGNORECASE)


@dataclass
class DrooConfig:
    """Laufzeitkonfiguration des Upload-Servers."""

    port: int = 8000
    directory: Path = Path(".")
    message: str = ""
    picture: Optional[Path] = None
    publish_files: bool = False
    auth: str = ""
    ssl: Optional[Path] = None
    chmod: Optional[int] = None
    save_config: bool = False
    delete_config: bool = False
    config_file: Path = Path(".")
    max_upload: int = DEFAULT_MAX_UPLOAD
    allow_html_message: bool = False
    logging_enabled: bool = False
    wait_at_end: bool = False


def default_configfile() -> Path:
    """Plattformtypischer Pfad zur Config-Datei.

    Rueckgabe:
        Pfad unter APPDATA, Application Support oder ``~/.droo``.

    Fehlerfaelle:
        Keine.
    """
    appname = "droo"
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / appname
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / appname
    return Path.home() / f".{appname}"


def fullpath(path: str | Path) -> Path:
    """abspath + expanduser.

    Parameter:
        path: Relativer oder absoluter Pfad.

    Rueckgabe:
        Aufgeloester Path.

    Fehlerfaelle:
        OSError bei ungueltigen Pfaden (selten).
    """
    return Path(path).expanduser().resolve()


def parse_size(value: str) -> int:
    """Parst Byte-Angaben mit optionalem Suffix K/M/G.

    Parameter:
        value: z. B. ``1048576``, ``100M``, ``1G``.

    Rueckgabe:
        Groesse in Bytes (int ≥ 1).

    Fehlerfaelle:
        ValueError bei ungueltigem Format oder Wert < 1.

    Beispiel:
        parse_size("512M") == 536870912
    """
    text = value.strip().replace(" ", "")
    match = _SIZE_RE.fullmatch(text)
    if not match:
        raise ValueError(f"ungueltige Groesse: {value!r}")
    amount = int(match.group(1))
    suffix = match.group(2).upper()
    factor = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}[suffix]
    result = amount * factor
    if result < 1:
        raise ValueError("Groesse muss >= 1 Byte sein")
    return result


def save_options(cfg_path: Path, argv: Sequence[str]) -> None:
    """Schreibt CLI-Optionen (ohne Meta-Flags) in cfg_path.

    Parameter:
        cfg_path: Zieldatei.
        argv: Argumentliste ohne Programmname.

    Fehlerfaelle:
        OSError wenn Schreiben fehlschlaegt.
    """
    cfg_path = Path(cfg_path)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    skip_flags = {
        "--save-config",
        "--delete-config",
        "--Ende",
        "-E",
        "--version",
        "-V",
    }
    skip_next = False
    with cfg_path.open("w", encoding="utf-8") as out:
        for opt in argv:
            if skip_next:
                skip_next = False
                continue
            if opt in skip_flags:
                continue
            if opt == "--config-file":
                skip_next = True
                continue
            if opt.startswith("-"):
                out.write("\n")
            else:
                out.write(" ")
            out.write(opt)


def load_options(cfg_loc: Path) -> Dict[str, Any]:
    """Laedt Config-Datei als Argumentliste und parst sie.

    Parameter:
        cfg_loc: Pfad zur Config-Datei.

    Rueckgabe:
        Dict der gesetzten Optionen oder leeres Dict.

    Fehlerfaelle:
        OSError wird als leeres Dict behandelt.
    """
    cfg_loc = Path(cfg_loc)
    try:
        text = cfg_loc.read_text(encoding="utf-8")
    except OSError:
        return {}
    cmd: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            if " " in line:
                opt, rest = line.split(" ", 1)
                cmd.extend((opt, rest))
            else:
                cmd.append(line)
        else:
            cmd.append(line)
    return parse_args(cmd, as_dict=True)


def _build_parser() -> argparse.ArgumentParser:
    """Erzeugt den Argumentparser fuer droo.py."""
    parser = argparse.ArgumentParser(
        prog="droo.py",
        description=(
            "Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.\n"
            f"Version: {__version__} ({__date__})"
        ),
        epilog=(
            "Beispiele:\n"
            '  python droo.py -m "Hi, Datei bitte hier hochladen." -p avatar.png -d uploads\n'
            "  python droo.py --dl -a user:geheim --max-upload 100M 9000\n"
            "  python droo.py --version\n"
            "  python droo.py --log -E -d uploads"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=(
            f"Droo.py {__version__} ({__date__})\n"
            "Mini-Webserver zum Empfangen von Datei-Uploads."
        ),
    )
    parser.add_argument(
        "port",
        type=int,
        nargs="?",
        default=8000,
        help="Port (Standard: 8000)",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=".",
        help="Upload-Verzeichnis",
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        default="",
        help="Nachricht auf der Upload-Seite (Text; HTML nur mit --allow-html-message)",
    )
    parser.add_argument(
        "--allow-html-message",
        action="store_true",
        default=False,
        help="Erlaubt HTML in --message (XSS-Risiko bei unvertrauenswuerdigem Text)",
    )
    parser.add_argument(
        "-p",
        "--picture",
        type=str,
        default="",
        help="Bilddatei fuer die Upload-Seite",
    )
    parser.add_argument(
        "--publish-files",
        "--dl",
        action="store_true",
        default=False,
        help="Download-Links fuer Dateien im Upload-Ordner anzeigen",
    )
    parser.add_argument(
        "-a",
        "--auth",
        type=str,
        default="",
        help="HTTP-Basic-Auth als USER:PASS",
    )
    parser.add_argument(
        "--ssl",
        type=str,
        default="",
        help="PEM-Zertifikat (+Key) fuer HTTPS",
    )
    parser.add_argument(
        "--chmod",
        type=str,
        default=None,
        help="Dateirechte fuer Uploads (oktal, z. B. 644)",
    )
    parser.add_argument(
        "--max-upload",
        type=str,
        default=None,
        help="Max. Request-Body (Bytes oder K/M/G, Standard: 512M)",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        default=False,
        help="Datei-Logging einschalten (UTF-8, ASCII-Dateiname)",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        default=False,
        help="Datei-Logging ausschalten",
    )
    parser.add_argument(
        "-E",
        "--Ende",
        action="store_true",
        default=False,
        help='Am Ende auf "Hit any Key or Enter" warten',
    )
    parser.add_argument(
        "--save-config",
        action="store_true",
        default=False,
        help="Optionen in der Config-Datei speichern",
    )
    parser.add_argument(
        "--delete-config",
        action="store_true",
        default=False,
        help="Config-Datei loeschen und beenden",
    )
    parser.add_argument(
        "--config-file",
        default=str(default_configfile()),
        help="Pfad zur Config-Datei",
    )
    return parser


def parse_args(
    cmd: Optional[Sequence[str]] = None,
    *,
    ignore_defaults: bool = False,
    as_dict: bool = False,
) -> DrooConfig | Dict[str, Any]:
    """Parst Terminal-Argumente (oder cmd).

    Parameter:
        cmd: Optionale Argumentliste statt sys.argv.
        ignore_defaults: Nur explizit gesetzte Werte als Dict.
        as_dict: Immer Dict zurueckgeben.

    Rueckgabe:
        DrooConfig oder Dict.

    Fehlerfaelle:
        Beendet Prozess bei ungueltigen Parametern (argparse / Validierung).
    """
    parser = _build_parser()
    args = parser.parse_args(list(cmd) if cmd is not None else None)

    if args.log and args.no_log:
        print("Fehler: --log und --no-log schliessen sich aus", file=sys.stderr)
        sys.exit(1)

    picture: Optional[Path] = None
    if args.picture:
        pic = fullpath(args.picture)
        if pic.is_file():
            picture = pic
        else:
            print(f"Bild nicht gefunden: '{args.picture}'", file=sys.stderr)

    if args.delete_config:
        path = default_configfile()
        try:
            path.unlink()
            print(f"Geloescht: {path}")
        except FileNotFoundError:
            print(f"Keine Config-Datei: {path}")
        sys.exit(0)

    if args.auth and ":" not in args.auth:
        print("Fehler: --auth muss USER:PASSWORD sein", file=sys.stderr)
        sys.exit(1)

    ssl_path: Optional[Path] = None
    if args.ssl:
        ssl_path = fullpath(args.ssl)
        if not ssl_path.is_file():
            print(f"PEM-Datei nicht gefunden: '{args.ssl}'", file=sys.stderr)
            sys.exit(1)

    chmod_mode: Optional[int] = None
    if args.chmod is not None:
        try:
            chmod_mode = int(args.chmod, 8)
        except ValueError:
            print(f"Ungueltiger oktaler Wert fuer --chmod: '{args.chmod}'", file=sys.stderr)
            sys.exit(1)

    max_upload = DEFAULT_MAX_UPLOAD
    if args.max_upload is not None:
        try:
            max_upload = parse_size(args.max_upload)
        except ValueError as exc:
            print(f"Fehler: --max-upload: {exc}", file=sys.stderr)
            sys.exit(1)

    logging_enabled = bool(args.log) and not bool(args.no_log)

    cfg = DrooConfig(
        port=args.port,
        directory=fullpath(args.directory),
        message=args.message,
        picture=picture,
        publish_files=bool(args.publish_files),
        auth=args.auth or "",
        ssl=ssl_path,
        chmod=chmod_mode,
        save_config=bool(args.save_config),
        delete_config=False,
        config_file=fullpath(args.config_file),
        max_upload=max_upload,
        allow_html_message=bool(args.allow_html_message),
        logging_enabled=logging_enabled,
        wait_at_end=bool(args.Ende),
    )

    if as_dict or ignore_defaults:
        data = {
            "port": cfg.port,
            "directory": cfg.directory,
            "message": cfg.message,
            "picture": cfg.picture,
            "publish_files": cfg.publish_files,
            "auth": cfg.auth,
            "ssl": cfg.ssl,
            "chmod": cfg.chmod,
            "save_config": cfg.save_config,
            "delete_config": cfg.delete_config,
            "config_file": cfg.config_file,
            "max_upload": cfg.max_upload,
            "allow_html_message": cfg.allow_html_message,
            "logging_enabled": cfg.logging_enabled,
            "wait_at_end": cfg.wait_at_end,
        }
        if ignore_defaults:
            defaults = parse_args([], as_dict=True)
            assert isinstance(defaults, dict)
            # --no-log explizit: Logging aus, auch gegen Config
            if args.no_log:
                data["logging_enabled"] = False
            elif not args.log:
                data.pop("logging_enabled", None)
            data = {k: v for k, v in data.items() if defaults.get(k) != v}
            if args.no_log:
                data["logging_enabled"] = False
        return data
    return cfg


def merge_config(file_cfg: Dict[str, Any], term_cfg: Dict[str, Any]) -> DrooConfig:
    """Config-Datei mit Terminal-Overrides zusammenfuehren.

    Parameter:
        file_cfg: Geladene Dateiwerte.
        term_cfg: CLI-Overrides.

    Rueckgabe:
        Zusammengefuehrte DrooConfig.

    Fehlerfaelle:
        TypeError/ValueError bei kaputten Werten.
    """
    merged = dict(file_cfg)
    merged.update(term_cfg)
    base = DrooConfig(config_file=default_configfile())
    return DrooConfig(
        port=int(merged.get("port", base.port)),
        directory=Path(merged.get("directory", base.directory)),
        message=str(merged.get("message", "")),
        picture=Path(merged["picture"]) if merged.get("picture") else None,
        publish_files=bool(merged.get("publish_files", False)),
        auth=str(merged.get("auth", "") or ""),
        ssl=Path(merged["ssl"]) if merged.get("ssl") else None,
        chmod=merged.get("chmod"),
        save_config=bool(merged.get("save_config", False)),
        delete_config=False,
        config_file=Path(merged.get("config_file", default_configfile())),
        max_upload=int(merged.get("max_upload", base.max_upload)),
        allow_html_message=bool(merged.get("allow_html_message", False)),
        logging_enabled=bool(merged.get("logging_enabled", False)),
        wait_at_end=bool(merged.get("wait_at_end", False)),
    )
