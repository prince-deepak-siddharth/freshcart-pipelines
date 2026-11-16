import subprocess, re
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

S = []
S += [P("<b>Assignment: From Git to Gold</b>", ParagraphStyle("T", parent=H1, fontSize=17, alignment=1)),
      P("Data Engineering &middot; Pipeline Orchestration", ParagraphStyle("s", parent=B, alignment=1)),
      P("Name: ______________________ &nbsp;&nbsp; Roll No: ______________ &nbsp;&nbsp; GitHub: https://github.com/&lt;your-user&gt;/freshcart-pipelines", ParagraphStyle("s2", parent=B, alignment=1)),
      Spacer(1, 4)]

# ------------------------------------------------------------------ PART A
S += [P("Part A. Git and CI/CD", H1), P("A1. Repository", H2),
      P("Repository <b>freshcart-pipelines</b> with <font face='Courier'>README.md, .gitignore, requirements.txt, elt/, iris_project/, stream/, tests/test_prepare_data.py, .github/workflows/ci.yml</font>. "
        "<font face='Courier'>.gitignore</font> excludes <font face='Courier'>.env, *.pkl, *.csv, mage.log, __pycache__/</font> (plus caches and secrets). Commits made step by step (not one big commit):"),
      code(sh("git log --oneline")), P("A2. Where does each command act?", H2)]
S.append(tbl([
    ["Command", "Where the change happens", "What exactly happens?"],
    ["git init", "Working folder (creates the local repository)", "Creates a hidden .git folder in the project folder; from now on Git can store history there. No files are tracked yet."],
    ["git add train.py", "Working folder &rarr; staging area (index)", "Marks the current content of train.py to be part of the next commit; the file is not saved in history yet."],
    ["git commit -m \"msg\"", "Local repository (.git)", "Takes a snapshot of everything in the staging area and stores it as a new commit (with author, time, message and its parent). Nothing leaves my computer."],
    ["git remote add origin URL", "Local repository configuration (.git/config)", "Only stores a short name, origin, for the GitHub URL. No network traffic, no files change."],
    ["git push -u origin main", "Local repository &rarr; remote (GitHub)", "Uploads the commits that GitHub does not have yet and moves the remote main branch forward; -u remembers origin/main as the default for later push/pull."],
    ["git pull origin main", "Remote &rarr; local repository &rarr; working folder", "Downloads new commits from origin/main (fetch) and merges them into my current branch, which also updates the files in my working folder."]],
    [3.4, 4.6, 9.8]))
S += [P("<b>After git commit, can your teammate see your code on GitHub?</b> No. A commit only writes to my <i>local</i> repository (box 2 of the flow Working folder &rarr; Local Git &rarr; Remote Git &rarr; CI/CD). The code reaches GitHub, where the teammate can see it, only after <font face='Courier'>git push</font>.", B),
      P("A3. CI workflow", H2),
      P("<font face='Courier'>tests/test_prepare_data.py</font> imports <font face='Courier'>transform</font> from <font face='Courier'>iris_project.transformers.prepare_data</font> and asserts 120 train / 30 test rows. "
        "<font face='Courier'>.github/workflows/ci.yml</font> runs on every push: checkout &rarr; Python 3.12 &rarr; <font face='Courier'>pip install -r requirements.txt</font> &rarr; <font face='Courier'>pytest</font>. Block files import the Mage decorators only if they are missing and fall back to no-op decorators, so they import cleanly in CI without Mage. "
        "Local evidence of the red/green behaviour (the screenshots of the real GitHub Actions runs are in the appendix): with <font face='Courier'>TEST_SIZE = 0.3</font> pytest reports <font face='Courier'>assert 105 == 120</font> (red); after restoring 0.2 it passes (green)."),
      ]

# ------------------------------------------------------------------ PART B
S += [P("Part B. FreshCart ELT on Snowflake", H1), P("B1. Baseline run", H2),
      P("Notebook <font face='Courier'>elt/freshcart_elt.ipynb</font> (cell B1 compares each number with the expected one). Expected values: bronze 8 (6 web + 2 mobile), "
        "<font face='Courier'>silver.orders_clean</font> 6, quarantine 2 (ORD-1004, ORD-1006), orders after dedup 4, <b>GOLD: 4 orders, revenue Rs 7,785.00, 126 loyalty points</b>, rejected share 25%. Result on my Snowflake account: all eight comparisons show OK (8 / 6 / 2 / 4 / 4 / 7,785.00 / 126 / 25%). Screenshots: appendix.")]
