"""Is Anyone There? - "The Room: You vs AI" game + Sensor lab for the room occupancy model.

Research/demo prototype. The UI only talks to the FastAPI service (API_URL); it never loads the model itself and
never changes the 16 input features or their order (the API owns that).
Visual assets live in ui_assets.py, texts in ui_text.py and the scoring rules in game_logic.py.
"""
import os
import random
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
import streamlit as st

from game_logic import outcome, streak, tally
from ui_assets import (CSS, FONTS, LIGHT, LOGO, RTL_CSS, SOUND, TEMP, evidence_panel, icon, ltr, pick_card,
                       room_scene, trend_of)
from ui_text import TXT

ROOT = Path(__file__).resolve().parent
CO2 = ["S5_CO2", "S5_CO2_Slope"]
PIR = ["S6_PIR", "S7_PIR"]
FEATURES = TEMP + LIGHT + SOUND + CO2 + PIR  # same 16 names the API expects (the API fixes the model's order)

# Decimals shown in the Sensor lab fields. Unedited fields still send the exact recorded value.
DECIMALS = {"Temp": 2, "Light": 0, "Sound": 2, "S5_CO2": 0, "S5_CO2_Slope": 2}

# Typical values per number of people (median per sensor from the project's EDA, rounded).
# (people, CO2 ppm, light lux, temperature C, sound V)
TYPICAL = [(0, 355, 0, 25.3, 0.07), (1, 440, 64, 25.8, 0.13), (2, 685, 95, 26.0, 0.35), (3, 870, 144, 26.2, 0.27)]
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]


# ----------------------------------------------------------------------------------------------------------------
# API access
# ----------------------------------------------------------------------------------------------------------------
def get_api_url() -> str:
    url = os.environ.get("API_URL")
    if not url:
        try:
            url = st.secrets["API_URL"]
        except Exception:  # no secrets file / key
            url = None
    return (url or "http://127.0.0.1:8000").rstrip("/")


API_URL = get_api_url()


def _session() -> requests.Session:
    s = requests.Session()
    if (urlparse(API_URL).hostname or "") in ("localhost", "127.0.0.1", "::1"):
        s.trust_env = False  # a system/corporate proxy must never intercept calls to the local API
    return s


@st.cache_data(ttl=10, show_spinner=False)
def api_online(url: str) -> bool:
    try:
        r = _session().get(f"{url}/health", timeout=8)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except (requests.exceptions.RequestException, ValueError):
        return False


def call_api(payload: dict, t: dict):
    """Returns (response, None) on success or (None, {"msg": friendly text, "detail": technical text})."""
    try:
        r = _session().post(f"{API_URL}/predict", json=payload, timeout=60)
    except requests.exceptions.ConnectionError as exc:
        return None, {"msg": t["e_conn"], "detail": f"ConnectionError: {exc.__class__.__name__}"}
    except requests.exceptions.Timeout:
        return None, {"msg": t["e_slow"], "detail": "Timeout after 60 s"}
    except requests.exceptions.RequestException as exc:
        return None, {"msg": t["e_conn"], "detail": exc.__class__.__name__}
    if r.status_code == 422:
        try:
            d = "; ".join(f"{x['field']}: {x['message']}" for x in r.json()["detail"])
        except Exception:
            d = r.text[:200]
        return None, {"msg": t["e_bad"].format(d=d), "detail": "HTTP 422"}
    if r.status_code != 200:
        return None, {"msg": t["e_http"], "detail": f"HTTP {r.status_code}"}
    try:
        data = r.json()
        _ = int(data["count"]), dict(data["probabilities"])
        return data, None
    except (ValueError, KeyError, TypeError):
        return None, {"msg": t["e_http"], "detail": "Unexpected response format"}


# ----------------------------------------------------------------------------------------------------------------
# Data helpers
# ----------------------------------------------------------------------------------------------------------------
@st.cache_data
def load_examples() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "examples.csv")


examples = load_examples()
by_id = examples.set_index("sample_id")
ids = list(examples["sample_id"])
count_options = sorted(int(c) for c in examples["actual_count"].unique())


def dec_for(name: str) -> int:
    if name in DECIMALS:
        return DECIMALS[name]
    return next(d for key, d in DECIMALS.items() if key in name)


def avg(readings, names) -> float:
    return sum(float(readings[n]) for n in names) / len(names)


