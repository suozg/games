#!/usr/bin/env python3
import sys
import termios
import tty

# Константи для ігрових об'єктів
FLOOR = 0
WALL = 1
PLAYER = 2
BOX = 3
TARGET = 4
BOXTARGET = 5

# Рівні гри
LEVELS = [
    [
        "..111...",
        "..141...",
        "..1 1111",
        "1113 341",
        "14 32111",
        "111131..",
        "...141..",
        "...111..",
    ],
    [
        "11111111",
        "1 4   21",
        "1   43 1",
        "111 3111",
        "..1  1..",
        "..1  1..",
        "..1111..",
        "........",
    ],
    [
        "....1111",
        "..111  1",
        "111    1",
        "14  3121",
        "1443 3 1",
        "1114 3 1",
        "..111  1",
        "....1111",
    ],
]

# Символи для відображення в терміналі
SYMBOLS = {
    0: " ",  # Підлога
    1: "█",  # Стіна
    2: "@",  # Гравець
    3: "▤",  # Ящик
    4: "·",  # Ціль
    5: "▣",  # Ящик на цілі
}


def getch():
    """Зчитування натискання клавіші без потреби натискати Enter"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main():
    level_idx = 0

    while level_idx < len(LEVELS):
        raw_map = LEVELS[level_idx]
        max_y = len(raw_map)
        max_x = len(raw_map[0])

        map2 = [[0] * max_x for _ in range(max_y)]
        game_map = [[0] * max_x for _ in range(max_y)]

        px, py = 0, 0

        for y in range(max_y):
            for x in range(max_x):
                char = raw_map[y][x]
                if char in ". ":
                    val = FLOOR
                else:
                    val = int(char)
                map2[y][x] = val
                if val == PLAYER:
                    px, py = x, y

        def reset_level():
            nonlocal px, py
            for y in range(max_y):
                for x in range(max_x):
                    d = map2[y][x]
                    if d == TARGET:
                        d = FLOOR
                    if d == PLAYER:
                        px, py = x, y
                        d = FLOOR
                    game_map[y][x] = d
            game_map[py][px] = PLAYER

        reset_level()

        while True:
            # Очищення екрана та вивід інформації
            print("\033[H\033[J", end="")
            print(f"=== SOKOBAN === \nРІВЕНЬ {level_idx + 1}")
            print("Керування: Стрілки | 'q' — Вихід | Пробіл — Перезапуск\n")

            # Рендеринг поля
            for y in range(max_y):
                line = ""
                for x in range(max_x):
                    c = game_map[y][x]
                    if map2[y][x] == TARGET:
                        if c == FLOOR:
                            c = TARGET
                        elif c == BOX:
                            c = BOXTARGET
                    line += SYMBOLS.get(c, " ")
                print(line)

            # Перевірка виграшу
            won = all(
                map2[y][x] != TARGET or game_map[y][x] == BOX
                for y in range(max_y)
                for x in range(max_x)
            )

            if won:
                print("\nРівень пройдено! Натисніть будь-яку клавішу...")
                getch()
                break

            # Читання введення
            key = getch()
            
            # Вихід по клавіші 'q' або 'Q'
            if key in ("q", "Q"):
                print("\nДякуємо за гру!")
                sys.exit(0)
            elif key == " ":
                reset_level()
                continue

            px1, py1 = px, py
            if key == "\x1b[A":  # Вгору
                py1 -= 1
            elif key == "\x1b[B":  # Вниз
                py1 += 1
            elif key == "\x1b[D":  # Вліво
                px1 -= 1
            elif key == "\x1b[C":  # Вправо
                px1 += 1
            else:
                continue

            # Перевірка меж карти
            if not (0 <= px1 < max_x and 0 <= py1 < max_y):
                continue

            # Пересування ящика
            if game_map[py1][px1] == BOX:
                px2 = px1 * 2 - px
                py2 = py1 * 2 - py
                if 0 <= px2 < max_x and 0 <= py2 < max_y:
                    if game_map[py2][px2] == FLOOR:
                        game_map[py2][px2] = BOX
                        game_map[py1][px1] = FLOOR

            # Пересування гравця
            if game_map[py1][px1] == FLOOR:
                game_map[py][px] = FLOOR
                px, py = px1, py1
                game_map[py][px] = PLAYER

        level_idx += 1

    print("Вітаю! Ви пройшли всі рівні!")


if __name__ == "__main__":
    main()
