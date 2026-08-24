"""
Droo.py – Multipart-Upload ohne cgi (Python ≥ 3.10 / 3.13-tauglich).

Projekt:     Droo.py
Modul:       droo/upload.py
Version:     1.2.0
Stand:       2026-08-16
Abhaengig:   nur Python-Standardbibliothek (Python ≥ 3.10)
Bezug:       requirements.txt (leer – Stdlib only)
Lizenz:      BSD-3-Clause
Upstream:    https://github.com/stackp/Droopy (Pierre Duquesne)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Parst ``multipart/form-data`` streaming und schreibt Dateiteile direkt in
Tempdateien unter dem Upload-Verzeichnis (Prefix ``tmpdroopy``). Anschliessend
Umbenennung mit Nummerierung (``foto.png``, ``foto-1.png``, …).
Content-Length ist Pflicht; Request-Body wird gegen ``max_upload`` geprueft.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – Upload-Limit, Content-Length-Pflicht, exklusives Rename
Version 1.2.0 – 2026-08-16 – Vollstaendiger Dateikopf (Projekt-Metadaten)

Aufruf / Nutzung
----------------
  from pathlib import Path
  from droo.upload import save_uploads_from_request

  paths = save_uploads_from_request(
      rfile=handler.rfile,
      headers=handler.headers,
      directory=Path("uploads"),
      form_field="upfile",
      max_upload=512 * 1024 * 1024,
  )
"""

from __future__ import annotations

import os
import re
import tempfile
from email.parser import HeaderParser
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import BinaryIO, List, Mapping, Optional, Protocol, Tuple

from droo.config import DEFAULT_MAX_UPLOAD


class _Writable(Protocol):
    def write(self, data: bytes) -> int: ...


TMP_PREFIX = "tmpdroopy"

_CONTENT_TYPE_RE = re.compile(
    r"""multipart/form-data\s*;\s*boundary=("?)(?P<boundary>[^";\s]+)(\1)""",
    re.IGNORECASE,
)
_NAME_RE = re.compile(r'\bname="([^"]*)"', re.IGNORECASE)
_FILENAME_RE = re.compile(r'\bfilename="([^"]*)"', re.IGNORECASE)
_INVALID_FS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class UploadTooLargeError(ValueError):
    """Request-Body ueberschreitet das konfigurierte Maximum."""


class MissingContentLengthError(ValueError):
    """Content-Length-Header fehlt oder ist ungueltig."""


class _NullWriter:
    """Verwirft geschriebenen Bytes (fuer nicht genutzte Multipart-Parts)."""

    def write(self, data: bytes) -> int:
        return len(data)


class _LimitedReader:
    """Liest hoechstens ``limit`` Bytes vom zugrundeliegenden Stream."""

    def __init__(self, rfile: BinaryIO, limit: int) -> None:
        self._rfile = rfile
        self._remaining = max(0, limit)

    def read(self, n: int = -1) -> bytes:
        if self._remaining <= 0:
            return b""
        if n < 0 or n > self._remaining:
            n = self._remaining
        data = self._rfile.read(n) or b""
        self._remaining -= len(data)
        return data


class _PushbackReader:
    """Binary reader with pushback buffer."""

    def __init__(self, rfile: BinaryIO) -> None:
        self._rfile = rfile
        self._buf = bytearray()

    def push(self, data: bytes) -> None:
        if data:
            self._buf[0:0] = data

    def read(self, n: int) -> bytes:
        if n <= 0:
            return b""
        if self._buf:
            take = min(n, len(self._buf))
            out = bytes(self._buf[:take])
            del self._buf[:take]
            if len(out) == n:
                return out
            more = self._rfile.read(n - len(out))
            return out + (more or b"")
        return self._rfile.read(n) or b""

    def read_until(self, marker: bytes) -> bytes:
        """Read until marker; return data before marker (marker consumed)."""
        data = bytearray()
        mlen = len(marker)
        while True:
            idx = data.find(marker)
            if idx >= 0:
                before = bytes(data[:idx])
                rest = bytes(data[idx + mlen :])
                self.push(rest)
                return before
            chunk = self.read(65536)
            if not chunk:
                out = bytes(data)
                data.clear()
                return out
            data.extend(chunk)