def month_label(when: pd.Timestamp, lang: str) -> str:
    return when.strftime("%B %Y") if lang == "en" else f"{AR_MONTHS[when.month - 1]} {when.year}"


def source_label(source: str, lang: str) -> str:
    if lang == "en":
        return source
    return "ديسمبر 2017 (فترة التدريب)" if "December" in source else "يناير 2018 (فترة الاختبار)"


# ----------------------------------------------------------------------------------------------------------------
# HTML builders (single-line strings: no blank lines or indentation, so Markdown never turns them into code blocks)
# ----------------------------------------------------------------------------------------------------------------
def step_header(n: int, title: str) -> str:
    return f'<div class="step"><span class="n">{n}</span><span class="t">{title}</span></div>'


def scorebar(t: dict, hist: list, round_no: int, pop_you: bool, pop_ai: bool) -> str:
    sc, st_n = tally(hist), streak(hist)
    you_cls = "sb-pts pop" if pop_you else "sb-pts"
    ai_cls = "sb-pts pop" if pop_ai else "sb-pts"
    flame = f'<div class="streak{"" if st_n else " zero"}">{icon("flame", 14)}{t["streak"]} {st_n}</div>'
    return (f'<div class="scorebar"><div class="sb-side you"><span class="sb-who">{t["you"]}</span>'
            f'<span class="{you_cls}">{sc["you"]}</span></div>'
            f'<div class="sb-mid"><div class="sb-round">{t["round"]} {round_no}</div>{flame}</div>'
            f'<div class="sb-side ai"><span class="{ai_cls}">{sc["ai"]}</span><span class="sb-who">{t["ai"]}</span></div></div>')


def headline(eyebrow: str, title: str, sub: str, extra_cls: str = "") -> str:
    return (f'<div class="headline {extra_cls}"><div class="eyebrow">{eyebrow}</div><div class="ttl">{title}</div>'
            f'<div class="sub">{sub}</div></div>')


def details_table(r, t: dict) -> str:
    """This round's averages next to the typical value for 0, 1, 2 and 3 people (medians from the project data)."""
    rows = [(t["c_co2"], "ppm", float(r["S5_CO2"]), 1, "{:.0f}"),
            (t["c_light"], "lux", avg(r, LIGHT), 2, "{:.0f}"),
            (t["c_temp"], "°C", avg(r, TEMP), 3, "{:.1f}"),
            (t["c_sound"], "V", avg(r, SOUND), 4, "{:.2f}")]
    html = ""
    for name, unit, val, i, fmt in rows:
        closest = min(TYPICAL, key=lambda row: abs(row[i] - val))[0]
        chips = "".join(
            f'<div class="chip{" near" if row[0] == closest else ""}"><div class="cp">{icon("person", 12)}{row[0]}</div>'
            f'<div class="cv">{ltr(fmt.format(row[i]))}</div></div>' for row in TYPICAL)
        html += (f'<div class="cmp-row"><div class="cmp-h"><span>{name} <small>({unit})</small></span>'
                 f'<span class="cmp-v">{t["cmp_now"]}: <b>{ltr(fmt.format(val))}</b></span></div>'
                 f'<div class="chips">{chips}</div></div>')
    return f'<div class="cmp">{html}<div class="cmp-note">{t["cmp_note"]}</div></div>'


def versus(t: dict, guess: int, ai: int, truth: int) -> str:
    def card(label, val, ok, cls=""):
        mark = "" if ok is None else f'<span class="{"ok" if ok else "no"}">{icon("check" if ok else "cross", 20)}</span>'
        return f'<div class="vs-card {cls}"><div class="vl">{label}</div><div class="vv">{mark}{val}</div></div>'
    return ('<div class="versus">' + card(t["cmp_you"], t["people"](guess), guess == truth)
            + card(t["cmp_ai"], t["people"](ai), ai == truth) + card(t["cmp_truth"], t["people"](truth), None, "truth")
            + "</div>")


def prob_bars(probabilities: dict, predicted: int, t: dict) -> str:
    rows = ""
    for k in sorted(probabilities, key=int):
        p = min(max(float(probabilities[k]), 0.0), 1.0)
        top = " top" if int(k) == predicted else ""
        rows += (f'<div class="bar{top}"><span>{t["people"](int(k))}</span><div class="bt"><div class="bf" '
                 f'style="width:{p * 100:.1f}%"></div></div><span class="bp">{p:.1%}</span></div>')
    return f'<div class="bars">{rows}</div>'


