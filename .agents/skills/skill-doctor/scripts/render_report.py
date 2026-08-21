#!/usr/bin/env python3
"""Render a skill-doctor report.json into a shareable card and full report.

Outputs (next to report.json):
  card.html   - 1200x675 share card
  card.png    - screenshot of the card (if a Chromium-based browser is found)
  report.html - full report with per-skill breakdown and suggestions

Python 3.9+, stdlib only. Uses system fonts so the card renders identically
in old and new headless Chrome.
"""

import base64
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

GRADES = [
    (0.97, "A+"), (0.93, "A"), (0.90, "A-"),
    (0.87, "B+"), (0.83, "B"), (0.80, "B-"),
    (0.77, "C+"), (0.73, "C"), (0.70, "C-"),
    (0.60, "D"), (0.0, "F"),
]

MAC_BROWSERS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
PATH_BROWSERS = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"]
DIFFS_BUNDLE_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "pierre-diffs.js"
)


def grade_for(score: float) -> str:
    for threshold, letter in GRADES:
        if score >= threshold:
            return letter
    return "F"


def pct(score) -> int:
    return round(float(score) * 100)


def esc(v) -> str:
    value = v if v is not None else ""
    return html.escape(str(value))

def render_diff(diff_text: str, proposed_path: str = "") -> str:
    if not diff_text:
        return ""
    encoded = base64.b64encode(diff_text.encode("utf-8")).decode("ascii")
    filename = Path(proposed_path).name if proposed_path else "SKILL.md"
    return (
        f'<div class="diff-view" data-pierre-diff data-diff="{encoded}" '
        f'data-filename="{esc(filename)}">'
        f'<pre class="diff-fallback">{esc(diff_text)}</pre></div>'
    )


def embedded_diffs_script() -> str:
    if not DIFFS_BUNDLE_PATH.exists():
        raise RuntimeError(
            f"@pierre/diffs bundle missing: {DIFFS_BUNDLE_PATH}; "
            "restore it from warpdotdev/skill-doctor, which builds the bundle "
            "with `pnpm build:diffs`"
        )
    bundle = DIFFS_BUNDLE_PATH.read_text()
    return re.sub(r"</script", r"<\\/script", bundle, flags=re.IGNORECASE)


