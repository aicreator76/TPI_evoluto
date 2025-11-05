import sys
import codecs

ok = True
for f in sys.argv[1:]:
    try:
        with codecs.open(f, "r", "utf-8") as fh:
            fh.read()
    except Exception as e:
        ok = False
        print(f"[UTF-8 ERROR] {f}: {e}")
if not ok:
    sys.exit(1)