def clue_cards(readings, t: dict) -> str:
    tr = trend_of(float(readings["S5_CO2_Slope"]))
    motion_n = int(round(float(readings["S6_PIR"]))) + int(round(float(readings["S7_PIR"])))

    def ref(v):
        return t["ref_empty"].format(v=ltr(v))

    cards = [
        ("temp", t["c_temp"], f'{avg(readings, TEMP):.1f}<small>°C</small>', "", t["h_temp"], ref("25.3 °C")),
        ("light", t["c_light"], f'{avg(readings, LIGHT):.0f}<small>lux</small>', "", t["h_light"], ref("0 lux")),
        ("sound", t["c_sound"], f'{avg(readings, SOUND):.2f}<small>V</small>', "", t["h_sound"], ref("0.07 V")),
        ("co2", t["c_co2"], f'{float(readings["S5_CO2"]):.0f}<small>ppm</small>', "",
         f'{t["h_co2"]}: <b>{t["trend"][tr]}</b>', ref("355 ppm")),
        ("motion", t["c_motion"], t["motion_val"][1 if motion_n else 0], " sm", f'{motion_n} {t["h_motion2"]}',
         t["ref_motion"]),
    ]
    html = "".join(
        f'<div class="clue"><div class="ch">{icon(ic, 20)}<span class="cn">{name}</span></div>'
        f'<div class="cv{cls}">{value}</div><div class="cd">{desc}</div><div class="cr">{rf}</div></div>'
        for ic, name, value, cls, desc, rf in cards)
    return f'<div class="clues">{html}</div>'


def help_table(t: dict) -> str:
    head = "".join(f"<th>{c}</th>" for c in t["help_cols"])
    body = "".join(
        f"<tr><td>{t['people'](n)}</td><td>{co2}</td><td>{light}</td><td>{temp:.1f}</td><td>{snd:.2f}</td></tr>"
        for n, co2, light, temp, snd in TYPICAL)
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_help(t: dict, key: str) -> None:
    with st.expander(t["help_title"], expanded=False, icon=":material/help:"):
        st.markdown(f'<div class="note">{t["help_intro"]}</div>', unsafe_allow_html=True)
        st.markdown(help_table(t), unsafe_allow_html=True)
        for rule in t["help_rules"]:
            st.markdown(f"- {rule}")


def error_box(err: dict, t: dict, retry_cb, key: str) -> None:
    with st.container(border=True):
        st.error(err["msg"], icon=":material/error:")
        st.button(t["retry"], icon=":material/refresh:", on_click=retry_cb, key=f"retry_{key}")
        with st.expander(t["tech"]):
            st.write(f'{t["api_label"]}: `{API_URL}`  \n{err["detail"]}')


# ----------------------------------------------------------------------------------------------------------------
# Game state and callbacks. Phases: "guess" -> "locked" -> "revealed".
# A round is added to history exactly once, inside reveal(), and only when the API answered.
# ----------------------------------------------------------------------------------------------------------------
def new_round() -> None:
    pool = [i for i in ids if i not in st.session_state.used]
    if not pool:
        st.session_state.used, pool = [], ids
    st.session_state.sample_id = random.choice(pool)
    st.session_state.used.append(st.session_state.sample_id)
    st.session_state.phase = "guess"
    st.session_state.sel = None
    st.session_state.result = None
    st.session_state.error = None


def choose(n: int) -> None:
    if st.session_state.phase == "guess":
        st.session_state.sel = n


def lock_guess() -> None:
    if st.session_state.phase == "guess" and st.session_state.sel is not None:
        st.session_state.phase = "locked"


def reveal() -> None:
    if st.session_state.phase != "locked":  # never score the same round twice
        return
    t = TXT[st.session_state.lang]
    row = by_id.loc[st.session_state.sample_id]
    response, error = call_api({n: float(row[n]) for n in FEATURES}, t)
    if error:  # no fake prediction, no points
        st.session_state.error = error
        return
    st.session_state.error = None
    rec = {"sid": st.session_state.sample_id, "guess": int(st.session_state.sel), "ai": int(response["count"]),
           "truth": int(row["actual_count"])}
    st.session_state.history.append(rec)
    st.session_state.result = {**rec, "probabilities": response["probabilities"], "animate": True}
    st.session_state.phase = "revealed"


def next_round() -> None:
    if st.session_state.phase == "revealed":
        new_round()


