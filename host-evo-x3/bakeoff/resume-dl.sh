#!/bin/bash
while pgrep -f "halogen.aria" >/dev/null; do sleep 10; done
cd /srv/bakeoff/fn-q4kxl-strata && aria2c -i list.aria -x 16 -s 16 -j 1 -c --file-allocation=none --console-log-level=warn > ~/evo-x3/bakeoff/dl-strata-fn.log 2>&1; echo FN_DL_DONE >> ~/evo-x3/bakeoff/dl-strata-fn.log
cd /srv/bakeoff/glm/Maya-S24 && aria2c -i list.aria -x 16 -s 16 -j 1 -c --file-allocation=none --console-log-level=warn > ~/evo-x3/bakeoff/dl-glm.log 2>&1; sha256sum -c SHA256SUMS.expected >> ~/evo-x3/bakeoff/dl-glm.log 2>&1 && echo GLM_SHA_OK >> ~/evo-x3/bakeoff/dl-glm.log
