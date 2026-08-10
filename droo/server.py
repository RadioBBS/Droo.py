"""
Droo.py – HTTP-Server und Request-Handler.

Projekt:     Droo.py
Modul:       droo/server.py
Version:     1.1.0
Stand:       2026-08-10
Lizenz:      BSD-3-Clause (basiert auf stackp/Droopy)
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Threaded HTTP(S)-Server mit Upload-Formular, optionalen Download-Links,
Basic-Auth und Bildanzeige. Konfiguration ueber Handler-Fabrik (keine
Klassen-Globals). HTML-Escaping fuer Dateinamen; Upload-Limit; TLS-Defaults.

Historie
--------
Version 1.0.0 – 2026-07-25 – Erstveroeffentlichung
Version 1.1.0 – 2026-08-10 – XSS-Fix, Upload-Limit, TLS-Defaults, Logging

Aufruf / Nutzung
----------------
  from droo.server import run_server
  from droo.config import DrooConfig

  run_server(DrooConfig(port=8000, directory=Path("uploads")))
"""

from __future__ import annotations

import base64
import html
import mimetypes
import secrets
import shutil
import socket
import ssl
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Dict, Optional
from urllib.parse import quote, unquote

from droo.config import DEFAULT_MAX_UPLOAD, DrooConfig
from droo.i18n import LOCALISATIONS
from droo.logutil import log_error, log_info
from droo.templates import DEFAULT_TEMPLATES
from droo.upload import (
    MissingContentLengthError,
    UploadTooLargeError,
    list_published_files,
    safe_join,
    save_uploads_from_request,
)

FORM_FIELD = "upfile"
PICTURE_PATH = "/__droo/picture"


class Abort(Exception):
    """Socket-Fehler aus dem Handler als Abort weiterreichen."""


@dataclass
class HandlerSettings:
    """Pro-Server-Einstellungen fuer den Request-Handler."""

    directory: Path
    message: str = ""
    picture: Optional[Path] = None
    publish_files: bool = False
    file_mode: Optional[int] = None
    auth: str = ""
    certfile: Optional[Path] = None
    max_upload: int = DEFAULT_MAX_UPLOAD
    allow_html_message: bool = False
    templates: Optional[Dict[str, str]] = None
    localisations: Optional[Dict[str, Dict[str, str]]] = None

    def __post_init__(self) -> None:
        self.directory = Path(self.directory)
        if self.templates is None:
            self.templates = DEFAULT_TEMPLATES
        if self.localisations is None:
            self.localisations = LOCALISATIONS


