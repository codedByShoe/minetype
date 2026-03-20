import tkinter as tk
from tkinter import font as tkfont
import random
import json
import math
import struct
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk as PILImageTk

# ── Sound ─────────────────────────────────────────────────────────────────────
try:
    import pygame.mixer
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    _SOUND_OK = True
except Exception:
    _SOUND_OK = False


def _tone(freq, dur=0.12, vol=0.4, rate=44100):
    n = int(rate * dur)
    buf = bytearray(n * 2)
    for i in range(n):
        fade = min(1.0, (n - i) / max(1, n * 0.12))
        v = int(vol * 32767 * fade * math.sin(2 * math.pi * freq * i / rate))
        struct.pack_into('<h', buf, i * 2, max(-32767, min(32767, v)))
    return pygame.mixer.Sound(buffer=bytes(buf))


if _SOUND_OK:
    SND_CORRECT = _tone(784, 0.10)
    SND_WRONG   = _tone(165, 0.22)
    SND_LVL1    = _tone(523, 0.14)
    SND_LVL2    = _tone(659, 0.14)
    SND_LVL3    = _tone(784, 0.24)
else:
    SND_CORRECT = SND_WRONG = SND_LVL1 = SND_LVL2 = SND_LVL3 = None


def _play(snd):
    if _SOUND_OK and snd:
        try:
            snd.play()
        except Exception:
            pass


# ── Minecraft palette ─────────────────────────────────────────────────────────
BG        = "#0A0E14"
CARD_BG   = "#161B22"
STONE     = "#21262D"
STONE2    = "#2D333B"
CREEPER_G = "#3D6B1E"
DIAMOND   = "#58E8D8"
GOLD      = "#FCBE1F"
GRASS     = "#56A832"
LAVA      = "#F05050"
TEXT_MAIN = "#F0F6FC"
TEXT_DIM  = "#8B949E"
BORDER    = "#30363D"

# PIL font — loaded directly from .ttf, bypassing Tk's broken font system
def _find_ttf(bold=True):
    suffix = "-Bold" if bold else "-Regular"
    candidates = [
        # Arch / Manjaro
        f"/usr/share/fonts/liberation/LiberationMono{suffix}.ttf",
        f"/usr/share/fonts/TTF/LiberationMono{suffix}.ttf",
        f"/usr/share/fonts/noto/NotoSansMono{suffix}.ttf",
        f"/usr/share/fonts/TTF/DejaVuSansMono{suffix}.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
        # Ubuntu / Pop!_OS / Debian
        f"/usr/share/fonts/truetype/liberation/LiberationMono{suffix}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSansMono{'-Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/noto/NotoSansMono{suffix}.ttf",
        # Fedora / RHEL
        f"/usr/share/fonts/liberation-mono/LiberationMono{suffix}.ttf",
        # Bundled alongside this script (for packaged installs)
        os.path.join(os.path.dirname(__file__), "fonts", f"LiberationMono{suffix}.ttf"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Last resort: ask fontconfig
    try:
        import subprocess
        result = subprocess.run(
            ["fc-match", "--format=%{file}", "Liberation Mono:bold" if bold else "Liberation Mono"],
            capture_output=True, text=True, timeout=2,
        )
        path = result.stdout.strip()
        if path and os.path.exists(path):
            return path
    except Exception:
        pass
    return None

TTF_BOLD = _find_ttf(bold=True)
_PIL_FONT_CACHE: dict = {}

def _pil_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _PIL_FONT_CACHE:
        _PIL_FONT_CACHE[size] = ImageFont.truetype(TTF_BOLD, size)
    return _PIL_FONT_CACHE[size]

def _hex_rgba(h, alpha=255):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), alpha)

