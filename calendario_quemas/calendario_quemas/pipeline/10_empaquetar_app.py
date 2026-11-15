"""Convierte los binarios de la app (gzip) a texto base64 para publicarlos como archivos estáticos.
Uso: python3 10_empaquetar_app.py out/app_data app/data"""
import sys, os, glob, base64, shutil
src, dst = sys.argv[1:3]
os.makedirs(os.path.join(dst, "pts"), exist_ok=True)
def b64(f, out):
    b = open(f, "rb").read(); assert b[:2] == b"\x1f\x8b", f
    open(out, "w").write(base64.b64encode(b).decode("ascii"))
b64(os.path.join(src, "frag.bin.gz"), os.path.join(dst, "frag.txt"))
for f in sorted(glob.glob(os.path.join(src, "pts", "*.bin.gz"))):
    b64(f, os.path.join(dst, "pts", os.path.basename(f).replace(".bin.gz", ".txt")))
for f in ("meta.json", "validacion.json"): shutil.copy(os.path.join(src, f), os.path.join(dst, f))
