import importlib.util, pathlib
def load_hfix(H=pathlib.Path(__file__).parent, only=None):
    """merge hubfix/*.py in sorted order; a later entry may use None to keep the earlier w1/w2, and omits the 3rd element to keep an earlier trimmed correct option"""
    d = {}
    for p in sorted((H/"hubfix").glob("*.py")):
        if only and not only(p.stem): continue
        s = importlib.util.spec_from_file_location("hf"+p.stem, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        for k, v in m.HFIX.items():
            o = d.get(k)
            if o:
                w1 = v[0] if v[0] is not None else o[0]; w2 = v[1] if v[1] is not None else o[1]
                v = (w1, w2, v[2]) if len(v) > 2 else ((w1, w2, o[2]) if len(o) > 2 else (w1, w2))
            d[k] = v
    return d