# ---------- Sensor lab state ----------
def load_lab_example(sid: str) -> None:
    """Put one recorded example into the lab: exact values are kept in lab_base, fields show rounded values."""
    row = by_id.loc[sid]
    st.session_state.lab_id = sid
    st.session_state.lab_base = {n: float(row[n]) for n in FEATURES}
    for n in FEATURES:
        if n in PIR:
            st.session_state[f"lab_{n}"] = bool(round(float(row[n])))
        else:
            st.session_state[f"lab_{n}"] = round(float(row[n]), dec_for(n))
    st.session_state.lab_result = None


def lab_another() -> None:
    flt = st.session_state.get("lab_filter")
    pool = [i for i in ids if i != st.session_state.get("lab_id")
            and (flt in (None, "any") or int(by_id.loc[i, "actual_count"]) == flt)]
    if pool:
        load_lab_example(random.choice(pool))


def lab_value(name: str) -> float:
    """Value that is sent to the API: the exact recorded value unless the user changed the field."""
    base = st.session_state.lab_base[name]
    shown = st.session_state[f"lab_{name}"]
    if name in PIR:
        return float(shown)
    if abs(float(shown) - round(base, dec_for(name))) < 1e-9:
        return base
    return float(shown)


def lab_payload() -> dict:
    return {n: lab_value(n) for n in FEATURES}


def lab_estimate() -> None:
    t = TXT[st.session_state.lang]
    payload = lab_payload()
    response, error = call_api(payload, t)
    st.session_state.lab_result = {"payload": payload, "response": response, "error": error}


if "lang" not in st.session_state:
    st.session_state.lang = "en"
    st.session_state.used = []
    st.session_state.history = []
    st.session_state.show_splash = True
    new_round()
    load_lab_example(random.choice(ids))

# ----------------------------------------------------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Is Anyone There?", page_icon=":material/sensor_door:", layout="wide")

splash_slot = st.empty()  # always created first so the layout never shifts
if st.session_state.pop("show_splash", False):  # shown once per session, never on later reruns
    splash_slot.markdown(
        FONTS + CSS + f'<div class="splash"><div class="si">{LOGO}<div class="st">Is Anyone There?</div>'
        f'<div class="sa">فيها أحد؟</div><div class="ss">{TXT["en"]["splash_sub"]}</div></div></div>',
        unsafe_allow_html=True)
else:
    splash_slot.empty()

lang = st.session_state.lang
t = TXT[lang]
st.markdown(FONTS + CSS + (RTL_CSS if lang == "ar" else ""), unsafe_allow_html=True)

online = api_online(API_URL)
top_l, top_r = st.columns([4, 1.4], vertical_alignment="center")
with top_l:
    st.markdown(f'<div class="brand">{LOGO}<span class="bn">{t["brand"]}</span>'
                f'<span class="status{"" if online else " off"}"><span class="dot"></span>'
                f'{t["ai_on"] if online else t["ai_off"]}</span></div>', unsafe_allow_html=True)
with top_r:
    choice = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True,
                      index=0 if lang == "en" else 1, label_visibility="collapsed")
    new_lang = "en" if choice == "English" else "ar"
    if new_lang != lang:
        st.session_state.lang = new_lang
        st.rerun()

if not online:
    with st.container(border=True):
        st.warning(f"**{t['off_title']}**  \n{t['off_msg']}", icon=":material/cloud_off:")
        st.button(t["retry"], icon=":material/refresh:", key="retry_global", on_click=api_online.clear)
        with st.expander(t["tech"]):
            st.write(f'{t["api_label"]}: `{API_URL}`')
            st.caption(t["how_to_start"])
            st.code("python -m uvicorn app.main:app", language="bash")

tab_play, tab_lab, tab_about = st.tabs([f":material/meeting_room: {t['tab_play']}",
                                        f":material/science: {t['tab_lab']}", f":material/info: {t['tab_about']}"])