def make_handler(settings: HandlerSettings):
    """Erzeugt eine Handler-Klasse mit gebundenen Settings.

    Parameter:
        settings: HandlerSettings-Instanz.

    Rueckgabe:
        Subklasse von BaseHTTPRequestHandler.
    """

    class DrooUploadHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"
        cfg = settings

        def log_message(self, fmt: str, *args) -> None:
            line = "%s - %s" % (self.address_string(), fmt % args)
            sys.stderr.write(line + "\n")
            log_info("%s", line)

        def _header(self, name: str, default: str = "") -> str:
            return self.headers.get(name, default)

        def _check_auth(self) -> bool:
            if not self.cfg.auth:
                return True
            received = self._header("Authorization", "")
            expected = "Basic " + base64.b64encode(self.cfg.auth.encode("utf-8")).decode(
                "ascii"
            )
            if not secrets.compare_digest(received, expected):
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="Droo"')
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                return False
            return True

        @staticmethod
        def _prefcode_tuple(prefcode: str) -> tuple:
            bits = prefcode.split(";q=")
            if len(bits) == 1:
                return (1.0, bits[0].strip())
            try:
                return (float(bits[1]), bits[0].strip())
            except ValueError:
                return (0.0, bits[0].strip())

        def _choose_language(self) -> Dict[str, str]:
            assert self.cfg.localisations is not None
            accepted = []
            hdr = self._header("Accept-Language", "")
            if hdr:
                accepted = [self._prefcode_tuple(p) for p in hdr.split(",")]
                accepted.sort(key=lambda x: x[0], reverse=True)
            lang = "en"
            locs = self.cfg.localisations
            for _q, code in accepted:
                if code in locs:
                    lang = code
                    break
                short = code.split("-", 1)[0]
                if short in locs:
                    lang = short
                    break
            return locs.get(lang, locs["en"])

        def _format_message(self) -> str:
            if not self.cfg.message:
                return ""
            text = self.cfg.message
            if not self.cfg.allow_html_message:
                text = html.escape(text, quote=True)
            return f'<div id="message">{text}</div>'

        def _html(self, page: str) -> str:
            assert self.cfg.templates is not None
            dico = dict(self._choose_language())
            dico["message"] = self._format_message()
            if self.cfg.picture and self.cfg.picture.is_file():
                dico["divpicture"] = (
                    f'<div class="box"><img src="{PICTURE_PATH}"/></div>'
                )
            else:
                dico["divpicture"] = ""

            links = ""
            if self.cfg.publish_files:
                for name in list_published_files(self.cfg.directory):
                    encoded = quote(name)
                    safe_name = html.escape(name, quote=True)
                    links += f'<a href="/{encoded}">{safe_name}</a>'
                links = f'<div id="files">{links}</div>'
            dico["files"] = links

            if self.client_address[0] in ("127.0.0.1", "::1"):
                dico["port"] = self.server.server_port  # type: ignore[attr-defined]
                dico["ssl"] = int(self.cfg.certfile is not None)
                dico["linkurl"] = self.cfg.templates["linkurl"] % dico
            else:
                dico["linkurl"] = ""
            return self.cfg.templates[page] % dico

        def _send_headers(self, code: int, headers: Dict[str, object], end: bool = False) -> None:
            self.send_response(code)
            for key, value in headers.items():
                self.send_header(key, str(value))
            if end:
                self.end_headers()

        def _send_html(self, html_text: str) -> None:
            data = html_text.encode("utf-8")
            self._send_headers(
                200,
                {
                    "Content-type": "text/html; charset=utf-8",
                    "Content-length": len(data),
                },
                end=True,
            )
            self.wfile.write(data)

        def _send_plain_error(self, code: int, message: str) -> None:
            body = message.encode("utf-8")
            self.close_connection = True
            self._send_headers(
                code,
                {
                    "Content-type": "text/plain; charset=utf-8",
                    "Content-length": len(body),
                    "Connection": "close",
                },
                end=True,
            )
            self.wfile.write(body)

        def _send_file(self, localpath: Path) -> None:
            ctype = mimetypes.guess_type(str(localpath))[0] or "application/octet-stream"
            with localpath.open("rb") as fh:
                size = fh.seek(0, 2)
                fh.seek(0)
                self._send_headers(
                    200,
                    {"Content-length": size, "Content-type": ctype},
                    end=True,
                )
                shutil.copyfileobj(fh, self.wfile)

        def do_GET(self) -> None:  # noqa: N802
            if not self._check_auth():
                return
            raw = unquote(self.path.lstrip("/"))
            if self.cfg.picture and self.path == PICTURE_PATH:
                self._send_file(self.cfg.picture)
                return
            if self.cfg.publish_files and raw:
                local = safe_join(self.cfg.directory, raw)
                if local is not None:
                    self._send_file(local)
                    return
            self._send_html(self._html("main"))

        def do_POST(self) -> None:  # noqa: N802
            if not self._check_auth():
                return
            try:
                self.log_message("Started file transfer")
                paths = save_uploads_from_request(
                    rfile=self.rfile,
                    headers=self.headers,
                    directory=self.cfg.directory,
                    form_field=FORM_FIELD,
                    file_mode=self.cfg.file_mode,
                    max_upload=self.cfg.max_upload,
                )
                for path in paths:
                    self.log_message("Received: %s", path.name)
                if self.cfg.publish_files:
                    self._send_headers(301, {"Location": "/"}, end=True)
                else:
                    self._send_html(self._html("success"))
            except MissingContentLengthError as exc:
                log_error("%s", exc)
                self._send_plain_error(411, "Content-Length required")
            except UploadTooLargeError as exc:
                log_error("%s", exc)
                self._send_plain_error(413, "Payload Too Large")
            except Exception as exc:  # noqa: BLE001 — Fehlerseite an Client
                self.log_message("%r", exc)
                log_error("Upload-Fehler: %r", exc)
                self._send_html(self._html("error"))

        def handle(self) -> None:
            try:
                super().handle()
            except socket.error as exc:
                self.log_message("%s", exc)
                raise Abort(str(exc)) from exc

    return DrooUploadHandler


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded Server; Abort-Exceptions nicht als Crash loggen."""

    daemon_threads = True

    def handle_error(self, request, client_address) -> None:  # type: ignore[no-untyped-def]
        exc = sys.exc_info()[0]
        if exc is Abort:
            return
        super().handle_error(request, client_address)


def run_server(cfg: DrooConfig, timeout: int = 3 * 60) -> None:
    """Startet den Droo-Server (blockierend bis KeyboardInterrupt).

    Parameter:
        cfg: Laufzeitkonfiguration.
        timeout: Socket-Timeout in Sekunden.

    Fehlerfaelle:
        OSError bei Portbindung; ssl.SSLError bei PEM-Problemen.
    """
    socket.setdefaulttimeout(timeout)
    settings = HandlerSettings(
        directory=cfg.directory,
        message=cfg.message,
        picture=cfg.picture,
        publish_files=cfg.publish_files,
        file_mode=cfg.chmod,
        auth=cfg.auth,
        certfile=cfg.ssl,
        max_upload=cfg.max_upload,
        allow_html_message=cfg.allow_html_message,
    )
    handler = make_handler(settings)
    httpd = ThreadedHTTPServer(("", cfg.port), handler)

    if cfg.ssl:
        # Moderne TLS-Defaults der Python-SSLContext (ohne schwache Cipher-Overrides)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(certfile=str(cfg.ssl))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    log_info("Server lauscht auf Port %s (max_upload=%s)", cfg.port, cfg.max_upload)
    httpd.serve_forever()
