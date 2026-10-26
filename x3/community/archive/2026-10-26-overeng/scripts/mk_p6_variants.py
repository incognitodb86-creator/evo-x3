import json, copy
P=r"C:\AI\community\shots\p6_1min_community.json"
base=json.load(open(P,encoding="utf-8"))
cut=" Then, about five seconds in, cut within this clip ([Shot 2]) to a close-up of her face and shoulders as she smiles at the camera."
def mk(tag, ab, cuts):
    out=[]
    for s in base:
        s=copy.deepcopy(s); s["id"]=s["id"].replace("p6_1min", "p6_1min_"+tag); s["antiburn"]=ab
        if cuts: s["beat"]=s["beat"]+cut
        out.append(s)
    f=P.replace("p6_1min_community", "p6_1min_"+tag); json.dump(out, open(f,"w",encoding="utf-8"), indent=1); print(f)
mk("ab05", 0.5, False); mk("cuts", None, True); mk("cuts_ab05", 0.5, True)