# Inlined from ../assets/warp-pixel-icon.svg so the rendered HTML is
# self-contained (headless-Chrome screenshots load no external files).
WARP_MARK = (
    '<svg class="mark" viewBox="0 0 37 35" fill="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M5.3135 2L30.9247 2.00011L30.9208 3.79847L32.5185 3.79657L32.5145 5.43448L34.2294 5.44055L34.2286 28.6954H32.5239C32.507 29.1933 32.5153 29.7328 32.5106 30.2357L30.9319 30.2411C30.9297 30.4979 30.9757 31.7709 30.8834 31.8934C28.193 31.9264 25.4541 31.9005 22.7582 31.9013H5.30484L5.30653 30.2425L3.72927 30.2364L3.73053 28.6969L2 28.6933L2.0009 5.43272C2.57577 5.43872 3.15074 5.4375 3.72561 5.42899L3.73161 3.79621L5.30915 3.79222L5.3135 2Z" fill="white"/>'
    '<path d="M32.5146 5.43457L32.5186 3.79688L30.9209 3.79883L30.9248 2H5.31348L5.30957 3.79199L3.73145 3.7959L3.72559 5.42871C3.15075 5.43722 2.57581 5.43861 2.00098 5.43262L2 28.6934L3.73047 28.6973L3.72949 30.2363L5.30664 30.2422L5.30469 31.9014H22.7578C24.7798 31.9008 26.8265 31.9149 28.8584 31.9082L30.8838 31.8936C30.976 31.7707 30.9295 30.4984 30.9316 30.2412L32.5107 30.2354C32.5154 29.7326 32.5066 29.1931 32.5234 28.6953H34.2285L34.2295 5.44043L32.5146 5.43457ZM36.2285 30.6953H34.5068L34.4922 32.2285L32.8643 32.2334C32.8528 32.2884 32.8385 32.3523 32.8184 32.4209C32.7937 32.5048 32.7066 32.7965 32.4805 33.0967L31.8896 33.8809L30.9082 33.8936C28.2026 33.9268 25.4275 33.9007 22.7588 33.9014H3.30273L3.30371 32.2344L1.72754 32.2285L1.72949 30.6924L0 30.6895L0.000976562 3.41211L1.7334 3.42969L1.73926 1.80078L3.31348 1.79785L3.31836 0H32.9287L32.9248 1.79688L34.5234 1.79395L34.5186 3.44043L36.2295 3.44727L36.2285 30.6953Z" fill="black"/>'
    '<path d="M29.3721 5.42529C29.889 5.44429 30.4337 5.42268 30.96 5.43213L30.9551 7.04248C31.4775 7.03408 32.01 7.03929 32.5332 7.03857C32.4937 9.42093 32.5257 11.8903 32.5254 14.2798L32.5273 27.1108L30.9609 27.1089L30.959 28.7026L29.375 28.6987C29.3772 29.13 29.3813 29.5667 29.373 29.9976C29.3705 30.1337 29.3832 30.1651 29.3057 30.2358L6.91699 30.2378C6.89889 29.7353 6.91168 29.2118 6.91699 28.7075C6.3669 28.7025 5.8167 28.7025 5.2666 28.7075L5.26465 27.1099L3.68457 27.1089L3.68652 7.04639C4.2055 7.03529 4.7404 7.03916 5.26074 7.03564L5.2666 5.43018C5.80821 5.42385 6.35003 5.42572 6.8916 5.43506C6.88988 4.88796 6.892 4.34052 6.89746 3.79346H29.3711L29.3721 5.42529ZM9.33887 10.6978C9.18647 10.9765 9.21901 11.161 9.22461 11.4819C9.07998 11.4801 8.94005 11.4569 8.8291 11.5347C8.80072 11.622 8.80582 11.6213 8.81152 11.7144C8.68917 11.8074 8.60774 11.7932 8.44434 11.7866C8.36301 11.8515 8.30578 11.9057 8.30176 12.0259C8.28478 12.536 8.29109 13.0721 8.29102 13.5825L8.29297 21.5659C8.29326 22.3844 8.28546 23.2155 8.30371 24.0337C8.30778 24.2156 8.35142 24.2999 8.43848 24.4575C8.64083 24.5041 8.98427 24.4882 9.2041 24.4878C9.19663 24.7586 9.20523 25.128 9.30859 25.3823C9.48375 25.4631 17.0821 25.4211 17.8965 25.4204C17.9026 25.0264 17.915 24.6167 17.9082 24.2241H16.7715C15.5491 24.2241 14.2971 24.2119 13.0771 24.228C13.0791 24.0268 13.0716 23.637 13.1133 23.4565C13.2509 23.3435 13.2926 23.4911 13.3193 23.3413C13.3427 23.2103 13.2843 23.1435 13.3555 23.0181L13.501 22.9917C13.5902 22.8227 13.538 22.0611 13.5391 21.8169L13.9902 21.813C13.989 21.1612 13.9793 20.4819 13.9971 19.8325L14.5029 19.8267C14.5003 19.1758 14.5017 18.5244 14.5068 17.8735L14.9639 17.8696C14.9614 17.3226 14.861 16.4429 15.1162 16.0063C15.2178 15.9719 15.2439 15.9747 15.3477 15.9692C15.4618 15.8341 15.4034 14.2978 15.4043 14.0024L15.9121 14.0005C15.9243 13.3773 15.9407 12.7118 15.9258 12.0903L16.3555 12.0786L16.3506 10.6968C14.0515 10.6966 11.6291 10.6614 9.33887 10.6978ZM18.3584 8.38721C18.3588 8.86591 18.3663 9.36324 18.3584 9.84033L17.9102 9.84229L17.9043 11.48L17.375 11.478L17.374 14.0005L16.8447 14.0015L16.8418 15.9761L16.3652 15.981C16.3592 16.2914 16.413 17.4264 16.3115 17.5913C16.2316 17.6037 16.1517 17.6171 16.0723 17.6323C16.0557 17.7205 16.0531 17.753 16.0479 17.8394C15.9931 17.8723 15.9824 17.8775 15.9229 17.8999C15.8611 18.2051 15.899 19.4273 15.8906 19.8267L15.415 19.8335C15.4087 20.1999 15.4041 21.3175 15.3438 21.604C15.1385 21.7756 14.9409 21.8339 14.9404 22.0278C14.9396 22.3503 14.9419 22.6858 14.9414 23.0083L26.9736 23.0093C26.9722 22.6145 27.0284 22.4491 27.1084 22.0679C27.2287 21.9942 27.4175 22.067 27.4541 22.0269C27.6718 21.7854 27.5123 21.8049 27.9785 21.8228L27.9805 13.7983C27.9805 12.5388 28.0332 10.7775 27.96 9.54639C27.8386 9.54865 27.6757 9.56604 27.5723 9.51611C27.5224 9.2171 27.4479 9.21398 27.1523 9.16064C26.9526 8.99617 26.9654 8.6242 26.9736 8.38623L18.3584 8.38721Z" fill="black"/>'
    "</svg>"
)


