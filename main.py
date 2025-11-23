import os
import sys
import random
import pygame

# ---------- Base path ----------
BASE_DIR = os.path.dirname(__file__)
def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)

# ---------- Init ----------
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skjebnesvanger kamp")
clock = pygame.time.Clock()

# ---------- Musikk ----------
def play_loop(theme):
    try:
        pygame.mixer.music.load(asset_path("music", theme))
        pygame.mixer.music.play(-1)
    except Exception:
        pass

def play_once(theme):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(asset_path("music", theme))
        pygame.mixer.music.play()
    except Exception:
        pass

play_loop("Never_Surrender.ogg")

def play_game_over():
    play_once("Game_Over.ogg")

def play_victory():
    play_once("Ship.ogg")

# ---------- Spillparametre ----------
SPILLER_MAX = 50
FIENDE_MAX = 50
spiller_hp = SPILLER_MAX
fiende_hp = FIENDE_MAX
game_active = True

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

items = {
    "☕ Kopp te": {"count": 3, "heal": True, "amount": (5, 15)},
    "🍬 Brente mandler": {"count": 3, "buff": True, "multiplier": 1.1, "duration": 2}
}
damage_multiplier = 1.0

# ---------- Assets ----------
def load_and_scale(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

bg = load_and_scale(asset_path("backgrounds", "haunted_bg.png"), (WIDTH, HEIGHT))

spiller_sprite = load_and_scale(asset_path("sprites", "AneMaren.png"), (96,96))
anemaren_glad  = load_and_scale(asset_path("sprites", "anemaren_glad.png"), (96,96))
anemaren_redd  = load_and_scale(asset_path("sprites", "anemaren_redd.png"), (96,96))
fiende_sprite  = load_and_scale(asset_path("sprites", "Heks.png"), (160,160))

current_sprite = spiller_sprite

SPILLER_POS = (60, 280)
FIENDE_POS  = (440, 80)

# ---------- Fonts ----------
font = pygame.font.SysFont("Courier", 20)
small = pygame.font.SysFont("Courier", 16)
big = pygame.font.SysFont("Courier", 24)

textbox_text = "En ekkel Ond Heks dukker opp!"

# ---------- Tegnefunksjoner ----------
def draw_hp_bar(x, y, hp, max_hp, color):
    ratio = max(0.0, min(1.0, hp / max_hp))
    pygame.draw.rect(screen, (40,40,40), (x-2, y-2, 104, 14), 2)
    pygame.draw.rect(screen, (220,220,220), (x, y, 100, 10))
    pygame.draw.rect(screen, color, (x, y, int(100*ratio), 10))

def draw_textbox(text):
    box = pygame.Rect(20, HEIGHT-120, WIDTH-40, 100)
    pygame.draw.rect(screen, (255,255,255), box)
    pygame.draw.rect(screen, (0,0,0), box, 2)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        txt = small.render(line, True, (0,0,0))
        screen.blit(txt, (30, HEIGHT-110 + i*20))

def draw_labels():
    # Ane Maren under sprite
    am = big.render("Ane Maren", True, (255,255,255))
    name_bg = pygame.Surface((am.get_width()+10, am.get_height()+10))
    name_bg.fill((0,0,128))
    screen.blit(name_bg, (SPILLER_POS[0], SPILLER_POS[1]+100))
    screen.blit(am, (SPILLER_POS[0]+5, SPILLER_POS[1]+105))
    draw_hp_bar(SPILLER_POS[0], SPILLER_POS[1]+135, spiller_hp, SPILLER_MAX, (0,200,0))

    # Ond Heks under sprite
    heks = big.render("Ond Heks", True, (255,255,255))
    name_bg2 = pygame.Surface((heks.get_width()+10, heks.get_height()+10))
    name_bg2.fill((0,0,128))
    screen.blit(name_bg2, (FIENDE_POS[0], FIENDE_POS[1]+160))
    screen.blit(heks, (FIENDE_POS[0]+5, FIENDE_POS[1]+165))
    draw_hp_bar(FIENDE_POS[0], FIENDE_POS[1]+190, fiende_hp, FIENDE_MAX, (200,0,0))

# ---------- Kamplogikk ----------
def heks_angrep():
    global spiller_hp, textbox_text, current_sprite, game_active
    if not game_active: return
    forbannelse, damage = random.choice(forbannelser)
    spiller_hp = max(0, spiller_hp - damage)
    textbox_text = f"Ond Heks brukte {forbannelse}!\nAne Maren mistet {damage} HP."
    current_sprite = anemaren_redd
    if spiller_hp == 0:
        textbox_text = "💀 Ane Maren besvimte!"
        play_game_over()
        game_active = False

def maren_angrep():
    global fiende_hp, textbox_text, current_sprite, game_active
    if not game_active: return
    navn, base = random.choice(angrep)
    damage = int(base * damage_multiplier)
    textbox_text = f"Ane Maren brukte {navn}!\nOnd Heks mistet {damage} HP."
    fiende_hp = max(0, fiende_hp - damage)
    current_sprite = anemaren_glad
    if fiende_hp == 0:
        textbox_text = "✨ Ond Heks ble beseiret!"
        play_victory()
        game_active = False

def bruk_item(valg):
    global spiller_hp, damage_multiplier, textbox_text, current_sprite
    if not game_active: return
    if valg == "☕ Kopp te":
        if items[valg]["count"] <= 0:
            textbox_text = "❌ Ingen te igjen!"
            return
        heal = random.randint(*items[valg]["amount"])
        spiller_hp = min(SPILLER_MAX, spiller_hp + heal)
        items[valg]["count"] -= 1
        textbox_text = f"Ane Maren drikker te ☕\nHun fikk tilbake {heal} HP."
        current_sprite = spiller_sprite
    elif valg == "🍬 Brente mandler":
        if items[valg]["count"] <= 0:
            textbox_text = "❌ Ingen brente mandler igjen!"
            return
        damage_multiplier = items[valg]["multiplier"]
        textbox_text = "Ane Maren spiser brente mandler 🍬\nHun blir sterkere!"
        items[valg]["count"] -= 1
        current_sprite = anemaren_glad

def do_run():
    global textbox_text, game_active
    textbox_text = "🏃‍♀️ Ane Maren flyktet fra kampen!"
    play_game_over()
    game_active = False

# ---------- Menyer ----------
menu_index = 0
menu_items = ["Fight", "Item", "Run"]

item_menu_open = False
item_index = 0
item_options = ["☕ Kopp te", "🍬 Brente mandler"]

def draw_menu():
    if item_menu_open:
        # Item undermeny
        panel_w, panel_h = 200, 100
        panel_x, panel_y = WIDTH - panel_w - 20, HEIGHT - panel_h - 20
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (0, 0, 128), panel)
        pygame.draw.rect(screen, (255, 255, 255), panel, 2)

        for i, label in enumerate(item_options):
            prefix = "▶ " if i == item_index else "  "
            txt = font.render(prefix + label, True, (255, 255, 255))
            screen.blit(txt, (panel_x + 12, panel_y + 10 + i * 32))
    else:
        # Hovedmeny
        panel_w, panel_h = 160, 120
        panel_x, panel_y = WIDTH - panel_w - 20, HEIGHT - panel_h - 20
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (0, 0, 128), panel)
        pygame.draw.rect(screen, (255, 255, 255), panel, 2)

        for i, label in enumerate(menu_items):
            prefix = "▶ " if i == menu_index else "  "
            txt = font.render(prefix + label, True, (255, 255, 255))
            screen.blit(txt, (panel_x + 12, panel_y + 10 + i * 32))

