import pygame
import time
import os
import sys


file_dir = os.path.dirname("TechWTimTutorial-onlineGame")
sys.path.append(file_dir)
from game import Game,Block

class GameBoard:
    
    def __init__(self,win):
        
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.color = (255,255,255)
        win.fill(self.color)
        self.drawGrid(win)
        pygame.display.update()
        
    def drawGrid(self, surface):
            width = pygame.Surface.get_width(surface)
            height = int(pygame.Surface.get_height(surface) * .9)
            grey = (105,105,105)
            
            col = width//10
            row = height//10
            for i in range(0,width,col):
                
                pygame.draw.line(surface, grey,start_pos=(i+col,0),end_pos=(i+col,height))

            for i in range(0,height,row):
                
                pygame.draw.line(surface, grey,start_pos=(0,i+row),end_pos=(width,i+row))

width = height = 500
win = pygame.display.set_mode((width,height))
pygame.display.set_caption("test game board")

sprites_list = pygame.sprite.Group()

width = pygame.Surface.get_width(win)//10
height = pygame.Surface.get_height(win)//10

b = Block(width=width*3,height=height*3)


sprites_list.add(b)

G = GameBoard(win)
run = True 


while run:
    for event in pygame.event.get():
        
        if event.type == pygame.quit or event.type == pygame.QUIT:
            run = False
    
    b.draw_sprite(50,50)
    sprites_list.update()
    sprites_list.draw(win)
    pygame.display.update()
    
    
pygame.quit()
    