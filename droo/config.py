"""
Droo.py – Konfiguration und CLI-Argumente.

Projekt:     Droo.py
Modul:       droo/config.py
Version:     1.0.0
Stand:       2026-07-25
Lizenz:      BSD-3-Clause (basiert auf stackp/Droopy)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Argumentparser, Default-Config-Pfad (%APPDATA%\\droo bzw. ~/.droo), Speichern
und Laden der Optionen.

Aufruf / Nutzung
----------------
  from droo.config import parse_args, default_configfile, load_options

  args = parse_args()
  cfg = load_options(default_configfile())
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


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


def default_configfile() -> Path:
    """Plattformtypischer Pfad zur Config-Datei."""
    appname = "droo"
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / appname
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / appname
    return Path.home() / f".{appname}"


def fullpath(path: str | Path) -> Path:
    """abspath + expanduser."""
    return Path(path).expanduser().resolve()


def save_options(cfg_path: Path, argv: Sequence[str]) -> None:
    """Schreibt CLI-Optionen (ohne --save-config/--delete-config) in cfg_path."""
    cfg_path = Path(cfg_path)
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    skip_next = False
    with cfg_path.open("w", encoding="utf-8") as out:
        for opt in argv:
            if skip_next:
                skip_next = False
                continue
            if opt in ("--save-config", "--delete-config"):
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
    """Laedt Config-Datei als Argumentliste und parst sie."""
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


def parse_args(
    cmd: Optional[Sequence[str]] = None,
    *,
    ignore_defaults: bool = False,
    as_dict: bool = False,
) -> DrooConfig | Dict[str, Any]:
    """Parst Terminal-Argumente (oder cmd)."""
    parser = argparse.ArgumentParser(
        prog="droo.py",
        description="Droo.py – Mini-Webserver zum Empfangen von Datei-Uploads.",
        epilog=(
            'Beispiel:\n  python droo.py -m "Hi, Datei bitte hier hochladen." '
            "-p avatar.png -d uploads"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="Nachricht auf der Upload-Seite (HTML erlaubt)",
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
    args = parser.parse_args(list(cmd) if cmd is not None else None)

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
        }
        if ignore_defaults:
            defaults = parse_args([], as_dict=True)
            assert isinstance(defaults, dict)
            data = {k: v for k, v in data.items() if defaults.get(k) != v}
        return data
    return cfg


def merge_config(file_cfg: Dict[str, Any], term_cfg: Dict[str, Any]) -> DrooConfig:
    """Config-Datei mit Terminal-Overrides zusammenfuehren."""
    merged = dict(file_cfg)
    merged.update(term_cfg)
    # Ensure required keys with defaults
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
    )
