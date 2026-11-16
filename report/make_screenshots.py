"""Renders the REAL saved outputs (elt/freshcart_elt.ipynb, evidence/*.txt, evidence/stream/*.log) as PNG images
using headless Firefox. Nothing is invented: every panel is text copied from a saved output file."""
import html, json, os, re, subprocess

OUT = "screenshots"; os.makedirs(OUT, exist_ok=True)
nb = json.load(open("../elt/freshcart_elt.ipynb"))

def out_text(prefix, nth=0, skip_first_n=0):
    hits = [c for c in nb["cells"] if c["cell_type"] == "code" and "".join(c["source"]).startswith(prefix)]
    txt = ""
    for o in hits[nth].get("outputs", []):
        txt += ("".join(o.get("text", "")) or "".join(o.get("data", {}).get("text/plain", ""))) + "\n"
    txt = txt.replace("\\n", " ")
    txt = re.sub(r"[ ]{2,}(?=[\"\]])", " ", txt)
    return "\n".join(l.rstrip() for l in txt.splitlines() if l.strip())

def tail(t, n): return "\n".join(t.splitlines()[-n:])
def rd(p): return open(p).read().rstrip()

CSS = """body{margin:0;padding:18px;font:13px/1.45 'DejaVu Sans Mono',monospace;background:%s}
.p{margin:0 0 14px 0;border:1px solid %s;border-radius:6px;overflow:hidden;background:%s}
.h{padding:6px 12px;font:600 12px 'DejaVu Sans',sans-serif;background:%s;color:%s;border-bottom:1px solid %s}
pre{margin:0;padding:10px 12px;white-space:pre;color:%s}
.row{display:flex;gap:14px}.row .p{flex:1;min-width:0}"""
NOTE = CSS % ("#ffffff", "#cfcfcf", "#ffffff", "#f3f3f3", "#333", "#cfcfcf", "#202020")
TERM = CSS % ("#1b1d23", "#3a3f4b", "#0f1115", "#2b2f3a", "#d7dae0", "#3a3f4b", "#d7dae0")

def render(name, panels, style, width=1180, cols=1, foot=None):
    def pan(t, body): return f"<div class='p'><div class='h'>{html.escape(t)}</div><pre>{html.escape(body)}</pre></div>"
    items = [pan(t, b) for t, b in panels]
    if cols == 2:
        rows = ["<div class='row'>" + "".join(items[i:i + 2]) + "</div>" for i in range(0, len(items), 2)]
        body = "".join(rows)
    else:
        body = "".join(items)
    if foot: body += f"<div style='font:11px sans-serif;color:#888'>{html.escape(foot)}</div>"
    page = f"<html><head><meta charset='utf-8'><style>{style}</style></head><body>{body}</body></html>"
    lines = sum(len(b.splitlines()) + 3 for _, b in panels) if cols == 1 else \
            sum(max(len(panels[i][1].splitlines()), len(panels[min(i + 1, len(panels) - 1)][1].splitlines())) + 3 for i in range(0, len(panels), 2))
    height = int(60 + lines * 19.5)
    hp = f"/tmp/claude-1000/shots/{name}.html"; open(hp, "w").write(page)
    subprocess.run(["firefox", "--headless", "--no-remote", "--profile", "/tmp/claude-1000/ffprofile",
                    f"--window-size={width},{height}", "--screenshot", os.path.abspath(f"{OUT}/{name}.png"), "file://" + hp],
                   capture_output=True, timeout=120)
    print(name, os.path.exists(f"{OUT}/{name}.png"))

FOOT = "Output copied from the saved notebook elt/freshcart_elt.ipynb (executed on my Snowflake account)."

# B1
render("B1_baseline", [("run_pipeline()  -  first run (last lines)", tail(out_text("run_pipeline()", 0), 16)),
                       ("B1: first run compared with the expected numbers", out_text("# B1: compare"))], NOTE, foot=FOOT)
# B3
render("B3_reasons", [("B3 before: reasons for ORD-1006 (silver.orders_checked / quarantine)", out_text('print("--- silver.orders_checked (recomputed every run) ---")')),
                      ("B3 after the new rule (the notebook table truncates the 3rd reason as 'unsupp...')", out_text('print("--- silver.orders_checked ---")')),
                      ("Full reasons array: read-only query run afterwards in the same account", rd("evidence/b3_reasons_after.txt"))], NOTE, foot=FOOT)
# B4
render("B4_scd2", [("B4: prediction vs actual (after adding the CUST-02 Gold event)", tail(out_text("new_event = "), 7)),
                   ("dim.customers_scd2 for CUST-02", out_text("show(\"SELECT * FROM dim.customers_scd2 WHERE cust_id = 'CUST-02'")),
                   ("B4 idempotency: one more run changes nothing", tail(out_text("snap = snapshot()"), 4))], NOTE, foot=FOOT)
# B5
render("B5_quality_check", [("B5: run with the mock order ORD-9001 (new check fails on purpose)", tail(out_text("MOCK_WEB_ORDERS.append"), 11)),
                            ("B5: after removing ORD-9001 from bronze and gold, all six checks pass", tail(out_text("MOCK_WEB_ORDERS[:] ="), 11))], NOTE, foot=FOOT)
# Bonus
render("Bonus_stream_to_gold", [("Bonus: batch 2 (same five orders delivered again) - gold totals unchanged", tail(out_text("publish_orders()\nrun_stream_batch(seconds=60)\nshow"), 12)),
                                ("gold.fct_orders after both batches", out_text('show("SELECT order_id, order_date, tier, amount, currency, a'))], NOTE, foot=FOOT)

# C1: terminal
c1 = "\n".join(l for l in rd("evidence/c1_mage_run_test.txt").splitlines() if "FutureWarning" not in l)
render("C1_mage_run_test", [("$ mage run iris_project iris_classifier --test", c1)], TERM)

# D2 / D3: drivers + dispatcher (real 2-minute run logs)
def short(l):                         # keep the readable part of a driver line, cut the long JSON body
    return re.sub(r"\s+body=.*$", "  body={...no zone field...}", l) if "REJECTED" in l else l
def dlines(p, n_ack, n_nack):
    ls = rd(p).splitlines()
    acks = [l for l in ls if "-> ACK" in l or "Waiting" in l][:n_ack]
    nacks = [short(l) for l in ls if "REJECTED" in l][:n_nack]
    return "\n".join(acks + ["..."] + nacks)
def disp(p):
    ls = rd(p).splitlines()
    fmt = lambda l: re.sub(r"\s+\{.*?\}", "", l) + ("   <-- BAD message (no zone)" if "BAD" in l else "")
    fmt = lambda l: (l.split("{")[0].rstrip() + ("   <-- BAD message (no zone field)" if "BAD" in l else ""))
    return "\n".join([fmt(l) for l in ls[:9]] + ["..."] + [fmt(l) for l in ls if "BAD" in l][:3])
panels = [("$ python stream/dispatcher.py --duration 120   (every 10th message is bad)", disp("evidence/stream/d2_dispatcher.log")),
          ("$ python stream/driver.py Ravi \"bangalore.koramangala.*\"", dlines("evidence/stream/driver_Ravi.log", 7, 2)),
          ("$ python stream/driver.py Arjun \"bangalore.*.ride\"", dlines("evidence/stream/driver_Arjun.log", 7, 2)),
          ("$ python stream/driver.py Control \"bangalore.#\"", dlines("evidence/stream/driver_Control.log", 7, 2))]
render("D2_D3_stream_consoles", panels, TERM, width=1300, cols=1)
