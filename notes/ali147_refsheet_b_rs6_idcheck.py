r"""RS6 read-only check: why did the harness refuse the REFSHEET_B job id?

ralph.ps1 has two job-id gates:
  line 184 (all kinds): if($id -notmatch '^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+_s\d+)$'){ Log "P7 job refused: bad id" }
  line 265 (kind graph/dip): if($id -notmatch '^ali147_pool_[a-z0-9]+_s\d+$'){ refused: graph/dip ids are ali147_pool_<arm>_s<seed> }
The arm segment is [a-z0-9]+ - no underscore, so the id the RS5/RS6 task lines name
(ali147_pool_refsheet_b_s51080000) can never pass. No render, no result.json.
This script only compiles the two .NET-regex-equivalent patterns in Python and prints the verdicts.
"""
import re

GATE1 = r"^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+_s\d+)$"   # ralph.ps1:184
GATE2 = r"^ali147_pool_[a-z0-9]+_s\d+$"                          # ralph.ps1:265 (graph/dip)

IDS = [
    "ali147_pool_ctrl_s51080000",        # rendered (CTRL)
    "ali147_pool_refsheet_s51080000",    # rendered (RS4) - arm segment has no underscore
    "ali147_pool_refsheet_b_s51080000",  # RS5/RS6 arm - the id TASKS.md names
    "ali147_pool_refsheetb_s51080000",   # underscore removed: passes both gates
]

for i in IDS:
    print("%-38s gate1(184)=%-5s gate2(265,graph/dip)=%s" % (i, bool(re.match(GATE1, i)), bool(re.match(GATE2, i))))

print("dip ids in the same family:", re.match(GATE1, "ali147_pool_dip_s51080000"), re.match(GATE2, "ali147_pool_dip_s51080000"))