S += [P("B2. Trace ORD-1003 and ORD-1005", H2),
      P("<b>1. Bronze.</b> Two rows in <font face='Courier'>bronze.orders_raw</font>, stored exactly as received. Web: <font face='Courier'>{order_id: ORD-1003, cust_email: meera@outlook.com, cust_name: MEERA S, order_date: 2026-09-02, amount: null, currency: INR, pincode: 400050, updated_at: 2026-09-02 09:10:00}</font>. "
        "Mobile: <font face='Courier'>{orderId: ORD-1003, customer:{email: Meera@Outlook.com, name: Meera S}, orderDate: 02/09/2026, total:{value: \"2,100.00\", currency: INR}, deliveryPin: 400050, updatedAt: 2026-09-02T18:40:00}</font>. "
        "The names differ because they come from two different systems (flat snake_case website API vs nested camelCase mobile API); ELT loads them untouched and fixes the shape later in SQL."),
      P("<b>2. Silver.</b> In the <font face='Courier'>unified</font> CTE web uses <font face='Courier'>raw:order_id, raw:cust_email, raw:amount...</font> and mobile uses <font face='Courier'>raw:orderId, raw:customer.email, raw:total.value, raw:total.currency, raw:deliveryPin, raw:updatedAt</font> &rarr; same columns. "
        "The <font face='Courier'>typed</font> CTE then normalises: <font face='Courier'>LOWER(TRIM(cust_email))</font> (both &rarr; meera@outlook.com), <font face='Courier'>INITCAP(RTRIM(TRIM(cust_name),'.'))</font> (&rarr; Meera S), "
        "<font face='Courier'>COALESCE(TRY_TO_DATE(..,'YYYY-MM-DD'), TRY_TO_DATE(..,'DD/MM/YYYY'),..)</font> (both &rarr; 2026-09-02; the mobile day-first date fails the first format), "
        "<font face='Courier'>TRY_TO_DECIMAL(REGEXP_REPLACE(amount,'[^0-9.-]',''),12,2)</font> (web NULL, mobile 2100.00 after the comma is stripped), <font face='Courier'>UPPER(TRIM(currency))</font>, <font face='Courier'>TRY_TO_TIMESTAMP_NTZ(updated_at)</font>. "
        "Both rows have an empty <font face='Courier'>reasons</font> array (a NULL amount is allowed), so both are in <font face='Courier'>silver.orders_clean</font>; the web one has <font face='Courier'>amount_missing = TRUE</font>."),
      P("<b>3. Dedup.</b> <font face='Courier'>QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_seq DESC) = 1</font> numbers the copies of each order newest first. The mobile copy (updated_at 18:40) is newer than the web copy (09:10), gets row number 1 and survives; the web copy (no amount) gets 2 and is dropped. If the timestamps were equal, the higher <font face='Courier'>ingest_seq</font> (later arrival) would win, so re-runs give the same answer."),
      P("<b>4. Gold.</b> <font face='Courier'>amount_inr = ROUND(2100.00 x 1.0, 2) = 2100.00</font> (INR rate is 1.0 from <font face='Courier'>ref.fx_daily</font>). Meera is Platinum since 2022-11-01, multiplier 3: <font face='Courier'>loyalty_points = FLOOR(2100 / 100) x 3 = 21 x 3 = 63</font>; <font face='Courier'>is_high_value</font> = TRUE (&ge; 2000)."),
      P("<b>ORD-1005 vs ORD-1001.</b> The table is <font face='Courier'>dim.customers_scd2</font>, joined in <font face='Courier'>silver.orders_enriched</font> with <font face='Courier'>c.email = o.email AND o.order_date BETWEEN c.valid_from AND c.valid_to</font>. Priya (CUST-01) has two periods: Silver 2023-04-10..2026-09-02 and Gold 2026-09-03..9999-12-31. "
        "ORD-1005 is dated 2026-09-03 &rarr; Gold period &rarr; multiplier 2 (<font face='Courier'>ref.tier_multiplier</font>): FLOOR(899/100) x 2 = 8 x 2 = 16 points. ORD-1001 is dated 2026-09-01 &rarr; Silver period &rarr; FLOOR(1250/100) x 1 = 12 points. The tier is the one valid <i>on the order date</i>, not today's tier.")]
