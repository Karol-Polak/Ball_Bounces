import math
import random
import pygame

# ---------- Ustawienia ----------
W, H = 1000, 900
CENTER = pygame.math.Vector2(W // 2, H // 2)
ARENA_R = 320
BALL_R = 12
FPS = 120

TARGET_HITS = 100                # punkty do wygranej
STEAL_RADIUS = BALL_R + 4        # „grubość” chwytania
STEAL_SUBDIVS = 12               # ile mikro-kroków toru piłki sprawdzamy w klatce
MIN_BALLS, MAX_BALLS = 2, 4

BG = (10, 10, 12)
WHITE = (240, 240, 240)
PANEL_BG = (0, 0, 0, 160)
BALL_COLORS = [
    (60, 130, 255),   # Niebieski
    (40, 200, 90),    # Zielony
    (255, 170, 35),   # Pomarańczowy
    (220, 70, 200),   # Różowy
]
LINE_ALPHA = 180

NAME_BY_INDEX = ["Niebieski", "Zielony", "Pomarańczowy", "Różowy"]

#---------- Geometria ----------
def reflect(v: pygame.math.Vector2, normal: pygame.math.Vector2) -> pygame.math.Vector2:
    n = normal.normalize()
    return v - 2 * v.dot(n) * n

def clamp_inside_circle(pos, center, arena_r, ball_r):
    to_pos = pos - center
    dist = to_pos.length()
    if dist + ball_r > arena_r:
        n = to_pos.normalize() if dist != 0 else pygame.math.Vector2(1, 0)
        pos = center + n * (arena_r - ball_r - 0.5)
        return True, n, pos
    return False, None, pos

def resolve_ball_collision(p1, p2):
    if not (p1.alive and p2.alive):
        return
    delta = p2.pos - p1.pos
    dist = delta.length()
    min_dist = p1.r + p2.r
    if dist == 0:
        delta = pygame.math.Vector2(1, 0)
        dist = 1.0

    if dist < min_dist:
        n = delta.normalize()
        overlap = (min_dist - dist) * 0.5
        p1.pos -= n * overlap
        p2.pos += n * overlap

        v1n = p1.vel.dot(n)
        v2n = p2.vel.dot(n)
        p1.vel += (v2n - v1n) * n
        p2.vel += (v1n - v2n) * n

def point_segment_distance(p, a, b):
    ab = b - a
    ab2 = ab.dot(ab)
    if ab2 < 1e-12:
        return (p - a).length()
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab2))
    proj = a + ab * t
    return (p - proj).length()

# ---------- Obiekty gry ----------
class Ball:
    def __init__(self, color, name, speed_range=(180, 260)):
        self.base_color = color
        self.color = color
        self.name = name
        self.r = BALL_R
        ang = random.uniform(0, 2 * math.pi)
        rad = random.uniform(0, ARENA_R - 4 * BALL_R)
        self.pos = CENTER + pygame.math.Vector2(math.cos(ang), math.sin(ang)) * rad
        ang_v = random.uniform(0, 2 * math.pi)
        sp = random.uniform(*speed_range)
        self.vel = pygame.math.Vector2(math.cos(ang_v), math.sin(ang_v)) * sp

        self.prev_pos = self.pos.copy()
        self.score = 0                # liczba posiadanych linii (punktów)
        self.hit_points = []          # kotwice na obwodzie
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.prev_pos = self.pos.copy()
        self.pos += self.vel * dt

        # kolizja ze ścianą okręgu = odbicie + linia
        collided, normal, new_pos = clamp_inside_circle(self.pos, CENTER, ARENA_R, self.r)
        if collided:
            self.pos = new_pos
            self.vel = reflect(self.vel, normal)
            anchor = CENTER + normal * ARENA_R
            self.hit_points.append(anchor)
            self.score += 1

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, self.pos, self.r)

# ---------- Rysowanie ----------
def draw_arena(surface):
    pygame.draw.circle(surface, WHITE, CENTER, ARENA_R, 3)

def draw_connections(surface, balls):
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for b in balls:
        if not b.alive:
            continue
        col = b.base_color
        for anchor in b.hit_points:
            pygame.draw.line(layer, (*col, LINE_ALPHA), anchor, b.pos, 2)
    surface.blit(layer, (0, 0))

