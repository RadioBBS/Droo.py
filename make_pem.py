"""
Droo.py – Self-Signed-PEM mit OpenSSL erzeugen.

Projekt:     Droo.py
Modul:       make_pem.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   OpenSSL im PATH (vorherige Pruefung); Python ≥ 3.10, Stdlib
Bezug:       requirements.txt (leer – Stdlib only); droo.py --ssl <pem>
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Prueft, ob ``openssl`` erreichbar ist, und erzeugt ein selbstsigniertes
Zertifikat inkl. privatem Schluessel als kombinierte PEM-Datei.
Ausgabeverzeichnis = aktuelles Arbeitsverzeichnis (Startverzeichnis).

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Versionshistorie an Styleguide angeglichen
Version 1.2.0 – 2026-08-16 – Vollstaendiger Dateikopf (Projekt-Metadaten)

Aufruf / Nutzung
----------------
  python make_pem.py
  python make_pem.py -o droo.pem
  python make_pem.py --days 365 --cn localhost
  python make_pem.py --force

Danach z. B.:

  python droo.py --ssl droo.pem -a user:geheim
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from project_meta import __created_with__, __date__, __license__, __version__

_ = (__created_with__, __license__)

DEFAULT_NAME = "droo.pem"
DEFAULT_DAYS = 365
DEFAULT_CN = "localhost"

# Haeufige Windows-Installationspfade, falls openssl nicht im PATH liegt
_WINDOWS_OPENSSL_CANDIDATES = (
    Path(r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe"),
    Path(r"C:\Program Files\OpenSSL-Win32\bin\openssl.exe"),
    Path(r"C:\Program Files (x86)\OpenSSL-Win32\bin\openssl.exe"),
    Path(r"C:\Program Files\Git\usr\bin\openssl.exe"),
    Path(r"C:\Program Files\Git\mingw64\bin\openssl.exe"),
    Path(r"C:\OpenSSL-Win64\bin\openssl.exe"),
)


def find_openssl() -> str | None:
    """Pfad zu openssl (PATH oder bekannte Installationsorte) bzw. None."""
    which = shutil.which("openssl")
    if which:
        return which
    for candidate in _WINDOWS_OPENSSL_CANDIDATES:
        if candidate.is_file():
            return str(candidate)
    # ProgramFiles aus Umgebung (andere Laufwerke / Locale)
    for env_key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        base = os.environ.get(env_key)
        if not base:
            continue
        for rel in (
            "OpenSSL-Win64/bin/openssl.exe",
            "OpenSSL-Win32/bin/openssl.exe",
            "Programs/OpenSSL/bin/openssl.exe",
            "Git/usr/bin/openssl.exe",
        ):
            path = Path(base) / rel
            if path.is_file():
                return str(path)
    return None


def require_openssl() -> str:
    """OpenSSL suchen; bei Fehlen mit Meldung beenden."""
    path = find_openssl()
    if path:
        try:
            proc = subprocess.run(
                [path, "version"],
                capture_output=True,
                text=True,
                check=False,
            )
            version = (proc.stdout or proc.stderr or "").strip().splitlines()[0]
        except OSError as exc:
            print(f"OpenSSL gefunden, aber nicht ausfuehrbar: {exc}", file=sys.stderr)
            sys.exit(2)
        print(f"OpenSSL gefunden: {path}")
        if version:
            print(f"  {version}")
        return path

    print(
        "Fehler: OpenSSL wurde nicht gefunden (nicht im PATH).\n"
        "Bitte OpenSSL installieren und die Shell neu starten.\n"
        "  Windows: https://slproweb.com/products/Win32OpenSSL.html\n"
        "  oder: winget install ShiningLight.OpenSSL",
        file=sys.stderr,
    )
    sys.exit(1)


def build_pem(
    openssl: str,
    out_path: Path,
    *,
    days: int,
    common_name: str,
    key_bits: int = 2048,
) -> None:
    """Erzeugt kombinierte PEM (Key + Zertifikat) unter out_path."""
    # req -x509 schreibt Key und Cert in eine Datei, wenn -keyout == -out
    cmd = [
        openssl,
        "req",
        "-x509",
        "-newkey",
        f"rsa:{key_bits}",
        "-keyout",
        str(out_path),
        "-out",
        str(out_path),
        "-days",
        str(days),
        "-nodes",
        "-subj",
        f"/CN={common_name}",
    ]
    print("Erzeuge PEM …")
    print(" ", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"OpenSSL-Fehler (Exit {exc.returncode}).", file=sys.stderr)
        sys.exit(exc.returncode or 1)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="make_pem.py",
        description="Erzeugt eine self-signed PEM-Datei fuer droo.py --ssl (via OpenSSL).",
        epilog="Ausgabeverzeichnis ist immer das aktuelle Arbeitsverzeichnis.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_NAME,
        help=f"Dateiname im Startverzeichnis (Standard: {DEFAULT_NAME})",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Gueltigkeit in Tagen (Standard: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--cn",
        default=DEFAULT_CN,
        help=f"Common Name / CN (Standard: {DEFAULT_CN})",
    )
    parser.add_argument(
        "--bits",
        type=int,
        default=2048,
        help="RSA-Schluessellaenge (Standard: 2048)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Vorhandene Datei ueberschreiben",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstieg."""
    args = parse_args(argv)
    print(f"make_pem.py (Droo.py v{__version__}, {__date__})")
    print(f"Startverzeichnis: {Path.cwd()}\n")

    openssl = require_openssl()

    # Nur Dateiname – Ausgabe immer relativ zum CWD (Startverzeichnis)
    name = Path(args.output).name
    if not name:
        print("Fehler: ungueltiger Ausgabename.", file=sys.stderr)
        return 1
    out_path = Path.cwd() / name

    if out_path.exists() and not args.force:
        print(
            f"Datei existiert bereits: {out_path}\n"
            "Mit --force ueberschreiben oder anderen Namen mit -o waehlen.",
            file=sys.stderr,
        )
        return 1

    if args.days < 1:
        print("Fehler: --days muss >= 1 sein.", file=sys.stderr)
        return 1

    build_pem(
        openssl,
        out_path,
        days=args.days,
        common_name=args.cn,
        key_bits=args.bits,
    )

    if not out_path.is_file() or out_path.stat().st_size == 0:
        print("Fehler: PEM-Datei wurde nicht erzeugt.", file=sys.stderr)
        return 1

    print(f"\nFertig: {out_path}")
    print(f"Beispiel: python droo.py --ssl {out_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