S += [P("B3. New validation rule", H2),
      P("Added inside <font face='Courier'>ARRAY_CONSTRUCT_COMPACT(...)</font> of SQL_10: "),
      code("IFF(currency IS NULL OR currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL)"),
      P("<b>reasons for ORD-1006</b> (<font face='Courier'>silver.orders_checked</font>): before <font face='Courier'>[\"bad_email\",\"bad_pincode\"]</font>, after <font face='Courier'>[\"bad_email\",\"bad_pincode\",\"unsupported_currency\"]</font> (it is a EUR order). "
        "<b>Gold total:</b> unchanged (4 orders, Rs 7,785.00, 126 points), because ORD-1006 was already rejected (bad email, bad pincode) and never reached gold; the new rule only adds a third reason. "
        "<b>Second quarantine row?</b> No. The INSERT into <font face='Courier'>quarantine.orders</font> has <font face='Courier'>WHERE NOT EXISTS (SELECT 1 FROM quarantine.orders q WHERE q.source = c.source AND EQUAL_NULL(q.order_id, c.order_id) AND EQUAL_NULL(q.row_data:UPDATED_AT::TIMESTAMP_NTZ, c.updated_at))</font>; the same source + order + version is already there, so nothing is added. "
        "Consequence: the old quarantine row keeps its old two reasons, while the recomputed <font face='Courier'>silver.orders_checked</font> shows three. <b>Observed:</b> after the change <font face='Courier'>silver.orders_checked</font> showed three reasons for ORD-1006, quarantine still had one row, and gold stayed at 4 orders / Rs 7,785.00 / 126 points.")]
S += [P("B4. Change history and idempotency", H2),
      P("<i>Predictions were written before running (they are also in the notebook cell before the run).</i> Base: ORD-1002 = 42.50 USD x 83.20 = Rs 3,536.00, FLOOR(3536/100) = 35 base points, dated 2026-09-01.")]
S.append(tbl([["Quantity", "Your prediction", "Actual after run"],
    ["Rows for CUST-02 in dim.customers_scd2", "2 (Silver 2024-01-15..2026-08-14, Gold 2026-08-15..9999-12-31); was 1", "2 (as predicted)"],
    ["Tier used for ORD-1002", "Gold (2026-09-01 is inside the new Gold period); was Silver", "Gold (as predicted)"],
    ["Loyalty points for ORD-1002", "35 x 2 = 70 (was 35 x 1 = 35)", "70 (as predicted)"],
    ["Total loyalty points in gold", "126 - 35 + 70 = 161", "161 (as predicted)"],
    ["Gold rows whose published_at changed", "1 (only ORD-1002; all other row_hash values are unchanged)", "1 (as predicted)"]], [5.2, 8.4, 4.2]))
S += [P("<b>Why re-running is safe.</b> Every gold row carries <font face='Courier'>row_hash = HASH(all business columns)</font>. The <font face='Courier'>MERGE ... ON t.order_id = s.order_id</font> has <font face='Courier'>WHEN MATCHED AND t.row_hash &lt;&gt; s.row_hash THEN UPDATE</font>, so a row that did not change is not touched (its <font face='Courier'>published_at</font> stays), a changed row is updated in place, and a new order is inserted. Because the key is <font face='Courier'>order_id</font>, running twice can never create duplicates, and the same input gives the same output. "
        "Bronze still grows by 8 order rows on every run because it is an append-only copy of whatever was extracted (the extract step re-sends the same sample records each run); that is intended, because the raw history is kept. The growth is harmless because silver deduplicates (QUALIFY ROW_NUMBER) and quarantine/gold are keyed, so only bronze gets bigger.", B),
      P("B5. New quality check", H2),
      P("Sixth check in <font face='Courier'>quality_checks()</font> (should be 0): <font face='Courier'>SELECT COUNT_IF(amount_inr IS NULL AND amount IS NOT NULL) FROM gold.fct_orders</font> (an order with an amount whose rupee value is missing, usually a missing FX rate). "
        "<b>Failing on purpose:</b> mock web order ORD-9001 (USD 10.00, dated 2026-08-20, valid email/pincode). The FX table starts on 2026-09-01, so the order has no rate, <font face='Courier'>amount_inr</font> is NULL and the check prints <b>PROBLEM</b> (also &quot;orders with an amount but no FX rate&quot;). "
        "<b>Removing it:</b> deleting it from the Python list is not enough, since bronze is append-only and the gold MERGE never deletes; I also ran <font face='Courier'>DELETE FROM bronze.orders_raw WHERE raw:order_id = 'ORD-9001'</font> and the same for gold, then re-ran: all checks OK. <b>Observed:</b> with ORD-9001 both the new check and &quot;orders with an amount but no FX rate&quot; printed PROBLEM (1); after the cleanup all six checks were OK again."),
      P("<b>ELT vs ETL.</b> For FreshCart ELT is better because the raw data is loaded first and kept untouched in bronze, so a wrong rule (like the currency rule in B3 or the tier change in B4) can be fixed and recomputed from the raw copy without calling the APIs again, and the heavy cleaning runs as SQL on Snowflake's scalable compute instead of a separate server. Loading raw also keeps an audit trail and makes re-runs cheap. "
        "<b>ETL would still win</b> when sensitive data (e.g. card numbers or personal identifiers) must be masked or removed <i>before</i> it may land in the warehouse, for compliance; ELT would store the raw sensitive values first.")]

