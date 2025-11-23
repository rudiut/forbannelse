import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random
import pygame

# ---------- Base path ----------
BASE_DIR = os.path.dirname(__file__)
def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)

# ---------- Lydoppsett ----------
pygame.mixer.init()
pygame.mixer.music.load(asset_path("music", "Never_Surrender.ogg"))
pygame.mixer.music.play(-1)  # loop kampmusikk

def play_game_over():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_path("music", "Game_Over.ogg"))
    pygame.mixer.music.play()

def play_victory():
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_path("music", "Ship.ogg"))
    pygame.mixer.music.play()
    victory_animation()

# ---------- Spillparametre ----------
SPILLER_MAX = 50
FIENDE_MAX = 50
spiller_hp = SPILLER_MAX
fiende_hp = FIENDE_MAX

forbannelser = [
    ("⚡ Lynskudd", 10),
    ("🕷️ Evig kløe", 5),
    ("🤢 Dårlig mage", 7),
    ("🐌 Sneglefart", 8),
    ("🤯 Forferdelig hodepine", 12),
]

angrep = [
    ("🗣️ Motargument", 10),
    ("👀 Kritisk blikk", 7),
    ("⚡ Kjapp replikk", 12),
]

# ---------- Items og buff ----------
items = {
    "☕ Kopp te": {"count": 3, "heal": True, "amount": (5, 15)},
    "🍬 Brente mandler": {"count": 3, "buff": True, "multiplier": 1.1, "duration": 2}
}
damage_multiplier = 1.0
buff_rounds_left = 0

# ---------- Tkinter setup ----------
root = tk.Tk()
root.title("Skjebnesvanger kamp")
WIDTH, HEIGHT = 400, 300
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

def load_sprite(filename, size=(96, 96)):
    img = Image.open(asset_path("sprites", filename)).resize(size, Image.NEAREST)
    return ImageTk.PhotoImage(img)

def try_load_sprite(filename, size=(96, 96)):
    try:
        return load_sprite(filename, size)
    except Exception:
        return None