def find_chrome():
    import os
    override = os.environ.get("CHROME_PATH")
    if override and Path(override).exists():
        return override
    for p in MAC_BROWSERS:
        if Path(p).exists():
            return p
    for name in PATH_BROWSERS:
        found = shutil.which(name)
        if found:
            return found
    return None


# Design tokens lifted from warp.dev/factories (factories-landing.css):
# white ground with a dot grid, Matter-Mono-ish monospace, #2a1eff accent,
# hairline rgba(13,10,61) rules, square corners, lowercase labels,
# uppercase wide-tracked meta bars.
CARD_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1200px; height: 675px; overflow: hidden; }
body {
  --fg: #1a1522; --muted: #5d5966; --muted-2: #918d9a;
  --accent: #2a1eff; --accent-2: #7267ff; --ok: #3f6b3f;
  --line: rgba(13, 10, 61, 0.16); --line-soft: rgba(13, 10, 61, 0.07);
  --bg: #ffffff; --bg-panel: #f6f5fb; --yellow: #eef17c;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background:
    radial-gradient(circle at 1px 1px, var(--line-soft) 1px, transparent 0) 0 0 / 22px 22px,
    var(--bg);
  color: var(--fg); padding: 40px 48px; font-size: 13px; line-height: 1.65;
}
::selection { background: #2a1eff; color: #fff; }
.fig { height: 100%; display: flex; flex-direction: column; border: 1px solid var(--line); background: var(--bg); }
.fig-bar {
  display: flex; justify-content: space-between; align-items: center; gap: 14px;
  padding: 10px 16px; border-bottom: 1px solid var(--line);
  font-size: 11px; color: var(--muted-2); letter-spacing: 0.1em; text-transform: uppercase;
}
.fig-bar .rule { flex: 1; height: 1px; background: var(--line); }
.fig-bar .icon { border: 1px solid var(--line); padding: 1px 6px; }
.fig-body {
  flex: 1; display: flex; flex-direction: column; padding: 30px 36px 0;
  background-image: radial-gradient(circle at 1px 1px, var(--line-soft) 1.2px, transparent 0);
  background-size: 26px 26px;
}
.title { font-size: 34px; font-weight: 500; letter-spacing: -2px; }
.main { display: flex; align-items: center; gap: 56px; flex: 1; }
.grade-wrap { text-align: center; flex: none; }
.grade { font-size: 170px; font-weight: 600; line-height: 1; letter-spacing: -8px; color: var(--accent); }
.grade-label { font-size: 11px; color: var(--muted-2); margin-top: 8px; text-transform: uppercase; letter-spacing: 0.14em; }
.bars { flex: 1; display: flex; flex-direction: column; gap: 28px; }
.bar-row .bar-head { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; font-weight: 500; }
.bar-name { color: var(--fg); text-transform: lowercase; }
.bar-val { color: var(--fg); font-weight: 600; font-variant-numeric: tabular-nums; }
.bar-track { height: 8px; background: var(--line-soft); box-shadow: inset 0 0 0 1px var(--line); }
.bar-fill { height: 100%; background: var(--accent); }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--line); border-bottom: none; background: var(--bg-panel); }
.stat { padding: 18px 24px 16px; border-left: 1px solid var(--line); }
.stat:first-child { border-left: none; }
.stat .num { font-size: 40px; font-weight: 600; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.stat .lbl { font-size: 12px; color: var(--muted); margin-top: 2px; text-transform: lowercase; }
.footer {
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px solid var(--line); padding: 14px 16px; background: var(--bg);
}
.stamp { display: flex; align-items: center; gap: 11px; }
.stamp .mark { width: 27px; height: 26px; flex: none; display: block; }
.stamp-name { font-size: 15px; font-weight: 600; letter-spacing: -0.03em; text-transform: lowercase; }
.stamp-sub { font-size: 11px; color: var(--muted-2); text-transform: lowercase; letter-spacing: 0.02em; }
.cta { font-size: 13px; font-weight: 600; color: var(--fg); background: var(--yellow); border: 1px solid var(--fg); padding: 8px 14px; text-transform: lowercase; }
.cta b { color: var(--accent); }
"""


def render_card(r) -> str:
    scores = r["scores"]
    stats = r["stats"]
    grade = r.get("grade") or grade_for(scores["overall"])
    bars = "".join(
        f"""<div class="bar-row"><div class="bar-head"><span class="bar-name">{esc(name)}</span>
        <span class="bar-val">{pct(val)}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:{pct(val)}%"></div></div></div>"""
        for name, val in [
            ("Efficiency", scores.get("efficiency", 0)),
            ("Code Quality", scores.get("code_quality", 0)),
            ("Skill Coverage", scores.get("skill_coverage", 0)),
        ]
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CARD_CSS}</style></head><body>
<div class="fig">
  <div class="fig-bar"><span>{esc(r.get('handle') or 'agent skill report')}</span><span class="rule"></span>
    <span>{esc(stats.get('sessions_scanned', 0))} conversations found &middot; last {esc(stats.get('window_days', 45))} days</span>
    <span class="icon">{esc(r.get('harness', 'codex'))}</span></div>
  <div class="fig-body">
    <div class="title">{esc(r.get('title', 'Agent Skill Report'))}</div>
    <div class="main">
      <div class="grade-wrap"><div class="grade">{esc(grade)}</div><div class="grade-label">overall</div></div>
      <div class="bars">{bars}</div>
    </div>
  </div>
  <div class="stats">
    <div class="stat"><div class="num">{esc(stats.get('sessions_analyzed', 0))}</div><div class="lbl">conversations scored</div></div>
    <div class="stat"><div class="num">{esc(stats.get('skills_found', 0))}</div><div class="lbl">skills installed</div></div>
    <div class="stat"><div class="num">{esc(stats.get('skills_used', 0))}</div><div class="lbl">skills used</div></div>
  </div>
  <div class="footer">
    <div class="stamp">{WARP_MARK}<div>
      <div class="stamp-name">warp factories</div>
      <div class="stamp-sub">scored by /skill-doctor</div>
    </div></div>
    <div class="cta">{esc(r.get('cta_label', 'automate this \u2192 warp.dev/factories/request-access'))}</div>
  </div>