# ------------------------------------------------------------------ PART C
S += [P("Part C. ML pipeline with Mage", H1), P("C1. Block graph and run", H2),
      Image("block_graph.png", width=15.5 * cm, height=15.5 * cm * 3.2 / 9.5 * 0.97),
      P("Baseline blocks: load_iris (data_loader) &rarr; prepare_data (transformer) &rarr; train_model (transformer) &rarr; save_results (data_exporter), each with a <font face='Courier'>@test</font>; C3 adds evaluate_model, C4 adds validate_iris. "
        "Output of <font face='Courier'>mage run iris_project iris_classifier --test</font> (every block reports <i>1/1 tests passed</i>) is in the appendix."),
      P("C2. Tests as a gate (max_depth runs, iris_predictions.csv deleted before each run)", H2)]
S.append(tbl([["max_depth", "Test accuracy", "test_accuracy passed?", "iris_predictions.csv created?"],
              ["1", "0.6667", "No (below the 0.90 threshold)", "No"], ["2", "0.9333", "Yes", "Yes"], ["3", "0.9667", "Yes", "Yes"],
              ["4", "0.9333", "Yes", "Yes"], ["5", "0.9333", "Yes", "Yes"]], [2.4, 3.4, 6.2, 5.8]))
S += [P("<b>How a failing @test stops save_results.</b> Mage runs a block's <font face='Courier'>@test</font> functions right after the block. If an assertion fails, Mage raises an exception (<i>Failed to pass tests for block train_model</i>) and the run ends; downstream blocks are never started, so <font face='Courier'>save_results</font> does not execute and no CSV is written (max_depth=1). "
        "This is better than saving first and checking afterwards because a bad result is never saved: no one can pick up a poor file by mistake, there is nothing to delete or roll back, and the failure shows up at the exact block that caused it.")]
S += [P("C3. Evaluation branch", H2),
      P("<font face='Courier'>train_model</font> now has two downstream blocks. Edited <font face='Courier'>metadata.yaml</font> (train_model entry and the added block):"),
      code("- uuid: train_model\n  ...\n  downstream_blocks:\n  - save_results\n  - evaluate_model\n...\n- uuid: evaluate_model\n  name: evaluate_model\n  type: transformer\n  language: python\n  upstream_blocks:\n  - train_model\n  downstream_blocks: []"),
      P("Result for max_depth=3 (30 test rows): confusion matrix (rows = true, columns = predicted) setosa 10/0/0, versicolor 0/9/1, virginica 0/0/10. Metrics: setosa P=1.000 R=1.000 F1=1.000; versicolor P=1.000 R=0.900 F1=0.947; virginica P=0.909 R=1.000 F1=0.952; accuracy 0.967. Mage UI screenshot of the branch: appendix."),
      P("C4. Own block", H2),
      P("<font face='Courier'>validate_iris</font> (transformer, between load_iris and prepare_data). Its <font face='Courier'>@test</font> asserts there are no missing values and exactly 3 classes, so bad input data stops the pipeline before training. Committed to the repository; pytest/CI still pass.")]

