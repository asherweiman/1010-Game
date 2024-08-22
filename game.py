from random import randint,randrange
import pygame as pg

class Block(pg.sprite.Sprite):
    
    def __init__(self, color=(0,0,0), width = 0, height = 0, matrix = [],x=0,y=0):
        pg.sprite.Sprite.__init__(self)
        
        self.color = color
        
        if len(matrix) != 0:
            self.matrix = matrix
        else:
            self.matrix = self.genblock()
        
        self.placed = False
        
        self.width = width
        self.height = height *.9
        
        self.image = pg.surface.Surface([width,height],pg.SRCALPHA)
        self.draw_matrix()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    # draws block on sprite image surface
    def draw_matrix(self):
        
        # draw matrix 
        
        # set scaling for single squares
        w = self.width/3
        h = self.height/3
        grey = (105,105,105)
        
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):
                pg.draw.rect(self.image, self.color, pg.Rect(col*w,row*h,w,h))

        
        # draw top border line
        pg.draw.line(self.image,grey,start_pos=(0,0),end_pos=(len(self.matrix[0])*w,0))
                
        # draw left border line
        pg.draw.line(self.image,grey, start_pos=(0,0), end_pos=(0, len(self.matrix)*h))        
        
        # draw grid overtop 
        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):
                pg.draw.line(self.image,grey,start_pos=(col*w+w,row*h),end_pos=(col*w+w,row*h + h))
        
            pg.draw.line(self.image,grey,start_pos=(0,(row+1)*h),end_pos=((col+1)*w,(row+1)*h))
            
    def genblock(self): 
                 
        blockspace = [[],[],[]]
        row = 0 
        
        # fill in rows of block with 1s
        for row in blockspace:
            if randint(0,3) < 3:
                row.append(1)
                row *= randint(1,3)
            else:
                break
        
        # delete excess rows
        i = len(blockspace) - 1
        while len(blockspace[i]) == 0:
            if i == 0:
                blockspace[i].append(1)  
            else:
                blockspace.pop()
                i -= 1
                
        return blockspace

    def update(self,rel):
        
        self.rect.move_ip(rel)
        
    def placeBlock(self):
        
        self.rect.x = 50*(self.rect.x//50)
        self.rect.y = 45*(self.rect.y//45)
        self.placed = True
        
                    

class Game:
    
    def __init__(self) -> None:
        # migth not need this self.p1Move = None
        # might not need this self.p2Move = None
        # TODO self.ready = False
        self.board = [[0 for i in range(10)] for i in range(10)]
        self.totalmoves: int = 0
        # TODO 
        self.wins: int = 0
        
        # colors 
        self.color_pallete = [(255,255,255),
                              (0,0,0),
                              (35,110,35),
                              (188,210,208),
                              (210,208,188),
                              (93,87,107)]  
        self.player_turn = 0

    def connected(self):
        return self.ready

    def pickColor(self):
        return self.color_pallete[randint(2, len(self.color_pallete) - 1)]
    
    def drawBoard(self, win: pg.Surface):
        
        block_width = win.get_width()//10
        block_height = win.get_height()//10
        grey = (105,105,105)
        white = (255,255,255)
        win.fill((white))
        
        
        # draw blocks:
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                print("color: ", self.board[row][col])
                pg.draw.rect(win,
                             self.color_pallete[self.board[row][col]],
                             pg.Rect((col*block_width,row*block_height),(block_width,block_height)))
        
        # draw lines:
        
        for i in range(0,win.get_width(),block_width):
        
            pg.draw.line(win, grey,start_pos=(i+block_width,0),end_pos=(i+block_width,win.get_height()))

        for i in range(0,win.get_height(),block_height):
        
            pg.draw.line(win, grey,start_pos=(0,i+block_height),end_pos=(win.get_width(),i+ block_height))
        
        
        return win
    
    
    def notOccupied(self,row,col,block):
        out = True
        
        # outside of board
        if row + len(block) > len(self.board) or col+ len(block) > len(self.board):
            out = False 
        
        # inside of board
        else:
            i = 0
            while i < len(block) and i + row < len(self.board):
                j = 0
                while j < len(block[i]) and j + col < len(self.board):
                   
                    if block[i][j] > 0 and self.board[row+i][col+j] > 0:
                        return False
                    j += 1
                i += 1
                
        return out
     
    def placeBlock(self, top_left, block: Block) -> bool:
      
        block_matrix = block.matrix
        out = False
        (row,col) = top_left
        color_val = self.color_pallete.index(block.color)
        print(row,col)
        if (9 >= row >= 0) and (9 >= col>= 0):
            
            #print(self.notOccupied(row,col,block_matrix))
            
            if self.notOccupied(row,col,block_matrix):
                out = True
                i = 0
                while i < len(block_matrix) and i + row < len(self.board):
                    j = 0
                    while j < len(block_matrix[i]) and j + col < len(self.board):
                        if block_matrix[i][j] > 0:
                            self.board[row+i][col+j] = color_val
                        j += 1
                        
                    i += 1
                
        return out
        
    # handles clearing board and checking for available moves on the board
    def endTurn(self, block: Block) -> bool:
        
        # clear rows
        clear_row = [0]*10
        for row in range(len(self.board)):
            if self.board[row].count(0) == 0:
                self.board[row] = clear_row
                
        # clear cols
        for i in range(len(self.board[0])):
            clear = True
            if self.board[0][i] == 1:
                for row in self.board:
                    if row[i] == 0:
                        clear = False
                if clear:
                    for row in self.board:
                        row[i] = 0
        
        block_matrix = block.matrix 
        
        # check if there is an available move
        lose = True
        
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.notOccupied(row,col,block_matrix):
                    lose = False
                    break  
        return lose            
    
    
# testing game board  
"""pg.init()
g = Game()
b = Block(width=10,height=10)

for i in b.matrix:
    print(i)  
print("\n")
g.placeBlock((0,0),b)
for i in g.board:
    print(i)
    

win = pg.display.set_mode((500,500))
run = True
surf = pg.surface.Surface((500,450))
surf = g.drawBoard(surf)
win.blit(surf,(0,0))
while run:
    for event in pg.event.get():
        if event.type == pg.quit or event.type == pg.QUIT:
            run = False
    pg.display.update()
"""
