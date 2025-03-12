import lskd, time, TexUI, random

last_key   = "d"
body       = ["<"] * 5
screen     = TexUI.Display(32, 16)
coordinate = [screen.width // 2, screen.height // 2]
food       = "@"

def create_food():
    global last_food_pos
    last_food_pos = [random.randint(1, screen.width - 2 - 1), random.randint(1, screen.height - 2 - 1 - 1)]

def draw_screen():
    screen.clear()
    screen.draw_box(0, 1, screen.width - 1, screen.height - 1, "#")
    screen.draw_char(last_food_pos[0] + 1, last_food_pos[1] + 2, food)

def update_snake(coor, body_type):
    coordinate[coor[0]] += coor[1]
    body.pop(0)
    body.append(body_type)

TexUI.clear_terminal()

create_food()
draw_screen()
screen.draw_str(0, 0, "Press enter to start")

screen.flush()
input()

while 1:
    if lskd.on_press():
        key = lskd.translate(lskd.char.get(), last_key)
        last_key = key if key != None else last_key

    draw_screen()
    screen.draw_str(0, 0, f"[Snake Length: {len(body)}]")

    if last_key == "ESC":
        exit("terminated")

    if last_key == "d" and body[-1] != ">":
        last_dir = last_key
        update_snake((0, 1), "<")

    elif last_key == "a" and body[-1] != "<":
        last_dir = last_key
        update_snake((0, -1), ">")

    elif last_key == "s" and body[-1] != "v":
        last_dir = last_key
        update_snake((1, 1), "^")

    elif last_key == "w" and body[-1] != "^":
        last_dir = last_key
        update_snake((1, -1), "v")
    else:
        update_snake(
            *{
                "d": ((0, 1), "<"),
                "a": ((0, -1), ">"),
                "s": ((1, 1), "^"),
                "w": ((1, -1), "v"),
            }.get(last_dir, ((0, 0), ""))
        )

    offset = [0, 0]
    for segment in body[: :-1]:
        current_cell = screen.get_char(coordinate[0] + offset[0], coordinate[1] + offset[1])
        if current_cell == food:
            body.insert(0, body[0])
            create_food()
        elif current_cell != screen.default_fill:
            input("end game")
            exit()

        screen.draw_char(coordinate[0] + offset[0], coordinate[1] + offset[1], "█")

        offset[0] += {"<": -1, ">": 1}.get(segment, 0)
        offset[1] += {"^": -1, "v": 1}.get(segment, 0)

    screen.flush(0, 0)

    # update speed
    time.sleep(1 / (7 + len(body) / 3))