# ------------------------------------------------------------------ PART D
S += [P("Part D. Food-order stream with RabbitMQ", H1), P("D1. Routing on paper (predictions made before running)", H2)]
S.append(tbl([["#", "Routing key", "Receiving queues"],
    ["1", "bangalore.koramangala.food", "Ravi (koramangala.*), Meena (*.food), Control (bangalore.#)"],
    ["2", "bangalore.indiranagar.ride", "Priya (indiranagar.*), Arjun (*.ride), Control"],
    ["3", "bangalore.whitefield.ride", "Arjun (*.ride), Control"],
    ["4", "chennai.tnagar.food", "Karthik (exact match) only"],
    ["5", "chennai.whitefield.ride", "dropped (no pattern matches; Control is bangalore only)"],
    ["6", "bangalore.koramangala", "Control only"]], [0.8, 5.6, 11.4]))
S += [P("<b>Question 6.</b> The key has only two words. <font face='Courier'>*</font> matches <i>exactly one</i> word, so <font face='Courier'>bangalore.koramangala.*</font> (Ravi), <font face='Courier'>bangalore.indiranagar.*</font>, <font face='Courier'>bangalore.*.ride</font> and <font face='Courier'>bangalore.*.food</font> all need three words and cannot match. "
        "<font face='Courier'>#</font> matches <i>zero or more</i> words, so <font face='Courier'>bangalore.#</font> matches <font face='Courier'>bangalore.koramangala</font> (one word after bangalore), and would even match plain <font face='Courier'>bangalore</font>. Karthik's pattern is an exact three-word key. So only Control receives it.", B),
      P("D2. Build it", H2),
      P("<font face='Courier'>stream/dispatcher.py</font> publishes every 2 s a JSON message <font face='Courier'>{id, city, zone, type, ts}</font> to the topic exchange <font face='Courier'>rapido-dispatch</font> with routing key <font face='Courier'>city.zone.type</font>; <font face='Courier'>stream/driver.py NAME PATTERN</font> declares a private (exclusive) queue, binds it with PATTERN, prints each request and ACKs. "
        "Run with six drivers (Ravi, Priya, Arjun, Meena, Karthik, Control) against a local RabbitMQ 3 (Docker). To prove D1, the dispatcher published exactly the six keys of the table; the console output below shows each key reached exactly the predicted queues (key 5 reached nobody):"),
      Preformatted("\n".join(
          [l[:118] for l in rd("stream/d1_dispatcher.log").splitlines()[:6]]), CODE)]
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
S += [P("Then the dispatcher ran for 2 minutes (60 messages) with all six drivers; ACK/NACK counts per driver: " +
        "; ".join(f"{os.path.basename(f)[7:-4]} {open(f).read().count('-> ACK')} ACK / {open(f).read().count('REJECTED')} NACK" for f in sorted(glob.glob("evidence/stream/driver_*.log"))) + ". (Excerpt of console output in the appendix.)")]
S += [P("D3. ACK and NACK", H2),
      P("<font face='Courier'>driver.py</font> now calls <font face='Courier'>basic_nack(delivery_tag, requeue=False)</font> when the message has no <font face='Courier'>zone</font> field (or is not valid JSON) and <font face='Courier'>basic_ack</font> otherwise; the dispatcher (<font face='Courier'>--bad-every 10</font>) makes every 10th message bad. "
        "In the 2-minute run the drivers printed <i>REJECTED (no zone) -&gt; NACK, requeue=False</i> for messages #10, #20, ... #60 (the matching drivers only) and <i>-&gt; ACK</i> for all others: the bad ones are discarded, the good ones processed (appendix)."),
      P("<b>Driver crashes before sending the ACK?</b> The broker keeps a delivered message as &quot;unacknowledged&quot; until it gets an ACK. When the driver's connection dies, the broker puts the message back into the queue (marked redelivered) and delivers it again to a consumer of that queue, so it is not lost (at-least-once delivery; the driver may therefore see it twice and processing should tolerate duplicates). "
        "Caveat for my setup: my driver queues are <i>exclusive</i> and auto-delete, so they vanish with the connection; with a durable named queue the message would be redelivered, with my private queue it disappears with the queue."),
      P("<b>requeue=True for an always-bad message?</b> The broker returns it to the head of the queue, the driver receives it again, rejects it again, and so on: an endless poison-message loop that wastes CPU/network and, with prefetch 1, blocks the good messages behind it. That is why bad messages are NACKed with <font face='Courier'>requeue=False</font> (or routed to a dead-letter exchange for inspection).")]

