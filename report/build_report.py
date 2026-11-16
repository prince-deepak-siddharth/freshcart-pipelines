import subprocess, re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                                PageBreak, Preformatted, KeepTogether)

ROOT = ".."
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT).stdout.strip()
def rd(p): return open(f"evidence/{p}").read().rstrip()

ss = getSampleStyleSheet()
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Helvetica", fontSize=8.8, leading=11.4, spaceAfter=3)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=13, textColor=colors.HexColor("#1f4e79"), spaceBefore=8, spaceAfter=3)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=10.2, textColor=colors.HexColor("#2e75b6"), spaceBefore=6, spaceAfter=2)
CODE = ParagraphStyle("C", fontName="Courier", fontSize=6.6, leading=7.8)
TC = ParagraphStyle("TC", parent=B, fontSize=7.8, leading=9.6, spaceAfter=0)
TH = ParagraphStyle("TH", parent=TC, textColor=colors.white, fontName="Helvetica-Bold")
def P(t, st=B): return Paragraph(t, st)
def tbl(rows, widths, header=True):
    data = [[Paragraph(str(c), TH if (header and i == 0) else TC) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if header: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")))
    t.setStyle(TableStyle(st)); t._rows = rows; t._header = header; return t
def code(t): return Preformatted(t, CODE)

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 7); c.setFillColor(colors.grey)
    c.drawString(1.6 * cm, 0.9 * cm, "Assignment: From Git to Gold"); c.drawRightString(A4[0] - 1.6 * cm, 0.9 * cm, f"Page {d.page}"); c.restoreState()

BLS = ParagraphStyle("BL", parent=B, leftIndent=13, bulletIndent=3, spaceAfter=1.8)
BLS2 = ParagraphStyle("BL2", parent=BLS, leftIndent=26, bulletIndent=16)
SUB = "&nbsp;&nbsp;&ndash; "
def BL(items):
    return [Paragraph(t[len(SUB):], BLS2, bulletText="\u2013") if t.startswith(SUB) else Paragraph(t, BLS, bulletText="\u2022") for t in items]
F = lambda t: "<font face='Courier'>" + t + "</font>"

S = []
S += [P("<b>Assignment: From Git to Gold</b>", ParagraphStyle("T", parent=H1, fontSize=17, alignment=1)),
      P("Data Engineering &middot; Pipeline Orchestration", ParagraphStyle("s", parent=B, alignment=1)),
      P("Name: ______________________ &nbsp;&nbsp; Roll No: ______________ &nbsp;&nbsp; GitHub: https://github.com/&lt;your-user&gt;/freshcart-pipelines", ParagraphStyle("s2", parent=B, alignment=1)),
      Spacer(1, 4)]

# ------------------------------------------------------------------ PART A
S += [P("Part A. Git and CI/CD", H1), P("A1. Repository", H2)]
S += BL(["Repository <b>freshcart-pipelines</b> contains " + F("README.md, .gitignore, requirements.txt, elt/, iris_project/, stream/, tests/test_prepare_data.py, .github/workflows/ci.yml") + ".",
         F(".gitignore") + " excludes " + F(".env, *.pkl, *.csv, mage.log, __pycache__/") + " (plus caches and secrets); a " + F(".env.example") + " with placeholders is committed instead.",
         "Work was committed step by step (not one big commit). Output of " + F("git log --oneline") + ":"]) + [code(sh("git log --oneline")), P("A2. Where does each command act?", H2)]
S.append(tbl([
    ["Command", "Where the change happens", "What exactly happens?"],
    ["git init", "Working folder (creates the local repository)", "Creates a hidden .git folder in the project folder; from now on Git can store history there. No files are tracked yet."],
    ["git add train.py", "Working folder &rarr; staging area (index)", "Marks the current content of train.py to be part of the next commit; the file is not saved in history yet."],
    ["git commit -m \"msg\"", "Local repository (.git)", "Takes a snapshot of everything in the staging area and stores it as a new commit (author, time, message, parent). Nothing leaves my computer."],
    ["git remote add origin URL", "Local repository configuration (.git/config)", "Only stores a short name, origin, for the GitHub URL. No network traffic, no files change."],
    ["git push -u origin main", "Local repository &rarr; remote (GitHub)", "Uploads the commits GitHub does not have yet and moves the remote main branch forward; -u remembers origin/main as the default for later push/pull."],
    ["git pull origin main", "Remote &rarr; local repository &rarr; working folder", "Downloads new commits from origin/main (fetch) and merges them into my current branch, which also updates the files in my working folder."]],
    [3.4, 4.6, 9.8]))
S += [P("<b>After git commit, can your teammate see your code on GitHub?</b>")]
S += BL(["<b>No.</b> A commit only writes to my <i>local</i> repository (box 2 of the flow Working folder &rarr; Local Git &rarr; Remote Git &rarr; CI/CD).",
         "The code reaches GitHub, where the teammate can see it, only after " + F("git push") + "."])
S += [P("A3. CI workflow", H2)]
S += BL([F("tests/test_prepare_data.py") + " imports " + F("transform") + " from " + F("iris_project.transformers.prepare_data") + " and asserts 120 train / 30 test rows.",
         F(".github/workflows/ci.yml") + " runs on every push: checkout &rarr; Python 3.12 &rarr; " + F("pip install -r requirements.txt") + " &rarr; " + F("pytest") + ".",
         "Block files import the Mage decorators only if they are missing and fall back to no-op decorators, so they import cleanly in CI without Mage.",
         "Red/green behaviour (checked locally; screenshots of the real GitHub runs are in the appendix): with " + F("TEST_SIZE = 0.3") + " pytest reports " + F("assert 105 == 120") + " (red); after restoring 0.2 it passes (green)."])

# ------------------------------------------------------------------ PART B
S += [P("Part B. FreshCart ELT on Snowflake", H1), P("B1. Baseline run", H2)]
S += BL(["Notebook " + F("elt/freshcart_elt.ipynb") + " was run top to bottom on my own Snowflake account; a cell compares every number with the expected one.",
         "Expected and observed: bronze 8 (6 web + 2 mobile); " + F("silver.orders_clean") + " 6; quarantine 2 (ORD-1004, ORD-1006); orders after dedup 4; <b>GOLD: 4 orders, revenue Rs 7,785.00, 126 loyalty points</b>; rejected share 25%.",
         "Result: all eight comparisons show OK. Screenshots: appendix."])
S += [P("B2. Trace ORD-1003 and ORD-1005", H2), P("<b>ORD-1003</b>")]
S += BL(["<b>1. Bronze:</b> two rows in " + F("bronze.orders_raw") + ", stored exactly as received.",
         "Web copy: " + F("{order_id: ORD-1003, cust_email: meera@outlook.com, cust_name: MEERA S, order_date: 2026-09-02, amount: null, currency: INR, pincode: 400050, updated_at: 2026-09-02 09:10:00}"),
         "Mobile copy: " + F("{orderId: ORD-1003, customer:{email: Meera@Outlook.com, name: Meera S}, orderDate: 02/09/2026, total:{value: \"2,100.00\", currency: INR}, deliveryPin: 400050, updatedAt: 2026-09-02T18:40:00}"),
         "The field names differ because they come from two different systems (flat snake_case website API vs nested camelCase mobile API); ELT loads them untouched and fixes the shape later in SQL.",
         "<b>2. Silver:</b> in the " + F("unified") + " CTE web uses " + F("raw:order_id, raw:cust_email, raw:amount ...") + " and mobile uses " + F("raw:orderId, raw:customer.email, raw:total.value, raw:total.currency, raw:deliveryPin, raw:updatedAt") + ", so both map to the same columns.",
         "The " + F("typed") + " CTE then normalises:",
         "&nbsp;&nbsp;&ndash; " + F("LOWER(TRIM(cust_email))") + ": both become meera@outlook.com",
         "&nbsp;&nbsp;&ndash; " + F("INITCAP(RTRIM(TRIM(cust_name),'.'))") + ": both become Meera S",
         "&nbsp;&nbsp;&ndash; " + F("COALESCE(TRY_TO_DATE(..,'YYYY-MM-DD'), TRY_TO_DATE(..,'DD/MM/YYYY'), ..)") + ": both become 2026-09-02 (the mobile day-first date fails the first format)",
         "&nbsp;&nbsp;&ndash; " + F("TRY_TO_DECIMAL(REGEXP_REPLACE(amount,'[^0-9.-]',''),12,2)") + ": web stays NULL, mobile becomes 2100.00 (comma stripped)",
         "&nbsp;&nbsp;&ndash; " + F("UPPER(TRIM(currency))") + " and " + F("TRY_TO_TIMESTAMP_NTZ(updated_at)") + " make currency and timestamps comparable.",
         "Both rows have an empty " + F("reasons") + " array (a NULL amount is allowed), so both go to " + F("silver.orders_clean") + "; the web one has " + F("amount_missing = TRUE") + ".",
         "<b>3. Dedup:</b> " + F("QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_seq DESC) = 1") + " numbers the copies of each order newest first.",
         "The mobile copy (updated_at 18:40) is newer than the web copy (09:10), so it gets row number 1 and survives; the web copy (no amount) gets 2 and is dropped.",
         "If the timestamps were equal, the higher " + F("ingest_seq") + " (later arrival) would win, so re-runs give the same answer.",
         "<b>4. Gold:</b> " + F("amount_inr = ROUND(2100.00 x 1.0, 2) = 2100.00") + " (the INR rate is 1.0 in " + F("ref.fx_daily") + ").",
         "Meera is Platinum since 2022-11-01 (multiplier 3): " + F("loyalty_points = FLOOR(2100 / 100) x 3 = 21 x 3 = 63") + "; " + F("is_high_value") + " = TRUE (&ge; 2000)."])
S += [P("<b>ORD-1005 vs ORD-1001</b>")]
S += BL(["The responsible table is " + F("dim.customers_scd2") + ", joined in " + F("silver.orders_enriched") + " with " + F("c.email = o.email AND o.order_date BETWEEN c.valid_from AND c.valid_to") + ".",
         "Priya (CUST-01) has two periods: Silver 2023-04-10 to 2026-09-02 and Gold 2026-09-03 to 9999-12-31.",
         "ORD-1005 is dated 2026-09-03 &rarr; Gold period &rarr; multiplier 2 (" + F("ref.tier_multiplier") + "): FLOOR(899/100) x 2 = 8 x 2 = <b>16 points</b>.",
         "ORD-1001 is dated 2026-09-01 &rarr; Silver period &rarr; FLOOR(1250/100) x 1 = <b>12 points</b>.",
         "So the tier used is the one valid <i>on the order date</i>, not today's tier."])
S += [P("B3. New validation rule", H2), P("Line added inside " + F("ARRAY_CONSTRUCT_COMPACT(...)") + " of SQL_10:"),
      code("IFF(currency IS NULL OR currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)")]
S += BL(["<b>reasons for ORD-1006</b> (" + F("silver.orders_checked") + "): before " + F('["bad_email","bad_pincode"]') + "; after " + F('["bad_email","bad_pincode","unsupported_currency"]') + " (it is a EUR order).",
         "<b>Does the gold total change?</b> No: still 4 orders, Rs 7,785.00, 126 points. ORD-1006 was already rejected (bad email, bad pincode) and never reached gold; the rule only adds a third reason.",
         "<b>Second quarantine row?</b> No. The INSERT into " + F("quarantine.orders") + " has " + F("WHERE NOT EXISTS (... q.source = c.source AND EQUAL_NULL(q.order_id, c.order_id) AND EQUAL_NULL(q.row_data:UPDATED_AT::TIMESTAMP_NTZ, c.updated_at))") + ".",
         "The same source + order + version is already in quarantine, so nothing is added.",
         "Consequence: the old quarantine row keeps its old two reasons, while the recomputed " + F("silver.orders_checked") + " shows three.",
         "<b>Observed on Snowflake:</b> three reasons in silver, one quarantine row, gold unchanged."])
S += [P("B4. Change history and idempotency", H2),
      P("<i>Predictions were written before running (they are also in the notebook cell before the run).</i> Basis: ORD-1002 = 42.50 USD x 83.20 = Rs 3,536.00, FLOOR(3536/100) = 35 base points, dated 2026-09-01.")]
S.append(tbl([["Quantity", "Your prediction", "Actual after run"],
    ["Rows for CUST-02 in dim.customers_scd2", "2 (Silver 2024-01-15..2026-08-14, Gold 2026-08-15..9999-12-31); was 1", "2 (as predicted)"],
    ["Tier used for ORD-1002", "Gold (2026-09-01 is inside the new Gold period); was Silver", "Gold (as predicted)"],
    ["Loyalty points for ORD-1002", "35 x 2 = 70 (was 35 x 1 = 35)", "70 (as predicted)"],
    ["Total loyalty points in gold", "126 - 35 + 70 = 161", "161 (as predicted)"],
    ["Gold rows whose published_at changed", "1 (only ORD-1002; all other row_hash values are unchanged)", "1 (as predicted)"]], [5.2, 8.4, 4.2]))
S += [P("<b>Why re-running is safe (row_hash + MERGE) and why bronze still grows by 8 rows</b>")]
S += BL(["Every gold row carries " + F("row_hash = HASH(all business columns)") + ".",
         "The " + F("MERGE ... ON t.order_id = s.order_id") + " updates a row only " + F("WHEN MATCHED AND t.row_hash <> s.row_hash") + "; unchanged rows are not touched (their " + F("published_at") + " stays), changed rows are updated in place, new orders are inserted.",
         "Because the key is " + F("order_id") + ", running twice can never create duplicates and the same input gives the same output. Observed: a third run changed 0 rows and the total stayed 161.",
         "Bronze grows by 8 order rows on every run because it is an append-only copy of whatever was extracted (the sample records are re-sent each run); this keeps the raw history.",
         "The growth is harmless: silver de-duplicates (QUALIFY ROW_NUMBER) and quarantine/gold are keyed, so only bronze gets bigger."])
S += [P("B5. New quality check", H2)]
S += BL(["<b>Sixth check</b> in " + F("quality_checks()") + " (should be 0): " + F("SELECT COUNT_IF(amount_inr IS NULL AND amount IS NOT NULL) FROM gold.fct_orders") + " (an amount whose rupee value is missing, usually a missing FX rate).",
         "<b>Failing on purpose:</b> mock web order ORD-9001 (USD 10.00, dated 2026-08-20, otherwise valid).",
         "The FX table starts on 2026-09-01, so the order has no rate, " + F("amount_inr") + " is NULL and the check prints <b>PROBLEM</b> (also &quot;orders with an amount but no FX rate&quot;).",
         "<b>Removing it:</b> deleting it from the Python list is not enough, because bronze is append-only and the gold MERGE never deletes.",
         "I also ran " + F("DELETE FROM bronze.orders_raw WHERE raw:order_id = 'ORD-9001'") + " and the same for gold, then re-ran.",
         "<b>Observed:</b> with ORD-9001 two checks showed PROBLEM (1); after the cleanup all six checks were OK again."])
S += [P("<b>ELT vs ETL for FreshCart</b>")]
S += BL(["<b>Why ELT is better:</b> raw data is loaded first and kept untouched in bronze.",
         "A wrong rule (like the currency rule in B3 or the tier change in B4) can be fixed and recomputed from the raw copy without calling the APIs again.",
         "The heavy cleaning runs as SQL on Snowflake's scalable compute instead of a separate server, and raw storage gives an audit trail and cheap re-runs.",
         "<b>Where ETL would still win:</b> when sensitive data (e.g. card numbers or personal identifiers) must be masked or removed <i>before</i> it may land in the warehouse, for compliance; ELT would store the raw sensitive values first."])

# ------------------------------------------------------------------ PART C
S += [P("Part C. ML pipeline with Mage", H1), P("C1. Block graph and run", H2),
      Image("block_graph.png", width=15.5 * cm, height=15.5 * cm * 3.2 / 9.5 * 0.97)]
S += BL(["Baseline blocks: load_iris (data_loader) &rarr; prepare_data (transformer) &rarr; train_model (transformer) &rarr; save_results (data_exporter), each with a " + F("@test") + ".",
         "C3 adds the evaluate_model branch; C4 adds validate_iris.",
         "Output of " + F("mage run iris_project iris_classifier --test") + ": every block reports <i>1/1 tests passed</i> (appendix)."])
S += [P("C2. Tests as a gate (max_depth runs, iris_predictions.csv deleted before each run)", H2)]
S.append(tbl([["max_depth", "Test accuracy", "test_accuracy passed?", "iris_predictions.csv created?"],
              ["1", "0.6667", "No (below the 0.90 threshold)", "No"], ["2", "0.9333", "Yes", "Yes"], ["3", "0.9667", "Yes", "Yes"],
              ["4", "0.9333", "Yes", "Yes"], ["5", "0.9333", "Yes", "Yes"]], [2.4, 3.4, 6.2, 5.8]))
S += [P("<b>How a failing @test stops save_results</b>")]
S += BL(["Mage runs a block's " + F("@test") + " functions right after the block.",
         "If an assertion fails, Mage raises an exception (<i>Failed to pass tests for block train_model</i>) and the run ends.",
         "Downstream blocks are never started, so " + F("save_results") + " does not execute and no CSV is written (max_depth=1).",
         "<b>Why better than saving first and checking afterwards:</b> a bad result is never saved, so nobody can pick up a poor file by mistake.",
         "There is nothing to delete or roll back, and the failure shows up at the exact block that caused it."])
S += [P("C3. Evaluation branch", H2), P(F("train_model") + " now has two downstream blocks. Edited " + F("metadata.yaml") + ":"),
      code("- uuid: train_model\n  ...\n  downstream_blocks:\n  - save_results\n  - evaluate_model\n...\n- uuid: evaluate_model\n  name: evaluate_model\n  type: transformer\n  language: python\n  upstream_blocks:\n  - train_model\n  downstream_blocks: []")]
S += [P("Confusion matrix and metrics for max_depth=3 (30 test rows; output of the evaluate_model block):")]
S.append(tbl([["true \\ predicted", "setosa", "versicolor", "virginica"],
              ["setosa", "10", "0", "0"], ["versicolor", "0", "9", "1"], ["virginica", "0", "0", "10"]], [4.0, 3.0, 3.0, 3.0]))
S.append(Spacer(1, 4))
S.append(tbl([["class", "precision", "recall", "f1", "support"],
              ["setosa", "1.000", "1.000", "1.000", "10"], ["versicolor", "1.000", "0.900", "0.947", "10"],
              ["virginica", "0.909", "1.000", "0.952", "10"], ["accuracy", "-", "-", "0.967", "30"]], [3.5, 3.0, 3.0, 3.0, 3.0]))
S += BL(["The Mage UI screenshot of the branched graph is in the appendix."])
S += [P("C4. Own block", H2)]
S += BL([F("validate_iris") + " (transformer) sits between load_iris and prepare_data.",
         "Its " + F("@test") + " asserts there are no missing values and exactly 3 classes, so bad input stops the pipeline before training.",
         "Committed to the repository; pytest/CI still pass."])

# ------------------------------------------------------------------ PART D
S += [P("Part D. Food-order stream with RabbitMQ", H1), P("D1. Routing on paper (predictions made before running)", H2)]
S.append(tbl([["#", "Routing key", "Receiving queues"],
    ["1", "bangalore.koramangala.food", "Ravi (koramangala.*), Meena (*.food), Control (bangalore.#)"],
    ["2", "bangalore.indiranagar.ride", "Priya (indiranagar.*), Arjun (*.ride), Control"],
    ["3", "bangalore.whitefield.ride", "Arjun (*.ride), Control"],
    ["4", "chennai.tnagar.food", "Karthik (exact match) only"],
    ["5", "chennai.whitefield.ride", "dropped (no pattern matches; Control is bangalore only)"],
    ["6", "bangalore.koramangala", "Control only"]], [0.8, 5.6, 11.4]))
S += [P("<b>Question 6: which patterns can and cannot match a two-word key?</b>")]
S += BL([F("*") + " matches <i>exactly one</i> word, so " + F("bangalore.koramangala.*") + ", " + F("bangalore.indiranagar.*") + ", " + F("bangalore.*.ride") + " and " + F("bangalore.*.food") + " all need three words and <b>cannot</b> match.",
         F("#") + " matches <i>zero or more</i> words, so " + F("bangalore.#") + " <b>can</b> match " + F("bangalore.koramangala") + " (and even plain " + F("bangalore") + ").",
         "Karthik's pattern is an exact three-word key, so it cannot match either. Only Control receives the message."])
S += [P("D2. Build it", H2)]
S += BL([F("stream/dispatcher.py") + " publishes a JSON message " + F("{id, city, zone, type, ts}") + " every 2 s to the topic exchange " + F("rapido-dispatch") + " with routing key " + F("city.zone.type") + ".",
         F("stream/driver.py NAME PATTERN") + " declares a private (exclusive) queue, binds it with PATTERN, prints each request and ACKs it.",
         "Run with six drivers (Ravi, Priya, Arjun, Meena, Karthik, Control) against a local RabbitMQ 3 in Docker.",
         "Proof for D1: the dispatcher published exactly the six keys of the table; each key reached exactly the predicted queues (key 5 reached nobody):"]) + [
      Preformatted("\n".join([l[:118] for l in rd("stream/d1_dispatcher.log").splitlines()[:6]]), CODE)]
d1 = []
import glob, os
for key in ["bangalore.koramangala.food", "bangalore.indiranagar.ride", "bangalore.whitefield.ride", "chennai.tnagar.food", "chennai.whitefield.ride", "bangalore.koramangala"]:
    who = []
    for f in sorted(glob.glob("evidence/stream/d1/driver_*.log")):
        name = os.path.basename(f)[7:-4]
        for l in open(f):
            if re.search(r"key=" + re.escape(key) + r"\s+got", l): who.append(name)
    d1.append([key, ", ".join(who) if who else "(none: dropped)"])
S.append(tbl([["Routing key", "Queues that actually received it (from the driver logs)"]] + d1, [6.5, 11.3]))
S += BL(["Then the dispatcher ran for 2 minutes (60 messages) with all six drivers.",
         "ACK / NACK per driver: " + "; ".join(f"{os.path.basename(f)[7:-4]} {open(f).read().count('-> ACK')} / {open(f).read().count('REJECTED')}" for f in sorted(glob.glob("evidence/stream/driver_*.log"))) + ". Console excerpts are in the appendix."])
S += [P("D3. ACK and NACK", H2)]
S += BL([F("driver.py") + " calls " + F("basic_nack(delivery_tag, requeue=False)") + " when a message has no " + F("zone") + " field (or is not valid JSON) and " + F("basic_ack") + " otherwise.",
         "The dispatcher (" + F("--bad-every 10") + ") makes every 10th message bad.",
         "Proof: the drivers printed <i>REJECTED (no zone) -&gt; NACK, requeue=False</i> for messages #10, #20 ... #60 (only the drivers whose pattern matched) and <i>-&gt; ACK</i> for all others: bad ones are discarded, good ones processed (appendix)."])
S += [P("<b>What happens if the driver crashes before sending the ACK?</b>")]
S += BL(["The broker keeps a delivered message as &quot;unacknowledged&quot; until it gets an ACK.",
         "When the driver's connection dies, the broker puts the message back into the queue (marked redelivered) and delivers it again, so it is not lost.",
         "This is at-least-once delivery: the message may be processed twice, so processing should tolerate duplicates.",
         "Caveat for my setup: my driver queues are <i>exclusive</i> and auto-delete, so they vanish with the connection; with a durable named queue the message would be redelivered."])
S += [P("<b>What would requeue=True do for a message that is always bad?</b>")]
S += BL(["The broker returns it to the head of the queue, the driver receives it again, rejects it again, and so on: an endless poison-message loop.",
         "It wastes CPU/network and, with prefetch 1, blocks the good messages behind it.",
         "That is why bad messages are NACKed with " + F("requeue=False") + " (or routed to a dead-letter exchange for inspection)."])

# ------------------------------------------------------------------ BONUS
S += [P("Bonus. Stream into the lakehouse (+10)", H1)]
S += BL([F("stream/order_publisher.py") + " publishes five FreshCart-style order messages to the durable queue " + F("freshcart.orders") + ".",
         F("stream/lakehouse_consumer.py") + " (also embedded in the notebook's Bonus section) collects messages for one minute and ACKs them once the batch is in memory.",
         "The notebook then calls " + F('write_landing("web", orders, run_id)') + " &rarr; " + F("load_file(...)") + " &rarr; the same transform SQL, so the orders reach " + F("gold.fct_orders") + ".",
         "<b>Idempotency:</b> the second batch re-delivers the same order_ids; bronze grows, silver de-duplicates, and the gold MERGE only touches rows whose row_hash changed.",
         "<b>Observed:</b> batch 1 and batch 2 both ended with 9 orders, Rs 14,534.00 and 324 loyalty points (4 + 5 orders). Screenshots: appendix."])

# ------------------------------------------------------------------ PART E
S += [P("Part E. How the four pieces fit together", H1), Image("integration.png", width=16.2 * cm, height=16.2 * cm * 6.6 / 10 * 0.97)]
S += BL(["<b>Code in Git:</b> every push triggers CI, which runs pytest on the Mage block code.",
         "<b>ELT pipeline:</b> turns raw API data into bronze &rarr; silver &rarr; gold in Snowflake.",
         "<b>ML pipeline:</b> trains on data and refuses to save a bad model (test gate).",
         "<b>Stream:</b> feeds events (orders) into the same bronze layer through landing files (bonus)."])
S += [P("Reflection: one thing that broke", H2)]
S += BL(["<b>What broke:</b> my first RabbitMQ run failed with " + F("pika.exceptions.AMQPConnectionError") + " in every script, although the Docker container looked started.",
         "<b>How I found the cause:</b> " + F("docker logs rabbit") + " showed the broker had crashed at start-up (<i>Error when reading /var/lib/rabbitmq/.erlang.cookie: eacces</i>), so nothing listened on port 5672; a quick connection test in Python confirmed it.",
         "<b>How I fixed it:</b> started the container with " + F("--user root -e RABBITMQ_ERLANG_COOKIE=...") + "; the same scripts then connected.",
         "<b>Two smaller problems:</b> background drivers ignored Ctrl-C (SIGINT) and mixed two runs in the logs, fixed by stopping them with SIGTERM; " + F("mage-ai") + " would not install on the newest Python, so I used Python 3.12 (the same version as the CI workflow).",
         "<b>Lesson:</b> read the logs of the component that is silently down before debugging my own code."])

# ------------------------------------------------------------------ APPENDIX
S += [PageBreak(), P("Appendix (evidence; excluded from the 8-page limit)", H1),
      P("<b>Evidence in this appendix:</b> the screenshots are at the start (section \"Screenshots\"), followed by text copies of the raw outputs. The GitHub Actions list is a real screenshot; the Snowflake panels are rendered from the saved notebook outputs and the Mage UI is a real browser screenshot of my local Mage server.", B),
      P("A3. pytest, local red then green", H2), code(rd("a3_red_pytest.txt")[-700:] + "\n\n" + rd("a3_green_pytest.txt")),
      P("C1. mage run iris_project iris_classifier --test", H2), code(rd("c1_mage_run_test.txt")),
      P("C2. max_depth runs (raw output)", H2), code(rd("c2_depth_runs.txt")),
      P("D3. Console excerpt, 2-minute run (Control and Meena)", H2),
      code("\n".join(rd("stream/driver_Control.log").splitlines()[:16] + ["..."] + [l for l in rd("stream/driver_Control.log").splitlines() if "REJECTED" in l])),
      code("\n".join(rd("stream/driver_Meena.log").splitlines()[:8])),
      P("D2. Dispatcher excerpt", H2), code("\n".join(l[:150] for l in rd("stream/d2_dispatcher.log").splitlines()[:12]))]



# ---- screenshots (real pixels where possible; see captions) ----
from PIL import Image as _PI
def _shot(title, fname, caption, w=16.5):
    p = "screenshots/" + fname
    out = [P("<b>" + title + "</b>", B)]
    if os.path.exists(p):
        iw, ih = _PI.open(p).size
        out += [Image(p, width=w * cm, height=w * cm * ih / iw),
                P("<font color='#666666'><i>" + caption + "</i></font>", ParagraphStyle("cap", parent=B, fontSize=7.5, spaceAfter=8))]
    else:
        out += [P("<font color='#888888'><i>[ Insert screenshot here ]</i></font>", B), Spacer(1, 70)]
    return [KeepTogether(out)]
LOCAL = "Rendered from the real saved output of the notebook elt/freshcart_elt.ipynb (run on my own Snowflake account)."
S += [P("Screenshots", H2)]
S += _shot("A3 - GitHub Actions: green, red (test_size = 0.3) and green again after the fix", "A3_github_actions_runs.png",
           "Screenshot of the public Actions page of the repository: CI #1 green, CI #2 red, CI #3 green (fix). Add your own screenshot of the red run's failing pytest step if you wish.")
S += _shot("B1 - Baseline run and comparison with the expected numbers", "B1_baseline.png", LOCAL)
S += _shot("B3 - reasons for ORD-1006 before and after the new rule", "B3_reasons.png", LOCAL)
S += _shot("B4 - SCD2 change, prediction vs actual, idempotency", "B4_scd2.png", LOCAL)
S += _shot("B5 - new check fails on purpose, then passes after cleanup", "B5_quality_check.png", LOCAL)
S += _shot("C1 - mage run iris_project iris_classifier --test", "C1_mage_run_test.png", "Terminal output of the real run (saved from the command; see evidence/c1_mage_run_test.txt).")
S += _shot("C3 - Mage UI: pipeline graph with the branch", "c3_mage_ui.png", "Real screenshot of the Mage UI (local server, headless browser): train_model has two downstream blocks, save_results and evaluate_model.", w=16.5)
S += _shot("D2 / D3 - dispatcher and three drivers (2-minute run): ACK and NACK", "D2_D3_stream_consoles.png", "Console output of the real 2-minute run (evidence/stream/*.log); long JSON bodies of the NACKed lines are abbreviated.")
S += _shot("Bonus - gold totals identical after both stream batches", "Bonus_stream_to_gold.png", LOCAL)
S += [PageBreak()]

# ---- appendix: text copies of the Snowflake notebook outputs ----
import json
_nb = json.load(open("../elt/freshcart_elt.ipynb"))
def _out(prefix, nth=0, tail=None, head=None):
    hits = [c for c in _nb["cells"] if c["cell_type"] == "code" and "".join(c["source"]).startswith(prefix)]
    c = hits[nth]; txt = ""
    for o in c.get("outputs", []):
        txt += ("".join(o.get("text", "")) or "".join(o.get("data", {}).get("text/plain", ""))) + "\n"
    txt = txt.replace("\u20b9", "Rs ").replace("\\n", " ")
    txt = re.sub(r"[ ]{2,}(?=[\"\]])", " ", txt)
    lines = [l.rstrip() for l in txt.splitlines() if l.strip()]
    if head: lines = lines[:head]
    if tail: lines = lines[-tail:]
    return "\n".join(l[:135] for l in lines)
S += [P("Snowflake outputs (copied from elt/freshcart_elt.ipynb, run on my own account)", H2),
      P("<b>B1</b> - first run compared with the expected numbers:"), code(_out("# B1: compare")),
      P("<b>B3</b> - reasons for ORD-1006 before and after the new rule; quarantine and gold:"),
      code(_out('print("--- silver.orders_checked (recomputed every run) ---")')), code(_out('print("--- silver.orders_checked ---")')),
      P("<b>B3</b> - full reasons array and quarantine row, from a read-only query run afterwards (the notebook table above is truncated by pandas):"), code(rd("b3_reasons_after.txt")),
      P("<b>B4</b> - prediction vs actual, and the SCD2 rows of CUST-02:"), code(_out("new_event = ", tail=7)), code(_out("show(\"SELECT * FROM dim.customers_scd2 WHERE cust_id = 'CUST-02'")),
      P("<b>B4</b> - idempotency (third run):"), code(_out("snap = snapshot()", tail=3)),
      P("<b>B5</b> - the new check fails on purpose (ORD-9001), then everything is OK after cleanup:"),
      code(_out("MOCK_WEB_ORDERS.append", tail=9)), code(_out("MOCK_WEB_ORDERS[:] =", tail=9)),
      P("<b>Bonus</b> - gold after the second batch (identical to the first):"), code(_out("publish_orders()\nrun_stream_batch(seconds=60)\nshow", tail=6)),
      code(_out('show("SELECT order_id, order_date, tier, amount, currency, a'))]

if __name__ == "__main__":
  doc = SimpleDocTemplate("Report.pdf", pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.4 * cm, bottomMargin=1.6 * cm,
                        title="From Git to Gold - Report")
  doc.build(S, onFirstPage=footer, onLaterPages=footer)
  print("built")