</div>
</body></html>"""


def render_full(r) -> str:
    scores = r["scores"]
    grade = r.get("grade") or grade_for(scores["overall"])
    skill_rows = "".join(
        f"""<tr><td><code>{esc(s.get('name'))}</code></td><td>{esc(s.get('sessions', 0))}</td>
        <td>{pct(s['efficiency']) if s.get('efficiency') is not None else '—'}</td>
        <td>{pct(s['code_quality']) if s.get('code_quality') is not None else '—'}</td>
        <td>{esc(s.get('note', ''))}</td></tr>"""
        for s in r.get("per_skill", [])
    ) or "<tr><td colspan=5>No skills detected in any scored session.</td></tr>"
    findings = "".join(
        f"<li>{esc(finding)}</li>" for finding in r.get("top_findings", [])
    )

    suggestions = "".join(
        f"""<li><b><code>{esc(s.get('skill'))}</code></b> — {esc(s.get('change'))}
        {('<div class="muted">Evidence: ' + esc(s['evidence']) + '</div>') if s.get('evidence') else ''}
        {render_diff(s.get('diff', ''), s.get('proposed_path', ''))}</li>"""
        for s in r.get("suggestions", [])
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{esc(r.get('title', 'Agent Skill Report'))}</title><style>
body {{
  --fg: #1a1522; --muted: #5d5966; --muted-2: #918d9a; --accent: #2a1eff;
  --ok: #3f6b3f; --err: #b23a2f;
  --line: rgba(13, 10, 61, 0.16); --line-soft: rgba(13, 10, 61, 0.07); --bg-panel: #f6f5fb;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  background: radial-gradient(circle at 1px 1px, var(--line-soft) 1px, transparent 0) 0 0 / 22px 22px, #fff;
  color: var(--fg); max-width: 900px; margin: 0 auto; padding: 48px 24px; line-height: 1.65; font-size: 13px; }}
::selection {{ background: var(--accent); color: #fff; }}
h1 {{ font-weight: 500; letter-spacing: -2px; font-size: 34px; margin: 4px 0 0; }}
h2 {{ font-weight: 500; letter-spacing: -1px; font-size: 20px; margin: 40px 0 8px; }}
.tag {{ font-size: 11px; color: var(--accent); text-transform: lowercase; }}
.tag::before {{ content: "# "; }}
.grade {{ font-size: 64px; font-weight: 600; color: var(--accent); letter-spacing: -3px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 12px; border: 1px solid var(--line); background: #fff; }}
th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line-soft); font-size: 12.5px; vertical-align: top; }}
th {{ color: var(--muted-2); text-transform: uppercase; font-size: 10px; letter-spacing: 0.1em; border-bottom: 1px solid var(--line); }}
code {{ background: var(--bg-panel); border: 1px solid var(--line-soft); padding: 1px 5px; }}
li {{ margin-bottom: 10px; }}
p {{ color: var(--muted); font-weight: 500; }}
a {{ color: var(--accent); }}
.muted {{ color: var(--muted-2); font-size: 12px; }}
.diff-view {{ display: grid; gap: 10px; max-width: 100%; margin: 10px 0 4px; }}
.diff-view > * {{ min-width: 0; }}
.diff-fallback {{ background: var(--bg-panel); border: 1px solid var(--line); padding: 13px 16px;
  color: var(--muted); font-size: 12px; line-height: 1.7; overflow-x: auto; margin: 0;
  white-space: pre; }}
.stamp {{ display: flex; align-items: center; gap: 11px; }}
.stamp .mark {{ width: 27px; height: 26px; flex: none; display: block; }}
.stamp-name {{ font-size: 15px; font-weight: 600; letter-spacing: -0.03em; text-transform: lowercase; }}
.stamp-sub {{ font-size: 11px; color: var(--muted-2); text-transform: lowercase; letter-spacing: 0.02em; }}
.stamp-row {{ border: 1px solid var(--line); background: #fff; padding: 12px 16px; margin-bottom: 20px; }}
</style></head><body>
<div class="stamp stamp-row">{WARP_MARK}<div>
  <div class="stamp-name">warp factories</div>
  <div class="stamp-sub">scored by /skill-doctor</div>
</div></div>
<div class="tag">skill-doctor</div>
<h1>{esc(r.get('title', 'Agent Skill Report'))}</h1>
<p class="muted">Generated {esc(r.get('generated_at', ''))} &middot; harness: {esc(r.get('harness', 'codex'))} &middot; all analysis ran locally</p>
<div class="grade">{esc(grade)}</div>
<p>Overall {pct(scores['overall'])} &middot; Efficiency {pct(scores.get('efficiency', 0))} &middot; Code Quality {pct(scores.get('code_quality', 0))} &middot; Skill Coverage {pct(scores.get('skill_coverage', 0))}</p>
<h2>Findings</h2><ul>{findings}</ul>
<h2>Per-skill breakdown</h2>
<table><tr><th>Skill</th><th>Sessions</th><th>Efficiency</th><th>Code quality</th><th>Note</th></tr>{skill_rows}</table>
<h2>Suggested skill changes</h2><ol>{suggestions}</ol>
<h2>Do this automatically</h2>
<div class="stamp stamp-row">{WARP_MARK}<div>
  <div class="stamp-name">warp factories</div>
  <div class="stamp-sub">continuous scoring &middot; continuous skill tuning</div>
</div></div>
<p>This report is a one-shot version of the self-improvement loop in Warp's software factories, where scorers run
across every agent run and skills get tuned continuously. <a href="{esc(r.get('cta_url', 'https://warp.dev/factories/request-access'))}">Request early access to automate this &rarr;</a></p>
<script>{embedded_diffs_script()}</script>
</body></html>"""