# ------------------------------------------------------------------ BONUS
S += [P("Bonus. Stream into the lakehouse (+10)", H1),
      P("<font face='Courier'>stream/order_publisher.py</font> publishes five FreshCart-style order messages to the durable queue <font face='Courier'>freshcart.orders</font>; <font face='Courier'>stream/lakehouse_consumer.py</font> (also embedded in the notebook's Bonus section) collects messages for one minute, ACKs them after the batch is in memory, "
        "and the notebook then calls <font face='Courier'>write_landing(\"web\", orders, run_id)</font> &rarr; <font face='Courier'>load_file(...)</font> &rarr; the same transform SQL, so the orders reach <font face='Courier'>gold.fct_orders</font>. The batch is idempotent: running it twice re-delivers the same order_ids, bronze grows, silver deduplicates, the gold MERGE only touches rows whose row_hash changed; the gold totals stay the same "
        "<b>Observed:</b> batch 1 and batch 2 both ended with 9 orders, Rs 14,534.00, 324 loyalty points (4 + 5 orders; the five streamed orders were collected in 60 s each time). Screenshots of both runs: appendix.")]

# ------------------------------------------------------------------ PART E
S += [P("Part E. How the four pieces fit together", H1), Image("integration.png", width=16.2 * cm, height=16.2 * cm * 6.6 / 10 * 0.97),
      P("Code lives in Git; every push triggers CI, which runs pytest on the Mage block code. The ELT pipeline turns raw API data into bronze &rarr; silver &rarr; gold in Snowflake, the ML pipeline trains on data and refuses to save a bad model, and the stream feeds events (orders) into the same bronze layer through the landing files."),
      P("Reflection: one thing that broke", H2),
      P("<b>What broke:</b> my first RabbitMQ run failed with <font face='Courier'>pika.exceptions.AMQPConnectionError</font> in every script, although the Docker container looked started. "
        "<b>Finding the cause:</b> <font face='Courier'>docker logs rabbit</font> showed the broker had crashed at start-up (<i>Error when reading /var/lib/rabbitmq/.erlang.cookie: eacces</i>), so nothing listened on port 5672; a quick connection test in Python confirmed it. "
        "<b>Fix:</b> start the container with <font face='Courier'>--user root -e RABBITMQ_ERLANG_COOKIE=...</font>; after that the same scripts connected. A second problem: the first demo logs mixed two runs because background drivers ignored Ctrl-C (SIGINT); stopping them with SIGTERM gave clean logs. "
        "A third: <font face='Courier'>mage-ai</font> would not install on the newest Python, so I used Python 3.12, the same version as the CI workflow. Lesson: read the logs of the component that is silently down before debugging my own code.")]

# ------------------------------------------------------------------ APPENDIX
S += [PageBreak(), P("Appendix (evidence; excluded from the 8-page limit)", H1),
      P("<b>Screenshots to insert before submitting</b> (cannot be produced by the code itself): (1) GitHub Actions green run; (2) red run from test_size = 0.3 and the fixing commit; (3) Snowflake outputs (they are also saved inside elt/freshcart_elt.ipynb) for B1, B3, B4, B5 and the Bonus runs; (4) Mage UI graph with the branch (via the Cloudflare tunnel).", B),
      P("A3. pytest, local red then green", H2), code(rd("a3_red_pytest.txt")[-700:] + "\n\n" + rd("a3_green_pytest.txt")),
      P("C1. mage run iris_project iris_classifier --test", H2), code(rd("c1_mage_run_test.txt")),
      P("C2. max_depth runs (raw output)", H2), code(rd("c2_depth_runs.txt")),
      P("D3. Console excerpt, 2-minute run (Control and Meena)", H2),
      code("\n".join(rd("stream/driver_Control.log").splitlines()[:16] + ["..."] + [l for l in rd("stream/driver_Control.log").splitlines() if "REJECTED" in l])),
      code("\n".join(rd("stream/driver_Meena.log").splitlines()[:8])),
      P("D2. Dispatcher excerpt", H2), code("\n".join(l[:150] for l in rd("stream/d2_dispatcher.log").splitlines()[:12]))]

if __name__ == "__main__":
  doc = SimpleDocTemplate("Report.pdf", pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.4 * cm, bottomMargin=1.6 * cm,
                        title="From Git to Gold - Report")
  doc.build(S, onFirstPage=footer, onLaterPages=footer)
  print("built")
