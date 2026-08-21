"""Small dependency-free web interface for ProofPilot."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.planner import make_plan

ROOT = Path(__file__).parent

HTML = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ProofPilot</title>
<style>body{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px;background:#101827;color:#e5e7eb}h1{color:#93c5fd}p{color:#b6c2d9}textarea{width:100%;min-height:100px;padding:14px;border-radius:10px;background:#172338;color:#fff;border:1px solid #334155;font-size:16px}button{margin-top:12px;padding:11px 18px;border:0;border-radius:9px;background:#60a5fa;color:#08111f;font-weight:700;cursor:pointer}#meta{margin-top:20px;color:#93c5fd}.step{background:#172338;border:1px solid #334155;border-radius:10px;padding:14px;margin:12px 0}.step h3{margin:0 0 8px;color:#bfdbfe}.label{font-size:12px;text-transform:uppercase;color:#94a3b8;letter-spacing:.06em}</style>
<body><h1>ProofPilot</h1><p>Turn an ambiguous goal into actions with verifiable evidence and explicit risks.</p>
<textarea id="goal" placeholder="Example: Launch a small online workshop next month"></textarea><br><button onclick="plan()">Build evidence plan</button><div id="meta"></div><section id="steps"></section>
<script>const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));async function plan(){const goal=document.getElementById('goal').value;const meta=document.getElementById('meta');const out=document.getElementById('steps');meta.textContent='Planning…';out.innerHTML='';try{const r=await fetch('/api/plan',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({goal})});const d=await r.json();meta.textContent=`Mode: ${esc(d.mode)} · ${d.steps.length} steps`;out.innerHTML=d.steps.map(s=>`<article class="step"><h3>${esc(s.order)}. ${esc(s.action)}</h3><div class="label">Evidence</div><div>${esc(s.evidence)}</div><div class="label">Risk</div><div>${esc(s.risk)}</div></article>`).join('')}catch(e){meta.textContent=esc(e.message)}}</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, b'{"ok":true}', "application/json")
        else:
            self._send(200, HTML.encode())

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/plan":
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            result = make_plan(str(payload.get("goal", "")))
            self._send(200, json.dumps(result).encode(), "application/json")
        except Exception as exc:
            self._send(400, json.dumps({"error": str(exc)}).encode(), "application/json")


if __name__ == "__main__":
    print("ProofPilot listening on http://127.0.0.1:8080")
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