def screenshot(chrome: str, html_path: Path, png_path: Path) -> bool:
    with tempfile.TemporaryDirectory() as profile:
        cmd = [
            chrome, "--headless", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
            f"--user-data-dir={profile}", "--force-device-scale-factor=2",
            "--window-size=1200,675", f"--screenshot={png_path}", html_path.resolve().as_uri(),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError):
            return False
    return res.returncode == 0 and png_path.exists()


def main():
    report_path = Path(sys.argv[1] if len(sys.argv) > 1 else "./skill-doctor-report/report.json").expanduser()
    if not report_path.exists():
        print(f"error: {report_path} not found", file=sys.stderr)
        sys.exit(1)
    r = json.loads(report_path.read_text())
    r.setdefault("grade", grade_for(r["scores"]["overall"]))
    out_dir = report_path.parent

    card_path = out_dir / "card.html"
    full_path = out_dir / "report.html"
    png_path = out_dir / "card.png"
    card_path.write_text(render_card(r))
    full_path.write_text(render_full(r))
    print(f"card:   {card_path}")
    print(f"report: {full_path}")

    chrome = find_chrome()
    if chrome and screenshot(chrome, card_path, png_path):
        print(f"png:    {png_path}  (1200x675 @2x — ready to share)")
    else:
        print("png:    no Chromium-based browser found — opening card.html; screenshot it at 1200x675")
        webbrowser.open(card_path.resolve().as_uri())


if __name__ == "__main__":
    main()