def handle_menu_selection():
    global item_menu_open
    choice = menu_items[menu_index]
    if choice == "Fight":
        if game_active:
            maren_angrep()
            if game_active and fiende_hp > 0 and spiller_hp > 0:
                heks_angrep()
    elif choice == "Item":
        item_menu_open = True
    elif choice == "Run":
        do_run()

def handle_item_selection():
    global item_menu_open
    choice = item_options[item_index]
    if game_active:
        bruk_item(choice)
        if game_active and fiende_hp > 0 and spiller_hp > 0:
            heks_angrep()
    item_menu_open = False

# ---------- Main loop ----------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Tastestyring
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,):
                if item_menu_open:
                    item_menu_open = False
                else:
                    running = False
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if item_menu_open:
                    item_index = (item_index + 1) % len(item_options)
                else:
                    menu_index = (menu_index + 1) % len(menu_items)
            elif event.key in (pygame.K_UP, pygame.K_w):
                if item_menu_open:
                    item_index = (item_index - 1) % len(item_options)
                else:
                    menu_index = (menu_index - 1) % len(menu_items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if item_menu_open:
                    handle_item_selection()
                else:
                    handle_menu_selection()

        # Mus-klikk på meny
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if item_menu_open:
                panel_w, panel_h = 200, 100
                panel_x, panel_y = WIDTH - panel_w - 20, HEIGHT - panel_h - 20
                if panel_x <= event.pos[0] <= panel_x + panel_w and panel_y <= event.pos[1] <= panel_y + panel_h:
                    rel_y = event.pos[1] - panel_y
                    item_index = min(len(item_options) - 1, max(0, rel_y // 32))
                    handle_item_selection()
            else:
                panel_w, panel_h = 160, 120
                panel_x, panel_y = WIDTH - panel_w - 20, HEIGHT - panel_h - 20
                if panel_x <= event.pos[0] <= panel_x + panel_w and panel_y <= event.pos[1] <= panel_y + panel_h:
                    rel_y = event.pos[1] - panel_y
                    menu_index = min(len(menu_items) - 1, max(0, rel_y // 32))
                    handle_menu_selection()

    # Tegn alt
    screen.blit(bg, (0, 0))
    screen.blit(current_sprite, SPILLER_POS)
    screen.blit(fiende_sprite, FIENDE_POS)

    draw_labels()
    draw_textbox(textbox_text)
    draw_menu()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()