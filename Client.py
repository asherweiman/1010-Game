import pygame 
import sys
from game import Block, Game
from Network import Network


width = height= 500

square_size = (width//10, int(height*.9)//10)
clientnumber = 0
default_x = 250
default_y = 450


    
def draw_board(width,height):
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
    
    win = pygame.display.set_mode((width,height))
    clock = pygame.time.Clock()
    
    game = Game()
    game_board = draw_board(width, int(height*.9))
    win.blit(game_board,(0,0))
    game.board = n.recv_msg()
    game_board = game.drawBoard(game_board)
    
    
    block_data = n.recv_msg()
    print("here", block_data)
    startBlock = Block(block_data[1],(width//10)*3,(height//10)*3, block_data[0], default_x,default_y)
    
    pygame.display.set_caption(str(block_data[4]))
    
    player_num = block_data[4]
    print("I am: ", player_num)
    dragging_list = pygame.sprite.Group()
    
    placed_list = pygame.sprite.Group()
    placed_list.add(startBlock)
    
    while run:
         
        end_turn = False
        
        # start of new turn
        if block_data[0] != startBlock.matrix:
            print("new turn")
            placed_list.remove(startBlock)
            (x,y) = startBlock.rect.topleft
            game.placeBlock((y//45,x//50),startBlock)
            for i in game.board:
                print(i)
            lose_game = game.endTurn(startBlock)
            print("\n\n")
            for i in game.board:
                print(i)
            #print(lose_game)
            game_board = game.drawBoard(game_board)
            startBlock =  Block(block_data[1],(width//10)*3,(height//10)*3, block_data[0],default_x,default_y)
            placed_list.add(startBlock)
           
        # not this players turn only moves sprite around 
        if player_num != block_data[4]:
            
            startBlock.rect.x = block_data[2]
            startBlock.rect.y = block_data[3]
            startBlock.placeBlock()
          
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
                #placed_list.add(startBlock)
                dragging_list.empty()
                startBlock.placeBlock()
                 
                end_turn = True
                
            elif event.type == pygame.MOUSEMOTION:
                dragging_list.update(event.rel)
        
        x, y = startBlock.rect.topleft
        n.send([x,y,end_turn])
        
                
        # draw everything on screen   
        win.fill((255,255,255)) 
        win.blit(game_board,(0,0))
        
        placed_list.draw(win)
        dragging_list.draw(win)
        pygame.display.update()
        
        clock.tick(60)
        
        #print("before recv")
        block_data = n.recv_msg()
        #print(block_data)
        
        # handle invalid turns
        if end_turn and block_data[4] == player_num:
            startBlock.placed = False
            startBlock.rect.x = block_data[2]
            startBlock.rect.y = block_data[3]  
            placed_list.add(startBlock)   
            
       
    print("end game")   
    sys.exit()
       
main()