# ---------- THE ROOM (game) ----------
with tab_play:
    phase = st.session_state.phase
    hist = st.session_state.history
    res = st.session_state.result
    animate = bool(res and res.get("animate"))
    round_no = len(hist) if phase == "revealed" else len(hist) + 1
    pop_you = animate and res["guess"] == res["truth"]
    pop_ai = animate and res["ai"] == res["truth"]
    st.markdown(scorebar(t, hist, round_no, pop_you, pop_ai), unsafe_allow_html=True)

    row = by_id.loc[st.session_state.sample_id]
    when = pd.to_datetime(row["datetime"])
    eyebrow = f'{t["round"]} {round_no} · {ltr(when.strftime("%Y-%m-%d %H:%M"))} · {month_label(when, lang)}'

    if phase == "revealed":
        kind = outcome(res["guess"], res["ai"], res["truth"])
        title, sub = t[f"h_{kind}"], t[f"s_{kind}"].format(c=t["people"](res["truth"]))
        head_cls = ("win " if kind in ("you", "both") else "") + ("anim" if animate else "")
    else:
        title, sub = (t["h_guess"], t["s_guess"]) if phase == "guess" else (t["h_locked"], t["s_locked"])
        head_cls = ""
    head_html = headline(eyebrow, title, sub, head_cls)
    ev_html = evidence_panel(row, t)

    scene_col, ev_col = st.columns([1.55, 1], gap="large")
    with scene_col:
        # on phones the right column drops below, so the headline and evidence are repeated here (mobile only)
        st.markdown(f'<div class="only-mobile">{head_html}</div>', unsafe_allow_html=True)
        if phase == "revealed":
            st.markdown(room_scene(True, res["truth"], animate=animate, celebrate=res["guess"] == res["truth"],
                                   caption=t["scene_note"]), unsafe_allow_html=True)
        else:
            st.markdown(room_scene(False, caption=t["scene_note"]), unsafe_allow_html=True)
        st.markdown(f'<div class="only-mobile">{ev_html}</div>', unsafe_allow_html=True)

        if phase in ("guess", "locked"):
            locked = phase == "locked"
            st.markdown(f'<div class="eyebrow pick-q">{t["pick_q"]}</div>', unsafe_allow_html=True)
            with st.container(key="pickrow"):
                for n, col in enumerate(st.columns(4)):
                    with col, st.container(key=f"pickc{n}"):
                        st.markdown(pick_card(n, t["card"](n), st.session_state.sel == n, locked),
                                    unsafe_allow_html=True)
                        st.button(t["people"](n), key=f"pickb{n}", on_click=choose, args=(n,), disabled=locked)
            if not locked:
                st.button(t["lock"], type="primary", icon=":material/lock:", on_click=lock_guess,
                          disabled=st.session_state.sel is None, key="lock_btn")
                if st.session_state.sel is None:
                    st.caption(t["lock_hint"])
            else:
                c_chip, c_btn = st.columns([1, 1], vertical_alignment="center")
                with c_chip:
                    st.markdown(f'<div class="locked-chip">{icon("lock", 18)}{t["locked_as"]}: '
                                f'<b>{st.session_state.sel}</b></div>', unsafe_allow_html=True)
                with c_btn:
                    st.button(t["open"], type="primary", icon=":material/door_open:", on_click=reveal, key="open_btn",
                              use_container_width=True)
                if st.session_state.error:
                    error_box(st.session_state.error, t, reveal, "play")
        else:
            st.markdown(versus(t, res["guess"], res["ai"], res["truth"]), unsafe_allow_html=True)
            st.button(t["next"], type="primary", icon=":material/arrow_forward:", on_click=next_round, key="next_btn",
                      use_container_width=True)
            with st.expander(t["prob_title"], icon=":material/bar_chart:"):
                st.markdown(prob_bars(res["probabilities"], res["ai"], t), unsafe_allow_html=True)
                st.caption(t["prob_note"])
            if animate:  # the reveal animation plays once; later reruns show the final state
                st.session_state.result["animate"] = False
    with ev_col:
        st.markdown(f'<div class="only-desktop">{head_html}{ev_html}</div>', unsafe_allow_html=True)
        with st.expander(t["details"], icon=":material/table_rows:"):
            st.markdown(details_table(row, t), unsafe_allow_html=True)

    st.markdown(f'<div class="foot">{t["foot"]}</div>', unsafe_allow_html=True)

