"""Rebuild + apply every authoring file. usage: python3 apply_all.py [name ...]  (default: all)"""
import subprocess, sys, pathlib, importlib.util
H = pathlib.Path(__file__).parent
names = sys.argv[1:] or sorted(p.stem for p in (H / "authoring").glob("*.py") if not p.stem.startswith("id_part"))
names.sort(key=lambda n: (n == "other_animals", n))          # other_animals after nutrition
for n in names:
    spec = importlib.util.spec_from_file_location(n, H / "authoring" / f"{n}.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    b = subprocess.run(["python3", str(H / "build_bank.py"), str(H / "authoring" / f"{n}.py")], capture_output=True, text=True)
    first = (b.stdout.splitlines() or [b.stderr.strip()[-200:]])[0]
    flags = ["--exclusive"] if n != "other_animals" else ["--sub=Physical Health|Nutrition & Husbandry"]
    if getattr(m, "STATIC", False): flags.append("--static")
    a = subprocess.run(["node", str(H / "apply_bank.js"), m.PAGE, str(H / "banks" / f"{n}.json")] + flags, capture_output=True, text=True)
    print(n, "|", first.split("|")[0].split(":")[-1].strip() if b.returncode == 0 else "BUILD FAIL", "|", (a.stdout.strip().splitlines() or [a.stderr[-200:]])[-1][:110])