# ---------- Bakgrunn og sprites ----------
bg_image = ImageTk.PhotoImage(
    Image.open(asset_path("backgrounds", "haunted_bg.png")).resize((WIDTH, HEIGHT), Image.NEAREST)
)
canvas.create_image(WIDTH//2, HEIGHT//2, image=bg_image)

spiller_sprite = load_sprite("AneMaren.png")                 # nøytral (må finnes)
anemaren_glad  = try_load_sprite("anemaren_glad.png")        # glad
anemaren_redd  = try_load_sprite("anemaren_redd.png")        # skremt
anemaren_klar  = try_load_sprite("anemaren_klar.png")        # kampklar (valgfritt)
anemaren_op    = try_load_sprite("anemaren_op.png")          # OP (valgfritt)
fiende_sprite  = load_sprite("Heks.png")

SPILLER_POS = (60, 220)
FIENDE_POS  = (320, 60)
spiller_img = canvas.create_image(*SPILLER_POS, image=spiller_sprite)
fiende_img  = canvas.create_image(*FIENDE_POS, image=fiende_sprite)

# ---------- UI ----------
spiller_label = tk.Label(root, text="Ane Maren", font=("Courier", 12, "bold"))
spiller_label.pack(anchor="w", padx=20)
spiller_bar = ttk.Progressbar(root, length=200, maximum=SPILLER_MAX)
spiller_bar.pack(anchor="w", padx=20)
spiller_bar.config(value=spiller_hp)

buff_icon = tk.Label(root, text="", font=("Courier", 12))
buff_icon.pack(anchor="w", padx=20)

fiende_label = tk.Label(root, text="Ond Heks", font=("Courier", 12, "bold"))
fiende_label.pack(anchor="e", padx=20)
fiende_bar = ttk.Progressbar(root, length=200, maximum=FIENDE_MAX)
fiende_bar.pack(anchor="e", padx=20)
fiende_bar.config(value=fiende_hp)

textbox = tk.Label(
    root,
    text="En ekkel Ond Heks dukker opp!",
    font=("Courier", 12),
    bg="white",
    width=40,
    height=4,
    relief="solid"
)
textbox.pack(pady=10)

# ---------- Sprite-velger ----------
def set_sprite(status, varighet=800):
    variant = spiller_sprite
    if status == "glad" and anemaren_glad:
        variant = anemaren_glad
    elif status == "redd" and anemaren_redd:
        variant = anemaren_redd
    elif status == "klar" and anemaren_klar:
        variant = anemaren_klar
    elif status == "op" and anemaren_op:
        variant = anemaren_op

    canvas.itemconfig(spiller_img, image=variant)

    # Midlertidige uttrykk går tilbake til nøytral
    if status in ["glad", "redd", "klar"]:
        root.after(varighet, lambda: canvas.itemconfig(spiller_img, image=spiller_sprite))

# ---------- Animasjoner ----------
def blink(sprite_id, times=3, interval=120):
    def step(i=0, visible=True):
        if i >= times * 2:
            canvas.itemconfigure(sprite_id, state='normal')
            return
        canvas.itemconfigure(sprite_id, state=('normal' if visible else 'hidden'))
        root.after(interval, step, i+1, not visible)
    step()

def shake(sprite_id, origin, cycles=3, dx=5, delay=40):
    x0, y0 = origin
    seq = []
    for _ in range(cycles):
        seq += [dx, -dx, dx, -dx]
    def step(i=0):
        if i >= len(seq):
            canvas.coords(sprite_id, x0, y0)
            return
        canvas.move(sprite_id, seq[i], 0)
        root.after(delay, step, i+1)
    step()

def disable_buttons():
    fight_button.config(state="disabled")
    item_button.config(state="disabled")
    run_button.config(state="disabled")

def victory_animation():
    # Konfetti
    for _ in range(30):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT//2)
        color = random.choice(["red", "yellow", "blue", "green", "purple", "orange"])
        c = canvas.create_oval(x, y, x+5, y+5, fill=color, outline="")
        def fall(ci=c):
            canvas.move(ci, 0, 10)
            if canvas.coords(ci)[1] < HEIGHT:
                root.after(100, fall, ci)
        fall()
    # Blinkende stjerner
    for _ in range(10):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT//2)
        s = canvas.create_text(x, y, text="✦", fill="white", font=("Courier", 14))
        def blink_star(si=s, visible=True, count=0):
            if count > 6: return
            canvas.itemconfigure(si, state=('normal' if visible else 'hidden'))
            root.after(300, blink_star, si, not visible, count+1)
        blink_star()

# ---------- Kamplogikk ----------
def heks_angrep():
    global spiller_hp
    forbannelse, damage = random.choice(forbannelser)
    spiller_hp = max(0, spiller_hp - damage)
    spiller_bar.config(value=spiller_hp)
    textbox.config(text=f"Ond Heks brukte {forbannelse}!\nAne Maren mistet {damage} HP.")
    set_sprite("redd")
    blink(spiller_img)
    if spiller_hp == 0:
        textbox.config(text="💀 Ane Maren besvimte!")
        play_game_over()
        disable_buttons()

def maren_angrep():
    global fiende_hp, spiller_hp, damage_multiplier, buff_rounds_left
    # Vis OP-sprite hvis buff aktiv, ellers glad
    if buff_rounds_left > 0 and anemaren_op:
        set_sprite("op", varighet=0)  # OP-sprite blir stående mens buff varer
    else:
        set_sprite("glad")

    # Dynamisk ult når lav HP
    if spiller_hp <= int(SPILLER_MAX * 0.3):
        navn = "🧨 Voksenkjeft"
        base = 20
        damage = max(1, int(base * damage_multiplier))
        textbox.config(text=f"Ane Maren fyrer av {navn}!\nOnd Heks mister {damage} HP!")
    else:
        navn, base = random.choice(angrep)
        damage = max(1, int(base * damage_multiplier))
        textbox.config(text=f"Ane Maren brukte {navn}!\nOnd Heks mistet {damage} HP.")

    fiende_hp = max(0, fiende_hp - damage)
    fiende_bar.config(value=fiende_hp)
    shake(spiller_img, SPILLER_POS)

    # Buff teller ned etter spillerens angrep
    if buff_rounds_left > 0:
        buff_rounds_left -= 1
        if buff_rounds_left > 0:
            buff_icon.config(text=f"🔥 OP ({buff_rounds_left})")
        else:
            damage_multiplier = 1.0
            buff_icon.config(text="")
            textbox.config(text=textbox.cget("text") + "\nBuffen fra mandlene er borte.")
            # Gå tilbake til kampklar hvis sprite finnes, ellers nøytral
            if anemaren_klar:
                set_sprite("klar")
            else:
                canvas.itemconfig(spiller_img, image=spiller_sprite)

    if fiende_hp == 0:
        textbox.config(text="✨ Ond Heks ble beseiret!")
        play_victory()
        disable_buttons()
    else:
        root.after(800, heks_angrep)

# ---------- Items ----------
def bruk_item(valg):
    global spiller_hp, damage_multiplier, buff_rounds_left

    if valg == "☕ Kopp te":
        if items[valg]["count"] <= 0:
            textbox.config(text="❌ Ingen te igjen!")
            return
        heal = random.randint(*items[valg]["amount"])
        spiller_hp = min(SPILLER_MAX, spiller_hp + heal)
        spiller_bar.config(value=spiller_hp)
        textbox.config(text=f"Ane Maren drikker te ☕\nHun fikk tilbake {heal} HP.")
        items[valg]["count"] -= 1
        # Vis kampklar hvis finnes
        set_sprite("klar")
        root.after(800, heks_angrep)

    elif valg == "🍬 Brente mandler":
        if items[valg]["count"] <= 0:
            textbox.config(text="❌ Ingen brente mandler igjen!")
            return
        damage_multiplier = items[valg]["multiplier"]
        buff_rounds_left = items[valg]["duration"]
        items[valg]["count"] -= 1
        textbox.config(text="Ane Maren spiser brente mandler 🍬\nHun blir 10% sterkere i 2 runder!")
        buff_icon.config(text=f"🔥 OP ({buff_rounds_left})")
        # Vis OP-sprite hvis tilgjengelig, ellers glad
        if anemaren_op:
            set_sprite("op", varighet=0)
        else:
            set_sprite("glad")
        root.after(800, heks_angrep)

def velg_item():
    win = tk.Toplevel(root)
    win.title("Velg Item")
    win.resizable(False, False)

    info = tk.Label(win, text="Velg et item å bruke:", font=("Courier", 12))
    info.pack(pady=8)

    def btn_text(navn):
        return f"{navn} ({items[navn]['count']} igjen)"

    btn_te = tk.Button(win, text=btn_text("☕ Kopp te"),
                       font=("Courier", 12),
                       command=lambda: (bruk_item("☕ Kopp te"), win.destroy()))
    btn_te.pack(pady=5, padx=10, fill="x")
    if items["☕ Kopp te"]["count"] == 0:
        btn_te.config(state="disabled")

    btn_mandler = tk.Button(win, text=btn_text("🍬 Brente mandler"),
                            font=("Courier", 12),
                            command=lambda: (bruk_item("🍬 Brente mandler"), win.destroy()))
    btn_mandler.pack(pady=5, padx=10, fill="x")
    if items["🍬 Brente mandler"]["count"] == 0:
        btn_mandler.config(state="disabled")

# ---------- Meny ----------
menu_frame = tk.Frame(root)
menu_frame.pack(pady=10)

fight_button = tk.Button(menu_frame, text="Fight", command=maren_angrep,
                         font=("Courier", 12), width=10)
fight_button.grid(row=0, column=0, padx=5)

item_button = tk.Button(menu_frame, text="Item", command=velg_item,
                        font=("Courier", 12), width=10)
item_button.grid(row=0, column=1, padx=5)

def do_run():
    textbox.config(text="🏃‍♀️ Ane Maren flyktet fra kampen!")
    disable_buttons()
    play_game_over()  # liten dramatisk avslutning på flukt

run_button = tk.Button(menu_frame, text="Run", command=do_run,
                       font=("Courier", 12), width=10)
run_button.grid(row=0, column=2, padx=5)

# ---------- Start ----------
root.mainloop()
