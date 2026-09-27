# Auto-propagates fixes to duplicate authoring items (same correct option + distractors as a fixed item).
import importlib.util, pathlib
_H = pathlib.Path(__file__).parent.parent
_fx = {}
for _p in sorted((_H/"hubfix").glob("h[0-8]*.py")):
    _s = importlib.util.spec_from_file_location("hp"+_p.stem, _p); _m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m); _fx.update(_m.HFIX)
_items = {}
for _f in sorted((_H/"authoring").glob("*.py")):
    _s = importlib.util.spec_from_file_location("ap"+_f.stem, _f); _m = importlib.util.module_from_spec(_s)
    try: _s.loader.exec_module(_m)
    except Exception: continue
    for _k, _it in enumerate(_m.ITEMS, 1):
        if _it[0] != "keep": _items[(_f.stem, _k)] = _it
_by = {}
for _key, _v in _fx.items():
    if _key in _items: _by[tuple(_items[_key][2:5])] = _v
HFIX = {}
for _key, _it in _items.items():
    if _key not in _fx and tuple(_it[2:5]) in _by: HFIX[_key] = _by[tuple(_it[2:5])]
