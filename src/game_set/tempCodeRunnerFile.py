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