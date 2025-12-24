import random
import sys
import time
import pygame
from pygame.locals import *
from collections import deque
import threading

Screen_Height = 480
Screen_Width = 600
Size = 20
Line_Width = 1
Area_x = (0, Screen_Width // Size - 1)
Area_y = (2, Screen_Height // Size - 1)
Food_Style_List = [(10, (255, 100, 100)), (20, (100, 255, 100)), (30, (100, 100, 255))]
Light = (100, 100, 100)
Dark = (200, 200, 200)
Black = (0, 0, 0)
Red = (200, 30, 30)
Back_Ground = (40, 40, 60)

lock = threading.Lock()

def print_txt(screen, font, x, y, text, fcolor=(255, 255, 255)):
    Text = font.render(text, True, fcolor)
    screen.blit(Text, (x, y))

def init_snake():
    snake = deque()
    for i in range(5):
        snake.append((i, Area_y[0]))
    return snake

def create_food(snake, foods):
    while len(foods) < 10:
        food_x = random.randint(Area_x[0], Area_x[1])
        food_y = random.randint(Area_y[0], Area_y[1])
        food = (food_x, food_y)
        if food not in snake and food not in foods:
            food_style = Food_Style_List[random.randint(0, 2)]
            foods.append((food, food_style))

def food_style():
    return Food_Style_List[random.randint(0, 2)]

def game_logic(screen, font1, font2, snake, foods, pos, score, orispeed, speed, game_over, game_start, pause):
    while True:
        cur_time = time.time()
        if cur_time - last_move_time > speed:
            with lock:
                if not pause:
                    last_move_time = cur_time
                    cur_head = snake[0]
                    next_s = (cur_head[0] + pos[0], cur_head[1] + pos[1])
                    if next_s in foods:
                        snake.appendleft(next_s)
                        score += foods[foods.index(next_s)][1][0]
                        foods.remove(next_s)
                        create_food(snake, foods)
                        speed = orispeed - 0.03 * (score // 100)
                    else:
                        if Area_x[0] <= next_s[0] <= Area_x[1] and Area_y[0] <= next_s[1] <= Area_y[1] and next_s not in snake:
                            snake.appendleft(next_s)
                            snake.pop()
                        else:
                            game_over = True

                    if len(snake) > 10 and speed > 0.3:
                        speed = 0.3
                    elif len(snake) > 30 and speed > 0.15:
                        speed = 0.15

            screen.fill(Back_Ground)
            for x in range(Size, Screen_Width, Size):
                pygame.draw.line(screen, Black, (x, Area_y[0] * Size), (x, Screen_Height), Line_Width)
            for y in range(Area_y[0] * Size, Screen_Height, Size):
                pygame.draw.line(screen, Black, (0, y), (Screen_Width, y), Line_Width)

            for food, style in foods:
                pygame.draw.rect(screen, style[1], (food[0] * Size, food[1] * Size, Size, Size), 0)

            for s in snake:
                pygame.draw.rect(screen, Dark, (s[0] * Size + Line_Width, s[1] * Size + Line_Width,
                                               Size - Line_Width * 2, Size - Line_Width * 2), 0)

            print_txt(screen, font1, 30, 7, f'速度: {score // 100}')
            print_txt(screen, font1, 450, 7, f'得分: {score}')

            if game_over:
                if game_start:
                    fwidth, fheight = font2.size('GAME OVER')
                    print_txt(screen, font2, (Screen_Width - fwidth) // 2, (Screen_Height - fheight) // 2, 'GAME OVER', Red)

            pygame.display.update()

            time.sleep(0.01)  # 防止游戏逻辑线程占用过多CPU资源

def main():
    global snake, foods, pos, score, orispeed, speed, game_over, game_start, last_move_time, pause

    pygame.init()
    screen = pygame.display.set_mode((Screen_Width, Screen_Height))
    pygame.display.set_caption('贪吃蛇')
    font1 = pygame.font.SysFont('SimHei', 24)
    font2 = pygame.font.SysFont(None, 72)

    snake = init_snake()
    foods = []
    create_food(snake, foods)
    pos = (1, 0)
    game_over = True
    game_start = False
    score = 0
    orispeed = 0.3
    speed = orispeed
    last_move_time = None
    pause = False

    game_thread = threading.Thread(target=game_logic, args=(screen, font1, font2, snake, foods, pos, score, orispeed, speed, game_over, game_start, pause))
    game_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                with lock:
                    if event.key == K_RETURN:
                        if game_over:
                            game_start = True
                            game_over = False
                            snake = init_snake()
                            foods = []
                            create_food(snake, foods)
                            pos = (1, 0)
                            score = 0
                            last_move_time = time.time()
                            pause = False

                    elif event.key == K_SPACE:
                        if not game_over:
                            pause = not pause

                    elif event.key in (K_UP, K_w):
                        if pos != (0, 1):
                            pos = (0, -1)

                    elif event.key in (K_DOWN, K_s):
                        if pos != (0, -1):
                            pos = (0, 1)

                    elif event.key in (K_LEFT, K_a):
                        if pos != (1, 0):
                            pos = (-1, 0)

                    elif event.key in (K_RIGHT, K_d):
                        if pos != (-1, 0):
                            pos = (1, 0)

                    elif event.key == K_ESCAPE:
                        sys.exit()


if __name__ == '__main__':
    main(intitle='贪吃蛇')
