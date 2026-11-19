r"""One-off diagnostic (read-only, CPU): find the first character where the
summary's quoted Extender exception_message stops matching the archived FIX4 .out.
"""
import difflib

S = r"C:\AI\community\notes\ali147_summary.md"
J = r"C:\AI\community\p7\jobs\ali147_pool_fix4_s51080000.out.failed-20261022"

st = open(S, encoding="utf-8").read()
jt = open(J, encoding="utf-8", errors="replace").read()

i = st.find('"exception_message"')
frag = st[i:st.find('"exception_type"', i)]
print("summary fragment len=%d" % len(frag))
print("FRAG: %r" % frag)
j = jt.find('"exception_message"')
real = jt[j:jt.find('"exception_type"', j)]
print("REAL len=%d" % len(real))
print("REAL: %r" % real)
sm = difflib.SequenceMatcher(None, frag, real)
for tag, a1, a2, b1, b2 in sm.get_opcodes():
    if tag != "equal":
        print("DIFF %s frag[%d:%d]=%r real[%d:%d]=%r"
              % (tag, a1, a2, frag[a1:a2], b1, b2, real[b1:b2]))
print("frag in real:", frag in real, "real in frag:", real in frag)
