"""Class-level split of the V4 - V0 (and V1 - V0) per-class F1 change by whether the attacked device is seen in training.

A twinned device is a target of a test capture if it carries >= 10% of its packets. A class is "unseen" if a test
target carries < 1% of the packets of that class's training captures, "seen" if all its targets appear in training,
and "none" if no twinned device reaches 10% in its test captures.

  python scripts/20_seen_unseen_split.py [results/twin_study/results_rerun/twin] [target-share]
"""
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

DEVICES = ["Blink_Camera", "Ecobee_Camera", "M1T_Camera", "Multifunctional_Pager", "Owltron_Camera", "SenseU", "Singcall"]
T_CRIT = {2: 4.303, 4: 2.776}


def class_of(fname):
    base = re.sub(r"_(train|test)\.pcap$", "", fname)
    return re.sub(r"\d+$", "", base)


def shares(path):
    pk = defaultdict(lambda: defaultdict(float))     # (class, split) -> device -> packets
    for r in csv.DictReader(open(path)):
        n = float(r["packets"])
        for d in DEVICES:
            pk[(class_of(r["file"]), r["split"])][d] += n * float(r[d] or 0)
        pk[(class_of(r["file"]), r["split"])]["_total"] += n
    return pk


def per_class(run):
    pc = json.load(open(run / "metrics.json"))["test"]["label19"]["per_class"]
    return {k: (v["f1"] if isinstance(v, dict) else v) for k, v in pc.items()}


def norm(c):
    return c.replace("TCP_IP-", "").replace("MQTT-", "MQTT-")


def main(twin_dir, target=0.10):
    twin_dir = Path(twin_dir)
    pk = shares(twin_dir / "pcap_mac_shares.csv")
    groups = {}
    for (cls, split), dev in pk.items():
        if split != "test":
            continue
        tot = dev["_total"]
        targets = [d for d in DEVICES if dev[d] / tot >= target]
        train = pk.get((cls, "train"))
        if not targets:
            groups[norm(cls)] = "none"
        elif train and all(train[d] / train["_total"] >= 0.01 for d in targets):
            groups[norm(cls)] = "seen"
        else:
            groups[norm(cls)] = "unseen"
    for a, b, seeds in (("V4", "V0", [42, 43, 44, 45, 46]), ("V1", "V0", [42, 43, 44])):
        diffs = defaultdict(list)          # group -> per-seed group mean
        per_cls = defaultdict(list)
        for s in seeds:
            fa = per_class(twin_dir / f"trace_moe_official_T16_{a}_seed{s}")
            fb = per_class(twin_dir / f"trace_moe_official_T16_{b}_seed{s}")
            g = defaultdict(list)
            for c in fa:
                key = norm(c)
                grp = "benign" if key.lower().startswith("benign") else groups.get(key, "?")
                g[grp].append(fa[c] - fb[c])
                per_cls[(grp, key)].append(fa[c] - fb[c])
            for grp, v in g.items():
                diffs[grp].append(statistics.mean(v))
        n_cls = len(per_cls)
        print(f"\n{a} - {b} ({len(seeds)} seeds), target share {target:.0%}, classes {n_cls}")
        for grp in ("unseen", "seen", "none", "benign", "?"):
            v = diffs.get(grp)
            if not v:
                continue
            m = statistics.mean(v) * 100
            h = T_CRIT[len(v) - 1] * statistics.stdev(v) / len(v) ** 0.5 * 100 if len(v) > 1 else 0
            names = sorted(k for (gg, k) in per_cls if gg == grp)
            contrib = sum(statistics.mean(per_cls[(grp, k)]) for k in names) / n_cls * 100
            print(f"  {grp:7s} n={len(names):2d}  mean {m:+.2f} pt [{m - h:+.2f}, {m + h:+.2f}]  share of macro change {contrib:+.2f} pt")
            if a == "V4":
                print("          " + ", ".join(f"{k} {statistics.mean(per_cls[(grp, k)]) * 100:+.1f}" for k in names))


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[1] / "results" / "twin_study" / "results_rerun" / "twin"
    main(sys.argv[1] if len(sys.argv) > 1 else default, float(sys.argv[2]) if len(sys.argv) > 2 else 0.10)
