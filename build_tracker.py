import glob, json, re, html

VARIANTS = ["Normal","Gold","Gummy","Galaxy","Holofoil","Cube","Gem","Quack"]
VCOLOR = {
 "Normal":"#c7d0dd","Gold":"#ffb300","Gummy":"#ff3d9a","Galaxy":"#a855f7",
 "Holofoil":"#26e0b5","Cube":"#8ef123","Gem":"#38bdf8","Quack":"#ffe14d",
}
# token in filename -> variant column
TOKMAP = {
 "Default":"Normal","": "Normal","Gold":"Gold","Candy":"Gummy","Galaxy":"Galaxy",
 "Holo":"Holofoil","Holofoil":"Holofoil","Cube":"Cube","Gem":"Gem","Quack":"Quack",
}
# nice display names + preferred order
NAMES = {
 "Water":"Water","Earth":"Earth","Fire":"Fire","Fishy":"Fishy","Air":"Air",
 "Ghost":"Ghost","ZeroPoint":"Zero Point","Seven":"Seven","King":"King","Boss":"Boss",
 "Punk":"Punk","Sleepy":"Sleepy","Drifter":"Drifter","Soccer":"Soccer","Duck":"Duck",
 "GrimReaper":"Grim Reaper","RedDemon":"Red Demon","FossilMeal":"Fossil Meal",
 "BurntPeanut":"Burnt Peanut","CokeParmesan":"Coke Parmesan","CompanyStargazer":"Stargazer",
}
ORDER = ["Water","Earth","Fire","Fishy","Air","Duck","Ghost","RedDemon","King","Drifter",
 "Soccer","Sleepy","Punk","Boss","Seven","FossilMeal","GrimReaper","ZeroPoint",
 "BurntPeanut","CokeParmesan","CompanyStargazer"]

data = {}  # sprite -> {variant: filename}
for f in sorted(glob.glob("T_Icon_BR_*.webp")):
    core = f[len("T_Icon_BR_"):-len(".webp")].replace("Creature_Sprite_","")
    # strip trailing _ui _L UI L noise tokens
    parts = [p for p in core.split("_") if p not in ("ui","L","UI")]
    sprite = parts[0]
    rest = parts[1:]
    # determine variant
    var = None
    for tok in rest:
        if tok in TOKMAP:
            var = TOKMAP[tok]; break
    if var is None:
        # unvault / ch7s3 / default-less -> Normal
        var = "Normal"
    data.setdefault(sprite, {})
    # don't overwrite a real Normal with an unvault dup unless empty
    if var not in data[sprite]:
        data[sprite][var] = f

sprites = [s for s in ORDER if s in data] + [s for s in data if s not in ORDER]
rows = []
total = 0
for s in sprites:
    cells = {}
    for v in VARIANTS:
        if v in data[s]:
            cells[v] = data[s][v]; total += 1
    rows.append({"key":s,"name":NAMES.get(s,s),"cells":cells})

payload = {"variants":VARIANTS,"vcolor":VCOLOR,"rows":rows,"total":total}
json.dump(payload, open("sprite_data.json","w"))
print("sprites:",len(rows),"total variant icons:",total)