def draw_panel(surface, balls, font):
    # parametry wyglądu
    PAD_X = 12         # padding wewnętrzny panelu (lewo/prawo)
    PAD_Y = 8          # padding góra/dół
    ICON_R = 7         # promień kółka
    ICON_W = ICON_R * 2 + 2
    GAP_ICON_TEXT = 8  # odstęp kółko–tekst
    GAP_ITEMS = 24     # odstęp między graczami

    # przygotuj napisy i policz szerokości
    items = []
    total_w = PAD_X * 2
    max_h = 0
    for b in balls:
        label = f"{b.name}: {b.score}" + ("" if b.alive else " (X)")
        text = font.render(label, True, (220, 220, 220))
        item_w = ICON_W + GAP_ICON_TEXT + text.get_width()
        items.append((b, text, item_w))
        total_w += item_w + GAP_ITEMS
        max_h = max(max_h, text.get_height())

    if items:
        total_w -= GAP_ITEMS   # ostatni element nie ma odstępu po prawej

    panel_w = total_w
    panel_h = PAD_Y * 2 + max(ICON_W, max_h)

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill(PANEL_BG)

    # rysowanie elementów obok siebie
    x = PAD_X
    y_center = panel_h // 2
    for b, text, item_w in items:
        # kółko
        circ = pygame.Surface((ICON_W, ICON_W), pygame.SRCALPHA)
        pygame.draw.circle(
            circ,
            b.base_color if b.alive else (120, 120, 120),
            (ICON_W // 2, ICON_W // 2),
            ICON_R
        )
        panel.blit(circ, (x, y_center - ICON_W // 2))
        x += ICON_W + GAP_ICON_TEXT
        # tekst
        panel.blit(text, (x, y_center - text.get_height() // 2))
        x += text.get_width() + GAP_ITEMS

    # wyśrodkuj panel u góry
    surface.blit(panel, ((W - panel_w) // 2, 12))


def draw_centered_colored_win(screen, font, winner_ball):
    t1 = font.render("Wygrywa ", True, WHITE)
    t2 = font.render(winner_ball.name, True, winner_ball.base_color)
    t3 = font.render("!", True, WHITE)
    total_w = t1.get_width() + t2.get_width() + t3.get_width()
    x = (W - total_w) // 2
    y = H // 2 - t1.get_height() // 2
    screen.blit(t1, (x, y)); x += t1.get_width()
    screen.blit(t2, (x, y)); x += t2.get_width()
    screen.blit(t3, (x, y))

# Napisy poza okręgiem
def y_above_circle(text_h, margin=8):
    return max(10, int(CENTER.y - ARENA_R - text_h - margin))

def y_below_circle(text_h, margin=12):
    y = int(CENTER.y + ARENA_R + margin)
    if y + text_h <= H - 10:
        return y
    return y_above_circle(text_h, margin + 4)

# ---------- Przejmowanie linii + „śmierć kulki” ----------
def process_steals_and_collect_deaths(balls):
    to_remove = set()

    # snapshot indeksów żywych
    alive_indices = [idx for idx, b in enumerate(balls) if b.alive]

    for i in alive_indices:
        bi = balls[i]
        if not bi.alive:
            continue
        for j in alive_indices:
            if i == j:
                continue
            bj = balls[j]
            if not bj.alive or j in to_remove:
                continue

            k = 0
            while k < len(bj.hit_points):
                anchor = bj.hit_points[k]
                stolen = False

                for s in range(STEAL_SUBDIVS + 1):
                    t = s / float(STEAL_SUBDIVS)
                    p = bi.prev_pos * (1 - t) + bi.pos * t
                    end = bj.pos
                    if point_segment_distance(p, anchor, end) <= STEAL_RADIUS:
                        # przejęcie anchoru
                        bi.hit_points.append(anchor)
                        bj.hit_points.pop(k)
                        bi.score += 1
                        bj.score = max(0, bj.score - 1)
                        stolen = True

                        if len(bj.hit_points) == 0:
                            to_remove.add(j)
                        break

                if not stolen:
                    k += 1

    return sorted(to_remove)

# ---------- Pętla gry ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pierwsze 100 punktów wygrywa")
    clock = pygame.time.Clock()
    big = pygame.font.SysFont("Arial", 44, bold=True)
    small = pygame.font.SysFont("Arial", 22)

    current_players = 2  # domyślnie 2

    def new_balls(n):
        balls = []
        for i in range(n):
            color = BALL_COLORS[i % len(BALL_COLORS)]
            name = NAME_BY_INDEX[i % len(NAME_BY_INDEX)]
            balls.append(Ball(color, name))
        return balls

    balls = new_balls(current_players)
    winner_ball = None
    started = False  # start po S

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- zdarzenia ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    balls = new_balls(current_players)
                    winner_ball = None
                    started = False
                if e.key == pygame.K_s:
                    if winner_ball is None:
                        started = True
                # wybór liczby graczy 2-4
                if winner_ball is None and not started:
                    if e.key == pygame.K_2:
                        current_players = 2
                        balls = new_balls(current_players)
                    elif e.key == pygame.K_3:
                        current_players = 3
                        balls = new_balls(current_players)
                    elif e.key == pygame.K_4:
                        current_players = 4
                        balls = new_balls(current_players)

        # --- aktualizacja ---
        if started and winner_ball is None:
            # ruch tylko żywych
            for b in balls:
                if b.alive:
                    b.update(dt)

            # kolizje między ŻYWYMI kulkami
            for a in range(len(balls)):
                for b in range(a + 1, len(balls)):
                    resolve_ball_collision(balls[a], balls[b])

            to_remove = process_steals_and_collect_deaths(balls)

            # usuwanie martwych KULEK z planszy
            if to_remove:
                for idx in to_remove:
                    balls[idx].alive = False
                for idx in reversed(to_remove):
                    del balls[idx]

            # zwycięzca na zasadzie „ostatni żywy”
            alive_now = [b for b in balls if b.alive]
            if len(alive_now) == 1:
                winner_ball = alive_now[0]
                started = False
            elif len(alive_now) == 0:
                # skrajny przypadek: wszyscy padli jednocześnie – brak zwycięzcy
                started = False

            # alternatywne zwycięstwo na punkty
            if winner_ball is None:
                for b in alive_now:
                    if b.score >= TARGET_HITS:
                        winner_ball = b
                        started = False
                        break

        # --- rysowanie ---
        screen.fill(BG)
        draw_arena(screen)
        draw_connections(screen, balls)
        for b in balls:
            if b.alive:
                b.draw(screen)
        draw_panel(screen, balls, small)

        title = small.render(
            "Pierwszy do 100 pkt wygrywa!  (2/3/4 = liczba kulek, S = start, R = restart)",
            True, WHITE
        )
        screen.blit(title, ((W - title.get_width()) // 2,
                            y_above_circle(title.get_height(), margin=10)))

        if not started and winner_ball is None:
            hint = big.render(f"Naciśnij S aby rozpocząć  ({len(balls)} graczy)", True, WHITE)
            screen.blit(hint, ((W - hint.get_width()) // 2,
                               y_below_circle(hint.get_height(), margin=14)))

        if winner_ball is not None:
            draw_centered_colored_win(screen, big, winner_ball)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
