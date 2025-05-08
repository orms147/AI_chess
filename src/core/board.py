import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.const import *
from src.core.square import Square
from src.core.piece import *
from src.core.move import Move

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
            rook_col = 0 if diff < 0 else 7
            rook = self.squares[initial.row][rook_col].piece
            new_rook_col = 3 if diff < 0 else 5
            self.squares[initial.row][rook_col].piece = None
            self.squares[initial.row][new_rook_col].piece = rook

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
    # Check if it's a castling move
    if abs(initial.col - final.col) != 2:
        return False
        
    # Get the king and determine which side we're castling
    king = self.squares[initial.row][initial.col].piece
    if not isinstance(king, King) or king.moved:
        return False
        
    # Determine which rook we're using
    is_queenside = final.col < initial.col
    rook_col = 0 if is_queenside else 7
    rook = self.squares[initial.row][rook_col].piece
    
    # Check if rook exists and hasn't moved
    if not isinstance(rook, Rook) or rook.moved:
        return False
        
    # Check if path is clear
    start_col = min(initial.col, rook_col) + 1
    end_col = max(initial.col, rook_col)
    for col in range(start_col, end_col):
        if not self.squares[initial.row][col].isempty():
            return False
            
    # Check if king is in check or would move through check
    for col in range(initial.col, final.col + (1 if is_queenside else -1), -1 if is_queenside else 1):
        if self.is_king_checked(king.color):
            return False
            
    return True

  def set_true_en_passant(self, piece):
    if not isinstance(piece, Pawn):
        return

    for row in range(ROWS):
        for col in range(COLS):
            if isinstance(self.squares[row][col].piece, Pawn):
                self.squares[row][col].piece.en_passant = False
    piece.en_passant = True

  def in_check(self, piece, move):
    # Create a temporary board and piece for testing the move
    temp_board = copy.deepcopy(self)
    temp_piece = copy.deepcopy(piece)
    
    # Make the move on the temporary board
    temp_board.move(temp_piece, move, testing=True)
    
    # Find the king's position
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            square = temp_board.squares[row][col]
            if square.has_teammate(piece.color) and isinstance(square.piece, King):
                king_pos = (row, col)
                break
        if king_pos:
            break
            
    if not king_pos:
        return False
        
    # Check if any enemy piece can capture the king
    for row in range(ROWS):
        for col in range(COLS):
            square = temp_board.squares[row][col]
            if square.has_enemy_piece(piece.color):
                enemy_piece = square.piece
                temp_board.calc_moves(enemy_piece, row, col, bool=False)
                for move in enemy_piece.moves:
                    if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                        return True
    return False

  def valid_move(self, piece, move):
    return move in piece.moves

  def calc_moves(self, piece, row, col, bool=True):
    #clear
    piece.clear_moves()

    # Caculate move of piece

    # Move method 
    def pawn():
      piece = self.squares[row][col].piece
      
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
                  final = Square(move_row, col)
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
      
      # diagonal captures
      move_cols = [col - 1, col + 1]  # 2 col: right and left to move
      move_row = row + piece.dir
      for move_col in move_cols:
          if Square.in_range(move_col):
              if self.squares[move_row][move_col].has_enemy_piece(piece.color):
                  # new move
                  initial = Square(row, col)
                  final = Square(move_row, move_col)
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
      
      # Check for en passant captures
      for move_col in [col-1, col+1]:
          if Square.in_range(move_col) and row == r:
              if self.squares[row][move_col].has_enemy_piece(piece.color):
                  p = self.squares[row][move_col].piece
                  if isinstance(p, Pawn) and p.en_passant:
                      # create initial and final move squares
                      initial = Square(row, col)
                      final = Square(fr, move_col)
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
            move = Move(initial, final)
            # check potencial checks
            if bool:
                if not self.in_check(piece, move):
                    piece.add_move(move)
                else:
                    pass
            else:
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
    if isinstance(piece, Knight):
        knight()
        # Debug: In ra các nước đi của mã trước khi lọc khi vua bị chiếu
        # print(f"[DEBUG] Knight moves before filter (row={row}, col={col}): {[str(m) for m in piece.moves]}")

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

    if bool and not isinstance(piece, King):
        # Kiểm tra xem vua có đang bị chiếu không
        king_row, king_col = None, None
        for r in range(ROWS):
            for c in range(COLS):
                if self.squares[r][c].has_piece():
                    p = self.squares[r][c].piece
                    if isinstance(p, King) and p.color == piece.color:
                        king_row, king_col = r, c
                        break
            if king_row is not None:
                break
        
        # Nếu vua đang bị chiếu
        if king_row is not None:
            king = self.squares[king_row][king_col].piece
            # Kiểm tra xem vua có đang bị chiếu không
            enemy_color = 'black' if piece.color == 'white' else 'white'
            is_checked = False
            for r in range(ROWS):
                for c in range(COLS):
                    if self.squares[r][c].has_piece():
                        p = self.squares[r][c].piece
                        if p.color == enemy_color:
                            # Tính toán các nước đi hợp lệ cho quân địch
                            temp_piece = copy.deepcopy(p)
                            temp_board = copy.deepcopy(self)
                            temp_board.calc_moves(temp_piece, r, c, bool=False)
                            for m in temp_piece.moves:
                                if isinstance(self.squares[king_row][king_col].piece, King) and m.final.row == king_row and m.final.col == king_col:
                                    is_checked = True
                                    break
                    if is_checked:
                        break
                if is_checked:
                    break
            
            # Nếu vua đang bị chiếu, lọc các nước đi
            if is_checked:
                # Lưu trữ các nước đi hợp lệ
                valid_moves = []
                
                # Kiểm tra từng nước đi có thể giải quyết tình trạng chiếu không
                for move in piece.moves:
                    # Thử nước đi trên bản sao của bàn cờ
                    temp_piece = copy.deepcopy(piece)
                    temp_board = copy.deepcopy(self)
                    temp_board.move(temp_piece, move, testing=True)
                    
                    # Kiểm tra xem sau nước đi, vua có còn bị chiếu không
                    still_checked = False
                    for r in range(ROWS):
                        for c in range(COLS):
                            if temp_board.squares[r][c].has_piece():
                                p = temp_board.squares[r][c].piece
                                if p.color == enemy_color:
                                    # Tính toán các nước đi hợp lệ cho quân địch
                                    temp_board.calc_moves(p, r, c, bool=False)
                                    for m in p.moves:
                                        # Tìm vị trí vua sau nước đi
                                        temp_king_row, temp_king_col = king_row, king_col
                                        for kr in range(ROWS):
                                            for kc in range(COLS):
                                                if temp_board.squares[kr][kc].has_piece():
                                                    pk = temp_board.squares[kr][kc].piece
                                                    if isinstance(pk, King) and pk.color == piece.color:
                                                        temp_king_row, temp_king_col = kr, kc
                                                        break
                                            if temp_king_row != king_row or temp_king_col != king_col:
                                                break
                                        
                                        if m.final.row == temp_king_row and m.final.col == temp_king_col:
                                            still_checked = True
                                            break
                                    if still_checked:
                                        break
                            if still_checked:
                                break
                        if still_checked:
                            break
                    
                    # Nếu nước đi giải quyết được tình trạng chiếu
                    if not still_checked:
                        valid_moves.append(move)
                
                # Debug: In ra các nước đi của mã sau khi lọc khi vua bị chiếu
                if isinstance(piece, Knight):
                    # print(f"[DEBUG] Knight moves after filter (row={row}, col={col}): {[str(m) for m in valid_moves]}")
                    pass
                # Thay thế danh sách nước đi bằng các nước đi hợp lệ
                piece.moves = valid_moves
                
  def is_king_checked(self, color):
    # Find the king's position
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            square = self.squares[row][col]
            if square.has_teammate(color) and isinstance(square.piece, King):
                king_pos = (row, col)
                break
        if king_pos:
            break
            
    if not king_pos:
        return False
        
    # Check if any enemy piece can capture the king
    for row in range(ROWS):
        for col in range(COLS):
            square = self.squares[row][col]
            if square.has_enemy_piece(color):
                enemy_piece = square.piece
                self.calc_moves(enemy_piece, row, col, bool=False)
                for move in enemy_piece.moves:
                    if move.final.row == king_pos[0] and move.final.col == king_pos[1]:
                        return True
    return False
  
  def is_checkmate(self, color):
    # First check if the king is in check
    if not self.is_king_checked(color):
        return False
        
    # Try all possible moves for all pieces of the given color
    for row in range(ROWS):
        for col in range(COLS):
            square = self.squares[row][col]
            if square.has_teammate(color):
                piece = square.piece
                self.calc_moves(piece, row, col, bool=True)
                if piece.moves:  # If there are any valid moves, it's not checkmate
                    return False
    return True
  
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