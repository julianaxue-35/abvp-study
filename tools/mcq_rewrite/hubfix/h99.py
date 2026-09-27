# Auto-propagates fixes to duplicate authoring items (same original correct option + distractors as a fixed item).
import importlib.util, pathlib, sys
_H = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_H)); from hubload import load_hfix
_fx = load_hfix(_H, only=lambda s: s[0]=='h' and s[1] in '012345678')
_fx5 = load_hfix(_H, only=lambda s: s.startswith('h5') or s.startswith('h6'))
_items = {}
for _f in sorted((_H/"authoring").glob("*.py")):
    _s = importlib.util.spec_from_file_location("ap"+_f.stem, _f); _m = importlib.util.module_from_spec(_s)
    try: _s.loader.exec_module(_m)
    except Exception: continue
    for _k, _it in enumerate(_m.ITEMS, 1):
        if _it[0] != "keep": _items[(_f.stem, _k)] = _it
_by = {}; _by5 = {}
for _key, _v in _fx.items():
    if _key in _items: _by[tuple(_items[_key][2:5])] = _v
for _key, _v in _fx5.items():
    if _key in _items: _by5[tuple(_items[_key][2:5])] = _v
HFIX = {}
for _key, _it in _items.items():
    _t = tuple(_it[2:5])
    if _key not in _fx and _t in _by: HFIX[_key] = _by[_t]
    if _t in _by5 and _key not in _fx5:                       # propagate later (absolute-word) rewrites to duplicates
        _v = _by5[_t]
        if _key not in _fx and _key not in HFIX:              # no earlier fix: fill Nones from the original
            _v = (_v[0] if _v[0] is not None else _it[3], _v[1] if _v[1] is not None else _it[4]) + tuple(_v[2:])
        HFIX[_key] = _v
