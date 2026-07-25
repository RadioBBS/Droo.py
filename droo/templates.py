"""
Droo.py – HTML/CSS-Templates (Layout aus stackp/Droopy).

Projekt:     Droo.py
Modul:       droo/templates.py
Version:     1.0.0
Stand:       2026-07-25
Lizenz:      BSD-3-Clause
Erstellt mit: Cursor KI Model Auto (Composer)

Beschreibung
------------
Seiten ``main``, ``success``, ``error`` und ``linkurl`` mit %-Platzhaltern
fuer i18n und Server-Inhalte.

Aufruf / Nutzung
----------------
  from droo.templates import DEFAULT_TEMPLATES
  html = DEFAULT_TEMPLATES["main"] % context
"""

from __future__ import annotations

from typing import Dict

MAIN_TMPL = '''
<!doctype html>
<html>
<head>
<title>%(maintitle)s</title>

<meta name="viewport"
      content="width=device-width,initial-scale=1,maximum-scale=1" />
<style type="text/css">
<!--
* {margin: 0; padding: 0;}
body {text-align: center; background-color: #eee; font-family: sans-serif;
      color:#777;}
div {word-wrap: break-word;}
img {max-width: 100%%;}
a {color: #4499cc; text-decoration: none;}
.container {max-width: 700px; margin: auto; background-color: #fff;}
.box {padding-top: 20px; padding-bottom: 20px;}
#linkurl {background-color: #333;}
#linkurl a {color: #ddd; text-decoration: none;}
#linkurl a:hover {color: #fff;}
#message {padding: 5px 0; font-size: 2em; font-weight: lighter;
          letter-spacing: -2px; line-height: 50px; color: #aaa;}
#sending {display: none; font-style: italic;}
#sending .text {padding-top: 10px; color: #bbb; font-size: 0.8em;}
#wrapform {height: 90px; padding-top:40px;}
#progress {display: inline;  border-collapse: separate; empty-cells: show;
           border-spacing: 24px 0; padding: 0; vertical-align: bottom;}
#progress td {height: 17px; width: 17px; background-color: #eee;
              padding: 0px; border-radius: 90px; box-shadow: 0 0 3px #bbb;}
#userinfo {padding-bottom: 20px;}
#files {
  margin: auto;
  padding: 13px 0;
  text-align: left;
  overflow: auto;
  margin-bottom: 20px;
}
#files a {text-decoration: none; display: block; padding: 10px 20px;}
#files a:nth-child(2n+1) {background-color: #F7F7F7;}
#files a:link {color: #4499cc}
#files a:visited {color: #a0c0e0}
#files a:hover {background-color:#f0f0f0}
--></style>
<script language="JavaScript">
function swap() {
   document.getElementById("form").style.display = "none";
   document.getElementById("sending").style.display = "block";
   pulse(0);
}

function pulse(i) {
    var NUMCELL = 5;
    var cell = document.getElementById("cell-" + (i %% NUMCELL));
    var prev = document.getElementById("cell-"+((i - 1 + NUMCELL) %% NUMCELL));
    cell.style.backgroundColor = "#7ac";
    prev.style.backgroundColor = "#eee";
    setTimeout(function() {pulse(i+1);}, 300);
}

function onunload() {
   document.getElementById("form").style.display = "block";
   document.getElementById("sending").style.display = "none";
}
</script></head>
<body>
%(linkurl)s
<div class="container">
<div id="wrapform">
  <div id="form" class="box">
    <form method="post" enctype="multipart/form-data" action="">
      <input name="upfile" type="file" multiple="yes">
      <input value="%(submit)s" onclick="swap()" type="submit">
    </form>
  </div>
  <div id="sending" class="box">
    <table id="progress">
      <tr>
        <td id="cell-0"/><td id="cell-1"/><td id="cell-2"/>
        <td id="cell-3"/><td id="cell-4"/>
      </tr>
    </table>
    <div class="text">%(sending)s</div>
  </div>
</div>

<div id="userinfo">
  %(message)s
  %(divpicture)s
</div>

%(files)s
</div>
</body>
</html>
'''

