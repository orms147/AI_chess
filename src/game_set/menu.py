import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.const import *
from src.game_set.game import Game  # Import Game class to use its show_bg method

class MainMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess Game')
        self.font_large = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 30, bold=True)
        self.running = True
        
        # Create a game instance just for the background
        self.game = Game()
        
        # Button dimensions
        self.button_width = 300
        self.button_height = 60
        self.button_margin = 20
        
        # Define buttons
        self.buttons = [
            {
                'text': 'Player vs Player',
                'rect': pygame.Rect((WIDTH - self.button_width) // 2, 
                                    HEIGHT // 2 - self.button_height - self.button_margin,
                                    self.button_width, self.button_height),
                'action': self.start_player_vs_player
            },
            {
                'text': 'Player vs Computer',
                'rect': pygame.Rect((WIDTH - self.button_width) // 2, 
                                    HEIGHT // 2,
                                    self.button_width, self.button_height),
                'action': self.start_player_vs_computer
            },
            {
                'text': 'Computer vs Computer',
                'rect': pygame.Rect((WIDTH - self.button_width) // 2, 
                                    HEIGHT // 2 + self.button_height + self.button_margin,
                                    self.button_width, self.button_height),
                'action': self.start_computer_vs_computer
            },
            {
                'text': 'Exit',
                'rect': pygame.Rect((WIDTH - self.button_width) // 2, 
                                    HEIGHT // 2 + 2 * (self.button_height + self.button_margin),
                                    self.button_width, self.button_height),
                'action': self.exit_game
            }
        ]
        
        # Colors
        self.bg_color = (50, 50, 50)
        self.button_color = (119, 154, 88)
        self.button_hover_color = (162, 209, 119)
        self.text_color = (234, 234, 200)
        self.title_color = (234, 234, 200)
        
        # Create a semi-transparent overlay
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128))  # RGBA: Black with 50% transparency
    
    def draw_text(self, text, font, color, x, y, center=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def draw_menu(self):
        # Draw chess board background
        self.game.show_bg(self.screen)
        
        # Apply semi-transparent overlay to make buttons more visible
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw title
        self.draw_text('Chess Game', self.font_large, self.title_color, WIDTH // 2, HEIGHT // 4)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Check if mouse is over button
            if button['rect'].collidepoint(mouse_pos):
                color = self.button_hover_color
            else:
                color = self.button_color
            
            # Draw button
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=10)
            pygame.draw.rect(self.screen, self.text_color, button['rect'], 2, border_radius=10)
            
            # Draw button text
            self.draw_text(button['text'], self.font_medium, self.text_color, 
                          button['rect'].centerx, button['rect'].centery)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for button in self.buttons:
                        if button['rect'].collidepoint(event.pos):
                            button['action']()
    
    def start_player_vs_player(self):
        print("Starting Player vs Player game")
        from main import Main
        main = Main()
        main.mainloop()
        pygame.display.set_mode((WIDTH, HEIGHT))  # Restore the window after returning
    
    def start_player_vs_computer(self):
        print("Starting Player vs Computer game")
        # Implement Player vs Computer mode
        self.show_not_implemented()
    
    def start_computer_vs_computer(self):
        print("Starting Computer vs Computer game")
        # Implement Computer vs Computer mode
        self.show_not_implemented()
    
    def exit_game(self):
        self.running = False
        pygame.quit()
        sys.exit()
    
    def show_not_implemented(self):
        """Show a message for features not yet implemented"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Draw message box
        message_box = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
        pygame.draw.rect(self.screen, self.bg_color, message_box, border_radius=10)
        pygame.draw.rect(self.screen, self.text_color, message_box, 2, border_radius=10)
        
        # Draw message text
        self.draw_text("Not Implemented Yet", self.font_medium, self.text_color, 
                       WIDTH // 2, HEIGHT // 2 - 30)
        self.draw_text("Coming soon...", self.font_medium, self.text_color, 
                       WIDTH // 2, HEIGHT // 2 + 30)
        
        pygame.display.update()
        
        # Wait for a key press or mouse click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
    
    def run(self):
        while self.running:
            self.draw_menu()
            self.handle_events()
            pygame.display.update()
            