# ---------- SENSOR LAB ----------
with tab_lab:
    st.markdown(f'<div class="intro"><b>{t["lab_intro_t"]}.</b> {t["lab_intro"]}</div>', unsafe_allow_html=True)

    st.markdown(step_header(1, t["s1"]), unsafe_allow_html=True)
    f1, f2 = st.columns([3, 2], vertical_alignment="bottom")
    with f1:
        st.segmented_control(t["filt"], ["any"] + count_options, default="any", key="lab_filter", on_change=lab_another,
                             format_func=lambda v: t["filt_any"] if v == "any" else t["people"](v))
    with f2:
        st.button(t["another"], icon=":material/shuffle:", on_click=lab_another, key="lab_another",
                  use_container_width=True)

    lab_row = by_id.loc[st.session_state.lab_id]
    lab_when = pd.to_datetime(lab_row["datetime"])
    truth_n = int(lab_row["actual_count"])
    st.markdown(
        f'<div class="tiles"><div class="tile"><div class="tn">'
        f'{t["ex_label"].format(n=ids.index(st.session_state.lab_id) + 1)}</div>'
        f'<div class="td">{source_label(lab_row["source"], lang)}<br>{ltr(lab_when.strftime("%Y-%m-%d %H:%M"))}</div></div>'
        f'<div class="tile"><div class="tn">{t["ex_rec"]}</div><div class="big">{t["people"](truth_n)}</div>'
        f'<div class="td">{t["ex_note"]}</div></div></div>', unsafe_allow_html=True)

    st.markdown(step_header(2, t["s2"]), unsafe_allow_html=True)
    current = lab_payload()
    st.markdown(clue_cards(current, t), unsafe_allow_html=True)
    st.write("")
    with st.expander(t["custom"], expanded=False, icon=":material/tune:"):
        st.caption(t["custom_hint"])
        for title, names, label, step, lo, hi in [
            (t["g_temp"], TEMP, t["l_temp"], 0.1, -50.0, 100.0),
            (t["g_light"], LIGHT, t["l_light"], 1.0, 0.0, None),
            (t["g_sound"], SOUND, t["l_sound"], 0.01, 0.0, None),
        ]:
            st.markdown(f"**{title}**")
            for i, (col, name) in enumerate(zip(st.columns(4), names), 1):
                with col:
                    st.number_input(label.format(i=i), key=f"lab_{name}", step=step, min_value=lo, max_value=hi,
                                    format=f"%.{dec_for(name)}f",
                                    help=t["help_sound"] if "Sound" in name and i == 1 else None)
        st.markdown(f"**{t['g_co2']}**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.number_input(t["l_co2"], key="lab_S5_CO2", step=1.0, min_value=0.0, max_value=100000.0, format="%.0f")
        with c2:
            st.number_input(t["l_slope"], key="lab_S5_CO2_Slope", step=0.05, format="%.2f", help=t["help_slope"])
        with c3:
            st.toggle(t["l_motion"].format(i=6), key="lab_S6_PIR", help=t["help_motion"])
        with c4:
            st.toggle(t["l_motion"].format(i=7), key="lab_S7_PIR", help=t["help_motion"])
        st.button(t["reset"], icon=":material/restart_alt:", on_click=load_lab_example,
                  args=(st.session_state.lab_id,), key="lab_reset")

    st.markdown(step_header(3, t["s3"]), unsafe_allow_html=True)
    st.button(t["estimate"], type="primary", icon=":material/insights:", on_click=lab_estimate, key="lab_ask")

    lab = st.session_state.lab_result
    if lab:
        st.markdown(step_header(4, t["s4"]), unsafe_allow_html=True)
        if lab["payload"] != current:  # readings changed: never show an old result as if it belonged to them
            st.markdown(f'<div class="stale">{t["stale"]}</div>', unsafe_allow_html=True)
        elif lab["error"]:
            error_box(lab["error"], t, lab_estimate, "lab")
        else:
            resp = lab["response"]
            pred = int(resp["count"])
            if current != st.session_state.lab_base:
                comp = t["est_edit_note"]
            else:
                comp = (f'{t["est_rec"]}: <b>{t["people"](truth_n)}</b><br>'
                        f'{t["est_match"] if pred == truth_n else t["est_diff"]}')
            st.markdown(f'<div class="result"><div class="rl">{t["est_title"]}</div>'
                        f'<div class="rv">{t["people"](pred)}</div><div class="rc">{comp}</div></div>',
                        unsafe_allow_html=True)
            st.write("")
            st.markdown(f'**{t["prob_title"]}**')
            st.markdown(prob_bars(resp["probabilities"], pred, t), unsafe_allow_html=True)
            st.caption(t["prob_note"])

    st.write("")
    render_help(t, "lab")

# ---------- ABOUT ----------
with tab_about:
    st.markdown(t["about"])
    render_help(t, "about")
