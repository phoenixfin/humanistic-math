"""Interactive labeling UI (Phase 1) — stdlib only.

Serves data/labels/label_sample.csv one theorem at a time; every grade is
written immediately to data/labels/labels_filled.csv (safe to stop and
resume). Keyboard: 0-3 grade, arrows navigate, n focuses notes.

    py scripts/label_ui.py [port]
"""

import csv
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "labels" / "label_sample.csv"
FILLED = ROOT / "data" / "labels" / "labels_filled.csv"
FIELDS = ["label", "statement", "description", "url",
          "significance_0_3", "notes"]

_lock = threading.Lock()


def load_items() -> list[dict]:
    with open(SAMPLE, encoding="utf-8") as fh:
        items = list(csv.DictReader(fh))
    if FILLED.exists():
        with open(FILLED, encoding="utf-8") as fh:
            done = {r["label"]: r for r in csv.DictReader(fh)}
        for it in items:
            prev = done.get(it["label"])
            if prev:
                it["significance_0_3"] = prev.get("significance_0_3", "")
                it["notes"] = prev.get("notes", "")
    return items


ITEMS = load_items()


def save() -> None:
    with _lock:
        tmp = FILLED.with_suffix(".tmp")
        with open(tmp, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows({k: it.get(k, "") for k in FIELDS} for it in ITEMS)
        tmp.replace(FILLED)


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>Significance labeling</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;display:flex;height:100vh}
 #left{width:44%;padding:1.2rem 1.5rem;box-sizing:border-box;overflow-y:auto}
 #right{flex:1;border:none;border-left:1px solid #ccc}
 #stmt{font-family:ui-monospace,monospace;background:#f6f6f6;padding:.8rem;
       border-radius:6px;white-space:pre-wrap;word-break:break-word}
 #desc{color:#444;line-height:1.45}
 .grades{display:flex;gap:.5rem;margin:1rem 0}
 .grades button{flex:1;padding:.9rem .2rem;font-size:1rem;border-radius:8px;
       border:2px solid #bbb;background:#fff;cursor:pointer}
 .grades button:hover{border-color:#333}
 .grades button.sel{border-color:#0a7;background:#e6f7f1}
 .hint{font-size:.78rem;color:#777;margin-top:.15rem}
 #bar{height:6px;background:#eee;border-radius:3px;margin-bottom:1rem}
 #fill{height:100%;background:#0a7;border-radius:3px;width:0}
 nav{display:flex;gap:.5rem;align-items:center;margin-top:.6rem}
 nav button{padding:.45rem .9rem;border-radius:6px;border:1px solid #bbb;
       background:#fff;cursor:pointer}
 #notes{width:100%;box-sizing:border-box;margin-top:.6rem;padding:.5rem;
       border:1px solid #ccc;border-radius:6px;font-family:inherit}
 #done{color:#0a7;font-weight:600;display:none;margin-top:.8rem}
 .lbl{font-weight:700;font-size:1.15rem}
 a{color:#06c}
</style></head><body>
<div id="left">
 <div id="bar"><div id="fill"></div></div>
 <div><span class="lbl" id="mmlabel"></span>
      <span id="pos" style="color:#888;float:right"></span></div>
 <p id="stmt"></p>
 <p id="desc"></p>
 <p><a id="ext" target="_blank">open on us.metamath.org &#8599;</a></p>
 <div class="grades">
  <div style="flex:1"><button id="g0" onclick="grade(0)">0</button>
   <div class="hint">mechanical / trivial</div></div>
  <div style="flex:1"><button id="g1" onclick="grade(1)">1</button>
   <div class="hint">minor lemma</div></div>
  <div style="flex:1"><button id="g2" onclick="grade(2)">2</button>
   <div class="hint">named / reusable</div></div>
  <div style="flex:1"><button id="g3" onclick="grade(3)">3</button>
   <div class="hint">landmark</div></div>
 </div>
 <textarea id="notes" rows="2" placeholder="notes (optional)"
   onchange="saveNotes()"></textarea>
 <nav>
  <button onclick="move(-1)">&#8592; prev</button>
  <button onclick="move(1)">next &#8594;</button>
  <button onclick="nextUnlabeled()">next unlabeled &#8677;</button>
 </nav>
 <p class="hint">keys: 0-3 grade &amp; advance · &#8592;/&#8594; navigate ·
    n notes</p>
 <p id="done">All 100 labeled &#10003; — run
    <code>py scripts/run_experiments.py</code></p>
</div>
<iframe id="right"></iframe>
<script>
let items=[],i=0;
function el(id){return document.getElementById(id)}
async function boot(){
  items=await (await fetch('/api/items')).json();
  i=items.findIndex(t=>t.significance_0_3==='');
  if(i<0)i=0;
  show();
}
function show(){
  const t=items[i];
  el('mmlabel').textContent=t.label;
  el('pos').textContent=(i+1)+' / '+items.length;
  el('stmt').textContent=t.statement;
  el('desc').textContent=t.description;
  el('ext').href=t.url;
  el('right').src=t.url;
  el('notes').value=t.notes||'';
  for(let g=0;g<4;g++)
    el('g'+g).className=(t.significance_0_3===String(g))?'sel':'';
  const n=items.filter(t=>t.significance_0_3!=='').length;
  el('fill').style.width=(100*n/items.length)+'%';
  el('done').style.display=(n===items.length)?'block':'none';
}
async function put(){
  const t=items[i];
  await fetch('/api/label',{method:'POST',
    body:JSON.stringify({label:t.label,
      significance_0_3:t.significance_0_3,notes:t.notes||''})});
}
function grade(g){
  items[i].significance_0_3=String(g);
  put().then(()=>{ if(items.some(t=>t.significance_0_3==='')) nextUnlabeled();
                   else show(); });
}
function saveNotes(){ items[i].notes=el('notes').value; put(); show(); }
function move(d){ i=(i+d+items.length)%items.length; show(); }
function nextUnlabeled(){
  const j=items.findIndex((t,k)=>k>i&&t.significance_0_3==='');
  const k=j>=0?j:items.findIndex(t=>t.significance_0_3==='');
  if(k>=0)i=k; show();
}
document.addEventListener('keydown',e=>{
  if(e.target.tagName==='TEXTAREA'){ if(e.key==='Escape')e.target.blur();
                                     return; }
  if(e.key>='0'&&e.key<='3')grade(+e.key);
  else if(e.key==='ArrowLeft')move(-1);
  else if(e.key==='ArrowRight')move(1);
  else if(e.key==='n'){e.preventDefault();el('notes').focus();}
});
boot();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, ctype: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            self._send(PAGE.encode(), "text/html; charset=utf-8")
        elif self.path == "/api/items":
            self._send(json.dumps(ITEMS).encode(), "application/json")
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/label":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n))
        for it in ITEMS:
            if it["label"] == req["label"]:
                it["significance_0_3"] = str(req["significance_0_3"])
                it["notes"] = req.get("notes", "")
        save()
        self._send(b"{}", "application/json")

    def log_message(self, *args) -> None:  # keep the console quiet
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
    print(f"labeling UI on http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
