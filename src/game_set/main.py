import pygame
import copy  # Import copy module for deepcopy
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

#import class
from src.core.const import *
from src.game_set.game import Game
from src.core.move import Move
from src.core.square import Square

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()

    def mainloop(self):
        
        #set default name :
        screen = self.screen 
        game = self.game
        board = game.board
        dragger = game.dragger  

        running = True
        while running:
            game.show_bg(screen)  
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
     
            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                #click down mouse event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    clicked_col = int(dragger.mouseX // SQSIZE) 
                    clicked_row = int(dragger.mouseY // SQSIZE)

                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        if piece.color == game.next_player:
                            board.calc_moves(piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos) 
                            dragger.drag_piece(piece)
                            #show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                #mouse motion event
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = int(event.pos[1] // SQSIZE)
                    motion_col = int(event.pos[0] // SQSIZE)
                    
                    # Check limit of board ?
                    if 0 <= motion_row < 8 and 0 <= motion_col < 8:
                        game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                #click up event
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        released_row = int(dragger.mouseY // SQSIZE)
                        released_col = int(dragger.mouseX // SQSIZE)

                        # Thêm kiểm tra giới hạn bàn cờ
                        if 0 <= released_row < 8 and 0 <= released_col < 8:
                            # create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            # valid move ?
                            if board.valid_move(dragger.piece, move) and dragger.piece.color == game.next_player:
                                # normal capture
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)

                                board.set_true_en_passant(dragger.piece)                            

                                # sounds
                                game.play_sound(captured)
                                # show methodss
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)

                                # next turn
                                game.next_turn()

                    dragger.undrag_piece()

                # key press
                elif event.type == pygame.KEYDOWN:  
                    
                    # reset
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
                    
                    # back to menu
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        return  # Return to menu

                #out
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


if __name__ == "__main__":
    from menu import MainMenu
    menu = MainMenu()
    menu.run()