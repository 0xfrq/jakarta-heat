"""Local corrected workstream browser check; never certifies a consolidated release."""
import json
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd
from playwright.sync_api import sync_playwright

# Deterministic CPU WebGL for this local test process; avoids host GPU/driver variance.
BROWSER_ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"]

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/remediation/qa/dashboard"
OUT.mkdir(parents=True, exist_ok=True)
INPUTS = ROOT / "data/processed/remediation_inputs"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--integrated", action="store_true")
args = parser.parse_args()
env = {**os.environ, "JHIM_INPUT_DIR": str(INPUTS), "JHIM_RS_PATH": str(INPUTS / "remote_sensing_grid.csv"),
       "JHIM_DEMOGRAPHIC_SUPPORT": str(INPUTS / "demographic_support.csv"), "PYTHONIOENCODING": "utf-8"}
if args.integrated:
    INPUTS = ROOT / "data/processed"
    for key in list(env):
        if key.startswith("JHIM_"):
            del env[key]
expected = pd.read_csv(ROOT / ("data/processed/modeling/merged_grid.csv" if args.integrated else "data/processed/modeling_remediation/merged_grid.csv"))
expected_age = int(expected.qa_age_source_no_support.sum())
expected_valid = f"{int(expected.valid.sum()):,}"
support_text = f"Dukungan sumber usia tidak tersedia pada {expected_age} grid"
command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "dashboard/app.py"),
           "--server.headless=true", "--server.address=127.0.0.1", "--server.port=8543", "--browser.gatherUsageStats=false"]
result = {"scope": "Agent3 corrected local workstream only; final integrated candidate NOT YET TESTED", "command": command, "pages": []}
result["browser_args"] = BROWSER_ARGS
result["console"] = []
if args.integrated:
    OUT = ROOT / "outputs/qa/rc1/dashboard"
    OUT.mkdir(parents=True, exist_ok=True)
    result["scope"] = "RC1 consolidated canonical inputs; provisional scientific policy"
