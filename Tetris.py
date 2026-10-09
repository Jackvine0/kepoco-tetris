Kfrom kepoco import display, buttonB, buttonA, buttonL, buttonR, buttonD, buttonC, Sprite
from random import choice
import utime

score = 0
level = 0
lines_cleared_total = 0
game_over = False

CELL_SIZE = 3
GRID_W = 11
GRID_H = 13

grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]

OShape = Sprite(3,3, bytearray([7,7,7]), 0,0,0,0,0)

SHAPES = [
    [(0,0),(0,1),(0,2),(0,3)],  # I
    [(0,0),(1,0),(0,1),(1,1)],  # O
    [(0,0),(1,0),(2,0),(1,1)],  # T
    [(0,0),(0,1),(0,2),(1,2)],  # L
    [(1,0),(1,1),(1,2),(0,2)],  # J
    [(1,0),(2,0),(0,1),(1,1)],  # S
    [(0,0),(1,0),(1,1),(2,1)],  # Z
]

piece_cells = []
piece_x = 0
piece_y = 0

next_piece = choice(SHAPES)

fall_speed = 500
last_fall = utime.ticks_ms()

soft_drop_delay = 80
soft_drop_last = 0

#functions

def draw_base_layout():
    display.fill(display.BLACK)
    display.setFont("/lib/font3x5.bin",3,5,1)
    display.drawRectangle(1,0,35,40,display.WHITE)
    display.drawText("Score:",38,0,display.WHITE)
    display.drawText("{:06d}".format(score),38,7,display.WHITE)
    display.drawText("Next:",38,14,display.WHITE)
    display.drawText("Level {}".format(level),38,34,display.WHITE)

def draw_game_over_screen():
    display.fill(display.BLACK)
    display.setFont("/lib/font3x5.bin",3,5,1)
    display.drawText("GAME OVER", 6, 14, display.WHITE)
    display.drawText("Score: {}".format(score), 6, 24, display.WHITE)
    display.update()

def draw_block_cell(gx, gy):
    OShape.x = 2 + gx * 3
    OShape.y = gy * 3
    display.drawSprite(OShape)

def draw_grid():
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x]:
                draw_block_cell(x, y)

def draw_piece():
    for ox, oy in piece_cells:
        draw_block_cell(piece_x + ox, piece_y + oy)

def draw_next_piece():
    px0 = 38
    py0 = 20
    for ox, oy in next_piece:
        OShape.x = px0 + ox * 4
        OShape.y = py0 + oy * 4
        display.drawSprite(OShape)


def can_shape_fit(cells, base_x, base_y):
    for ox, oy in cells:
        gx = base_x + ox
        gy = base_y + oy
        if gx < 0 or gx >= GRID_W:
            return False
        if gy < 0 or gy >= GRID_H:
            return False
        if grid[gy][gx]:
            return False
    return True

def lock_piece():
    for ox, oy in piece_cells:
        grid[piece_y + oy][piece_x + ox] = 1

def spawn_piece():
    global piece_cells, piece_x, piece_y, next_piece, game_over
    piece_cells = [(x, y) for (x, y) in next_piece]
    piece_x = GRID_W // 2 - 1
    piece_y = 0
    next_piece = choice(SHAPES)
    if not can_shape_fit(piece_cells, piece_x, piece_y):
        game_over = True

def clear_lines():
    global grid, score, level, lines_cleared_total
    new_rows = []
    cleared = 0

    for y in range(GRID_H):
        if all(grid[y][x] == 1 for x in range(GRID_W)):
            cleared += 1
        else:
            new_rows.append(grid[y])

    while len(new_rows) < GRID_H:
        new_rows.insert(0, [0]*GRID_W)
    grid = new_rows

    if cleared:
        lines_cleared_total += cleared
        if cleared == 1: base = 40
        elif cleared == 2: base = 100
        elif cleared == 3: base = 300
        elif cleared == 4: base = 1200
        else: base = 0
        score += base * (level + 1)
        update_level()

def update_level():
    global level, fall_speed, lines_cleared_total
    new_level = lines_cleared_total // 10
    if new_level != level:
        level = new_level
        fall_speed = max(100, 500 - level * 30)

def rotate_cells(cells):
    xs = [x for x,y in cells]
    ys = [y for x,y in cells]
    min_x, min_y = min(xs), min(ys)
    norm = [(x-min_x, y-min_y) for x,y in cells]
    w = max(x for x,y in norm) + 1
    h = max(y for x,y in norm) + 1
    rot = [(h-1-y, x) for x,y in norm]
    min_rx = min(x for x,y in rot)
    min_ry = min(y for x,y in rot)
    return [(x-min_rx, y-min_ry) for x,y in rot]

def try_rotate_piece():
    global piece_cells, piece_x
    rotated = rotate_cells(piece_cells)
    for dx in (0, -1, 1):
        if can_shape_fit(rotated, piece_x + dx, piece_y):
            piece_x += dx
            piece_cells = rotated
            return


spawn_piece()

#game loop

while True:

  
    if game_over:
        draw_game_over_screen()
        if buttonB.justPressed():
            break
        continue

    
    if buttonB.justPressed():
        break     

        continue

    

    draw_base_layout()
    draw_grid()
    draw_piece()
    draw_next_piece()

    now = utime.ticks_ms()


    if utime.ticks_diff(now, last_fall) > fall_speed:
        if can_shape_fit(piece_cells, piece_x, piece_y+1):
            piece_y += 1
        else:
            lock_piece()
            clear_lines()
            spawn_piece()
        last_fall = now

    
    if buttonD.pressed():
        if utime.ticks_diff(now, soft_drop_last) > soft_drop_delay:
            if can_shape_fit(piece_cells, piece_x, piece_y+1):
                piece_y += 1
            soft_drop_last = now

    
    if buttonL.justPressed() and can_shape_fit(piece_cells, piece_x-1, piece_y):
        piece_x -= 1
    if buttonR.justPressed() and can_shape_fit(piece_cells, piece_x+1, piece_y):
        piece_x += 1

    
    if buttonA.justPressed():
        try_rotate_piece()

    display.update()
