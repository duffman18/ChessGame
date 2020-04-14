#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Classes for the Chess Package
"""

import pieces as p
import player as pl


class ChessGame:
    def __init__(self):
        self.board = [[None] * 8 for i in range(8)]
        self.capturedWhite = []
        self.capturedBlack = []
        self.playerWhite = pl.Player(is_white=True)
        self.playerBlack = pl.Player(False, self.playerWhite)
        self.playerWhite.set_opponent(self.playerBlack)

    def __str__(self):
        """
        Method to define how this class is cast to a string.  I used this to output the board state in a human
        readable way.
        """
        ret_str = '+---' * 8 + '+\n'
        for r in self.board[::-1]:
            for cp in r:
                ret_str += '| {} '.format(str(cp or ' '))
            ret_str += '|\n' + '+---' * 8 + '+\n'
        return ret_str

    def new_game(self):
        """Sets up a new game state by clearing off board and making all new pieces."""
        # Clear board and player states
        self.board = [[None] * 8 for i in range(8)]
        self.capturedWhite = []
        self.capturedBlack = []
        self.playerWhite.clear()
        self.playerBlack.clear()

        # Create all the White pieces and put those objects on the board and add them to the White player
        temp_pieces = [p.Rook(self.playerWhite, (0, 0)), p.Knight(self.playerWhite, (0, 1)),
                       p.Bishop(self.playerWhite, (0, 2)), p.Queen(self.playerWhite, (0, 3)),
                       p.King(self.playerWhite, (0, 4)), p.Bishop(self.playerWhite, (0, 5)),
                       p.Knight(self.playerWhite, (0, 6)), p.Rook(self.playerWhite, (0, 7))]
        temp_pieces += [p.Pawn(self.playerWhite, (1, i)) for i in range(8)]
        for cp in temp_pieces:
            cp.set_board(self.board)
            self.playerWhite.add_piece(cp)
            self.board[cp.get_row()][cp.get_col()] = cp
        self.playerWhite.set_king(temp_pieces[4])

        # Create all the Black pieces and put those objects on the board and add them to the Black player
        temp_pieces = [p.Rook(self.playerBlack, (7, 0)), p.Knight(self.playerBlack, (7, 1)),
                       p.Bishop(self.playerBlack, (7, 2)), p.Queen(self.playerBlack, (7, 3)),
                       p.King(self.playerBlack, (7, 4)), p.Bishop(self.playerBlack, (7, 5)),
                       p.Knight(self.playerBlack, (7, 6)), p.Rook(self.playerBlack, (7, 7))]
        temp_pieces += [p.Pawn(self.playerBlack, (6, i)) for i in range(8)]
        for cp in temp_pieces:
            cp.set_board(self.board)
            self.playerBlack.add_piece(cp)
            self.board[cp.get_row()][cp.get_col()] = cp
        self.playerBlack.set_king(temp_pieces[4])

    def move(self, moving_player, start_pos, end_pos):
        """Method used to perform a move action on a piece
        Inputs:
        startPos -- Tuple with integer coordinates (x,y) for Piece that is moving
        endPos -- Tuple with integer coordinates (x,y) for final position of move
        """
        # Make sure the start and stop positions are on the board
        if max(start_pos) > 7 or min(start_pos) < 0:
            raise p.MoveError('Invalid Piece', 'Position of Piece not on the board', None, start_pos, end_pos)

        # Get the piece that is being moved
        moving_piece = self.board[start_pos[0]][start_pos[1]]

        # Make sure that there is a piece in that spot and make sure that it belongs to the correct player
        if moving_piece is None:
            raise p.MoveError('Invalid Piece', 'No Piece located on the selected position', moving_piece, start_pos,
                              end_pos)
        if moving_piece.get_player() != moving_player:
            raise p.MoveError('Invalid Piece', "Cannot move the opponent's Piece", moving_piece, start_pos, end_pos)

        # Make sure the stop position is on the board
        if max(end_pos) > 7 or min(end_pos) < 0:
            raise p.MoveError('Invalid Move', 'Position of Move not on the board', None, start_pos, end_pos)

        # Make sure that the piece is actually being moved
        if start_pos == end_pos:
            raise p.MoveError('MoveError', "Can't move a piece to it's own location.", moving_piece, start_pos,
                              end_pos)

        # Check the piece's logic to see if the input move is valid
        moving_piece.check_valid_move(end_pos)

        # Move logic
        # Check if there is a piece getting captured
        # if no capture just move the piece
        if self.board[end_pos[0]][end_pos[1]] is None:
            moving_piece.set_pos(end_pos)
            self.board[end_pos[0]][end_pos[1]] = moving_piece
            self.board[start_pos[0]][start_pos[1]] = None
        # if captured move captured piece to the appropriate captured list and move the piece
        else:
            capped_piece = self.board[end_pos[0]][end_pos[1]]
            # Make sure they aren't capturing their own piece.
            if capped_piece.player == moving_piece.get_player():
                raise p.MoveError('Invalid Move' 'Cannot capture your own Piece', moving_piece, start_pos, end_pos)
            # Cover En Passant by checking if the captured piece is a ghost pawn and switching capped piece to the
            # parent pawn.
            if isinstance(capped_piece, p.GhostPawn) and isinstance(moving_piece, p.Pawn):
                capped_piece = capped_piece.get_parent()
            capped_piece.set_pos(None)
            if capped_piece.isWhite:
                self.capturedWhite.append(capped_piece)
            else:
                self.capturedBlack.append(capped_piece)
            moving_piece.set_pos(end_pos)
            self.board[end_pos[0]][end_pos[1]] = moving_piece
            self.board[start_pos[0]][start_pos[1]] = None

        # Save that the piece has moved, this affects castle logic and pawn move logic
        moving_piece.set_moved()

        # Manage Ghost Pawns
        # If opponent has a ghost pawn, remove it
        opp_ghost_pawn = moving_player.get_opponent().ghost_pawn
        if opp_ghost_pawn is not None:
            gp_row = opp_ghost_pawn.get_row()
            gp_col = opp_ghost_pawn.get_col()
            self.board[gp_row][gp_col] = None
            moving_player.get_opponent().ghost_pawn = None
        # Check if a pawn moved 2 spaces this turn, them make a ghost pawn
        if isinstance(moving_piece, p.Pawn):
            diff_row = start_pos[0] - end_pos[0]
            if abs(diff_row) == 2:
                diff_row = diff_row / 2
                new_gp = p.GhostPawn(moving_piece, (start_pos[0] - diff_row, start_pos[1]))
                moving_player.ghost_pawn = new_gp
                self.board[new_gp.get_row()][new_gp.get_col()]

    def castle_right(self, moving_player):
        # TODO: Implement castle logic
        # -Test if valid move
        # --Move King and Rook
        pass

    def castle_left(self, moving_player):
        # TODO: Implement castle logic
        # -Test if valid move
        # --Move King and Rook
        pass


if __name__ == '__main__':
    import os

    def cls():
        os.system('cls' if os.name == 'nt' else 'clear')

    a = ChessGame()
    a.new_game()
    moving_player = a.playerWhite
    while 1:
        print(a)
        while 1:
            try:
                piece_row = int(input("Select Piece Row: "))
                piece_col = int(input("Select Piece Col: "))
                move_row = int(input("Move to Row: "))
                move_col = int(input("Move to Col: "))
                a.move(moving_player, (piece_row, piece_col), (move_row, move_col))
                break
            except TypeError:
                if move_row == 'CR':
                    a.castle_right(moving_player)
                    break
                elif move_row == 'CL':
                    a.castle_left(moving_player)
                    break
                else:
                    print('Not a valid input, Try Again.')
            except p.MoveError as err:
                print('{}: {}'.format(err.expression, err.message))
        cls()
        if moving_player.get_opponent().is_checkmate():
            print('Checkmate!')
            print('{} Wins!'.format('White' if moving_player.isWhite else 'Black'))
        if moving_player.get_opponent().is_checked():
            print('Check!')

        moving_player = moving_player.get_opponent()