def _shadow_rgba(h):
    r, g, b, _ = _hex_rgba(h)
    return (r // 5, g // 5, b // 5, 255)

# Tk label fonts — "fixed" is the only family available on this system
MONO = "TkFixedFont"

def _f(size, bold=False):
    return (MONO, size, "bold" if bold else "normal")

# ── Creeper pixel art (14×14) ─────────────────────────────────────────────────
FACE_NEUTRAL = [
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GG__GGGGG__GGG",
    "GG__GGGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGGG____GGGGG",
    "GGGGG____GGGGG",
    "GGG__GGGG__GGG",
    "GGG__GGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
]
FACE_HAPPY = [
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GG__GGGGG__GGG",
    "GG__GGGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGG______GGGG",
    "GGG__GGGG__GGG",
    "GGG__GGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
]
FACE_SAD = [
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GG__GGGGG__GGG",
    "GG__GGGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGG______GGGG",
    "GGG__GGGG__GGG",
    "GGG__GGGG__GGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGG",
]
PIXEL_MAP = {"G": CREEPER_G, "_": "#080808"}

# ── Streak achievements (streak_needed, message, bg_color) ────────────────────
ACHIEVEMENTS = [
    (3,  "GETTING WARM",      LAVA),
    (5,  "ON FIRE!",          LAVA),
    (10, "DIAMOND HANDS",     DIAMOND),
    (15, "UNSTOPPABLE!",      GOLD),
    (20, "LEGENDARY MINER!",  GOLD),
]

# ── Lessons ───────────────────────────────────────────────────────────────────
LESSONS = [
    {"name": "Home Row — Left",   "mode": "keys",  "keys": list("asdf"),
     "hint": "Rest on  A  S  D  F  — left hand!"},
    {"name": "Home Row — Right",  "mode": "keys",  "keys": list("jkl;"),
     "hint": "Rest on  J  K  L  ;  — right hand!"},
    {"name": "Full Home Row",     "mode": "keys",  "keys": list("asdfjkl;"),
     "hint": "Both hands on the home row!"},
    {"name": "Top Row",    "mode": "keys", "keys": list("qwertyuiop"),
     "hint": "Reach up to the top row!"},
    {"name": "Bottom Row", "mode": "keys", "keys": list("zxcvbnm"),
     "hint": "Reach down to the bottom row!"},
]  # word lessons are appended below after loading config

PRAISE = ["Awesome!", "Great job!", "Perfect!",
          "You rock!", "Nice one!", "BOOM!",
          "Legendary!", "EPIC!", "Pro move!"]

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".config" / "minetype"
CONFIG_FILE = CONFIG_DIR / "config.json"

_DEFAULT_CONFIG: dict = {
    "goal": 20,
    "word_lessons": [
        {
            "name": "Minecraft Words!",
            "hint": "Type the Minecraft word!",
            "words": ["dig", "mine", "axe", "bow", "hit", "run", "ore",
                      "bed", "eat", "pig", "cow", "sky", "log", "oak", "red"],
        },
        {
            "name": "More Minecraft!",
            "hint": "Keep going, Minecrafter!",
            "words": ["lava", "gold", "iron", "sand", "jump", "cave",
                      "farm", "fire", "wood", "bone", "mobs", "fish"],
        },
    ],
}


def _load_config() -> dict:
    """Load ~/.config/minetype/config.json, creating it with defaults if absent."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(_DEFAULT_CONFIG, f, indent=2)
        return dict(_DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE) as f:
            user = json.load(f)
        # Merge: user values override defaults, missing keys fall back to defaults
        merged = dict(_DEFAULT_CONFIG)
        merged.update(user)
        return merged
    except Exception:
        return dict(_DEFAULT_CONFIG)


def _build_word_lessons(cfg: dict) -> list:
    lessons = []
    for wl in cfg.get("word_lessons", _DEFAULT_CONFIG["word_lessons"]):
        lessons.append({
            "name":  wl.get("name", "Words"),
            "mode":  "words",
            "hint":  wl.get("hint", "Type the word!"),
            "words": [w.lower() for w in wl.get("words", []) if w.strip()],
        })
    return lessons


_CFG = _load_config()
GOAL = int(_CFG.get("goal", 20))

# Append word lessons from config after the hardcoded key-drill lessons
LESSONS.extend(_build_word_lessons(_CFG))

# ── Persistence ───────────────────────────────────────────────────────────────
SAVE_FILE = Path.home() / ".mine_type_save.json"


def _load_save():
    try:
        with open(SAVE_FILE) as f:
            d = json.load(f)
        stars = d.get("stars", [])
        while len(stars) < len(LESSONS):
            stars.append(0)
        return {"stars": stars, "best_score": d.get("best_score", 0)}
    except Exception:
        return {"stars": [0] * len(LESSONS), "best_score": 0}


def _write_save(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


# ── Keyboard layout ───────────────────────────────────────────────────────────
KB_ROWS = [list("qwertyuiop"), list("asdfghjkl;"), list("zxcvbnm")]
KW, KH, KG = 58, 50, 5


# ── App ───────────────────────────────────────────────────────────────────────
class TypingTutor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mine & Type!")
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda _e: self.root.attributes("-fullscreen", False))
        self.root.bind("<KeyPress>", self.on_key)

        self.save = _load_save()
        self.lesson_idx = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.target = ""
        self.word_pos = 0
        self.lesson_correct = 0
        self.lesson_wrong = 0
        self._tgt_text = ""
        self._tgt_color = TEXT_MAIN
        self._mascot_id = None
        self._overlay = None
        self._key_cooldown = False
        self._completing = False
        self._toast = None
        self._toast_after = None

        self._build_ui()
        self._show_title_screen()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar: title | lesson | score ──────────────────────────────────
        top = tk.Frame(self.root, bg=STONE, pady=0)
        top.pack(fill="x")

        # Left: logo
        tk.Label(top, text="⛏ Mine & Type!", font=_f(17, bold=True),
                 fg=GOLD, bg=STONE, padx=20, pady=14).pack(side="left")

        # Right: score
        score_block = tk.Frame(top, bg=STONE)
        score_block.pack(side="right", padx=20)
        self.lbl_score = tk.Label(score_block, text="Score: 0",
                                  font=_f(20, bold=True), fg=GOLD, bg=STONE)
        self.lbl_score.pack(side="right")
        self.lbl_streak = tk.Label(score_block, text="🔥 0",
                                   font=_f(14), fg=LAVA, bg=STONE, padx=16)
        self.lbl_streak.pack(side="right")
        self.lbl_best = tk.Label(score_block, text="Best: 0",
                                 font=_f(14), fg=TEXT_DIM, bg=STONE, padx=6)
        self.lbl_best.pack(side="right")

        # Center: lesson name
        self.lbl_lesson = tk.Label(top, text="", font=_f(14),
                                   fg=TEXT_DIM, bg=STONE)
        self.lbl_lesson.pack(side="left", padx=20, expand=True)

        # ── Stars bar ────────────────────────────────────────────────────────
        stars_bar = tk.Frame(self.root, bg=STONE2, pady=7)
        stars_bar.pack(fill="x")
        self.star_labels = []
        container = tk.Frame(stars_bar, bg=STONE2)
        container.pack()
        for i in range(len(LESSONS)):
            lbl = tk.Label(container, text="○", font=_f(14),
                           fg=TEXT_DIM, bg=STONE2, width=6, padx=2)
            lbl.pack(side="left")
            self.star_labels.append(lbl)

        # ── Main area: card (left) + side panel (right) ───────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Side panel: mascot + stats
        side = tk.Frame(main, bg=BG, width=220)
        side.pack(side="right", fill="y", padx=(12, 0))
        side.pack_propagate(False)

        self.mascot_cv = tk.Canvas(side, width=224, height=224,
                                   bg=BG, highlightthickness=0)
        self.mascot_cv.pack(pady=(16, 4))
        tk.Label(side, text="Creeper", font=_f(11, bold=True),
                 fg=CREEPER_G, bg=BG).pack()

        sep = tk.Frame(side, bg=STONE2, height=2)
        sep.pack(fill="x", pady=12, padx=10)

        self.lbl_side_streak = tk.Label(side, text="Streak\n0",
                                        font=_f(20, bold=True), fg=LAVA, bg=BG,
                                        justify="center")
        self.lbl_side_streak.pack(pady=6)
        self.lbl_side_best = tk.Label(side, text="Best\n0",
                                      font=_f(14), fg=TEXT_DIM, bg=BG,
                                      justify="center")
        self.lbl_side_best.pack()

        # Card
        self.card = tk.Frame(
            main, bg=CARD_BG,
            highlightbackground=BORDER, highlightthickness=3,
        )
        self.card.pack(side="left", fill="both", expand=True)

        self.lbl_hint = tk.Label(self.card, text="", font=_f(20, bold=True),
                                 fg=TEXT_DIM, bg=CARD_BG, wraplength=760)
        self.lbl_hint.pack(pady=(18, 4))

        # Canvas for all target drawing (key + word mode, with drop shadow)
        self.target_cv = tk.Canvas(self.card, bg=CARD_BG, highlightthickness=0)
        self.target_cv.pack(fill="both", expand=True)
        self._cv_w = self._cv_h = 0
        self.target_cv.bind("<Configure>", self._on_canvas_configure)

        self.lbl_feedback = tk.Label(self.card, text="", font=_f(20, bold=True),
                                     fg=DIAMOND, bg=CARD_BG)
        self.lbl_feedback.pack(pady=(6, 16))

        # ── Progress bar ──────────────────────────────────────────────────────
        prog_row = tk.Frame(self.root, bg=BG, pady=5)
        prog_row.pack(fill="x", padx=20)
        tk.Label(prog_row, text="Progress", font=_f(14),
                 fg=TEXT_DIM, bg=BG).pack(side="left")
        self.prog_cv = tk.Canvas(prog_row, height=24, bg=STONE2,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        self.prog_cv.pack(side="left", fill="x", expand=True, padx=10)
        self.prog_bar = self.prog_cv.create_rectangle(0, 0, 0, 24,
                                                       fill=GRASS, outline="")
        self.lbl_prog = tk.Label(prog_row, text=f"0 / {GOAL}", font=_f(14),
                                 fg=TEXT_DIM, bg=BG, width=7)
        self.lbl_prog.pack(side="left")

        # ── Keyboard ──────────────────────────────────────────────────────────
        kb_w = len(KB_ROWS[0]) * (KW + KG) + KG
        kb_h = len(KB_ROWS) * (KH + KG) + KG
        self.kb_cv = tk.Canvas(self.root, width=kb_w, height=kb_h,
                               bg=BG, highlightthickness=0)
        self.kb_cv.pack(pady=(4, 6))
        self._init_keyboard()

        # ── Nav buttons ───────────────────────────────────────────────────────
        nav = tk.Frame(self.root, bg=BG, pady=8)
        nav.pack(fill="x")
        tk.Button(nav, text="◀  Prev Lesson", font=_f(14),
                  fg=TEXT_MAIN, bg=STONE2, activebackground=LAVA,
                  activeforeground="white", relief="flat",
                  padx=16, pady=6, cursor="hand2",
                  command=self._prev_lesson).pack(side="left", padx=30)
        tk.Button(nav, text="Next Lesson  ▶", font=_f(14),
                  fg=BG, bg=DIAMOND, activebackground=GOLD,
                  activeforeground=BG, relief="flat",
                  padx=16, pady=6, cursor="hand2",
                  command=self._next_lesson).pack(side="right", padx=30)

        self._draw_mascot(FACE_NEUTRAL)

    # ── Title screen ──────────────────────────────────────────────────────────

    def _show_title_screen(self):
        self._title_anim_id = None
        self._title_sel = 0  # which lesson card is selected

        tf = tk.Frame(self.root, bg=BG)
        tf.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._title_frame = tf

        # ── Two-column layout ─────────────────────────────────────────────────
        tf.columnconfigure(0, weight=2)
        tf.columnconfigure(1, weight=3)
        tf.rowconfigure(0, weight=1)

        # ── Left panel: branding + creeper ───────────────────────────────────
        left = tk.Frame(tf, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 20), pady=40)
        left.rowconfigure(1, weight=1)

        # PIL title
        title_cv = tk.Canvas(left, bg=BG, highlightthickness=0, height=140)
        title_cv.pack(fill="x")
        title_cv.bind("<Configure>",
                      lambda e: self._draw_title_text(title_cv, e.width, e.height))

        tk.Label(left, text="A Minecraft Typing Adventure",
                 font=_f(13), fg=DIAMOND, bg=BG).pack(pady=(4, 20))

        # Creeper
        self._title_creeper_cv = tk.Canvas(
            left, width=252, height=252, bg=BG, highlightthickness=0
        )
        self._title_creeper_cv.pack()

        tk.Label(left, text="Click a level  —  or press any key",
                 font=_f(11), fg=TEXT_DIM, bg=BG).pack(pady=(20, 0))

        # ── Right panel: level selector ───────────────────────────────────────
        right = tk.Frame(tf, bg=STONE)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
        right.rowconfigure(1, weight=1)

        tk.Label(right, text="SELECT LEVEL",
                 font=_f(15, bold=True), fg=GOLD, bg=STONE,
                 pady=18).pack(fill="x")

        # Scrollable card area
        canvas_scroll = tk.Canvas(right, bg=STONE, highlightthickness=0)
        scrollbar = tk.Scrollbar(right, orient="vertical",
                                 command=canvas_scroll.yview)
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas_scroll.pack(side="left", fill="both", expand=True)

        card_container = tk.Frame(canvas_scroll, bg=STONE)
        card_window = canvas_scroll.create_window(
            (0, 0), window=card_container, anchor="nw"
        )

        def _resize_container(e):
            canvas_scroll.itemconfig(card_window, width=e.width)
        canvas_scroll.bind("<Configure>", _resize_container)

        def _update_scroll(_e=None):
            card_container.update_idletasks()
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        card_container.bind("<Configure>", _update_scroll)

        # Build one card per lesson
        self._level_cards = []
        for i, lesson in enumerate(LESSONS):
            stars = self.save["stars"][i] if i < len(self.save["stars"]) else 0
            star_str = {0: "New", 1: "★", 2: "★★", 3: "★★★"}.get(stars, "")

            mode_tag = "KEYS" if lesson["mode"] == "keys" else "WORDS"
            tag_color = DIAMOND if lesson["mode"] == "keys" else GOLD

            card = tk.Frame(card_container, bg=CARD_BG,
                            highlightthickness=2, highlightbackground=BORDER,
                            cursor="hand2")
            card.pack(fill="x", padx=16, pady=6)

            inner = tk.Frame(card, bg=CARD_BG, padx=14, pady=10)
            inner.pack(fill="x")

            # Lesson number + mode badge
            top_row = tk.Frame(inner, bg=CARD_BG)
            top_row.pack(fill="x")
            tk.Label(top_row, text=f"  {i + 1:02d}",
                     font=_f(13, bold=True), fg=TEXT_DIM, bg=CARD_BG).pack(side="left")
            tk.Label(top_row, text=f" {mode_tag} ",
                     font=_f(9, bold=True), fg=BG, bg=tag_color).pack(side="left", padx=6)
            tk.Label(top_row, text=star_str,
                     font=_f(12), fg=GOLD, bg=CARD_BG).pack(side="right")

            tk.Label(inner, text=lesson["name"],
                     font=_f(13, bold=True), fg=TEXT_MAIN, bg=CARD_BG,
                     anchor="w").pack(fill="x", pady=(4, 0))
            tk.Label(inner, text=lesson["hint"],
                     font=_f(10), fg=TEXT_DIM, bg=CARD_BG,
                     anchor="w").pack(fill="x")

            # Hover + click behaviour
            def _enter(_, c=card):
                c.config(highlightbackground=DIAMOND)
            def _leave(_, c=card, idx=i):
                c.config(highlightbackground=GOLD if idx == self._title_sel else BORDER)
            def _click(_, idx=i):
                self._title_sel = idx
                self._dismiss_title()

            for w in [card, inner] + list(inner.winfo_children()):
                w.bind("<Enter>", _enter)
                w.bind("<Leave>", _leave)
                w.bind("<Button-1>", _click)

            self._level_cards.append(card)

        # Highlight first card
        self._level_cards[0].config(highlightbackground=GOLD)

        # Override key binding — any key starts at lesson 0
        self.root.bind("<KeyPress>", lambda _e: self._dismiss_title())

        self._draw_title_creeper(FACE_NEUTRAL)
        self._animate_title_creeper(0)

    def _draw_title_text(self, cv, w, h):
        if w < 10 or h < 10 or not TTF_BOLD:
            return
        dummy = Image.new("RGBA", (1, 1))
        ddraw = ImageDraw.Draw(dummy)
        text = "MINE & TYPE!"
        lo, hi = 20, int(h * 0.78)
        while lo < hi - 2:
            mid = (lo + hi) // 2
            bb = ddraw.textbbox((0, 0), text, font=_pil_font(mid))
            lo = mid if (bb[2] - bb[0]) <= w * 0.82 else lo
            hi = mid if (bb[2] - bb[0]) > w * 0.82 else hi
        font = _pil_font(lo)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bb = draw.textbbox((0, 0), text, font=font)
        x = (w - (bb[2] - bb[0])) // 2 - bb[0]
        y = (h - (bb[3] - bb[1])) // 2 - bb[1]
        draw.text((x + 7, y + 7), text, font=font, fill=_shadow_rgba(GOLD))
        draw.text((x, y), text, font=font, fill=_hex_rgba(GOLD))
        photo = PILImageTk.PhotoImage(img)
        cv.delete("all")
        cv.create_image(0, 0, anchor="nw", image=photo)
        self._title_photo_ref = photo

    def _draw_title_creeper(self, face, ps=20):
        cv = self._title_creeper_cv
        cv.delete("all")
        size = len(face[0]) * ps
        cv.create_rectangle(0, 0, size, size, fill=CREEPER_G, outline="")
        for ri, row in enumerate(face):
            for ci, ch in enumerate(row):
                color = PIXEL_MAP.get(ch, CREEPER_G)
                if color != CREEPER_G:
                    cv.create_rectangle(
                        ci * ps, ri * ps, ci * ps + ps, ri * ps + ps,
                        fill=color, outline="",
                    )

    def _animate_title_creeper(self, step):
        if not hasattr(self, "_title_creeper_cv") or \
                not self._title_creeper_cv.winfo_exists():
            return
        # neutral…neutral…happy blink…neutral…neutral…happy blink
        seq = [
            (FACE_NEUTRAL, 1600),
            (FACE_HAPPY,    300),
            (FACE_NEUTRAL, 1200),
            (FACE_NEUTRAL,  800),
            (FACE_HAPPY,    400),
            (FACE_SAD,      200),
            (FACE_NEUTRAL, 1000),
        ]
        face, delay = seq[step % len(seq)]
        self._draw_title_creeper(face)
        self._title_anim_id = self.root.after(
            delay, lambda: self._animate_title_creeper(step + 1)
        )

    def _dismiss_title(self):
        aid = getattr(self, "_title_anim_id", None)
        if aid:
            self.root.after_cancel(aid)
        if hasattr(self, "_title_frame") and self._title_frame.winfo_exists():
            self._title_frame.destroy()
        self.root.bind("<KeyPress>", self.on_key)
        self.lesson_idx = getattr(self, "_title_sel", 0)
        self._load_lesson()

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def _init_keyboard(self):
        self._kb_rects = {}
        self._kb_texts = {}
        for ri, row in enumerate(KB_ROWS):
            indent = (len(KB_ROWS[0]) - len(row)) * (KW + KG) // 2
            for ci, key in enumerate(row):
                x1 = KG + indent + ci * (KW + KG)
                y1 = KG + ri * (KH + KG)
                r = self.kb_cv.create_rectangle(
                    x1, y1, x1 + KW, y1 + KH,
                    fill=STONE2, outline=BORDER, width=1,
                )
                t = self.kb_cv.create_text(
                    x1 + KW // 2, y1 + KH // 2,
                    text=key.upper(),
                    font=_f(13, bold=True),
                    fill=TEXT_DIM,
                )
                self._kb_rects[key] = r
                self._kb_texts[key] = t

    def _highlight_keys(self, target_char, lesson_keys=None):
        for k in self._kb_rects:
            self.kb_cv.itemconfig(self._kb_rects[k], fill=STONE2)
            self.kb_cv.itemconfig(self._kb_texts[k], fill=TEXT_DIM)
        if lesson_keys:
            for k in lesson_keys:
                if k in self._kb_rects:
                    self.kb_cv.itemconfig(self._kb_rects[k], fill="#1A3A1A")
                    self.kb_cv.itemconfig(self._kb_texts[k], fill=GRASS)
        keys = target_char if isinstance(target_char, (list, set)) else [target_char]
        for k in keys:
            if k in self._kb_rects:
                self.kb_cv.itemconfig(self._kb_rects[k], fill=DIAMOND)
                self.kb_cv.itemconfig(self._kb_texts[k], fill=BG)

    # ── Canvas target display ─────────────────────────────────────────────────

    def _on_canvas_configure(self, event):
        self._cv_w = event.width
        self._cv_h = event.height
        self._redraw_target()

    def _fit_pil_size(self, word: str, max_w: int, max_h: int) -> int:
        """Binary-search largest font size (px) so word fits within max_w × max_h."""
        lo, hi = 20, int(max_h * 0.82)
        dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy)
        while lo < hi - 2:
            mid = (lo + hi) // 2
            bb = draw.textbbox((0, 0), word.upper(), font=_pil_font(mid))
            if (bb[2] - bb[0]) <= max_w * 0.88:
                lo = mid
            else:
                hi = mid
        return lo

    def _redraw_target(self):
        cv = self.target_cv
        w, h = self._cv_w, self._cv_h
        if w < 10 or h < 10 or not self._tgt_text or not TTF_BOLD:
            return

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        lesson = LESSONS[self.lesson_idx]

        if lesson["mode"] == "keys":
            size = min(int(h * 0.72), int(w * 0.55))
            font = _pil_font(size)
            text = self._tgt_text.upper()
            bb = draw.textbbox((0, 0), text, font=font)
            x = (w - (bb[2] - bb[0])) // 2 - bb[0]
            y = (h - (bb[3] - bb[1])) // 2 - bb[1]
            draw.text((x + 6, y + 6), text, font=font,
                      fill=_shadow_rgba(self._tgt_color))
            draw.text((x, y), text, font=font,
                      fill=_hex_rgba(self._tgt_color))
        else:
            word = self._tgt_text
            pos = self.word_pos
            size = self._fit_pil_size(word, w, h)
            font = _pil_font(size)

            # Measure each character
            widths = []
            for ch in word:
                bb = draw.textbbox((0, 0), ch.upper(), font=font)
                widths.append(bb[2] - bb[0])

            total_w = sum(widths)
            # Vertical center using cap height
            cap_bb = draw.textbbox((0, 0), "A", font=font)
            y = (h - (cap_bb[3] - cap_bb[1])) // 2 - cap_bb[1]
            x = (w - total_w) // 2

            for i, (ch, cw) in enumerate(zip(word, widths)):
                if i < pos:
                    color = _hex_rgba(DIAMOND)
                    shadow = _shadow_rgba(DIAMOND)
                elif i == pos:
                    color = _hex_rgba(self._tgt_color)
                    shadow = _shadow_rgba(self._tgt_color)
                else:
                    color = _hex_rgba(TEXT_DIM)
                    shadow = None
                ch_bb = draw.textbbox((0, 0), ch.upper(), font=font)
                ox = x - ch_bb[0]
                if shadow:
                    draw.text((ox + 5, y + 5), ch.upper(), font=font, fill=shadow)
                draw.text((ox, y), ch.upper(), font=font, fill=color)
                x += cw

        photo = PILImageTk.PhotoImage(img)
        cv.delete("all")
        cv.create_image(0, 0, anchor="nw", image=photo)
        self._photo_ref = photo  # prevent GC

    # ── Mascot ────────────────────────────────────────────────────────────────

    def _draw_mascot(self, face, ps=16):
        cv = self.mascot_cv
        cv.delete("all")
        size = len(face[0]) * ps
        cv.create_rectangle(0, 0, size, size, fill=CREEPER_G, outline="")
        for ri, row in enumerate(face):
            for ci, ch in enumerate(row):
                color = PIXEL_MAP.get(ch, CREEPER_G)
                if color != CREEPER_G:
                    cv.create_rectangle(
                        ci * ps, ri * ps, ci * ps + ps, ri * ps + ps,
                        fill=color, outline="",
                    )

    def _mascot_react(self, face, reset_after=600):
        self._draw_mascot(face)
        if self._mascot_id:
            self.root.after_cancel(self._mascot_id)
        self._mascot_id = self.root.after(
            reset_after, lambda: self._draw_mascot(FACE_NEUTRAL)
        )

    # ── Lesson management ─────────────────────────────────────────────────────

    def _load_lesson(self):
        self.lesson_correct = 0
        self.lesson_wrong = 0
        self.streak = 0
        self.word_pos = 0
        self._completing = False
        self._key_cooldown = False
        self.lbl_streak.config(text="🔥 0")
        self.lbl_side_streak.config(text="Streak\n0")
        self._update_progress()
        self._update_stars()
        self._new_target()

    def _new_target(self):
        lesson = LESSONS[self.lesson_idx]
        self.lbl_lesson.config(
            text=f"Lesson {self.lesson_idx + 1} / {len(LESSONS)}   ·   {lesson['name']}"
        )
        self.lbl_hint.config(text=lesson["hint"])
        self.lbl_feedback.config(text="")
        self.card.config(highlightbackground=BORDER)

        if lesson["mode"] == "keys":
            self.target = random.choice(lesson["keys"])
            self.word_pos = 0
            self._tgt_text = self.target
            self._tgt_color = TEXT_MAIN
            self._redraw_target()
            self._highlight_keys(self.target, lesson["keys"])
        else:
            self.target = random.choice(lesson["words"])
            self.word_pos = 0
            self._tgt_text = self.target
            self._tgt_color = TEXT_MAIN
            self._redraw_target()
            self._highlight_keys(self.target[0])

    # ── Input ─────────────────────────────────────────────────────────────────

    def _clear_cooldown(self):
        self._key_cooldown = False

    def on_key(self, event):
        if self._overlay or self._key_cooldown:
            return
        self._key_cooldown = True
        self.root.after(150, self._clear_cooldown)
        key = event.char.lower()
        if not key or not key.isprintable():
            return

        lesson = LESSONS[self.lesson_idx]

        if lesson["mode"] == "keys":
            if key == self.target:
                self._on_correct()
            else:
                self._on_wrong(key, self.target)
        else:
            expected = self.target[self.word_pos]
            if key == expected:
                self.word_pos += 1
                if self.word_pos >= len(self.target):
                    self._on_correct()
                else:
                    self._redraw_target()
                    self._highlight_keys(self.target[self.word_pos])
            else:
                wrong_expected = expected
                self.word_pos = 0
                self._redraw_target()
                self._highlight_keys(self.target[0])
                self._on_wrong(key, wrong_expected)

    # ── Achievement toasts ────────────────────────────────────────────────────

    def _show_toast(self, text, bg):
        # Kill any existing toast
        if self._toast_after:
            self.root.after_cancel(self._toast_after)
            self._toast_after = None
        if self._toast:
            self._toast.destroy()

        frame = tk.Frame(self.root, bg=bg, padx=28, pady=12,
                         highlightthickness=3, highlightbackground=BG)
        tk.Label(frame, text=text, font=_f(18, bold=True),
                 fg=BG, bg=bg).pack()
        # Start above the window then slide down
        frame.place(relx=0.5, anchor="n", y=-70)
        self._toast = frame
        self._slide_toast(frame, target_y=60, step=8, hold=False)

    def _slide_toast(self, frame, target_y, step, hold):
        if not frame.winfo_exists():
            return
        cur_y = frame.winfo_y()
        if not hold:
            new_y = cur_y + step
            if new_y < target_y:
                frame.place(relx=0.5, anchor="n", y=new_y)
                self._toast_after = self.root.after(
                    12, lambda: self._slide_toast(frame, target_y, step, False))
            else:
                frame.place(relx=0.5, anchor="n", y=target_y)
                # Hold for 1.6 s then slide back up
                self._toast_after = self.root.after(
                    1600, lambda: self._slide_toast(frame, -70, step, True))
        else:
            new_y = cur_y - step
            if new_y > target_y:
                frame.place(relx=0.5, anchor="n", y=new_y)
                self._toast_after = self.root.after(
                    12, lambda: self._slide_toast(frame, target_y, step, True))
            else:
                frame.destroy()
                self._toast = None
                self._toast_after = None

    def _on_correct(self):
        lesson = LESSONS[self.lesson_idx]
        self.score += 10 if lesson["mode"] == "keys" else 30
        self.streak += 1
        self.best_streak = max(self.streak, self.best_streak)
        self.lesson_correct += 1

        self.lbl_score.config(text=f"Score: {self.score}")
        self.lbl_streak.config(text=f"🔥 {self.streak}")
        self.lbl_best.config(text=f"Best: {self.best_streak}")
        self.lbl_side_streak.config(text=f"Streak\n{self.streak}", fg=DIAMOND if self.streak > 4 else LAVA)
        self.lbl_side_best.config(text=f"Best\n{self.best_streak}")

        self.lbl_feedback.config(text=random.choice(PRAISE), fg=DIAMOND)
        self.card.config(highlightbackground=DIAMOND)
        self._tgt_color = DIAMOND
        self._redraw_target()

        _play(SND_CORRECT)
        self._mascot_react(FACE_HAPPY, 500)
        self._update_progress()

        for threshold, msg, color in ACHIEVEMENTS:
            if self.streak == threshold:
                self._show_toast(msg, color)
                break

        if self.lesson_correct >= GOAL and not self._completing:
            self._completing = True
            self.root.after(380, self._lesson_complete)
        else:
            delay = 400 if lesson["mode"] == "keys" else 620
            self.root.after(delay, self._new_target)

    def _on_wrong(self, pressed, expected):
        self.streak = 0
        self.lesson_wrong += 1
        self.lbl_streak.config(text="🔥 0")
        self.lbl_side_streak.config(text="Streak\n0", fg=LAVA)
        self.lbl_feedback.config(
            text=f"'{pressed.upper()}'  →  try  '{expected.upper()}'",
            fg=LAVA,
        )
        self.card.config(highlightbackground=LAVA)
        self._tgt_color = LAVA
        self._redraw_target()

        _play(SND_WRONG)
        self._mascot_react(FACE_SAD, 900)
        self._shake()

    # ── Progress & stars ──────────────────────────────────────────────────────

    def _update_progress(self):
        self.prog_cv.update_idletasks()
        bar_w = self.prog_cv.winfo_width()
        pct = min(self.lesson_correct / GOAL, 1.0)
        self.prog_cv.coords(self.prog_bar, 0, 0, int(bar_w * pct), 24)
        self.lbl_prog.config(text=f"{self.lesson_correct} / {GOAL}")

    def _update_stars(self):
        for i, lbl in enumerate(self.star_labels):
            s = self.save["stars"][i] if i < len(self.save["stars"]) else 0
            active = (i == self.lesson_idx)
            if s == 3:
                lbl.config(text="★★★", fg=GOLD if not active else DIAMOND)
            elif s == 2:
                lbl.config(text="★★☆", fg=GOLD if not active else DIAMOND)
            elif s == 1:
                lbl.config(text="★☆☆", fg=TEXT_DIM if not active else DIAMOND)
            else:
                lbl.config(text="○", fg=TEXT_DIM if not active else DIAMOND)

    # ── Level complete ────────────────────────────────────────────────────────

    def _calc_stars(self):
        total = self.lesson_correct + self.lesson_wrong
        acc = self.lesson_correct / max(total, 1)
        if acc >= 0.90:
            return 3
        if acc >= 0.75:
            return 2
        return 1

    def _lesson_complete(self):
        stars = self._calc_stars()
        if stars > self.save["stars"][self.lesson_idx]:
            self.save["stars"][self.lesson_idx] = stars
        if self.score > self.save["best_score"]:
            self.save["best_score"] = self.score
        _write_save(self.save)

        if _SOUND_OK:
            SND_LVL1.play()
            self.root.after(220, lambda: SND_LVL2.play())
            self.root.after(440, lambda: SND_LVL3.play())

        self._show_overlay(stars)

    def _show_overlay(self, stars):
        # Backdrop
        backdrop = tk.Frame(self.root, bg=BG)
        backdrop.place(relx=0, rely=0, relwidth=1, relheight=1)

        ov = tk.Frame(
            self.root, bg=CARD_BG,
            highlightbackground=DIAMOND, highlightthickness=4,
        )
        ov.place(relx=0.5, rely=0.5, anchor="center", width=520, height=360)
        self._overlay = ov
        self._backdrop = backdrop

        tk.Label(ov, text="LEVEL COMPLETE!", font=_f(28, bold=True),
                 fg=DIAMOND, bg=CARD_BG).pack(pady=(36, 4))
        tk.Label(ov, text=LESSONS[self.lesson_idx]["name"],
                 font=_f(14), fg=TEXT_DIM, bg=CARD_BG).pack()

        star_str = "★" * stars + "☆" * (3 - stars)
        tk.Label(ov, text=star_str, font=_f(52),
                 fg=GOLD, bg=CARD_BG).pack(pady=16)

        acc = self.lesson_correct / max(self.lesson_correct + self.lesson_wrong, 1)
        tk.Label(ov, text=f"Accuracy:  {acc:.0%}", font=_f(14),
                 fg=TEXT_DIM, bg=CARD_BG).pack()

        btn_row = tk.Frame(ov, bg=CARD_BG)
        btn_row.pack(pady=20)
        tk.Button(btn_row, text="Try Again", font=_f(14),
                  fg=TEXT_MAIN, bg=STONE2, relief="flat",
                  padx=14, pady=7, cursor="hand2",
                  command=self._retry).pack(side="left", padx=10)
        if self.lesson_idx < len(LESSONS) - 1:
            tk.Button(btn_row, text="Next Lesson  ▶", font=_f(14),
                      fg=BG, bg=DIAMOND, relief="flat",
                      padx=14, pady=7, cursor="hand2",
                      command=self._advance).pack(side="left", padx=10)

        self._flash_overlay(ov, 0)

    def _flash_overlay(self, ov, n):
        if not ov.winfo_exists():
            return
        colors = [DIAMOND, GOLD, GRASS, LAVA, DIAMOND, GOLD]
        ov.config(highlightbackground=colors[n % len(colors)])
        if n < 10:
            self.root.after(160, lambda: self._flash_overlay(ov, n + 1))

    def _retry(self):
        self._close_overlay()
        self._load_lesson()

    def _advance(self):
        self._close_overlay()
        if self.lesson_idx < len(LESSONS) - 1:
            self.lesson_idx += 1
            self._load_lesson()

    def _close_overlay(self):
        for attr in ("_overlay", "_backdrop"):
            w = getattr(self, attr, None)
            if w and w.winfo_exists():
                w.destroy()
        self._overlay = None

    # ── Shake ─────────────────────────────────────────────────────────────────

    def _shake(self, step=0, seq=(12, 0, -12, 0, 8, 0, -8, 0, 4, 0, -4, 0)):
        if step < len(seq):
            d = seq[step]
            self.card.pack_configure(padx=(max(d, 0), max(-d, 0)))
            self.root.after(36, lambda: self._shake(step + 1, seq))
        else:
            self.card.pack_configure(padx=0)

    # ── Lesson nav ────────────────────────────────────────────────────────────

    def _next_lesson(self):
        if self.lesson_idx < len(LESSONS) - 1:
            self.lesson_idx += 1
            self._load_lesson()

    def _prev_lesson(self):
        if self.lesson_idx > 0:
            self.lesson_idx -= 1
            self._load_lesson()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTutor(root)
    root.mainloop()
