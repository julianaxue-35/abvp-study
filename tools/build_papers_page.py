#!/usr/bin/env python3
"""Build supplementary/jsmcah_diplomate_papers.html: every JSMCAH + Diplomate-sheet paper (2021-2025)
as one reading list with abstracts. Same selection rule as build_mock_journal.in_focus_set()."""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_mock_journal as b

cat = json.load(open(os.path.join(HERE, "journal-catalog.json"), encoding="utf-8"))
src = open(os.path.join(ROOT, "supplementary", "additional_podcasts.html"), encoding="utf-8").read()
head_comment = src[:src.index("<html")]
nav = re.search(r"<nav .*?</nav>", src, re.S).group(0)
footer = re.search(r"<!-- ip-notice-footer -->.*?</footer>", src, re.S).group(0)

recs = [c for c in cat if b.in_focus_set(c) and (c.get("abstract") or "").strip()]
recs.sort(key=lambda c: (-(c.get("year") or 0), (c.get("title") or "").lower()))
E = lambda s: html.escape(re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip())

items = []
for c in recs:
    is_js = b.journal_tier(c) == "jsmcah"
    tags = ("js" if is_js else "dip")
    doi = c.get("doi") or ""
    link = f' &middot; <a href="https://doi.org/{E(doi)}" target="_blank" rel="noopener">DOI</a>' if doi else ""
    badge = '<span class="bd js">JSMCAH</span>' if is_js else '<span class="bd dip">Diplomate</span>'
    paras = "".join(f"<p>{E(p)}</p>" for p in re.split(r"\n\s*\n", c["abstract"]) if p.strip())
    items.append(
        f'<details class="art" data-t="{tags}" data-s="{E((c.get("title") or "") + " " + (c.get("journal") or "")).lower()}">'
        f'<summary><span class="yr">{c.get("year")}</span><span class="tt">{E(c.get("title"))}</span>{badge}</summary>'
        f'<div class="ab"><div class="meta">{E(c.get("journal"))} &middot; {c.get("year")}{link}</div>{paras}</div></details>')

n_js = sum(1 for c in recs if b.journal_tier(c) == "jsmcah"); n_dip = len(recs) - n_js
page = f'''<!DOCTYPE html>
{head_comment}<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JSMCAH and Diplomate Papers | ABVP Shelter Medicine RVS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{--ink:#0f3d3a;--paper:#f4efe4;--paper2:#fbf8f1;--line:#d9d0bd;--muted:#5d6b62;--shadow:0 1px 2px rgba(15,61,58,.08),0 8px 24px rgba(15,61,58,.06)}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);font-family:"Public Sans",system-ui,sans-serif;line-height:1.55}}
  .wrap{{max-width:880px;margin:0 auto;padding:0 16px}}
  header.top{{background:var(--ink);color:var(--paper2);padding:24px 0 20px;border-bottom:4px solid #5b584f}}
  .eyebrow{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#9ec9c2;margin:0 0 6px}}
  header.top h1{{font-family:"Fraunces",serif;font-weight:600;font-size:clamp(24px,4.5vw,38px);margin:0;line-height:1.1}}
  header.top .sub{{color:#cfe3dd;margin:10px 0 0;max-width:680px;font-size:15px}}
  main{{padding:20px 0 50px}}
  .tools{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 14px}}
  .tools input{{flex:1 1 220px;font:inherit;font-size:16px;padding:9px 11px;border:1.5px solid var(--line);border-radius:8px;background:#fff}}
  .chip{{font:inherit;font-size:13px;padding:7px 12px;border-radius:999px;border:1.5px solid var(--line);background:#fff;color:var(--ink);cursor:pointer}}
  .chip.on{{background:var(--ink);color:#fff;border-color:var(--ink)}}
  .count{{font-size:13px;color:var(--muted);margin:0 0 10px}}
  .art{{background:var(--paper2);border:1px solid var(--line);border-radius:10px;margin:0 0 8px;box-shadow:var(--shadow)}}
  .art summary{{cursor:pointer;padding:11px 14px;display:flex;gap:10px;align-items:baseline;list-style:none}}
  .art summary::-webkit-details-marker{{display:none}}
  .art summary::before{{content:"\\25B8";color:var(--muted)}} .art[open] summary::before{{content:"\\25BE"}}
  .yr{{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;flex:0 0 auto}}
  .tt{{font-weight:600;font-size:15px;flex:1 1 auto}}
  .bd{{font-size:10.5px;font-weight:700;border-radius:999px;padding:2px 8px;flex:0 0 auto;letter-spacing:.03em}}
  .bd.js{{background:#dcebe2;color:#1f7a4d}} .bd.dip{{background:#e2e4f2;color:#3c4a86}}
  .ab{{padding:0 14px 12px 40px;font-size:14.5px}} .ab p{{margin:0 0 9px}}
  .meta{{font-size:12.5px;color:var(--muted);margin:0 0 8px}} .meta a{{color:var(--ink)}}
  .hidden{{display:none!important}}
  @media(max-width:640px){{.wrap{{padding:0 12px}}.ab{{padding-left:14px}}.art summary{{flex-wrap:wrap}}}}
</style>
</head>
<body>
{nav}
<header class="top"><div class="wrap">
  <p class="eyebrow">ABVP Shelter Medicine Practice RVS &middot; Supplementary Material</p>
  <h1>JSMCAH and Diplomate Papers</h1>
  <p class="sub">Every <i>Journal of Shelter Medicine and Community Animal Health</i> paper and every paper on the Diplomate publications list, 2021&ndash;2025, in one place with its abstract. These are the papers in the mock exam&rsquo;s &ldquo;JSMCAH + Diplomate studies&rdquo; set.</p>
</div></header>
<main><div class="wrap">
  <div class="tools">
    <input id="q" type="search" placeholder="Search title or journal&hellip;" aria-label="Search papers">
    <button class="chip on" data-f="all">All ({len(recs)})</button>
    <button class="chip" data-f="js">JSMCAH ({n_js})</button>
    <button class="chip" data-f="dip">Diplomate ({n_dip})</button>
  </div>
  <p class="count" id="cnt"></p>
  {"".join(items)}
</div></main>
<script>
(function(){{
  var f='all',q=document.getElementById('q'),arts=[].slice.call(document.querySelectorAll('.art')),cnt=document.getElementById('cnt');
  function run(){{var s=q.value.trim().toLowerCase(),n=0;arts.forEach(function(a){{var ok=(f==='all'||a.dataset.t===f)&&(!s||a.dataset.s.indexOf(s)>-1);a.classList.toggle('hidden',!ok);if(ok)n++;}});cnt.textContent=n+' paper'+(n===1?'':'s')+' shown';}}
  q.addEventListener('input',run);
  [].forEach.call(document.querySelectorAll('.chip'),function(b){{b.onclick=function(){{f=b.dataset.f;[].forEach.call(document.querySelectorAll('.chip'),function(x){{x.classList.toggle('on',x===b);}});run();}};}});
  run();
}})();
</script>
{footer}
</body>
</html>
'''
out = os.path.join(ROOT, "supplementary", "jsmcah_diplomate_papers.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote", out, len(recs), "papers (JSMCAH", n_js, "| Diplomate-only", n_dip, ")")