log = (OUT / "server.log").open("w", encoding="utf-8")
proc = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
try:
    for _ in range(60):
        try:
            if urlopen("http://127.0.0.1:8543/_stcore/health", timeout=1).status == 200:
                break
        except Exception:
            time.sleep(.5)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True, args=BROWSER_ARGS)
        result["browser_version"] = browser.version
        gpu = browser.new_browser_cdp_session().send("SystemInfo.getInfo").get("gpu", {})
        result["graphics"] = {"devices": gpu.get("devices"), "glRenderer": gpu.get("auxAttributes", {}).get("glRenderer")}
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: result["console"].append({"type": msg.type, "text": msg.text[:1000]}))

        def settle(sentinel=None, timeout=240):
            # A script run is finished when the status widget is gone AND the page text is stable; the
            # status widget alone can be hidden before a rerun starts, giving half-rendered screenshots.
            if sentinel:
                page.get_by_text(sentinel, exact=False).first.wait_for(timeout=timeout * 1000)
            last, stable, start = None, 0, time.time()
            while time.time() - start < timeout:
                running = page.locator('[data-testid="stStatusWidget"]').count() and \
                    page.locator('[data-testid="stStatusWidget"]').first.is_visible()
                text = page.locator("body").inner_text()
                stable = stable + 1 if (text == last and not running) else 0
                if stable >= 3:
                    return
                last = text
                page.wait_for_timeout(700)
            raise TimeoutError("page did not settle")

        def shot(path):
            # Streamlit scrolls inside stMain, so full_page alone captures only the viewport; grow the viewport.
            vp = page.viewport_size
            height = page.evaluate("""() => { const m = document.querySelector('[data-testid="stMain"]')
                || document.querySelector('section.main'); return m ? m.scrollHeight : document.body.scrollHeight; }""")
            page.set_viewport_size({"width": vp["width"], "height": int(min(max(height + 80, vp["height"]), 9000))})
            page.wait_for_timeout(800)
            page.screenshot(path=str(path), full_page=True)
            page.set_viewport_size(vp)

        def collapse_sidebar():
            if page.locator('[data-testid="stSidebar"][aria-expanded="true"]').count():
                button = page.locator('[data-testid="stSidebarCollapseButton"] button, '
                                      '[data-testid="stSidebarCollapseButton"]').first
                button.click(force=True)
                page.wait_for_timeout(900)

        def errors_now():
            return page.locator('[data-testid="stException"]').all_text_contents()

        # The last element of each view is the sentinel that proves the whole script rendered.
        sentinels = {"Ikhtisar": None, "Penjelajah data": "Tampilkan grid dengan bendera", "Panas dan vegetasi": None,
                     "Model prioritas": "Bobot eksploratif", "Perbandingan model": None,
                     "Statistik spasial": "Interpretasi.", "Robustness / sensitivitas": "Ambang",
                     "Metode dan keterbatasan": None}
        def fresh_browser():
            global browser, page
            browser.close()
            browser = pw.chromium.launch(channel="msedge", headless=True, args=BROWSER_ARGS)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda msg: result["console"].append({"type": msg.type, "text": msg.text[:1000]}))
            page.goto("http://127.0.0.1:8543", wait_until="domcontentloaded")
            page.locator("h1").first.wait_for(timeout=240000)

        page.goto("http://127.0.0.1:8543", wait_until="domcontentloaded")
        page.locator("h1").first.wait_for(timeout=240000)
        # Verify continuous navigation at an ordinary viewport before large captures.
        navigation = []
        result["continuous_navigation"] = navigation
        for name, sentinel in sentinels.items():
            page.get_by_role("link", name=name, exact=False).first.click()
            page.get_by_text(support_text, exact=False).first.wait_for(timeout=240000)
            settle(sentinel)
            navigation.append({"page": name, "exceptions": errors_now(), "canonical_count_visible": expected_valid in page.locator("body").inner_text()})
        result["continuous_navigation"] = navigation
        result["capture_policy"] = "Fresh browser per route for large desktop/narrow screenshots; ordinary continuous navigation tested separately"
        for i, (name, sentinel) in enumerate(sentinels.items()):
            fresh_browser()
            page.get_by_role("link", name=name, exact=False).first.click()
            page.locator("h1").first.wait_for(timeout=240000)
            page.get_by_text(support_text, exact=False).first.wait_for(timeout=240000)
            settle(sentinel)
            body = page.locator("body").inner_text()
            record = {"page": name, "heading": page.locator("h1").first.inner_text(), "exceptions": errors_now(),
                      "mixed_period_visible": "2026" in body and "2024" in body,
                      "corrected_n_visible": expected_valid in body, "canvas_count": page.locator("canvas").count()}
            shot(OUT / f"page_{i}_desktop.png")
            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(900)
            collapse_sidebar()
            shot(OUT / f"page_{i}_narrow.png")
            record["narrow_sidebar_collapsed"] = not page.locator('[data-testid="stSidebar"][aria-expanded="true"]').count()
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.wait_for_timeout(500)
            if page.locator('[data-testid="stSidebar"][aria-expanded="false"]').count():
                page.locator('[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button').first.click(force=True)
                page.wait_for_timeout(900)
            result["pages"].append(record)

        if args.integrated:
            fresh_browser()
            page.get_by_role("link", name="Model prioritas", exact=False).first.click()
            settle("Bobot eksploratif")
            with page.expect_download() as pending_download:
                page.get_by_role("button", name="Unduh CSV", exact=True).first.click()
            download = pending_download.value
            target = OUT / "baseline_m4_download.csv"
            download.save_as(target)
            downloaded = pd.read_csv(target).set_index("grid_id")
            saved = pd.read_csv(ROOT / "data/processed/modeling/priority_models.csv").set_index("grid_id")
            saved = saved.loc[saved.m4_top]
            assert set(downloaded.index) == set(saved.index)
            np.testing.assert_allclose(downloaded.loc[saved.index, "skor"], saved.m4_score, atol=1e-12, rtol=0)
            np.testing.assert_array_equal(downloaded.loc[saved.index, "peringkat"], saved.m4_rank)
            assert downloaded.scientific_policy.eq("provisional_unsigned").all()
            assert downloaded.reference_scope.eq("thermal_demography_2024_OSM_2026-11-19_candidate_proxy").all()
            result["baseline_download"] = {"result": "PASS", "rows": len(downloaded), "suggested_filename": download.suggested_filename,
                                           "checks": ["canonical top IDs", "scores", "ranks", "period/policy metadata"]}
        # Real interactions on the corrected candidate (sampled, not exhaustive).
        interactions = []

        def interact(label, action, expect=None, page_name=None):
            try:
                if page_name:
                    fresh_browser()
                    page.get_by_role("link", name=page_name, exact=False).first.click()
                    settle(sentinels.get(page_name))
                action()
                settle(expect)
                body = page.locator("body").inner_text()
                interactions.append({"interaction": label, "exceptions": errors_now(),
                                     "expected_text": expect, "expected_visible": (expect in body) if expect else None})
            except Exception as exc:  # recorded as failure, never silently passed
                interactions.append({"interaction": label, "error": repr(exc)})

        def choose(select_label, option):
            box = page.get_by_label(select_label, exact=False).first
            box.click()
            page.get_by_role("option", name=option, exact=True).first.click()

        interact("spatial: LISA alternative two-sided", lambda: choose("Alternatif LISA", "two-sided"),
                 "Interpretasi.", "Statistik spasial")
        interact("spatial: BY correction", lambda: page.get_by_text("BY konservatif", exact=False).first.click(), "Interpretasi.")
        shot(OUT / "interaction_spatial_two_sided_BY_desktop.png")
        interact("spatial: uncorrected p<0.05", lambda: page.get_by_text("p < 0,05 tanpa koreksi", exact=False).first.click(),
                 "Interpretasi.")
        interact("priority: exploratory custom weights", lambda: page.get_by_text("Bobot eksploratif", exact=False).first.click(),
                 "EKSPLORATIF", "Model prioritas")
        shot(OUT / "interaction_custom_weights_desktop.png")
        interact("sidebar: DEMO mode labelled", lambda: page.get_by_text("DEMO (data sintetis)", exact=False).first.click(),
                 "MODE DEMO")
        interact("sidebar: back to real data", lambda: page.get_by_text("Data asli", exact=True).first.click(),
                 support_text)
        result["interactions"] = interactions
        result["page_errors"] = errors
        browser.close()
except Exception as exc:
    result["verification_error"] = repr(exc)
    try:
        result["failure_body"] = page.locator("body").inner_text(timeout=5000)
        page.screenshot(path=str(OUT / "failure.png"), timeout=5000)
    except Exception as diagnostic_error:
        result["failure_diagnostic_error"] = repr(diagnostic_error)
finally:
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    log.close()
    (OUT / "browser_check.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
bad_interaction = any(r.get("error") or r.get("exceptions") or r.get("expected_visible") is False
                      for r in result.get("interactions", []))
if "verification_error" in result or result.get("page_errors") or bad_interaction or \
        len(result["pages"]) != 8 or any(p["exceptions"] or not p["corrected_n_visible"] or not p["mixed_period_visible"] for p in result["pages"]) or \
        len(result.get("continuous_navigation", [])) != 8 or any(p["exceptions"] or not p["canonical_count_visible"] for p in result.get("continuous_navigation", [])):
    sys.exit(1)
