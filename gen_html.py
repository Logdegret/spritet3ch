import json, os
d = json.load(open("sprite_data.json"))
info = json.load(open("sprite_info.json")) if os.path.exists("sprite_info.json") else {}

# Use the community display names Codex found (strip the " Sprite" suffix), with a couple of overrides.
NAME_OVERRIDE = {"GrimReaper":"Grim Reaper"}
for r in d["rows"]:
    k = r["key"]
    if k in NAME_OVERRIDE:
        r["name"] = NAME_OVERRIDE[k]
    elif k in info and info[k].get("name"):
        r["name"] = info[k]["name"].replace(" Sprite","").strip()

DATA = json.dumps(d, separators=(",",":"))
INFO = json.dumps(info, separators=(",",":"))

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sprite T3CH &mdash; Fortnite Variant Tracker</title>
<script src="html2canvas.min.js"></script>
<style>
  :root{
    --bg0:#0a0e2a; --bg1:#131a4a; --panel:#0f1638cc; --panel2:#161f52;
    --line:#2a3573; --txt:#e8ecff; --dim:#8b97cf; --accent:#3aa8ff;
    --gold:#ffcf3a; --lost:#ff6b6b;
  }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{
    font-family:"Segoe UI",system-ui,Arial,sans-serif; color:var(--txt);
    background:
      radial-gradient(1200px 600px at 80% -10%, #2a1b6b55, transparent),
      radial-gradient(1000px 500px at 0% 0%, #0e2a6b55, transparent),
      linear-gradient(160deg,var(--bg0),#0a0f30 60%,#0b0a24);
    min-height:100vh; padding:22px;
  }
  .wrap{max-width:1520px;margin:0 auto}
  .top{
    display:flex;align-items:center;gap:22px;flex-wrap:wrap;
    background:linear-gradient(120deg,#12184a,#1a2160);
    border:1px solid var(--line);border-radius:16px;padding:16px 24px;
    box-shadow:0 10px 40px #0006;
  }
  .ring{position:relative;width:64px;height:64px;flex:0 0 auto}
  .ring svg{transform:rotate(-90deg)}
  .ring span{position:absolute;inset:0;display:grid;place-items:center;font-weight:800;font-size:14px}
  .title h1{margin:0;font-size:30px;font-weight:900;letter-spacing:1px;font-style:italic}
  .title h1 b{color:var(--accent)}
  .title p{margin:2px 0 0;color:var(--dim);font-size:12px;letter-spacing:2px;text-transform:uppercase}
  .count{margin-left:auto;font-size:26px;font-weight:900}
  .count b{color:var(--gold)}.count span{color:var(--dim);font-weight:700;font-size:18px}
  .count small{display:block;font-size:11px;color:var(--gold);letter-spacing:1px;text-align:right;font-weight:700}
  .actions{display:flex;gap:10px}
  button.act{
    background:#182056;border:1px solid var(--line);color:var(--txt);
    border-radius:10px;padding:9px 14px;font-weight:700;
    cursor:pointer;font-size:12px;letter-spacing:.5px;text-transform:uppercase;transition:.15s
  }
  button.act:hover{border-color:var(--accent);background:#20296b}
  button.reset{color:#ff8a8a}
  button.reset.armed{background:#5a1620;border-color:var(--lost);color:#fff}
  .toast .undo{cursor:pointer;color:#7fd0ff;text-underline-offset:2px}
  button.discord{background:#5865F2;border-color:#5865F2;color:#fff}
  button.discord:hover{background:#4752c4;border-color:#4752c4}
  button.sync{border-color:#5865F2;color:#c9cfff}
  button.sync:hover{background:#5865F2;color:#fff}
  button.sync.synced{background:#1c2b1c;border-color:#3ad17a;color:#8ef1a8}

  .modal-backdrop{position:fixed;inset:0;background:#00040fcc;backdrop-filter:blur(3px);
    display:none;place-items:center;z-index:100}
  .modal-backdrop.show{display:grid}
  .modal{width:320px;background:linear-gradient(160deg,#141d54,#0d1338);
    border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 20px 60px #000a}
  .modal h3{margin:0 0 12px;font-size:18px}
  .modal p{margin:0 0 12px;font-size:13px;color:var(--dim);line-height:1.5}
  .modal code{background:#0c1233;padding:2px 6px;border-radius:5px;color:#8ef1a8;font-size:12px}
  .modal input{width:100%;box-sizing:border-box;background:#0c1233;border:1px solid var(--line);
    color:var(--txt);border-radius:9px;padding:12px;font-size:20px;letter-spacing:6px;text-align:center;
    text-transform:uppercase;font-weight:800;margin-bottom:12px}
  .modal input:focus{outline:none;border-color:var(--accent)}
  .modal-actions{display:flex;gap:8px;justify-content:flex-end}
  .modal-err{color:var(--lost);font-size:12px;min-height:14px;margin:8px 0 0}
  .modal p b{color:#8ef1a8}
  .toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);
    background:#182056;border:1px solid var(--accent);color:var(--txt);padding:12px 20px;
    border-radius:12px;font-weight:700;font-size:13px;box-shadow:0 10px 30px #000a;z-index:99;
    opacity:0;pointer-events:none;transition:.2s}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  .key{display:flex;gap:20px;flex-wrap:wrap;align-items:center;
    margin:16px 0;padding:12px 20px;background:var(--panel);
    border:1px solid var(--line);border-radius:12px;font-size:12px;
    text-transform:uppercase;letter-spacing:1px;color:var(--dim)}
  .key .k{display:flex;align-items:center;gap:8px}
  .swatch{width:22px;height:22px;border-radius:6px;border:1px solid #ffffff22;display:grid;place-items:center;font-size:12px}
  .sw-owned{background:#123; box-shadow:inset 0 0 0 2px var(--accent)}
  .sw-master{background:#2a2408;box-shadow:inset 0 0 0 2px var(--gold);color:var(--gold)}
  .sw-lost{background:#2a1114;box-shadow:inset 0 0 0 2px var(--lost);color:var(--lost)}
  .sw-missing{background:#0c1130;border:1px solid #ffffff14}
  .sw-na{background:transparent;border:1px dashed #ffffff2e}

  .layout{display:flex;gap:18px;align-items:flex-start}
  .side{flex:0 0 250px;position:sticky;top:22px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin-bottom:16px;
    transform:translateZ(0);-webkit-transform:translateZ(0)}
  .card h3{margin:0 0 12px;font-size:12px;letter-spacing:2px;color:var(--dim);text-transform:uppercase}
  .card summary{margin:0 0 12px;font-size:12px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;
    cursor:pointer;list-style:none}
  .card summary::-webkit-details-marker{display:none}
  .card summary::after{content:"\25BE";float:right;color:var(--dim)}
  .card details[open] .vlist{margin-top:0}
  .scroll-hint{display:none;text-align:center;font-size:11px;color:var(--dim);padding:2px 0 8px;letter-spacing:.5px}
  .bar{height:9px;border-radius:20px;background:#0c1233;overflow:hidden;margin:6px 0 4px}
  .bar>i{display:block;height:100%;border-radius:20px;background:linear-gradient(90deg,#3aa8ff,#8ef123)}
  .statrow{display:flex;justify-content:space-between;font-size:13px;padding:4px 0;color:var(--dim)}
  .statrow b{color:var(--txt)}
  .filters{display:flex;gap:8px;flex-wrap:wrap}
  .filters button{flex:1;min-width:64px;background:#141c4c;border:1px solid var(--line);
    color:var(--dim);border-radius:9px;padding:8px 6px;cursor:pointer;font-weight:700;
    font-size:11px;text-transform:uppercase;letter-spacing:.5px}
  .filters button.on{background:var(--accent);color:#04122b;border-color:var(--accent)}
  .toggle-row{display:flex;align-items:center;gap:8px;margin-top:12px;font-size:12px;
    color:var(--dim);cursor:pointer;user-select:none}
  .toggle-row input{accent-color:var(--accent);width:15px;height:15px;cursor:pointer}
  .gridwrap.hide-na .cell.na{visibility:hidden}
  .vlist .vrow{display:flex;justify-content:space-between;font-size:13px;padding:4px 0;color:var(--dim)}
  .vlist .dot{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:8px}
  .vlist b{color:var(--txt)}

  .gridwrap{flex:1;overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:10px}
  table{border-collapse:separate;border-spacing:10px 12px;width:100%}
  th.vh{color:#081226;font-weight:900;font-size:13px;text-transform:uppercase;letter-spacing:1px;
    padding:10px 6px;border-radius:10px;text-align:center;min-width:96px;cursor:help;transition:.15s}
  th.vh:hover{filter:brightness(1.12);transform:translateY(-1px)}

  .vpop{width:280px}
  .vpop .vhead{display:flex;gap:14px;align-items:center;padding:14px 16px 10px}
  .vsample{position:relative;overflow:hidden;width:72px;height:72px;flex:0 0 auto;border-radius:12px;
    display:grid;place-items:center;background:radial-gradient(120% 120% at 50% 20%,#1a2570,#0b1030 72%);
    box-shadow:0 0 0 1px #ffffff1f}
  .vsample img{width:80%;height:80%;object-fit:contain;position:relative;z-index:1}
  .vsample .fx{opacity:1;border-radius:12px}
  th.corner{text-align:left;color:var(--dim);font-size:12px;letter-spacing:2px;
    text-transform:uppercase;padding-left:8px;min-width:150px}
  td.rowname{font-weight:800;font-size:16px;white-space:nowrap;padding-left:8px}
  td.rowname .rn{display:flex;align-items:center;gap:10px;cursor:help}
  td.rowname .pip{width:8px;height:8px;border-radius:50%;background:var(--accent);flex:0 0 auto}
  td.rowname .frac{display:block;font-size:11px;color:var(--dim);font-weight:600;margin-top:3px;letter-spacing:1px}
  td.rowname .rar{display:inline-block;font-size:9px;padding:1px 6px;border-radius:20px;margin-top:4px;
    letter-spacing:1px;font-weight:800;text-transform:uppercase}

  .cell{position:relative;width:96px;height:112px;border-radius:14px;margin:0 auto;
    display:grid;place-items:center;cursor:pointer;user-select:none;transition:.18s;
    background:linear-gradient(160deg,#0f1740,#0b1030);border:1px solid #ffffff10}
  .cell img{width:82%;height:82%;object-fit:contain;filter:grayscale(1) brightness(.55);transition:.18s;pointer-events:none;position:relative;z-index:1}
  .cell.na{cursor:default;border:1px dashed #ffffff22;background:#0a0e2a55}
  .cell.na::after{content:"";width:26px;height:26px;border-radius:50%;
    border:2px solid #ffffff22;position:absolute;
    background:radial-gradient(circle,transparent 40%,#ffffff10 42%)}
  /* owned */
  .cell.own img,.cell.master img{filter:none}
  .cell.own{box-shadow:0 0 0 2px var(--cc), 0 0 22px -4px var(--cc);
    background:radial-gradient(120% 120% at 50% 20%, var(--cc)22, #0b1030 70%)}
  /* mastered */
  .cell.master{box-shadow:0 0 0 2px var(--gold), 0 0 26px -3px var(--gold);
    background:radial-gradient(120% 120% at 50% 20%, #ffcf3a2e, #0b1030 70%)}
  /* lost */
  .cell.lost{box-shadow:inset 0 0 0 2px var(--lost)}
  .cell.lost img{filter:grayscale(1) brightness(.5) sepia(.4) hue-rotate(-30deg)}
  .cell .lock{position:absolute;bottom:8px;right:9px;font-size:13px;opacity:.5}
  .cell.own .lock,.cell.master .lock,.cell.lost .lock{display:none}
  .cell .chk{position:absolute;top:7px;left:8px;width:17px;height:17px;border-radius:5px;
    border:1px solid #ffffff2e;display:grid;place-items:center;font-size:11px;color:transparent;background:transparent}
  .cell.own .chk{background:var(--cc);color:#04122b;border-color:var(--cc);font-weight:900}
  .cell.own .chk::after{content:"\2713"}
  .cell .badge{position:absolute;top:6px;right:7px;font-size:14px;display:none;filter:drop-shadow(0 1px 2px #000)}
  .cell.master .badge{display:block}
  .cell.master .badge::after{content:"\1F451"}
  .cell.lost .chk{background:var(--lost);border-color:var(--lost);color:#2a0b0b}
  .cell.lost .chk::after{content:"\2716";font-weight:900}
  .cell:not(.na):hover{transform:translateY(-2px)}
  .cell:not(.na):hover img{filter:grayscale(.25) brightness(.95)}
  .cell.own:hover img,.cell.master:hover img{filter:none}
  .cell .chk,.cell .badge,.cell .lock{z-index:4}

  /* ---- variant special effects ---- */
  .fx{position:absolute;inset:0;border-radius:14px;overflow:hidden;pointer-events:none;
      z-index:2;opacity:0;transition:opacity .3s}
  .cell.own .fx,.cell.master .fx,.cell:not(.na):hover .fx{opacity:1}
  .cell.lost .fx{opacity:0 !important}
  @keyframes sheen{0%{background-position:135% 0}100%{background-position:-45% 0}}
  @keyframes holoShift{0%{background-position:135% 0,0 0}100%{background-position:-45% 0,220% 0}}
  @keyframes twinkle{0%,100%{filter:brightness(.5)}50%{filter:brightness(1.7)}}
  @keyframes drift{to{transform:rotate(360deg)}}
  @keyframes glitch{0%,100%{transform:translateX(0)}50%{transform:translateX(1px)}}

  .fx-Normal{mix-blend-mode:screen;background:linear-gradient(115deg,transparent 40%,#ffffff5c 52%,transparent 64%);
    background-size:250% 250%;animation:sheen 3.6s linear infinite}
  .fx-Gold{mix-blend-mode:screen;background:linear-gradient(115deg,transparent 32%,#fff6c8 46%,#ffcf3a 50%,transparent 66%);
    background-size:250% 250%;animation:sheen 2.6s linear infinite}
  .fx-Gummy{mix-blend-mode:screen;
    background:radial-gradient(60% 42% at 34% 24%,#ffffffcc,transparent 60%),
      linear-gradient(115deg,transparent 40%,#ff7ac9 55%,transparent 70%);
    background-size:auto,250% 250%;animation:sheen 3s linear infinite}
  .fx-Galaxy{mix-blend-mode:screen;
    background:radial-gradient(1.6px 1.6px at 20% 30%,#fff,transparent),
      radial-gradient(1.6px 1.6px at 72% 62%,#d6c7ff,transparent),
      radial-gradient(1.2px 1.2px at 42% 82%,#fff,transparent),
      radial-gradient(1.2px 1.2px at 86% 24%,#fff,transparent),
      radial-gradient(1.6px 1.6px at 56% 14%,#e9d5ff,transparent),
      radial-gradient(1.2px 1.2px at 12% 66%,#c9b3ff,transparent);
    animation:twinkle 2.3s ease-in-out infinite}
  .fx-Holofoil{mix-blend-mode:screen;opacity:.55;
    background:linear-gradient(115deg,transparent 30%,#ffffff88 50%,transparent 62%),
      repeating-linear-gradient(115deg,#c65cff55 0 14%,#4fd6ff55 14% 28%,#ffe89955 28% 42%,#7dffc255 42% 56%);
    background-size:250% 250%,250% 250%;animation:holoShift 4.4s linear infinite}
  .cell.own .fx-Holofoil,.cell.master .fx-Holofoil,.cell:not(.na):hover .fx-Holofoil{opacity:.55}
  .fx-Cube{mix-blend-mode:screen;
    background:repeating-linear-gradient(0deg,#8ef12330 0 2px,transparent 2px 4px),
      linear-gradient(115deg,transparent 34%,#b6ff5e 50%,transparent 66%);
    background-size:auto,250% 250%;animation:sheen 2.2s linear infinite,glitch 1.4s steps(2) infinite}
  .fx-Gem{mix-blend-mode:screen;
    background:linear-gradient(60deg,#00e5ff5c,transparent 42%),
      linear-gradient(-60deg,#c77dff5c,transparent 42%),
      linear-gradient(115deg,transparent 40%,#ffffff 52%,transparent 64%);
    background-size:auto,auto,250% 250%;animation:sheen 2.4s linear infinite}
  .fx-Quack{mix-blend-mode:screen;background:linear-gradient(115deg,transparent 34%,#fff1a6 52%,transparent 68%);
    background-size:250% 250%;animation:sheen 2.8s linear infinite}
  @media (prefers-reduced-motion: reduce){.fx{animation:none!important}}

  .foot{color:var(--dim);font-size:12px;text-align:center;margin:18px 0 4px}

  .ad-slot{margin:14px 0 0;min-height:90px;border:1px dashed #ffffff22;border-radius:12px;
    background:#0c1233a0;display:flex;align-items:center;justify-content:center;position:relative;
    transform:translateZ(0);-webkit-transform:translateZ(0)}
  .ad-slot:empty::before,.ad-slot:has(> :only-child:is(.ad-label))::before{
    content:"Ad slot — Adsterra Native Banner"; color:var(--dim); font-size:11px; letter-spacing:.5px}
  .ad-label{position:absolute;top:4px;left:8px;font-size:9px;letter-spacing:1px;
    text-transform:uppercase;color:#5a6699}

  /* ---------------- export image template ---------------- */
  .xcard{width:900px;padding:44px 50px 36px;font-family:"Segoe UI",system-ui,Arial,sans-serif;
    background:linear-gradient(170deg,#2e6bf0 0%,#1c3fb0 45%,#0f2170 100%)}
  .xeyebrow{color:#bcd6ff;font-size:13px;font-weight:800;letter-spacing:2px;text-transform:uppercase}
  .xtitle{color:#fff;font-size:52px;font-weight:900;font-style:italic;letter-spacing:1px;margin:4px 0 6px}
  .xsub{color:#c3d6ff;font-size:15px;margin-bottom:22px}
  .xbarwrap{height:10px;border-radius:20px;background:#ffffff2e;overflow:hidden}
  .xbar{height:100%;border-radius:20px;background:linear-gradient(90deg,#fff,#bcd6ff)}
  .xcount{color:#fff;font-weight:800;font-size:14px;text-align:right;margin:8px 0 26px}
  .xhead{display:flex;margin-bottom:10px}
  .xhead .xnamecol{width:190px;flex:0 0 auto}
  .xheadcells{display:flex;gap:10px;flex:1}
  .xheadcells div{flex:1;text-align:center;color:#dbe8ff;font-size:11px;font-weight:800;
    letter-spacing:1px;text-transform:uppercase;background:#ffffff22;border-radius:8px;padding:8px 2px}
  .xrow{display:flex;align-items:center;padding:14px 0;border-top:1px solid #ffffff1f}
  .xname{width:190px;flex:0 0 auto;color:#fff;font-weight:800;font-size:14px;letter-spacing:.5px;
    display:flex;align-items:center;gap:8px}
  .xdot{width:8px;height:8px;border-radius:50%;flex:0 0 auto}
  .xcells{display:flex;gap:10px;flex:1}
  .xcell{flex:1;aspect-ratio:1;border-radius:12px;display:grid;place-items:center;position:relative;overflow:hidden}
  .xcell.xna{background:transparent}
  .xcell.xmissing{background:#ffffff1a;box-shadow:inset 0 0 0 1px #ffffff2e}
  .xcell.xmissing img{width:78%;height:78%;object-fit:contain;filter:grayscale(1) brightness(.4);opacity:.65}
  .xcell.xmissing::after{content:"\1F512";font-size:17px;opacity:.9;position:absolute;
    bottom:5px;right:6px;filter:drop-shadow(0 1px 2px #000)}
  .xcell.xown{background:radial-gradient(120% 120% at 50% 20%, var(--cc)55, #ffffff18 70%);
    box-shadow:0 0 0 2px var(--cc)}
  .xcell.xown img{width:78%;height:78%;object-fit:contain}
  .xcrown{position:absolute;top:-6px;right:-4px;font-size:18px;filter:drop-shadow(0 1px 2px #000)}
  .xfoot{margin-top:26px;padding-top:18px;border-top:1px solid #ffffff2e;
    text-align:center;color:#dbe8ff;font-weight:700;font-size:13px;letter-spacing:1px}

  /* ---------------- mobile ---------------- */
  @media (max-width: 860px){
    body{padding:10px}
    .scroll-hint{display:block}
    .top{padding:12px 14px;gap:12px}
    .title h1{font-size:22px}
    .title p{font-size:10px;letter-spacing:1px}
    .ring{width:52px;height:52px}
    .ring svg{width:52px;height:52px}
    .count{margin-left:0;font-size:20px}
    .actions{width:100%;order:3;flex-wrap:wrap}
    .actions button{flex:1 1 auto;font-size:11px;padding:10px 8px}
    .key{gap:10px;font-size:11px;padding:10px 14px}
    .key .k:last-child{display:none}
    .layout{flex-direction:column}
    .side{flex:1 1 auto;position:static;width:100%;order:1;
      display:grid;grid-template-columns:1fr 1fr;gap:14px}
    .side .card:last-child{grid-column:1 / -1}
    .gridwrap{order:2;width:100%}
    .cell{width:66px;height:82px;border-radius:11px}
    .cell .chk{width:14px;height:14px;font-size:9px}
    .cell .lock{font-size:11px}
    table{border-spacing:6px 8px}
    th.vh{min-width:66px;font-size:10px;padding:8px 3px}
    th.corner{min-width:96px}
    td.rowname{font-size:13px}
    td.rowname .rar{font-size:8px}
    .pop{width:min(300px, calc(100vw - 24px))}
    .modal{width:min(320px, calc(100vw - 32px))}
  }
  @media (max-width: 520px){
    .side{grid-template-columns:1fr}
    .cell{width:58px;height:74px}
    th.vh{min-width:58px}
  }
  @media (hover: none){
    .cell:not(.na):hover{transform:none}
  }

  /* popup */
  .pop{position:fixed;z-index:50;width:300px;background:linear-gradient(160deg,#141d54,#0d1338);
    border:1px solid var(--line);border-radius:14px;padding:0;box-shadow:0 18px 50px #000a;
    opacity:0;transform:translateY(6px);pointer-events:none;transition:opacity .12s,transform .12s}
  .pop.show{opacity:1;transform:translateY(0);pointer-events:auto}
  .pop .phead{display:flex;gap:12px;padding:14px 16px 10px;align-items:center}
  .pop .pimg{position:relative;overflow:hidden;width:56px;height:56px;flex:0 0 auto;border-radius:10px;display:grid;place-items:center;
    background:radial-gradient(120% 120% at 50% 20%,var(--cc,#3aa8ff)33,#0b1030 70%);box-shadow:0 0 0 1px var(--cc,#3aa8ff)55}
  .pop .pimg img{width:82%;height:82%;object-fit:contain;position:relative;z-index:1}
  .pop .pimg .fx{opacity:1;border-radius:10px}
  .pop .pt h4{margin:0;font-size:17px;font-weight:900}
  .pop .pt .sub{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:1px;margin-top:2px}
  .pop .rar{display:inline-block;font-size:9px;padding:2px 8px;border-radius:20px;margin-top:6px;
    letter-spacing:1px;font-weight:800;text-transform:uppercase}
  .pop .pbody{padding:0 16px 12px;font-size:12.5px;line-height:1.5;color:#cdd6ff}
  .pop .pmeta{padding:0 16px 12px;font-size:11px;color:var(--dim)}
  .pop .pmeta span{color:#d6ddff}
  .pop .pactions{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:12px 14px;border-top:1px solid #ffffff12}
  .pop .pactions button{border:1px solid var(--line);background:#152060;color:var(--txt);
    border-radius:9px;padding:8px 4px;font-size:11px;font-weight:800;cursor:pointer;text-transform:uppercase;letter-spacing:.4px;transition:.12s}
  .pop .pactions button:hover{filter:brightness(1.2)}
  .pop .pactions .b-own{border-color:var(--accent)} .pop .pactions .b-own.on{background:var(--accent);color:#04122b}
  .pop .pactions .b-master{border-color:var(--gold)} .pop .pactions .b-master.on{background:var(--gold);color:#2a2408}
  .pop .pactions .b-lost{border-color:var(--lost)} .pop .pactions .b-lost.on{background:var(--lost);color:#2a0b0b}
  .pop .pactions .b-clear{color:var(--dim)}
  .pop .phint{font-size:10px;color:var(--dim);text-align:center;padding:0 0 10px;letter-spacing:.3px}

  .r-Rare{background:#12408f;color:#bcd8ff}
  .r-Epic{background:#5b1e9c;color:#e6ccff}
  .r-Legendary{background:#8a5a00;color:#ffe6a8}
  .r-Mythic{background:#7a1420;color:#ffc4c4}
  .r-Unknown{background:#2a3573;color:#aab6e8}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <div class="ring">
      <svg width="64" height="64" viewBox="0 0 64 64"><circle cx="32" cy="32" r="27" stroke="#20305e" stroke-width="7" fill="none"/>
      <circle id="ringp" cx="32" cy="32" r="27" stroke="#3aa8ff" stroke-width="7" fill="none"
        stroke-linecap="round" stroke-dasharray="169.6" stroke-dashoffset="169.6"/></svg>
      <span id="ringtxt">0%</span>
    </div>
    <div class="title">
      <h1>SPRITE <b>T3CH</b></h1>
      <p>Track every variant you've unlocked</p>
    </div>
    <div class="count"><b id="own">0</b> <span>/ <i id="tot">0</i></span>
      <small><span id="mast">0</span> mastered &#128081;</small></div>
    <div class="actions">
      <button class="act sync" id="syncBtn" onclick="openSync()">&#128279; Sync with Discord</button>
      <button class="act discord" onclick="copyDiscord()">&#128203; Copy for Discord</button>
      <button class="act" id="exportBtn" onclick="exportImage()">&#128247; Export Image</button>
      <button class="act" onclick="markAll('own')">Mark all</button>
      <button class="act reset" onclick="resetAll()">Reset</button>
    </div>
  </div>
  <div id="toast" class="toast"></div>

  <!-- sync modal -->
  <div class="modal-backdrop" id="syncBackdrop">
    <div class="modal">
      <h3>Sync with Discord</h3>
      <div id="syncUnlinked">
        <p>Run <code>/synccode</code> in Discord, then paste the 6-character code it gives you:</p>
        <input id="syncInput" maxlength="6" placeholder="ABC123" autocomplete="off" spellcheck="false">
        <div class="modal-actions">
          <button class="act" onclick="closeSync()">Cancel</button>
          <button class="act sync" onclick="submitSync()">Connect</button>
        </div>
        <p class="modal-err" id="syncErr"></p>
      </div>
      <div id="syncLinked" style="display:none">
        <p>Synced as <b id="syncName"></b> — your marks now save to Discord too.</p>
        <div class="modal-actions">
          <button class="act reset" onclick="unlinkSync()">Disconnect</button>
          <button class="act sync" onclick="closeSync()">Done</button>
        </div>
      </div>
    </div>
  </div>

  <div class="key">
    <span style="color:var(--txt);font-weight:800;letter-spacing:2px">KEY</span>
    <span class="k"><span class="swatch sw-owned">&#10003;</span>Owned</span>
    <span class="k"><span class="swatch sw-master">&#128081;</span>Mastered</span>
    <span class="k"><span class="swatch sw-lost">&#10006;</span>Lost</span>
    <span class="k"><span class="swatch sw-missing"></span>Missing</span>
    <span class="k"><span class="swatch sw-na"></span>Not available</span>
    <span class="k" style="margin-left:auto">Hover for info &amp; options &middot; click to mark &middot; double-click to master</span>
  </div>

  <div class="layout">
    <aside class="side">
      <div class="card">
        <h3>Collection</h3>
        <div class="bar"><i id="pbar" style="width:0%"></i></div>
        <div class="statrow"><span id="pct2">0%</span><span id="frac2">0 / 0</span></div>
        <div class="statrow" style="margin-top:6px"><span>&#128081; Mastered</span><b id="mast2">0</b></div>
        <div class="statrow"><span>&#10006; Lost</span><b id="lost2">0</b></div>
      </div>
      <div class="card">
        <h3>Show</h3>
        <div class="filters" id="filters">
          <button data-f="all" class="on">All</button>
          <button data-f="owned">Owned</button>
          <button data-f="missing">Missing</button>
          <button data-f="master">Mastered</button>
          <button data-f="lost">Lost</button>
        </div>
        <label class="toggle-row">
          <input type="checkbox" id="hideNA">
          <span>Hide unreleased (&#128683;)</span>
        </label>
      </div>
      <div class="card">
        <details open>
          <summary>By Variant</summary>
          <div class="vlist" id="vlist"></div>
        </details>
      </div>
    </aside>

    <div class="gridwrap">
      <div class="scroll-hint">&#8596; swipe to see all variants</div>
      <table id="grid"></table>
    </div>
  </div>
  <div class="foot">Fortnite Sprite T3CH &middot; fan-made collection tracker &middot; progress stored locally in your browser</div>

  <!-- Ad slot: Adsterra Native Banner -->
  <div class="ad-slot" id="ad-native-banner">
    <span class="ad-label">Advertisement</span>
    <script async="async" data-cfasync="false" src="https://pl30550800.effectivecpmnetwork.com/cb8fc8d61c634a47260db35be939a2ea/invoke.js"></script>
    <div id="container-cb8fc8d61c634a47260db35be939a2ea"></div>
  </div>
</div>

<!-- hover popup -->
<div class="pop" id="pop">
  <div class="phead">
    <div class="pimg" id="pImg"><img id="pImgI" src="" alt=""><span class="fx" id="pFx"></span></div>
    <div class="pt">
      <h4 id="pName">&mdash;</h4>
      <div class="sub" id="pSub"></div>
      <span class="rar r-Unknown" id="pRar">&mdash;</span>
    </div>
  </div>
  <div class="pbody" id="pDesc"></div>
  <div class="pmeta" id="pMeta"></div>
  <div class="pactions">
    <button class="b-own"    id="pOwn"    onclick="setStateFromPop('own')">Mark</button>
    <button class="b-master" id="pMaster" onclick="setStateFromPop('master')">Master</button>
    <button class="b-lost"   id="pLost"   onclick="setStateFromPop('lost')">Lost</button>
    <button class="b-clear"  id="pClear"  onclick="setStateFromPop(null)">Clear</button>
  </div>
  <div class="phint">Click cell = mark &middot; double-click = master</div>
</div>

<!-- variant effect popup -->
<div class="pop vpop" id="vpop">
  <div class="vhead">
    <div class="vsample" id="vSample"><img id="vImg" src="" alt=""><span class="fx" id="vFx"></span></div>
    <div class="pt">
      <h4 id="vName">&mdash;</h4>
      <div class="sub">Variant effect</div>
    </div>
  </div>
  <div class="pbody" id="vDesc"></div>
  <div class="phint">Live preview of the in-game effect</div>
</div>

<script>
const DATA = __DATA__;
const INFO = __INFO__;
// Perk data: the sprite's core ability is identical across variants — each variant
// layers one extra passive perk on top. Cube/Quack per community reporting, less certain.
const VINFO = {
  Normal:  {t:"Normal",   d:"The base finish — no bonus perk. Same core ability as every other variant, just no extra effect on top."},
  Gold:    {t:"Gold",     d:"Perk: 3× Sprite XP from eliminations. Same core ability as any variant, plus faster Sprite leveling."},
  Gummy:   {t:"Gummy",    d:"Perk: +20% Sprite Dust earned. Same core ability as any variant, plus more crafting/summoning currency."},
  Galaxy:  {t:"Galaxy",   d:"Perk: +30% ammo from pickups. Same core ability as any variant, plus more ammo when looting."},
  Holofoil:{t:"Holofoil", d:"Perk: better odds of finding rare Sprites. Same core ability as any variant, plus improved rare-sprite luck."},
  Cube:    {t:"Cube",     d:"Perk: grants Storm Overdrive (reported). Same core ability as any variant, plus this Cube-corrupted bonus."},
  Gem:     {t:"Gem",      d:"Perk: -30% fall damage taken. Same core ability as any variant, plus safer falls."},
  Quack:   {t:"Quack",    d:"Perk: not yet confirmed by the community. Same core ability as any variant — bonus effect TBA."},
};
const V = DATA.variants, VC = DATA.vcolor, ROWS = DATA.rows, TOTAL = DATA.total;
const KEY = "spriteLocker.v2";
let state = {};                 // "s|v" -> "own"|"master"|"lost"
try{ state = JSON.parse(localStorage.getItem(KEY)||"{}"); }catch(e){ state={}; }
let filter = "all";
const ROWMAP = {}; ROWS.forEach(r=>ROWMAP[r.key]=r);

function id(s,v){return s+"|"+v;}
function st(s,v){return state[id(s,v)]||null;}
const isCollected = x => x==="own"||x==="master";

/* ---------- Discord sync ---------- */
const API_BASE = "https://34.132.232.165.sslip.io/api";
const SITE_URL = "https://logdegret.github.io/spritet3ch/";
const SYNC_TOKEN_KEY = "spriteLocker.syncToken", SYNC_NAME_KEY = "spriteLocker.syncName";
let syncToken = localStorage.getItem(SYNC_TOKEN_KEY) || null;
let syncName  = localStorage.getItem(SYNC_NAME_KEY)  || null;
let syncPushTimer = null;

function save(){
  localStorage.setItem(KEY, JSON.stringify(state));
  if(syncToken){
    clearTimeout(syncPushTimer);
    syncPushTimer = setTimeout(()=>{
      fetch(API_BASE+"/set", {
        method:"POST", headers:{"Content-Type":"application/json","X-Sync-Token":syncToken},
        body: JSON.stringify({state})
      }).catch(()=>{ /* offline — localStorage still has it, will retry on next change */ });
    }, 400);
  }
}

function updateSyncButton(){
  const b=document.getElementById("syncBtn");
  b.classList.toggle("synced", !!syncToken);
  b.innerHTML = syncToken ? `&#128279; Synced: ${syncName}` : `&#128279; Sync with Discord`;
}
async function initSync(){
  updateSyncButton();
  if(!syncToken) return;
  try{
    const r = await fetch(API_BASE+"/state", {headers:{"X-Sync-Token":syncToken}});
    const j = await r.json();
    if(j.ok){ state = j.state || {}; localStorage.setItem(KEY, JSON.stringify(state)); refresh(); }
    else { syncToken=null; syncName=null; localStorage.removeItem(SYNC_TOKEN_KEY); localStorage.removeItem(SYNC_NAME_KEY); updateSyncButton(); }
  }catch(e){ toast("⚠️ Could not reach sync server — using local data"); }
}
function openSync(){
  document.getElementById("syncBackdrop").classList.add("show");
  document.getElementById("syncErr").textContent="";
  if(syncToken){
    document.getElementById("syncUnlinked").style.display="none";
    document.getElementById("syncLinked").style.display="block";
    document.getElementById("syncName").textContent=syncName;
  } else {
    document.getElementById("syncUnlinked").style.display="block";
    document.getElementById("syncLinked").style.display="none";
    const inp=document.getElementById("syncInput"); inp.value=""; setTimeout(()=>inp.focus(),50);
  }
}
function closeSync(){ document.getElementById("syncBackdrop").classList.remove("show"); }
async function submitSync(){
  const code=document.getElementById("syncInput").value.trim().toUpperCase();
  const errEl=document.getElementById("syncErr");
  if(code.length!==6){ errEl.textContent="Enter the 6-character code from /synccode."; return; }
  try{
    const r=await fetch(API_BASE+"/redeem",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code})});
    const j=await r.json();
    if(!j.ok){ errEl.textContent=j.error||"That code didn't work."; return; }
    syncToken=j.token; syncName=j.display_name;
    localStorage.setItem(SYNC_TOKEN_KEY, syncToken); localStorage.setItem(SYNC_NAME_KEY, syncName);
    // push whatever we have locally right now so nothing is lost, then pull merged truth
    await fetch(API_BASE+"/set",{method:"POST",headers:{"Content-Type":"application/json","X-Sync-Token":syncToken},body:JSON.stringify({state})});
    await initSync();
    toast(`✅ Synced as ${syncName}`);
    openSync();
  }catch(e){ errEl.textContent="Couldn't reach the sync server. Try again in a moment."; }
}
function unlinkSync(){
  syncToken=null; syncName=null;
  localStorage.removeItem(SYNC_TOKEN_KEY); localStorage.removeItem(SYNC_NAME_KEY);
  updateSyncButton(); closeSync(); toast("Disconnected — your marks now stay local only");
}
document.getElementById("syncBackdrop").addEventListener("click", e=>{ if(e.target.id==="syncBackdrop") closeSync(); });
document.getElementById("syncInput")?.addEventListener("keydown", e=>{ if(e.key==="Enter") submitSync(); });

function build(){
  const t = document.getElementById("grid");
  let h = "<thead><tr><th class='corner'>Sprite</th>";
  for(const v of V){ h += `<th class='vh' data-v='${v}' style="background:linear-gradient(180deg,${VC[v]},${VC[v]}cc)">${v} &#9432;</th>`; }
  h += "</tr></thead><tbody>";
  for(const r of ROWS){
    const info = INFO[r.key]||{};
    const rar = (info.rarity||"Unknown").split(" ")[0];
    h += `<tr data-sprite="${r.key}"><td class='rowname'>
      <div class='rn' data-info='${r.key}'><span class='pip'></span>
        <span>${r.name}<span class='frac' data-frac></span>
        <span class='rar r-${rar}'>${rar}</span></span></div></td>`;
    for(const v of V){
      const file = r.cells[v];
      if(!file){ h += `<td><div class='cell na'></div></td>`; continue; }
      h += `<td><div class='cell' data-s='${r.key}' data-v='${v}' style="--cc:${VC[v]}">
        <span class='chk'></span><span class='badge'></span>
        <img loading="lazy" src="${file}" alt="${r.name} ${v}">
        <span class='fx fx-${v}'></span>
        <span class='lock'>&#128274;</span></div></td>`;
    }
    h += "</tr>";
  }
  h += "</tbody>";
  t.innerHTML = h;

  const HOVER_OK = matchMedia("(hover: hover) and (pointer: fine)").matches;
  t.querySelectorAll(".cell:not(.na)").forEach(c=>{
    c.addEventListener("click", e=>{ cycle(c.dataset.s,c.dataset.v); });
    c.addEventListener("dblclick", e=>{ e.preventDefault(); setState(c.dataset.s,c.dataset.v,"master"); });
    if(HOVER_OK){
      c.addEventListener("mouseenter", ()=>schedulePop(c));
      c.addEventListener("mouseleave", clearSchedule);
    }
  });
  // row name hover -> info popup (no variant)
  t.querySelectorAll(".rn[data-info]").forEach(rn=>{
    rn.addEventListener("mouseenter", ()=>schedulePop(rn, rn.dataset.info));
    rn.addEventListener("mouseleave", clearSchedule);
  });
  // column header hover -> variant effect popup
  t.querySelectorAll("th.vh[data-v]").forEach(th=>{
    th.addEventListener("mouseenter", ()=>scheduleVar(th));
    th.addEventListener("mouseleave", clearVarSchedule);
  });
  refresh();
}

// single click cycles: none -> own -> master -> none  (lost only via popup/keep simple)
function cycle(s,v){
  const cur=st(s,v);
  const next = cur==null ? "own" : cur==="own" ? "master" : cur==="master" ? null : null;
  setState(s,v,next);
}
function setState(s,v,val){
  const k=id(s,v); if(val==null) delete state[k]; else state[k]=val;
  save(); refresh(); if(popCell) syncPopButtons();
}
function markAll(val){
  state={};
  if(val){ for(const r of ROWS) for(const v of V) if(r.cells[v]) state[id(r.key,v)]=val; }
  save(); refresh();
}
let resetArmed=false, resetTimer=null, resetBackup=null;
function resetAll(){
  if(!Object.keys(state).length){ toast("Nothing to reset — collection is already empty"); return; }
  if(!resetArmed){
    resetArmed=true;
    document.querySelector("button.reset").classList.add("armed");
    toast("⚠️ Click Reset again to clear everything");
    clearTimeout(resetTimer);
    resetTimer=setTimeout(disarmReset, 3500);
    return;
  }
  disarmReset();
  resetBackup=JSON.stringify(state);
  markAll(null);
  toastUndo("🧹 Collection cleared", ()=>{
    if(resetBackup){ state=JSON.parse(resetBackup); resetBackup=null; save(); refresh(); toast("↩️ Restored"); }
  });
}
function disarmReset(){ resetArmed=false; clearTimeout(resetTimer); document.querySelector("button.reset").classList.remove("armed"); }

function refresh(){
  let coll=0, mast=0, lost=0;
  const vcount={}; V.forEach(v=>vcount[v]=[0,0]);
  document.querySelectorAll(".cell:not(.na)").forEach(c=>{
    const s=st(c.dataset.s,c.dataset.v);
    c.classList.remove("own","master","lost");
    if(s) c.classList.add(s);
    if(isCollected(s)) coll++;
    if(s==="master") mast++;
    if(s==="lost") lost++;
    vcount[c.dataset.v][1]++; if(isCollected(s)) vcount[c.dataset.v][0]++;
  });
  document.querySelectorAll("#grid tbody tr").forEach(tr=>{
    let ro=0,rt=0,rm=0,rl=0;
    tr.querySelectorAll(".cell:not(.na)").forEach(c=>{rt++;
      if(c.classList.contains("own")||c.classList.contains("master"))ro++;
      if(c.classList.contains("master"))rm++;
      if(c.classList.contains("lost"))rl++;});
    const f=tr.querySelector("[data-frac]"); if(f) f.textContent = rt? ` ${ro}/${rt}`:"";
    let show=true;
    if(filter==="owned")   show = ro>0;
    if(filter==="missing") show = ro<rt;
    if(filter==="master")  show = rm>0;
    if(filter==="lost")    show = rl>0;
    tr.style.display = show? "":"none";
  });
  const pct = TOTAL? Math.round(coll/TOTAL*100):0;
  document.getElementById("own").textContent=coll;
  document.getElementById("tot").textContent=TOTAL;
  document.getElementById("mast").textContent=mast;
  document.getElementById("ringtxt").textContent=pct+"%";
  document.getElementById("ringp").style.strokeDashoffset=(169.6*(1-coll/TOTAL)).toFixed(1);
  document.getElementById("pbar").style.width=pct+"%";
  document.getElementById("pct2").textContent=pct+"%";
  document.getElementById("frac2").textContent=coll+" / "+TOTAL;
  document.getElementById("mast2").textContent=mast;
  document.getElementById("lost2").textContent=lost;
  const vl=document.getElementById("vlist");
  vl.innerHTML=V.map(v=>`<div class='vrow'><span><span class='dot' style="background:${VC[v]}"></span>${v}</span><b>${vcount[v][0]}/${vcount[v][1]}</b></div>`).join("");
}

document.getElementById("filters").addEventListener("click",e=>{
  const b=e.target.closest("button"); if(!b)return;
  filter=b.dataset.f;
  document.querySelectorAll("#filters button").forEach(x=>x.classList.toggle("on",x===b));
  refresh();
});

const HIDE_NA_KEY="spriteLocker.hideNA";
const hideNAbox=document.getElementById("hideNA");
hideNAbox.checked = localStorage.getItem(HIDE_NA_KEY)==="1";
document.querySelector(".gridwrap").classList.toggle("hide-na", hideNAbox.checked);
hideNAbox.addEventListener("change", ()=>{
  document.querySelector(".gridwrap").classList.toggle("hide-na", hideNAbox.checked);
  localStorage.setItem(HIDE_NA_KEY, hideNAbox.checked ? "1" : "0");
});

/* ---------- hover popup ---------- */
const pop=document.getElementById("pop");
let popTimer=null, popCell=null, popKey=null, popVariant=null, overPop=false;

function schedulePop(el, spriteKeyOnly){
  clearTimeout(popTimer);
  popTimer=setTimeout(()=>showPop(el, spriteKeyOnly), 320);
}
function clearSchedule(){
  clearTimeout(popTimer);
  popTimer=setTimeout(()=>{ if(!overPop) hidePop(); }, 160);
}
function showPop(el, spriteKeyOnly){
  const s = spriteKeyOnly || el.dataset.s;
  popKey=s; popVariant = spriteKeyOnly ? null : el.dataset.v;
  popCell = spriteKeyOnly ? null : el;
  const r=ROWMAP[s], info=INFO[s]||{};
  const rar=(info.rarity||"Unknown").split(" ")[0];
  const firstFile = popVariant ? r.cells[popVariant] : (r.cells[V.find(v=>r.cells[v])]);
  document.getElementById("pImgI").src = firstFile||"";
  document.getElementById("pFx").className = "fx" + (popVariant ? " fx-"+popVariant : "");
  document.getElementById("pImg").style.setProperty("--cc", popVariant?VC[popVariant]:"#3aa8ff");
  document.getElementById("pName").textContent = info.name || r.name;
  document.getElementById("pSub").textContent = [popVariant?popVariant+" variant":"", info.element||""].filter(Boolean).join(" · ");
  const rEl=document.getElementById("pRar"); rEl.textContent=rar; rEl.className="rar r-"+rar;
  document.getElementById("pDesc").textContent = info.desc || "No description available.";
  const meta=[];
  if(info.howToGet && info.howToGet!=="Unknown") meta.push(`How to get: <span>${info.howToGet}</span>`);
  if(info.chapter) meta.push(`Introduced: <span>${info.chapter}</span>`);
  document.getElementById("pMeta").innerHTML = meta.join("<br>");

  pop.classList.add("show");
  positionPop(pop, el);
  syncPopButtons();
}
function positionPop(popEl, el){
  const rect=el.getBoundingClientRect();
  const pw=popEl.offsetWidth, ph=popEl.offsetHeight;
  let left=rect.left-pw-12, top=rect.top;
  if(left<10) left=rect.right+12;
  if(left+pw>window.innerWidth-10) left=Math.max(10,(window.innerWidth-pw)/2);
  if(top+ph>window.innerHeight-10) top=window.innerHeight-ph-10;
  if(top<10) top=10;
  popEl.style.left=left+"px"; popEl.style.top=top+"px";
}
function hidePop(){ pop.classList.remove("show"); popCell=null; popKey=null; popVariant=null; }
function syncPopButtons(){
  const actions=pop.querySelector(".pactions");
  const cur = popVariant ? st(popKey,popVariant) : null;
  actions.style.display = popVariant ? "grid" : "none";
  pop.querySelector(".phint").style.display = popVariant ? "block":"none";
  document.getElementById("pOwn").classList.toggle("on",cur==="own");
  document.getElementById("pMaster").classList.toggle("on",cur==="master");
  document.getElementById("pLost").classList.toggle("on",cur==="lost");
}
function setStateFromPop(val){
  if(!popVariant) return;
  const cur=st(popKey,popVariant);
  setState(popKey,popVariant, cur===val ? null : val);
}
pop.addEventListener("mouseenter",()=>{overPop=true; clearTimeout(popTimer);});
pop.addEventListener("mouseleave",()=>{overPop=false; hidePop();});
window.addEventListener("scroll",()=>{ if(pop.classList.contains("show")) hidePop(); }, true);

/* ---------- variant effect popup ---------- */
const vpop=document.getElementById("vpop");
let vTimer=null, overVpop=false;
function scheduleVar(th){ clearTimeout(vTimer); vTimer=setTimeout(()=>showVarPop(th), 300); }
function clearVarSchedule(){ clearTimeout(vTimer); vTimer=setTimeout(()=>{ if(!overVpop) hideVarPop(); }, 160); }
function showVarPop(th){
  const v=th.dataset.v, vi=VINFO[v]||{t:v,d:""};
  const sample = (ROWS.find(r=>r.cells[v])||{cells:{}}).cells[v] || "";
  document.getElementById("vImg").src = sample;
  document.getElementById("vFx").className = "fx fx-"+v;
  document.getElementById("vSample").style.background =
    `radial-gradient(120% 120% at 50% 20%, ${VC[v]}33, #0b1030 72%)`;
  document.getElementById("vName").textContent = vi.t+" variant";
  document.getElementById("vDesc").textContent = vi.d;
  vpop.classList.add("show");
  positionPop(vpop, th);
}
function hideVarPop(){ vpop.classList.remove("show"); }
vpop.addEventListener("mouseenter",()=>{overVpop=true; clearTimeout(vTimer);});
vpop.addEventListener("mouseleave",()=>{overVpop=false; hideVarPop();});
window.addEventListener("scroll",()=>{ if(vpop.classList.contains("show")) hideVarPop(); }, true);

/* ---------- Export Image ---------- */
const RARITY_DOT = {Rare:"#3aa8ff", Epic:"#b06bff", Legendary:"#ffb300", Mythic:"#ff5c6c", Unknown:"#8b97cf"};
async function exportImage(){
  const btn=document.getElementById("exportBtn");
  const oldTxt=btn.innerHTML; btn.innerHTML="&#8987; Rendering&hellip;"; btn.disabled=true;
  try{
    if(typeof html2canvas==="undefined"){ toast("⚠️ Image library failed to load — check your connection"); return; }

    let coll=0, tot=0;
    const rowsHtml = ROWS.map(r=>{
      const info=INFO[r.key]||{}; const rar=(info.rarity||"Unknown").split(" ")[0];
      let cellsHtml="";
      for(const v of V){
        const file=r.cells[v];
        if(!file){ cellsHtml += `<div class="xcell xna"></div>`; continue; }
        tot++;
        const s=st(r.key,v);
        if(s==="master"){ coll++; cellsHtml+=`<div class="xcell xown" style="--cc:${VC[v]}"><img src="${file}"><span class="xcrown">&#128081;</span></div>`; }
        else if(s==="own"||s==="lost"){ coll++; cellsHtml+=`<div class="xcell xown" style="--cc:${VC[v]}"><img src="${file}"></div>`; }
        else { cellsHtml+=`<div class="xcell xmissing"><img src="${file}"></div>`; }
      }
      return `<div class="xrow"><div class="xname"><span class="xdot" style="background:${RARITY_DOT[rar]||RARITY_DOT.Unknown}"></span>${r.name.toUpperCase()}</div><div class="xcells">${cellsHtml}</div></div>`;
    }).join("");
    const pct = tot? Math.round(coll/tot*100):0;

    const root=document.createElement("div");
    root.style.cssText="position:fixed;left:-99999px;top:0;";
    root.innerHTML = `<div class="xcard" id="xcardInner">
      <div class="xeyebrow">Fortnite Collection Tracker</div>
      <div class="xtitle">SPRITE T3CH</div>
      <div class="xsub">Every Fortnite sprite &amp; variant &mdash; collected vs. missing</div>
      <div class="xbarwrap"><div class="xbar" style="width:${pct}%"></div></div>
      <div class="xcount">${coll} / ${tot} &middot; ${pct}%</div>
      <div class="xhead"><div class="xnamecol"></div><div class="xheadcells">${V.map(v=>`<div>${v}</div>`).join("")}</div></div>
      ${rowsHtml}
      <div class="xfoot">${SITE_URL.replace(/^https?:\/\//,"").replace(/\/$/,"")}</div>
    </div>`;
    document.body.appendChild(root);
    await new Promise(res=>setTimeout(res, 120));

    const canvas = await html2canvas(root.firstElementChild, {backgroundColor:null, scale:2, useCORS:true});
    root.remove();

    const a=document.createElement("a");
    a.download = "sprite-t3ch-collection.png";
    a.href = canvas.toDataURL("image/png");
    document.body.appendChild(a); a.click(); a.remove();
    toast("✅ Image downloaded!");
  }catch(e){
    toast("⚠️ Couldn't render the image — try again");
  }finally{
    btn.innerHTML=oldTxt; btn.disabled=false;
  }
}
window.exportImage = exportImage;

/* ---------- Copy for Discord ---------- */
function discordText(){
  const pad = Math.max(...ROWS.map(r=>r.name.length)) + 1;
  const L=[];
  L.push("|"+V.map(v=>v.toUpperCase()).join("|"));
  L.push("✅Have");
  L.push("👑Mastered");
  L.push("👻Lost — needs re-summon");
  L.push("❌Need");
  L.push("-".repeat(27));
  let coll=0, tot=0;
  for(const r of ROWS){
    let cells="";
    for(const v of V){
      if(!r.cells[v]){ cells+="|  "; continue; }
      tot++;
      const s=st(r.key,v);
      if(s==="master"){ cells+="|👑"; coll++; }
      else if(s==="own"){ cells+="|✅"; coll++; }
      else if(s==="lost"){ cells+="|👻"; }
      else { cells+="|❌"; }
    }
    L.push(r.name.padEnd(pad)+cells+"|");
  }
  L.push("");
  L.push(coll+"/"+tot+" collected");
  L.push("Track yours: "+SITE_URL);
  return "```\n"+L.join("\n")+"\n```";
}
function copyDiscord(){
  const txt=discordText();
  const done=ok=>toast(ok?"✅ Copied — paste into Discord!":"Copied to a text box below — select & copy");
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(()=>done(true)).catch(()=>fallbackCopy(txt,done));
  } else fallbackCopy(txt,done);
}
function fallbackCopy(txt,done){
  const ta=document.createElement("textarea");
  ta.value=txt; ta.style.cssText="position:fixed;top:20px;left:20px;width:60%;height:60%;z-index:999";
  document.body.appendChild(ta); ta.focus(); ta.select();
  let ok=false; try{ ok=document.execCommand("copy"); }catch(e){}
  if(ok){ ta.remove(); done(true); } else { done(false); setTimeout(()=>ta.remove(),8000); }
}
let toastT=null;
function toast(msg){
  const el=document.getElementById("toast");
  el.textContent=msg; el.style.pointerEvents="none"; el.classList.add("show");
  clearTimeout(toastT); toastT=setTimeout(()=>el.classList.remove("show"),2600);
}
function toastUndo(msg, undo){
  const el=document.getElementById("toast");
  el.innerHTML = msg + " &nbsp;<u class='undo'>Undo</u>";
  el.style.pointerEvents="auto"; el.classList.add("show");
  el.querySelector(".undo").onclick=()=>{ undo(); el.classList.remove("show"); };
  clearTimeout(toastT); toastT=setTimeout(()=>{el.classList.remove("show"); el.style.pointerEvents="none";},6000);
}

build();
initSync();
</script>
</body>
</html>'''

HTML = HTML.replace("__DATA__", DATA).replace("__INFO__", INFO)
open("index.html","w").write(HTML)
print("wrote index.html", len(HTML), "bytes; info keys:", len(json.loads(INFO)))
