import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.const import *
from src.core.board import Board
from src.ui.dragger import Dragger
from src.core.square import Square
from src.ui.config import Config

class Game:

  def __init__(self):



    
    #set default
    self.next_player = 'white'
    self.hovered_sqr = None
    self.board = Board()
    self.dragger = Dragger()
    self.config = Config()

  #Show back ground methods
  def show_bg(self, surface):
    for row in range(ROWS):
      for col in range(COLS):
        if(row + col) % 2 == 0 :
          color = (234, 234, 200) #light green
        else:
          color = (119, 154, 88) #dark green
        
        rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)

        pygame.draw.rect(surface, color, rect)
  
  def show_pieces(self, surface):
    for row in range(ROWS):
      for col in range(COLS):
        #has piece ?
        if self.board.squares[row][col].has_piece():      #have piece in real square :> 
          piece = self.board.squares[row][col].piece      #set call default\
          
          #all pieces except dragger piece 
          if piece is not self.dragger.piece:
            piece.set_texture()
            img = pygame.image.load(piece.texture)              #have set_texture method in piece
            img_center = col * SQSIZE + SQSIZE  // 2, row * SQSIZE + SQSIZE  // 2   #basic math center
            piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, piece.texture_rect)


  def show_moves(self, surface):
    if self.dragger.dragging:
      piece = self.dragger.piece

      #loop all valid moves
      for move in piece.moves:
        #color
        color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
        #rect
        rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
        #blit
        pygame.draw.rect(surface, color, rect)

  def show_last_move(self, surface):
    theme = self.config.theme

    if self.board.last_move:
        initial = self.board.last_move.initial
        final = self.board.last_move.final

        for pos in [initial, final]:
            # color
            color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
            # rect
            rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect)

  def show_hover(self, surface):
      if self.hovered_sqr:
          # color
          color = (180, 180, 180)
          # rect
          rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
          # blit
          pygame.draw.rect(surface, color, rect, width=3)

  # other methods

  def next_turn(self):
      self.next_player = 'white' if self.next_player == 'black' else 'black'

  def set_hover(self, row, col):
      self.hovered_sqr = self.board.squares[row][col]

  def change_theme(self):
      self.config.change_theme()

  def play_sound(self, captured=False):
      if captured:
          self.config.capture_sound.play()
      else:
          self.config.move_sound.play()

  def reset(self):
      self.__init__()