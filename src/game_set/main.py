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
                                
                                # Thêm kiểm tra chiếu hết sau mỗi lượt đi
                                current_player = game.next_player
                                if board.is_checkmate(current_player):
                                    winner = 'white' if current_player == 'black' else 'black'
                                    return_to_menu = self.show_game_over(winner)
                                    if return_to_menu:
                                        running = False
                                        return  # Return to menu

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

    def show_game_over(self, winner):
        """Hiển thị thông báo chiếu hết và nút quay về menu"""
        screen = self.screen
        game = self.game
        
        # Tạo overlay mờ
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # RGBA: Đen với 70% độ mờ
        screen.blit(overlay, (0, 0))
        
        # Tạo font
        font_large = pygame.font.SysFont('Arial', 40, bold=True)
        font_medium = pygame.font.SysFont('Arial', 30, bold=True)
        
        # Vẽ khung thông báo
        message_box = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(screen, (50, 50, 50), message_box, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), message_box, 2, border_radius=10)
        
        # Vẽ text thông báo
        text_color = (234, 234, 200)
        title_text = f"{winner.capitalize()} Wins!"
        title_surface = font_large.render(title_text, True, text_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_surface, title_rect)
        
        message_text = "Checkmate!"
        message_surface = font_medium.render(message_text, True, text_color)
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(message_surface, message_rect)
        
        # Vẽ nút trở về menu
        button_width, button_height = 200, 50
        button_rect = pygame.Rect((WIDTH - button_width) // 2, 
                                HEIGHT // 2 + 60,
                                button_width, button_height)
        button_color = (119, 154, 88)
        pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(screen, text_color, button_rect, 2, border_radius=10)
        
        # Vẽ text nút
        button_text = "Return to Menu"
        button_surface = font_medium.render(button_text, True, text_color)
        button_text_rect = button_surface.get_rect(center=button_rect.center)
        screen.blit(button_surface, button_text_rect)
        
        pygame.display.update()
        
        # Đợi cho đến khi người chơi nhấn nút
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        waiting = False
                        return True  # Trở về menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        return True  # Trở về menu
        
        return False

if __name__ == "__main__":
    from menu import MainMenu
    menu = MainMenu()
    menu.run()

def show_game_over(self, winner):
    """Hiển thị thông báo chiếu hết và nút quay về menu"""
    screen = self.screen
    game = self.game
    
    # Tạo overlay mờ
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # RGBA: Đen với 70% độ mờ
    screen.blit(overlay, (0, 0))
    
    # Tạo font
    font_large = pygame.font.SysFont('Arial', 40, bold=True)
    font_medium = pygame.font.SysFont('Arial', 30, bold=True)
    
    # Vẽ khung thông báo
    message_box = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, (50, 50, 50), message_box, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), message_box, 2, border_radius=10)
    
    # Vẽ text thông báo
    text_color = (234, 234, 200)
    title_text = f"{winner.capitalize()} Wins!"
    title_surface = font_large.render(title_text, True, text_color)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_surface, title_rect)
    
    message_text = "Checkmate!"
    message_surface = font_medium.render(message_text, True, text_color)
    message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(message_surface, message_rect)
    
    # Vẽ nút trở về menu
    button_width, button_height = 200, 50
    button_rect = pygame.Rect((WIDTH - button_width) // 2, 
                             HEIGHT // 2 + 60,
                             button_width, button_height)
    button_color = (119, 154, 88)
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, text_color, button_rect, 2, border_radius=10)
    
    # Vẽ text nút
    button_text = "Return to Menu"
    button_surface = font_medium.render(button_text, True, text_color)
    button_text_rect = button_surface.get_rect(center=button_rect.center)
    screen.blit(button_surface, button_text_rect)
    
    pygame.display.update()
    
    # Đợi cho đến khi người chơi nhấn nút
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False
                    return True  # Trở về menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    return True  # Trở về menu
    
    return False

# Thêm phương thức này vào cuối class Board trong file board.py
def is_checkmate(self, color):
    """
    Kiểm tra xem vua có màu cụ thể có bị chiếu hết không
    """
    # Đầu tiên kiểm tra xem vua có đang bị chiếu không
    if not self.is_king_checked(color):
        return False
    
    # Kiểm tra xem có nước đi nào có thể giải quyết tình trạng chiếu không
    for row in range(ROWS):
        for col in range(COLS):
            if self.squares[row][col].has_piece():
                piece = self.squares[row][col].piece
                if piece.color == color:
                    # Tính toán các nước đi hợp lệ cho mỗi quân cờ
                    self.calc_moves(piece, row, col)
                    # Nếu có ít nhất một nước đi hợp lệ, thì không phải chiếu hết
                    if len(piece.moves) > 0:
                        return False
    
    # Nếu không tìm thấy nước đi nào để thoát khỏi tình trạng chiếu, thì đó là chiếu hết
    return True