import pygame 
import os
import sys
from game import Block


#file_dir = os.path.dirname("TechWTimTutorial-onlineGame")
#sys.path.append(file_dir)
from Network import Network


width = height= 500
win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Client")

square_size = (width//10, int(height*.9)//10)
clientnumber = 0

    
def drawBoard(width,height):
    surf = pygame.surface.Surface((width,height))
    
    white = (255,255,255)
    grey = (105,105,105)
    
    surf.fill(white)
    
    col = width//10
    row = height//10
    for i in range(0,width,col):
        
        pygame.draw.line(surf, grey,start_pos=(i+col,0),end_pos=(i+col,height))

    for i in range(0,height,row):
        
        pygame.draw.line(surf, grey,start_pos=(0,i+row),end_pos=(width,i+row))
    return surf

 
def main():
    #pygame.init()
    run = True
    n = Network()
    print("made network")
    
    clock = pygame.time.Clock()
    
    game_board = drawBoard(width, int(height*.9))
    win.blit(game_board,(0,0))
    
    block_data = n.getBlock()
    print("here", block_data)
    startBlock = Block(block_data[1],(width//10)*3,(height//10)*3, block_data[0])
    
    player_num = block_data[4]
    
    dragging_list = pygame.sprite.Group()
    
    placed_list = pygame.sprite.Group()
    placed_list.add(startBlock)
    
    while run:
        
        
        end_turn = False
        if block_data[0] != startBlock.matrix:
            startBlock =  Block(block_data[1],(width//10)*3,(height//10)*3, block_data[0])

        if player_num != block_data[4]:
            
            startBlock.rect.x = block_data[2]
            startBlock.rect.y = block_data[3]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and player_num == block_data[4]:
                
                mouse_x, mouse_y = pygame.mouse.get_pos() 
                
                if startBlock.rect.collidepoint(mouse_x, mouse_y) and not startBlock.placed:
                    dragging_list.add(startBlock)
                    placed_list.remove(startBlock)
            
            elif event.type == pygame.MOUSEBUTTONUP and dragging_list.has(startBlock):
                placed_list.add(startBlock)
                dragging_list.empty()
                startBlock.placeBlock()
                
                end_turn = True
                
            elif event.type == pygame.MOUSEMOTION:
                dragging_list.update(event.rel)
        
        x, y = startBlock.rect.topleft
        n.send([x,y,end_turn])
        
          
        win.fill((255,255,255))      
        win.blit(game_board,(0,0))
        
        placed_list.draw(win)
        dragging_list.draw(win)
        pygame.display.update()
        
        clock.tick(60)
        
        block_data = n.connect()
main()