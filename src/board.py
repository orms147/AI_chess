from const import *
from square import Square
from piece import *
from move import Move

import copy

class Board:

  def __init__(self):
    self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
    self.last_move = None
    self._create()
    self._add_pieces('white')
    self._add_pieces('black')

  def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        # console board move update
        self.squares[int(initial.row)][int(initial.col)].piece = None
        self.squares[int(final.row)][int(final.col)].piece = piece

        if isinstance(piece, Pawn):
            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(
                        os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            
            # pawn promotion
            else:
                self.check_promotion(piece, final)

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

  def check_promotion(self, piece, final):
    if final.row == 0 or final.row == 7:
        self.squares[final.row][final.col].piece = Queen(piece.color)

  def castling(self, initial, final):
      return abs(initial.col - final.col) == 2

  def set_true_en_passant(self, piece):
    if not isinstance(piece, Pawn):
        return

    for row in range(ROWS):
        for col in range(COLS):
            if isinstance(self.squares[row][col].piece, Pawn):
                self.squares[row][col].piece.en_passant = False
    piece.en_passant = True

  def in_check(self, piece, move):
    temp_piece = copy.deepcopy(piece)
    temp_board = copy.deepcopy(self)
    temp_board.move(temp_piece, move, testing=True)
    
    for row in range(ROWS):
      for col in range(COLS):
        if temp_board.squares[row][col].has_enemy_piece(piece.color):
          p = temp_board.squares[row][col].piece
          temp_board.calc_moves(p, row, col, bool=False)
          for m in p.moves:
            if isinstance(m.final.piece, King):
              return True
    
    return False

  def valid_move(self, piece, move):
    return move in piece.moves

  def calc_moves(self, piece, row, col, bool=True):

    # Caculate move of piece

    # Move method 
    def pawn():
      piece = self.squares[row][col].piece
      if piece.color == 'black':
          if row != 1: piece.moved = True
      if piece.color == 'white':
          if row != 6: piece.moved = True
      # steps can move ( = 1 if moved)
      steps = 1 if piece.moved else 2

      # vertical move     piece.dir = -1 for white, = 1 for black
      start = row + piece.dir       
      end = row + piece.dir * (1 + steps)

      # Loop start -> end-1
      for move_row in range(start, end, piece.dir):  
          if Square.in_range(move_row):   # The piece in Board = true
              if self.squares[move_row][col].isempty(): # If don't have any piece
                  # new move
                  initial = Square(row, col)
                  final = Square(move_row, col, self.squares[move_row][col].piece)
                  move = Move(initial, final)
                  # check potencial checks
                  if bool:
                      if not self.in_check(piece, move):
                          # append new move
                          piece.add_move(move)
                  else:
                      # append new move
                      piece.add_move(move)
                  # got blocked
              else: break
              #not in range
          else: break
      
      # diagonal
      move_cols = [col - 1, col + 1]  # 2 col: right and left to move
      move_row = row + piece.dir
      for move_col in move_cols:
          if Square.in_range(move_col):
              if self.squares[move_row][move_col].has_enemy_piece(piece.color):
                  # new move
                  initial = Square(row, col)
                  final = Square(move_row, move_col, self.squares[move_row][move_col].piece)
                  move = Move(initial, final)
                  # check potencial checks
                  if bool:
                      if not self.in_check(piece, move):
                          # append new move
                          piece.add_move(move)
                  else:
                      # append new move
                      piece.add_move(move)

      # en passant moves
      r = 3 if piece.color == 'white' else 4
      fr = 2 if piece.color == 'white' else 5
      # left en pessant
      if Square.in_range(col-1) and row == r:
          if self.squares[row][col-1].has_enemy_piece(piece.color):
              p = self.squares[row][col-1].piece
              if isinstance(p, Pawn):
                  if p.en_passant:
                      # create initial and final move squares
                      initial = Square(row, col)
                      final = Square(fr, col-1, p)
                      # create a new move
                      move = Move(initial, final)
                      
                      # check potencial checks
                      if bool:
                          if not self.in_check(piece, move):
                              # append new move
                              piece.add_move(move)
                      else:
                          # append new move
                          piece.add_move(move)
      
      # right en pessant
      if Square.in_range(col+1) and row == r:
          if self.squares[row][col+1].has_enemy_piece(piece.color):
              p = self.squares[row][col+1].piece
              if isinstance(p, Pawn):
                  if p.en_passant:
                      # create initial and final move squares
                      initial = Square(row, col)
                      final = Square(fr, col+1, p)
                      # create a new move
                      move = Move(initial, final)
                      
                      # check potencial checks
                      if bool:
                          if not self.in_check(piece, move):
                              # append new move
                              piece.add_move(move)
                      else:
                          # append new move
                          piece.add_move(move)


    def knight():
      possible_moves = {
        (row - 2, col + 1),
        (row - 1, col + 2),
        (row + 1, col + 2),
        (row + 2, col + 1),
        (row + 2, col - 1),
        (row + 1, col - 2),
        (row - 1, col - 2),
        (row - 2, col - 1),
      }

      for possible_move in possible_moves:
        possible_move_row, possible_move_col = possible_move

        if Square.in_range(possible_move_row, possible_move_col):
          if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
            # Create new move
            initial = Square(row, col, piece.color)
            final = Square(possible_move_row, possible_move_col, piece.color)
            #
            move = Move(initial, final)
            # check potencial checks
            if bool:
                if not self.in_check(piece, move):
                    # append new move
                    piece.add_move(move)
                else: break
            else:
                # append new move
                piece.add_move(move)

    def straight_line_moves(incrs):
       for incr in incrs:
          row_incr, col_incr = incr
          possible_move_row = row + row_incr
          possible_move_col = col + col_incr
          
          while True:
            if Square.in_range(possible_move_row, possible_move_col):
              initial = Square(row, col, piece)
              final_piece = self.squares[possible_move_row][possible_move_col].piece
              final = Square(possible_move_row, possible_move_col, final_piece)
              #possible move 
              move = Move(initial, final)

              #empty
              if self.squares[possible_move_row][possible_move_col].isempty() :
                if bool:
                  if not self.in_check(piece, move):
                    # append new move
                    piece.add_move(move)
                else:
                  # append new move
                  piece.add_move(move)

              # has enemy piece = add move + break
              elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                  # check potencial checks
                  if bool:
                      if not self.in_check(piece, move):
                          # append new move
                          piece.add_move(move)
                  else:
                      # append new move
                      piece.add_move(move)
                  break

              # has team piece = break
              elif self.squares[possible_move_row][possible_move_col].has_teammate(piece.color):
                  break

            #not in range
            else: break

            #increase
            possible_move_row = possible_move_row + row_incr
            possible_move_col = possible_move_col + col_incr
 
    def king():
      adjs = [
          (row-1, col+0), # up
          (row-1, col+1), # up-right
          (row+0, col+1), # right
          (row+1, col+1), # down-right
          (row+1, col+0), # down
          (row+1, col-1), # down-left
          (row+0, col-1), # left
          (row-1, col-1), # up-left
      ]

      # normal moves
      for possible_move in adjs:
          possible_move_row, possible_move_col = possible_move

          if Square.in_range(possible_move_row, possible_move_col):
              if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                  # create squares of the new move
                  initial = Square(row, col)
                  final = Square(possible_move_row, possible_move_col) # piece=piece
                  # create new move
                  move = Move(initial, final)
                  # check potencial checks
                  if bool:
                      if not self.in_check(piece, move):
                          # append new move
                          piece.add_move(move)
                      else: break
                  else:
                      # append new move
                      piece.add_move(move)

      # castling moves
      if not piece.moved:
          # queen castling
          left_rook = self.squares[row][0].piece
          if isinstance(left_rook, Rook):
              if not left_rook.moved:
                  for c in range(1, 4):
                      # castling is not possible because there are pieces in between ?
                      if self.squares[row][c].has_piece():
                          break

                      if c == 3:
                          # adds left rook to king
                          piece.left_rook = left_rook

                          # rook move
                          initial = Square(row, 0)
                          final = Square(row, 3)
                          moveR = Move(initial, final)

                          # king move
                          initial = Square(row, col)
                          final = Square(row, 2)
                          moveK = Move(initial, final)

                          # check potencial checks
                          if bool:
                              if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                  # append new move to rook
                                  left_rook.add_move(moveR)
                                  # append new move to king
                                  piece.add_move(moveK)
                          else:
                              # append new move to rook
                              left_rook.add_move(moveR)
                              # append new move king
                              piece.add_move(moveK)

          # king castling
          right_rook = self.squares[row][7].piece
          if isinstance(right_rook, Rook):
              if not right_rook.moved:
                  for c in range(5, 7):
                      # castling is not possible because there are pieces in between ?
                      if self.squares[row][c].has_piece():
                          break

                      if c == 6:
                          # adds right rook to king
                          piece.right_rook = right_rook

                          # rook move
                          initial = Square(row, 7)
                          final = Square(row, 5)
                          moveR = Move(initial, final)

                          # king move
                          initial = Square(row, col)
                          final = Square(row, 6)
                          moveK = Move(initial, final)

                          # check potencial checks
                          if bool:
                              if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                  # append new move to rook
                                  right_rook.add_move(moveR)
                                  # append new move to king
                                  piece.add_move(moveK)
                          else:
                              # append new move to rook
                              right_rook.add_move(moveR)
                              # append new move king
                              piece.add_move(moveK)


    if isinstance(piece, Pawn): pawn()                #if it's Pawn  ( == piece.name == "Pawn")
    if isinstance(piece, Knight): knight()

    if isinstance(piece, Bishop): 
       straight_line_moves ([
          (-1, 1), #up right
          (-1, -1), #up left
          (1, 1),  #down right
          (1, -1), #down left
       ])

    if isinstance(piece, Rook): 
       straight_line_moves([
          (-1, 0), #up
          (1, 0),  #down
          (0, 1),  #right
          (0, -1), #left
       ])

    if isinstance(piece, Queen): 
       straight_line_moves ([
          (-1, 1), #up right
          (-1, -1), #up left
          (1, 1),  #down right
          (1, -1), #down left
          (-1, 0), #up
          (1, 0),  #down
          (0, 1),  #right
          (0, -1), #left
       ])

    if isinstance(piece, King): king()

  def _create(self):
    for row in range(ROWS):
      for col in range(COLS):
        self.squares[row][col] = Square(row, col )

  def _add_pieces(self, color):

    #set row default for white and black
    row_pawn, row_other = (6, 7) if color == "white" else (1, 0)

    #set col
    #pawns  (row = 6 and any col)
    for col in range(COLS):
      self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

    #knight (row = 7 and col = 1 or 6)
    self.squares[row_other][1] = Square(row_other, 1, Knight(color))
    self.squares[row_other][6] = Square(row_other, 6, Knight(color))

    #bishop (row = 7 and col = 2 or 5)
    self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
    self.squares[row_other][5] = Square(row_other, 5, Bishop(color))
        #self.squares[2][-3] = Square(2, -3, Bishop(color))

    #Rook (row = 7 and col = 0 or 7)
    self.squares[row_other][0] = Square(row_other, 0, Rook(color))
    self.squares[row_other][7] = Square(row_other, 7, Rook(color))
        #self.squares[4][4] = Square(4, 4, Rook(color))

    #queen (row = 7 and col = 3)
    self.squares[row_other][3] = Square(row_other, 3, Queen(color))
        #self.squares[4][3] = Square(4, 3, Queen(color))

    #king
    self.squares[row_other][4] = Square(row_other, 4, King(color))