SUCCESS_TMPL = '''
<!doctype html>
<html>
<head><title> %(successtitle)s </title>

<meta name="viewport"
      content="width=device-width,initial-scale=1,maximum-scale=1" />
<style type="text/css">
<!--
* {margin: 0; padding: 0;}
body {text-align: center; background-color: #eee; font-family: sans-serif;
      color:#777;}
div {word-wrap: break-word;}
img {max-width: 100%%;}
a {color: #4499cc; text-decoration: none;}
.container {max-width: 700px; margin: auto; background-color: #fff;}
.box {padding-top: 20px; padding-bottom: 20px;}
#linkurl {background-color: #333;}
#linkurl a {color: #ddd; text-decoration: none;}
#linkurl a:hover {color: #fff;}
#message {padding: 5px 0; font-size: 2em; font-weight: lighter;
          letter-spacing: -2px; line-height: 50px; color: #aaa;}
#sending {display: none; font-style: italic;}
#sending .text {padding-top: 10px; color: #bbb; font-size: 0.8em;}
#wrapform {height: 90px; padding-top:40px;}
#progress {display: inline;  border-collapse: separate; empty-cells: show;
           border-spacing: 24px 0; padding: 0; vertical-align: bottom;}
#progress td {height: 17px; width: 17px; background-color: #eee;
              padding: 0px; border-radius: 90px; box-shadow: 0 0 3px #bbb;}
#userinfo {padding-bottom: 20px;}
#files {
  margin: auto;
  padding: 13px 0;
  text-align: left;
  overflow: auto;
  margin-bottom: 20px;
}
#files a {text-decoration: none; display: block; padding: 10px 20px;}
#files a:nth-child(2n+1) {background-color: #F7F7F7;}
#files a:link {color: #4499cc}
#files a:visited {color: #a0c0e0}
#files a:hover {background-color:#f0f0f0}
--></style>
</head>
<body>
<div class="container">
<div id="wrapform">
  <div class="box">
    %(received)s
    <a href="/"> %(another)s </a>
  </div>
</div>

<div id="userinfo">
  %(message)s
  %(divpicture)s
</div>

</div>
</body>
</html>
'''

ERROR_TMPL = '''
<!doctype html>
<html>
<head><title> %(errortitle)s </title>

<meta name="viewport"
      content="width=device-width,initial-scale=1,maximum-scale=1" />
<style type="text/css">
<!--
* {margin: 0; padding: 0;}
body {text-align: center; background-color: #eee; font-family: sans-serif;
      color:#777;}
div {word-wrap: break-word;}
img {max-width: 100%%;}
a {color: #4499cc; text-decoration: none;}
.container {max-width: 700px; margin: auto; background-color: #fff;}
.box {padding-top: 20px; padding-bottom: 20px;}
#linkurl {background-color: #333;}
#linkurl a {color: #ddd; text-decoration: none;}
#linkurl a:hover {color: #fff;}
#message {padding: 5px 0; font-size: 2em; font-weight: lighter;
          letter-spacing: -2px; line-height: 50px; color: #aaa;}
#sending {display: none; font-style: italic;}
#sending .text {padding-top: 10px; color: #bbb; font-size: 0.8em;}
#wrapform {height: 90px; padding-top:40px;}
#progress {display: inline;  border-collapse: separate; empty-cells: show;
           border-spacing: 24px 0; padding: 0; vertical-align: bottom;}
#progress td {height: 17px; width: 17px; background-color: #eee;
              padding: 0px; border-radius: 90px; box-shadow: 0 0 3px #bbb;}
#userinfo {padding-bottom: 20px;}
#files {
  margin: auto;
  padding: 13px 0;
  text-align: left;
  overflow: auto;
  margin-bottom: 20px;
}
#files a {text-decoration: none; display: block; padding: 10px 20px;}
#files a:nth-child(2n+1) {background-color: #F7F7F7;}
#files a:link {color: #4499cc}
#files a:visited {color: #a0c0e0}
#files a:hover {background-color:#f0f0f0}
--></style>
</head>
<body>
<div class="container">
<div id="wrapform">
  <div class="box">
    %(problem)s
    <a href="/"> %(retry)s </a>
  </div>
</div>

<div id="userinfo">
  %(message)s
  %(divpicture)s
</div>

</div>
</body>
</html>
'''

LINKURL_TMPL = '''<div id="linkurl" class="box">
<a href="http://stackp.online.fr/droopy-ip.php?port=%(port)d&ssl=%(ssl)d"> %(discover)s
</a></div>'''

DEFAULT_TEMPLATES: Dict[str, str] = {
    'main': MAIN_TMPL,
    'success': SUCCESS_TMPL,
    'error': ERROR_TMPL,
    'linkurl': LINKURL_TMPL,
}