def basename_only(path: str) -> str:
    """Extrahiert und bereinigt den Dateinamen (keine Pfadanteile, keine FS-Sonderzeichen).

    Parameter:
        path: Roher Dateiname oder Pfad aus dem Multipart-Header.

    Rueckgabe:
        Nur der Basisname; Fallback ``upload.bin``.

    Fehlerfaelle:
        Keine.
    """
    name = PurePosixPath(path).name
    name = PureWindowsPath(name).name
    name = Path(name).name
    name = _INVALID_FS_CHARS.sub("_", name)
    name = name.strip(" .")
    return name or "upload.bin"


def unique_destination(directory: Path, filename: str) -> Path:
    """Zielpfad-Kandidat ohne Existenz-Garantie (siehe claim_destination).

    Parameter:
        directory: Upload-Ordner.
        filename: Wunschname.

    Rueckgabe:
        Erster freier Kandidat (name.ext, name-1.ext, …).
    """
    directory = Path(directory)
    safe = basename_only(filename)
    candidate = directory / safe
    if not candidate.exists():
        return candidate
    root, ext = os.path.splitext(safe)
    i = 1
    while True:
        candidate = directory / f"{root}-{i}{ext}"
        if not candidate.exists():
            return candidate
        i += 1


def claim_destination(directory: Path, filename: str, tmp_path: Path) -> Path:
    """Verschiebt tmp exklusiv auf einen freien Zielnamen (Race-sicher).

    Parameter:
        directory: Upload-Ordner.
        filename: Wunschname.
        tmp_path: Vorhandene Tempdatei.

    Rueckgabe:
        Endgueltiger Zielpfad.

    Fehlerfaelle:
        OSError bei Dateisystemfehlern.
    """
    directory = Path(directory)
    safe = basename_only(filename)
    root, ext = os.path.splitext(safe)
    i = 0
    while True:
        name = safe if i == 0 else f"{root}-{i}{ext}"
        dest = directory / name
        try:
            fd = os.open(str(dest), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            i += 1
            continue
        os.replace(str(tmp_path), str(dest))
        return dest


def _parse_boundary(content_type: str) -> bytes:
    match = _CONTENT_TYPE_RE.search(content_type or "")
    if not match:
        raise ValueError("Content-Type ist kein multipart/form-data mit boundary")
    return match.group("boundary").encode("ascii", errors="strict")


def _parse_part_headers(header_bytes: bytes) -> Tuple[str, Optional[str]]:
    text = header_bytes.decode("utf-8", errors="replace")
    headers = HeaderParser().parsestr(text)
    disp = headers.get("Content-Disposition", "")
    name_m = _NAME_RE.search(disp)
    file_m = _FILENAME_RE.search(disp)
    name = name_m.group(1) if name_m else ""
    filename = basename_only(file_m.group(1)) if file_m else None
    return name, filename


def _stream_part_body(reader: _PushbackReader, boundary: bytes, out: _Writable) -> bool:
    """Schreibe Part-Body bis zur naechsten Boundary.

    Returns:
        True wenn weitere Parts folgen, False bei schliessender Boundary (--).
    """
    delimiter = b"\r\n--" + boundary
    buf = bytearray()
    dlen = len(delimiter)
    while True:
        idx = buf.find(delimiter)
        if idx >= 0:
            out.write(buf[:idx])
            after = bytes(buf[idx + dlen :])
            if after.startswith(b"--"):
                reader.push(after[2:])
                return False
            if after.startswith(b"\r\n"):
                reader.push(after[2:])
                return True
            reader.push(after)
            peek = reader.read(2)
            if peek.startswith(b"--"):
                reader.push(peek[2:])
                return False
            if peek == b"\r\n":
                return True
            reader.push(peek)
            return True

        keep = dlen - 1
        if len(buf) > keep:
            out.write(buf[:-keep])
            del buf[:-keep]
        chunk = reader.read(65536)
        if not chunk:
            if buf:
                out.write(buf)
            return False
        buf.extend(chunk)


def _require_content_length(headers: Mapping[str, str], max_upload: int) -> int:
    """Liest und validiert Content-Length gegen max_upload."""
    cl = None
    if hasattr(headers, "get"):
        cl = headers.get("Content-Length") or headers.get("content-length")
    if cl is None or str(cl).strip() == "":
        raise MissingContentLengthError("Content-Length-Header fehlt")
    try:
        content_length = int(cl)
    except (TypeError, ValueError) as exc:
        raise MissingContentLengthError("Content-Length ungueltig") from exc
    if content_length < 0:
        raise MissingContentLengthError("Content-Length ungueltig")
    if content_length > max_upload:
        raise UploadTooLargeError(
            f"Upload zu gross: {content_length} Bytes (Maximum {max_upload})"
        )
    return content_length


def save_uploads_from_request(
    rfile: BinaryIO,
    headers: Mapping[str, str],
    directory: Path,
    form_field: str = "upfile",
    file_mode: Optional[int] = None,
    max_upload: int = DEFAULT_MAX_UPLOAD,
) -> List[Path]:
    """Parst den Request-Body und speichert alle Dateien des Formularfelds.

    Parameter:
        rfile: Binaerer Request-Stream.
        headers: HTTP-Header (Content-Type, Content-Length).
        directory: Upload-Zielordner.
        form_field: Name des Dateifeldes.
        file_mode: Optionale oktale Rechte.
        max_upload: Maximale Body-Groesse in Bytes.

    Rueckgabe:
        Liste gespeicherter Pfade.

    Fehlerfaelle:
        MissingContentLengthError, UploadTooLargeError, ValueError, OSError.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    content_type = ""
    if hasattr(headers, "get"):
        content_type = headers.get("Content-Type", "") or headers.get("content-type", "")
    content_length = _require_content_length(headers, max_upload)
    boundary = _parse_boundary(content_type)

    stream: BinaryIO = _LimitedReader(rfile, content_length)  # type: ignore[assignment]
    reader = _PushbackReader(stream)
    first = b"--" + boundary
    preamble = reader.read_until(first)
    _ = preamble
    peek = reader.read(2)
    if peek == b"--":
        return []
    if peek != b"\r\n":
        reader.push(peek)

    saved: List[Path] = []
    more = True
    while more:
        header_blob = reader.read_until(b"\r\n\r\n")
        field_name, filename = _parse_part_headers(header_blob)

        if filename is not None and field_name == form_field and filename != "":
            fd, tmp_name = tempfile.mkstemp(prefix=TMP_PREFIX, dir=str(directory))
            try:
                with os.fdopen(fd, "wb") as tmp:
                    more = _stream_part_body(reader, boundary, tmp)
                dest = claim_destination(directory, filename, Path(tmp_name))
                if file_mode is not None:
                    os.chmod(dest, file_mode)
                saved.append(dest)
            except Exception:
                try:
                    Path(tmp_name).unlink(missing_ok=True)
                except OSError:
                    pass
                raise
        else:
            more = _stream_part_body(reader, boundary, _NullWriter())

    return saved


def list_published_files(directory: Path) -> List[str]:
    """Dateinamen im Upload-Ordner (ohne Tempdateien), sortiert.

    Parameter:
        directory: Upload-Ordner.

    Rueckgabe:
        Sortierte Liste von Dateinamen.
    """
    directory = Path(directory)
    names: List[str] = []
    if not directory.is_dir():
        return names
    for path in directory.iterdir():
        if path.is_file() and not path.name.startswith(TMP_PREFIX):
            names.append(path.name)
    names.sort(key=lambda s: s.lower())
    return names


def safe_join(directory: Path, name: str) -> Optional[Path]:
    """Join nur wenn die aufgeloeste Datei unter directory liegt.

    Parameter:
        directory: Erlaubtes Basisverzeichnis.
        name: Angeforderter Name/Pfad.

    Rueckgabe:
        Aufgeloester Dateipfad oder None bei Traversal/Fehlen.
    """
    directory = directory.resolve()
    base = basename_only(name)
    if not base or base in (".", ".."):
        return None
    candidate = (directory / base).resolve()
    try:
        candidate.relative_to(directory)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate
