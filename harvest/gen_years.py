# Explicit era list. Output uses run.py's convention: positive = BC, negative = AD.
ys = []
# BC: 3000 -> 1, coarse (pages mostly redirect to centuries)
ys += list(range(3000, 0, -25))            # positive = BC
# AD 1 -> 999
ys += [-y for y in range(5, 1000, 5)]
# AD 1000 -> 1499
ys += [-y for y in range(1000, 1500, 4)]
# AD 1500 -> 1799
ys += [-y for y in range(1500, 1800, 3)]
# AD 1800 -> 1949
ys += [-y for y in range(1800, 1950, 2)]
# AD 1950 -> 2025
ys += [-y for y in range(1950, 2026)]
ys = sorted(set(ys), reverse=True)
open('/home/user/harvest/yearlist.txt','w').write(" ".join(str(y) for y in ys))
def era(y):
    if y > 0: return "3000-1 BC"
    y = -y
    if y < 1000: return "AD 1-999"
    if y < 1500: return "AD 1000-1499"
    if y < 1800: return "AD 1500-1799"
    if y < 1950: return "AD 1800-1949"
    return "AD 1950-2025"
import collections
c = collections.Counter(era(y) for y in ys)
print("total years:", len(ys))
for k in ["3000-1 BC","AD 1-999","AD 1000-1499","AD 1500-1799","AD 1800-1949","AD 1950-2025"]:
    print(f"  {k:16} {c[k]}")
