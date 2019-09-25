import colorama
from colorama import Fore, Back, Style
from player import Player
from piece import Piece
from queen_piece import Queen_piece
from square import Square
import os
#Class of board
class Board:
    def __init__(self,size_m = 8):
        self.matrix = []
        self.size_m = size_m

    def generate_squares(self,player1,player2):
        i = True
        for y in range(0,self.size_m):
            aux = []
            x = 0
            while x < self.size_m:
                if y < (self.size_m/2) -1 or y >= (self.size_m/2) + 1:                        
                    if i:
                        aux.append(Square(Fore.WHITE))
                        i = False
                    else:
                        if y > self.size_m/2:
                            player1.add_piece(Piece(player1.get_player_color()))
                            aux.append(Square(Fore.RED,player1.get_last_piece()))
                        else:
                            player2.add_piece(Piece(player2.get_player_color()))
                            aux.append(Square(Fore.RED,player2.get_last_piece()))
                        i = True
                else:
                    if i:
                        aux.append(Square(Fore.WHITE))
                        i = False
                    else:
                        aux.append(Square(Fore.RED))   
                        i = True
                x += 1
            if i:
                i = False
            else:
                i = True
            self.matrix.append(aux)

    def draw_matrix(self):
        clear = lambda: os.system('clear')
        clear()
        draw_b = 'x→ '
        reset = Style.RESET_ALL
        con = 0
        for a in range(1,self.size_m+1):
            draw_b += str(a) + ' '
        draw_b += ' y↓'
        draw_b += '\n'
        for row in self.matrix:
            draw_b += '   '
            for col in row:
                if col.is_piece_inside():
                    piece_string = col.get_piece().get_character() +' '
                    draw_b += col.piece_color() + piece_string+ reset
                else:
                    draw_b += col.color + '■ '+ reset
            con += 1
            draw_b += '|'+str(con) +'\n'
        print(draw_b)

    def move_piece(self,from_x,from_y,to_x,to_y,playing,opponent):
        
        dif_y,dir_y = self.difference_between(from_y,to_y), self.direction(from_y,to_y)
        dif_x,dir_x = self.difference_between(from_x,to_x), self.direction(from_x,to_x)

        if not self.verify_moves(from_x,from_y,to_x,to_y,playing,dif_x,dif_y,dir_y):
            return self.wrong(playing)

        if dif_x == 2:
            if not self.piece_can_eat(from_x,from_y,to_x,to_y,playing,dir_x,dir_y):
                return self.wrong(playing)
            opponent.remove_piece(self.matrix[to_y - dir_y][to_x - dir_x].get_piece())
            self.matrix[to_y - dir_y][to_x - dir_x].deallocate_piece()
            self.matrix[to_y][to_x].assign_piece(self.matrix[from_y][from_x].piece)
            self.matrix[from_y][from_x].deallocate_piece()
            if self.piece_can_eat_after_eat(to_x,to_y,playing) != []:
                self.draw_matrix()
                return playing
        else:
            self.matrix[to_y][to_x].assign_piece(self.matrix[from_y][from_x].piece)
            self.matrix[from_y][from_x].deallocate_piece()
        become_queen = to_y == 0 if playing.get_player_dir() == -1 and isinstance(self.matrix[to_y][to_x].get_piece(),Piece) else to_y == self.size_m -1
        if become_queen:
            playing.remove_piece(self.matrix[to_y][to_x].get_piece())
            new_queen = Queen_piece(self.matrix[to_y][to_x].piece_color())
            playing.add_piece(new_queen)
            self.matrix[to_y][to_x].deallocate_piece()
            self.matrix[to_y][to_x].assign_piece(new_queen)
        self.draw_matrix()
        return opponent        

    def wrong(self,pt,message = 'Wrong coordinates'):
        self.draw_matrix()
        print(message)
        return pt
    
    def verify_moves(self,from_x,from_y,to_x,to_y,playing,dif_x,dif_y,dir_y):
        
        if dif_x == 0 or dif_y == 0 or not self.coordinates_is_in_range(from_x,from_y) or not self.coordinates_is_in_range(to_x,to_y):
            return False
        
        if not self.matrix[from_y][from_x].is_piece_inside():
            return False

        if self.matrix[from_y][from_x].get_piece() not in playing.get_list_pieces():
            return False

        if self.matrix[to_y][to_x].is_piece_inside():
            return False
        
        if dif_x > 2 or dif_y > 2 or dif_x != dif_y:
            return False
        
        if not isinstance(self.matrix[from_y][from_x].get_piece(),Queen_piece) and dir_y != playing.get_player_dir():
            return False
        return True


    def verify_forced_movements(self,playing):
        forced = []
        change_y = 2 if playing.get_player_dir() == 1 else -2
        index_row = 0
        while index_row < self.size_m:
            index_col = 0
            while index_col < len(self.matrix[index_row]):
                forced = self.add_forced_movements(index_col,index_row,change_y,playing,forced)
                if isinstance(self.matrix[index_row][index_col].get_piece(),Queen_piece):
                    forced = self.add_forced_movements(index_col,index_row,change_y * -1,playing,forced)
                index_col += 1
            index_row += 1
        return forced
    
    def add_forced_movements(self,index_col,index_row,change_y,playing,forced):
        to_x = index_col + 2
        to_y = index_row + change_y
        dif_x,dif_y,dir_x,dir_y = self.difference_between_and_direction(index_col,index_row,to_x,to_y)

        if self.verify_moves(index_col,index_row,to_x,to_y,playing,dif_x,dif_y,dir_y):
    
            if self.piece_can_eat(index_col,index_row,to_x,to_y,playing,dir_x,dir_y):
                forced.append([index_col,index_row,to_x,to_y])
    
        to_x = index_col - 2
        dif_x, dir_x = self.difference_between(index_col,to_x),self.direction(index_col,to_x)
    
        if self.verify_moves(index_col,index_row,to_x,to_y,playing,dif_x,dif_y,dir_y):
    
            if self.piece_can_eat(index_col,index_row,to_x,to_y,playing,dir_x,dir_y):
    
                forced.append([index_col,index_row,to_x,to_y])
        return forced

    
    def piece_can_eat(self,from_x,from_y,to_x,to_y,playing,dir_x,dir_y):
        if self.matrix[to_y - dir_y][to_x - dir_x].is_piece_inside():
            if self.matrix[to_y - dir_y][to_x - dir_x].get_piece() not in playing.get_list_pieces():
                return True
        return False
    
    def piece_can_eat_after_eat(self,from_x,from_y,playing):
        moves = []
        to_x = from_x +2
        to_y = from_y +2
        moves = self.condition_to_eat_after_eat(from_x,from_y,playing,to_x,to_y,moves)
        to_x = from_x +2
        to_y = from_y -2
        moves = self.condition_to_eat_after_eat(from_x,from_y,playing,to_x,to_y,moves)
        to_x = from_x -2
        to_y = from_y +2
        moves = self.condition_to_eat_after_eat(from_x,from_y,playing,to_x,to_y,moves)
        to_x = from_x -2
        to_y = from_y -2
        moves = self.condition_to_eat_after_eat(from_x,from_y,playing,to_x,to_y,moves)
        return moves
    
    def condition_to_eat_after_eat(self,from_x,from_y,playing,to_x,to_y,moves):
        dir_x,dir_y = self.direction(from_x,to_x),self.direction(from_y,to_y)
        if self.verify_moves(from_x,from_y,to_x,to_y,playing,2,2,dir_y):
            if self.piece_can_eat(from_x,from_y,to_x,to_y,playing,dir_x,dir_y):
                moves.append([from_x,from_y,to_x,to_y])
        return moves


    def get_matrix(self):
        return self.matrix
    
    def coordinates_is_in_range(self,x,y):
        return True if (x < self.size_m and x >= 0) and (y <self.size_m and y >= 0) else False

    def difference_between(self,a,b):
        return a - b if a > b else b -a
    
    def direction(self,a,b):
        return -1 if a > b else +1

    def difference_between_and_direction(self,from_x,from_y,to_x,to_y):
        dif_x, dif_y =self.difference_between(from_x,to_x), self.difference_between(from_y,to_y)
        dir_x, dir_y = self.direction(from_x,to_x), self.direction(from_y,to_y)
        return dif_x, dif_y, dir_x, dir_y
