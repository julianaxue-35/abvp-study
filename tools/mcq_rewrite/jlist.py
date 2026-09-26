"""usage: python3 jlist.py <page-substring> [start] [n] [abstract_chars]  -> pending (not yet rewritten) articles for a page"""
import sys
from jr_lib import *
cat = load_cat(); jr = load_jr()
pg = sys.argv[1]; st = int(sys.argv[2]) if len(sys.argv) > 2 else 0; n = int(sys.argv[3]) if len(sys.argv) > 3 else 25; ac = int(sys.argv[4]) if len(sys.argv) > 4 else 1500
rows = [(i, r) for i, r in enumerate(cat) if pg in r["subdomain_page"] and r.get("mcq_v") != 2 and i not in jr]
print(f"# {pg}: {len(rows)} pending")
for i, r in rows[st:st + n]:
    print(f"\n#{i} [{r['year']}] {r['title']}\n{r['abstract'][:ac]}")
