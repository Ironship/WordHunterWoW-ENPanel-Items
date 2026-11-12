#!/usr/bin/env python3
"""Build the English item names for World of Warcraft: Forever.

Forever used the Classic set (Data/Classic): the names of Classic Era and Season
of Discovery, from Blizzard's Game Data API. Forever has items of its own, about
two thousand of them with ids from 230000 up, and renames some old ones (Gypsy
Sandals are Nomad Sandals there), and the API knows neither.

Forever ships thousands of items without a name in the client's files and sends the
name when it is ready. Efficient Games' EG Link output (CC BY 4.0, see README) keeps
what the server sent, in item_hotfixes.enUS.json, one file per client build. This
reads them and lays them over the Classic set, newest build last:

  * an item the server sent a name for is named from that;
  * an item it said is removed, or refused to describe yet, is left as it was;
  * a name that says the item is a placeholder (Deprecated ..., OLD ..., a test
    item) is left out.

Descriptions are not touched: what an item's row calls its description is the
flavour text, and Data/Classic holds the effect lines the tooltip shows.

    python Tools/build_forever_items.py --fetch

writes Data/Forever/NamesItem_000.lua. Nothing is fetched twice; the downloads land
in Data/cache/, which is not packaged.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / "Data" / "cache" / "eg"

# Efficient Games' repository at the revision the names were read from.
EG_REPO = "JIVESCORP/eg-link-output-wowf"
EG_REV = "164bd1e2d89579ada4ee5e2de7e5fd4db684a9f1"
EG_RAW = "https://raw.githubusercontent.com/%s/%s/" % (EG_REPO, EG_REV)

HEADER = "WordHunterWoW_ENNames_Item = WordHunterWoW_ENNames_Item or {}"
ROW = re.compile(r'^WordHunterWoW_ENNames_Item\[(\d+)\] = "((?:\\.|[^"\\])*)"\s*$')
PLACEHOLDER = re.compile(r"^(?:Deprecated|OLD|zz)\b|\bTest\b|\[PH\]|^<UNUSED", re.I)


def quote(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_number(build):
    return int(str(build).split(".")[-1])


def eg_files(directory):
    """item_hotfixes.enUS.json of every build, oldest first, the live game after the beta."""
    found = []
    for path in pathlib.Path(directory).glob("*/*/item_hotfixes.enUS.json"):
        found.append((build_number(path.parent.name), path.parent.parent.name == "wowf", path))
    return [path for _, _, path in sorted(found)]


def fetch(directory):
    print("reading", EG_RAW + "data/index.json")
    request = urllib.request.Request(EG_RAW + "data/index.json", headers={"User-Agent": "WordHunterWoW-ENPanel-Items/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        products = json.load(response)["products"]
    for product in ("wow_classic_beta", "wowf"):
        for build, datasets in products.get(product, {}).items():
            if "item_hotfixes.enUS" not in datasets:
                continue
            destination = pathlib.Path(directory) / product / build / "item_hotfixes.enUS.json"
            if destination.exists():
                continue
            url = EG_RAW + "data/%s/%s/item_hotfixes.enUS.json" % (product, build)
            print("downloading", url)
            destination.parent.mkdir(parents=True, exist_ok=True)
            request = urllib.request.Request(url, headers={"User-Agent": "WordHunterWoW-ENPanel-Items/1"})
            with urllib.request.urlopen(request, timeout=60) as response:
                destination.write_bytes(response.read())


def read_classic(path):
    names = {}
    for line in pathlib.Path(path).read_bytes().decode("utf-8").splitlines():
        match = ROW.match(line)
        if match:
            names[int(match.group(1))] = match.group(2)  # kept as written, escapes and all
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--classic", default=str(ROOT / "Data" / "Classic" / "NamesItem_000.lua"))
    parser.add_argument("--eg", default=str(CACHE), help="folder of Efficient Games' <product>/<build>/item_hotfixes.enUS.json")
    parser.add_argument("--fetch", action="store_true", help="download the files that are not there yet")
    parser.add_argument("--out", default=str(ROOT / "Data" / "Forever" / "NamesItem_000.lua"))
    args = parser.parse_args()

    if args.fetch:
        fetch(args.eg)
    files = eg_files(args.eg)
    if not files:
        sys.exit("%s holds no item_hotfixes.enUS.json; download them with --fetch" % args.eg)

    names = read_classic(args.classic)
    classic = len(names)
    sent = {}
    for path in files:  # a later build replaces an earlier one
        for key, record in json.loads(path.read_text(encoding="utf-8"))["items"].items():
            name = (record.get("name") or "").strip()
            if record.get("status") == "valid" and name:
                sent[int(key)] = name
    added = changed = skipped = 0
    for item_id, name in sent.items():
        if PLACEHOLDER.search(name):
            skipped += 1
            continue
        written = quote(name)[1:-1]
        if item_id not in names:
            added += 1
        elif names[item_id] != written:
            changed += 1
        names[item_id] = written
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [HEADER] + ['WordHunterWoW_ENNames_Item[%d] = "%s"' % (item_id, names[item_id]) for item_id in sorted(names)]
    # Bytes, not text: a text write on Windows turns every newline into CRLF.
    out.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    print("%d names: the %d of Classic, %d the server sent for items Classic lacks, %d renamed, %d placeholders left out"
          % (len(names), classic, added, changed, skipped))
    print("wrote", out)


if __name__ == "__main__":
    main()
