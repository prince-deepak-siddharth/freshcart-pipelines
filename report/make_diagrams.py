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
fig, ax = plt.subplots(figsize=(10, 6.6)); ax.set_xlim(0, 20); ax.set_ylim(0, 13); ax.axis("off")
# Git + CI lane
ax.text(0.2, 12.4, "1  CODE: Git  ->  CI", fontsize=9.5, weight="bold", color="#1f4e79")
for x, t in [(0.2, "Working\nfolder"), (3.4, "Local Git\n(.git)"), (6.6, "GitHub\n(remote)"), (9.8, "GitHub Actions\npytest (py3.12)")]:
    box(ax, x, 10.6, 2.6, 1.4, t, fc="#fff2cc", ec="#b38f00")
for x, lab in [(2.8, "add+commit"), (6.0, "push"), (9.2, "on every push")]:
    arrow(ax, x, 11.3, x + 0.6, 11.3); ax.text(x + 0.3, 12.1, lab, fontsize=6.5, ha="center")
ax.text(12.8, 11.3, "green = OK\nred = fix it", fontsize=7.5, va="center")
ax.text(15.6, 11.3, "repo: elt/  iris_project/\nstream/  tests/  .github/", fontsize=7.5, color="#555", va="center")
# ELT lane
ax.text(0.2, 9.3, "2  ELT on Snowflake (batch)", fontsize=9.5, weight="bold", color="#1f4e79")
elt = [(0.2, "Sample APIs\nweb, mobile,\nCRM, FX"), (3.4, "Landing files\n.json.gz\nwrite_landing()"), (6.6, "BRONZE\nraw VARIANT\nPUT+COPY INTO"),
       (9.8, "SILVER\nclean, dedup,\nSCD2, FX"), (13.0, "GOLD fct_orders\nMERGE\n(idempotent)")]
for x, t in elt: box(ax, x, 7.3, 2.6, 1.5, t, fc="#dbe9f6")
for x, _ in elt[:-1]: arrow(ax, x + 2.6, 8.05, x + 3.2, 8.05)
box(ax, 9.8, 5.4, 2.6, 1.3, "QUARANTINE\nbad rows +\nreasons", fc="#f8cecc"); arrow(ax, 11.1, 7.3, 11.1, 6.7)
box(ax, 16.3, 7.3, 3.3, 1.5, "quality_checks()\n6 checks, all = 0", fc="#d5e8d4"); arrow(ax, 15.6, 8.05, 16.3, 8.05)
# ML lane
ax.text(0.2, 4.7, "3  ML pipeline (Mage)", fontsize=9.5, weight="bold", color="#1f4e79")
ml = [(0.2, "load_iris"), (2.9, "validate_iris"), (5.6, "prepare_data"), (8.3, "train_model\n@test gate")]
for x, t in ml: box(ax, x, 2.9, 2.3, 1.3, t, fc="#e1d5e7", ec="#6c4a82")
for x, _ in ml[:-1]: arrow(ax, x + 2.3, 3.55, x + 2.7, 3.55)
box(ax, 11.4, 3.7, 2.3, 1.0, "save_results\n(CSV)", fc="#e1d5e7", ec="#6c4a82")
box(ax, 11.4, 2.2, 2.6, 1.0, "evaluate_model\n(metrics)", fc="#e1d5e7", ec="#6c4a82")
arrow(ax, 10.6, 3.7, 11.4, 4.2); arrow(ax, 10.6, 3.4, 11.4, 2.7)
# stream lane
ax.text(0.2, 1.6, "4  Stream (RabbitMQ)", fontsize=9.5, weight="bold", color="#1f4e79")
box(ax, 0.2, 0.0, 2.8, 1.2, "dispatcher.py\ncity.zone.type", fc="#ffe6cc", ec="#b35c00")
box(ax, 4.2, 0.0, 3.2, 1.2, "topic exchange\nrapido-dispatch", fc="#ffe6cc", ec="#b35c00")
box(ax, 8.6, 0.0, 3.0, 1.2, "driver queues\n(binding patterns)\nACK / NACK", fc="#ffe6cc", ec="#b35c00")
arrow(ax, 3.0, 0.6, 4.2, 0.6); arrow(ax, 7.4, 0.6, 8.6, 0.6)
box(ax, 13.4, 0.0, 3.2, 1.2, "bonus consumer\n1-min batch", fc="#ffe6cc", ec="#b35c00")
arrow(ax, 11.6, 0.6, 13.4, 0.6)
ax.text(12.5, 0.85, "orders\nqueue", fontsize=6.5, ha="center", color="#555")
arrow(ax, 15.0, 1.2, 15.0, 7.3, color="#b35c00")   # consumer -> landing/bronze lane
ax.text(15.15, 4.2, "write_landing()\n+ load_file()\n-> same bronze\n-> gold", fontsize=7, color="#b35c00")
# git feeds everything
arrow(ax, 1.5, 10.6, 1.5, 8.8, color="#999"); ax.text(1.7, 9.6, "notebooks / code\nversioned", fontsize=6.5, color="#777")
plt.savefig("integration.png", dpi=170, bbox_inches="tight"); plt.close()
print("ok")
