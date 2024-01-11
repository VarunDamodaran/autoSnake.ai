import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

#initialize
pygame.init()
font = pygame.font.Font('arial.ttf', 25)

#for directions
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# some constants and colours
WHITE = (255,255,255)
RED = (200,0,0)
GREEN = (31, 140, 44)
DARK_GREEN = (255, 87, 51)
BLUE = (24, 39, 204)
DARK_BLUE = (11, 21, 133)
BLACK = (0,0,0)

BLOCK_SZ = 20
VEL= 40

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        #3 blocks initially as the body
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SZ, self.head.y),
                      Point(self.head.x-(2*BLOCK_SZ), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SZ )//BLOCK_SZ )*BLOCK_SZ
        y = random.randint(0, (self.h-BLOCK_SZ )//BLOCK_SZ )*BLOCK_SZ
        self.food = Point(x, y)
        if self.food in self.snake:
            #case if food spawns on the snake body, try again
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # getting the key which player pressed
        for event in pygame.event.get():
            #quit case
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        #move
        self._move(action) # update head
        self.snake.insert(0, self.head)
        
        # game over case
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            #if for a long time, doesnt eat or doesnt die, we need to terminate, len factor is to give more time for larger snakes
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # new food/moving
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop() #move (remove the last part)
        
        #update display and clock
        self._update_ui()
        self.clock.tick(VEL)

        #return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits the boundary
        if pt.x > self.w - BLOCK_SZ or pt.x < 0 or pt.y > self.h - BLOCK_SZ or pt.y < 0:
            return True
        # hits its own body
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SZ, BLOCK_SZ))
            pygame.draw.rect(self.display, DARK_GREEN, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SZ, BLOCK_SZ))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        #has 3 actions straight, left, right

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]): #straight
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):#right
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] #turned right so right->down->left->up
        else: #left
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] #counter cw : right->up->left->down

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SZ
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SZ
        elif self.direction == Direction.DOWN:
            y += BLOCK_SZ
        elif self.direction == Direction.UP:
            y -= BLOCK_SZ

        self.head = Point(x, y)