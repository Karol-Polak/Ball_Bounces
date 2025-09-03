# Ball Bounces

Gra 2D w Pythonie (Pygame), w której kilka piłek odbija się wewnątrz okręgu.  
Celem jest zdobycie **100 punktów** lub wyeliminowanie wszystkich przeciwników.

<img width="1000" height="929" alt="image" src="https://github.com/user-attachments/assets/758cecba-cfb4-4add-97cf-c92b65a9a2a8" />

---

## Zasady gry

- W grze bierze udział **2–4 piłki**.
- Każda piłka odbija się od ściany okręgu.  
  Przy każdym odbiciu tworzona jest linia (tzw. *anchor*) od punktu styku do piłki.
- **Przejęcia linii**:
  - jeśli piłka przeleci przez linię przeciwnika, przejmuje ją (dodaje anchor do siebie, przeciwnik traci),
  - przejęcie dodaje punkt przejmującemu i odejmuje przeciwnikowi.
- **Śmierć**:
  - jeśli piłka straci wszystkie swoje linie → ginie i znika z planszy.
  - zwycięża ostatnia żywa piłka.
- Alternatywne zwycięstwo: pierwsza piłka, która osiągnie **100 punktów**.

---

## Sterowanie

- **S** – start gry.  
- **R** – restart (nowa rozgrywka, ta sama liczba graczy).  
- **2 / 3 / 4** – wybór liczby graczy (tylko przed startem gry).  
- **ESC / Zamknięcie okna** – wyjście z gry.

---

## Wymagania

- Python 3.9+  
- [Pygame](https://www.pygame.org/)

Instalacja zależności:
```bash
pip install pygame
