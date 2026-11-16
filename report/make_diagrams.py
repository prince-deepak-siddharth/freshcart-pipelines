"""Generates the two diagrams used in the report (block graph C1/C3/C4, integration diagram E2)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def box(ax, x, y, w, h, text, fc="#dbe9f6", ec="#1f4e79", fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

def arrow(ax, x1, y1, x2, y2, color="#333", style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle=style, color=color, lw=1.2))

# ---------------- block graph ----------------
fig, ax = plt.subplots(figsize=(9.5, 3.2)); ax.set_xlim(0, 19); ax.set_ylim(0, 6.4); ax.axis("off")
W, H = 3.3, 1.5
blocks = [(0.2, 2.5, "load_iris\n(data_loader)\n@test: 150 rows,\n'target' present", "#d5e8d4"),
          (4.0, 2.5, "validate_iris\n(transformer) [C4]\n@test: no NaN,\n exactly 3 classes", "#ffe6cc"),
          (7.8, 2.5, "prepare_data\n(transformer)\n@test: 120 train /\n30 test", "#dbe9f6"),
          (11.6, 2.5, "train_model\n(transformer)\n@test: accuracy\n>= 0.90  (GATE)", "#dbe9f6")]
for x, y, t, c in blocks: box(ax, x, y, W, H + 0.4, t, fc=c)
box(ax, 15.5, 4.3, 3.3, H + 0.2, "save_results\n(data_exporter)\n@test: CSV exists", fc="#f8cecc")
box(ax, 15.5, 0.4, 3.3, H + 0.2, "evaluate_model [C3]\n(transformer)\n@test: 3 classes + acc.", fc="#e1d5e7")
for i in range(3): arrow(ax, blocks[i][0] + W, 3.45, blocks[i + 1][0], 3.45)
arrow(ax, 11.6 + W, 3.8, 15.5, 5.0); arrow(ax, 11.6 + W, 3.1, 15.5, 1.3)
ax.text(9.5, 6.1, "iris_classifier pipeline (metadata.yaml)", ha="center", fontsize=10, weight="bold")
plt.savefig("block_graph.png", dpi=170, bbox_inches="tight"); plt.close()

# ---------------- integration diagram ----------------
fig, ax = plt.subplots(figsize=(11, 8.2)); ax.set_xlim(-0.3, 22); ax.set_ylim(-1.9, 13.6); ax.axis("off")
DONE = dict(fc="#c6e7c6", ec="#2e7d32")
def lane(y, title): ax.text(0.0, y, title, fontsize=10, weight="bold", color="#1f4e79")
def conn(x1, x2, y): arrow(ax, x1, y, x2, y)

# ---- lane 1: code -> CI ----
lane(12.9, "1  CODE: Git -> CI")
xs = [0.0, 3.4, 6.8, 10.2]
for x, t in zip(xs, ["Working\nfolder", "Local Git\n(.git)", "GitHub\n(remote)", "GitHub Actions\npytest (py3.12)"]):
    box(ax, x, 10.8, 2.7, 1.6, t, fc="#fff2cc", ec="#b38f00")
for x, lab in zip(xs[:3], ["add + commit", "push", "on every push"]):
    conn(x + 2.7, x + 3.4, 11.6); ax.text(x + 3.05, 12.55, lab, fontsize=6.5, ha="center")
conn(12.9, 13.7, 11.6)
box(ax, 13.7, 10.8, 3.6, 1.6, "CI result\ngreen = OK, merge\nred = fix first", **DONE)

# ---- lane 2: ELT ----
lane(9.9, "2  ELT on Snowflake (batch)")
ex = [0.0 + 2.95 * k for k in range(7)]
labels = ["Sample APIs\nweb, mobile,\nCRM, FX", "Landing files\n.json.gz\nwrite_landing()", "BRONZE\nraw VARIANT\nPUT + COPY",
          "SILVER\nclean, dedup,\nSCD2, FX", "GOLD\nfct_orders\nMERGE", "quality_checks()\n6 checks = 0"]
for x, t in zip(ex, labels): box(ax, x, 7.9, 2.5, 1.6, t, fc="#dbe9f6")
for k in range(5): conn(ex[k] + 2.5, ex[k + 1], 8.7)
conn(ex[5] + 2.5, ex[6], 8.7)
box(ax, ex[6], 7.9, 2.5, 1.6, "DONE\nGold data ready\nfor analytics", **DONE)
box(ax, ex[3], 5.85, 2.5, 1.25, "QUARANTINE\nbad rows +\nreasons", fc="#f8cecc"); arrow(ax, ex[3] + 1.25, 7.9, ex[3] + 1.25, 7.1)

# ---- lane 3: ML ----
lane(5.1, "3  ML pipeline (Mage)")
mx = [0.0, 3.0, 6.0, 9.0]
for x, t in zip(mx, ["load_iris", "validate_iris", "prepare_data", "train_model\n@test gate"]):
    box(ax, x, 3.1, 2.5, 1.5, t, fc="#e1d5e7", ec="#6c4a82")
for x in mx[:3]: conn(x + 2.5, x + 3.0, 3.85)
box(ax, 12.3, 3.9, 2.6, 1.1, "save_results\n(CSV)", fc="#e1d5e7", ec="#6c4a82")
box(ax, 12.3, 2.4, 2.6, 1.1, "evaluate_model\n(metrics)", fc="#e1d5e7", ec="#6c4a82")
arrow(ax, 11.5, 3.95, 12.3, 4.45); arrow(ax, 11.5, 3.75, 12.3, 2.95)
box(ax, 16.1, 3.0, 3.4, 1.7, "DONE\niris_predictions.csv\n+ confusion matrix", **DONE)
arrow(ax, 14.9, 4.45, 16.1, 4.0); arrow(ax, 14.9, 2.95, 16.1, 3.6)

# ---- lane 4: stream ----
lane(1.45, "4  Stream (RabbitMQ)")
box(ax, 0.0, -0.6, 2.9, 1.5, "dispatcher.py\ncity.zone.type", fc="#ffe6cc", ec="#b35c00")
box(ax, 3.8, -0.6, 3.1, 1.5, "topic exchange\nrapido-dispatch", fc="#ffe6cc", ec="#b35c00")
box(ax, 7.8, -0.6, 3.3, 1.5, "driver queues\n(binding patterns)\nACK / NACK", fc="#ffe6cc", ec="#b35c00")
conn(2.9, 3.8, 0.15); conn(6.9, 7.8, 0.15)
box(ax, 12.0, -0.6, 3.4, 1.5, "DONE\ngood = ACK\nbad = NACK (dropped)", **DONE); conn(11.1, 12.0, 0.15)
box(ax, 16.6, -0.6, 3.6, 1.5, "bonus consumer\n1-min batch of orders", fc="#ffe6cc", ec="#b35c00")
# exchange -> consumer: routed underneath the stream lane so it crosses no box
ax.plot([5.35, 5.35], [-0.6, -1.2], color="#b35c00", lw=1.2)
ax.plot([5.35, 18.4], [-1.2, -1.2], color="#b35c00", lw=1.2)
arrow(ax, 18.4, -1.2, 18.4, -0.6, color="#b35c00")
ax.text(11.9, -1.62, "same exchange: order messages for the bonus consumer", fontsize=6.5, ha="center", color="#b35c00")
# consumer -> bronze: up the right-hand side, then left under the quarantine box
ax.plot([19.9, 19.9], [0.9, 5.45], color="#b35c00", lw=1.2)
ax.plot([19.9, ex[2] + 1.25], [5.45, 5.45], color="#b35c00", lw=1.2)
ax.plot([ex[2] + 1.25, ex[2] + 1.25], [5.45, 7.2], color="#b35c00", lw=1.2)
arrow(ax, ex[2] + 1.25, 7.2, ex[2] + 1.25, 7.9, color="#b35c00")
ax.text(12.0, 5.6, "write_landing() + load_file() -> same bronze -> gold", fontsize=7, color="#b35c00", ha="center")
plt.savefig("integration.png", dpi=170, bbox_inches="tight", pad_inches=0.25); plt.close()
print("ok")
