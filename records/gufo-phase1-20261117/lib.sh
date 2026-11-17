# helpers: key is read from /etc/evo-x3/llm.env via sudo into a pipe each call; never stored or printed
hdr() { sudo bash -c '. /etc/evo-x3/llm.env; printf "Authorization: Bearer %s\n" "$LLM_KEY_BOX"'; }
kcurl() { curl -s -H @<(hdr) "$@"; }
mem() { echo "GTT_used_GiB=$(awk '{printf "%.2f",$1/1073741824}' /sys/class/drm/card*/device/mem_info_gtt_used | head -1) MemAvailable_GiB=$(awk '/MemAvailable/{printf "%.2f",$2/1048576}' /proc/meminfo) $(date +%T)"; }
running() { kcurl -m 10 http://127.0.0.1:8080/running | python3 -c 'import json,sys; print([(r["model"],r["state"]) for r in json.load(sys.stdin)["running"]])'; }
