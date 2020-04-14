#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Piece classes for the Chess Package
"""
# TODO: Possibly rework check_valid_move methods by making and using a gen_all_valid_moves methods
# This will make the logic for the check_valid_move methods cleaner and would also give access to a generator
# method that would be useful for checking for checkmate

import itertools as it


class Piece:
    """
    Base Class for the chess pieces, contains all the logic for interfacing with the pieces.
    Attributes:
    _player -- the player object that owns this piece
    _pos -- the position of the piece on the board
    _board -- board object os the piece has access to the current game state
    _moved -- boolean that stores if the piece has been moved before
    """
    def __init__(self, player, pos, board=None):
        self._player = player
        self._pos = pos
        self._board = board
        self._moved = False

    def get_row(self):
        """Returns the row index for this piece."""
        return self._pos[0]

    def get_col(self):
        """Returns the column index for this piece."""
        return self._pos[1]

    def get_pos(self):
        """Returns the position tuple"""
        return self._pos

    def get_player(self):
        """Returns the player that owns this piece"""
        return self._player

    def set_pos(self, pos):
        """Set the position attribute for the piece"""
        self._pos = pos

    def set_board(self, board):
        """Set the board object for the piece"""
        self._board = board

    def set_moved(self):
        """Set that this piece has been moved"""
        self._moved = True

    def has_moved(self):
        """Return if the peice has moved yet this game"""
        return self._moved


class Pawn(Piece):
    def __str__(self):
        return '\u2659' if self._player.isWhite else '\u265f'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        all_valid_moves = []
        r, c = self._pos
        if self._player.isWhite:
            # Straight Moves
            if self._board[r + 1][c] is None:
                all_valid_moves.append((r + 1, c))
                # Starting Move
                if not self._moved and self._board[r + 2][c] is None:
                    all_valid_moves.append((r + 2, c))
            # Capture Moves
            if c < 7 and self._board[r + 1][c + 1] is not None:
                if self._board[r + 1][c + 1].player.isWhite != self._player.isWhite:
                    all_valid_moves.append((r + 1, c + 1))
            if c > 0 and self._board[r + 1][c - 1] is not None:
                if self._board[r + 1][c - 1].player.isWhite != self._player.isWhite:
                    all_valid_moves.append((r + 1, c - 1))
        else:
            # Straight Moves
            if self._board[r - 1][c] is None:
                all_valid_moves.append((r - 1, c))
                # Starting Move
                if not self._moved and self._board[r - 2][c] is None:
                    all_valid_moves.append((r - 2, c))
            # Capture Moves
            if c < 7 and self._board[r - 1][c + 1] is not None:
                if self._board[r - 1][c + 1].player.isWhite != self._player.isWhite:
                    all_valid_moves.append((r - 1, c + 1))
            if c > 0 and self._board[r - 1][c - 1] is not None:
                if self._board[r - 1][c - 1].player.isWhite != self._player.isWhite:
                    all_valid_moves.append((r - 1, c - 1))
        # Check if there is any valid moves for this piece
        if not all_valid_moves:
            raise MoveError('Invalid Piece', 'No Valid Moves for Piece', self, self._pos, end_pos)
        # Check if the input move is part of this piece's valid move set
        if end_pos not in all_valid_moves:
            raise MoveError('Invalid Move', 'Not a Valid Move for Selected Piece', self, self._pos, end_pos)


class Rook(Piece):
    def __str__(self):
        return '\u2656' if self._player.isWhite else '\u265c'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        # Check if moving along row or column
        # -Loop through all board positions between start and end
        # --Check to make sure no piece is there blocking movement
        if end_pos[0] == self._pos[0]:
            for i in range(self._pos[1], end_pos[1], 1 if end_pos[1] > self._pos[1] else -1)[1:]:
                check_piece = self._board[self._pos[0]][i]
                if check_piece is not None and not isinstance(check_piece, GhostPawn):
                    raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)
        elif end_pos[1] == self._pos[1]:
            for i in range(self._pos[0], end_pos[0], 1 if end_pos[0] > self._pos[0] else -1)[1:]:
                check_piece = self._board[i][self._pos[1]]
                if check_piece is not None and not isinstance(check_piece, GhostPawn):
                    raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)
        # If the row or column does not stay the same then it is an invalid move for a Rook
        else:
            raise MoveError('Invalid Move', 'Not a valid method to move this piece type', self, self._pos, end_pos)


class Knight(Piece):
    def __str__(self):
        return '\u2658' if self._player.isWhite else '\u265e'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        r, c = self._pos
        moves = list(it.product((r - 1, r + 1), (c - 2, c + 2))) + list(it.product((r - 2, r + 2), (c - 1, c + 1)))
        # Build a list of all valid moves, 
        # with redundant bound check since that is scrubbed before this method is called
        all_valid_moves = [(x, y) for x, y in moves if 0 <= x < 8 and 0 <= y < 8]
        if end_pos not in all_valid_moves:
            raise MoveError('Invalid Move', 'Not a Valid Move for Selected Piece', self, self._pos, end_pos)


class Bishop(Piece):
    def __str__(self):
        return '\u2657' if self._player.isWhite else '\u265d'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        # Calc diffs for row & col
        diff_r = self._pos[0] - end_pos[0]
        diff_c = self._pos[1] - end_pos[1]

        # If the diffs are not equal then this is not a valid bishop move
        if diff_r != diff_c:
            raise MoveError('Invalid Move', 'Not a Valid Move for Selected Piece', self, self._pos, end_pos)

        # Check if any positions between start and end have any pieces in it
        # TODO: Need to figure out how best to ignore ghost pawns
        #  I don't like checking here in every piece that moves along lines
        for i in range(0, diff_r, 1 if diff_r > 0 else -1)[1:]:
            check_piece = self._board[self._pos[0] + i][self._pos[1] + i]
            if check_piece is not None and not isinstance(check_piece, GhostPawn):
                raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)


class Queen(Piece):
    def __str__(self):
        return '\u2655' if self._player.isWhite else '\u265b'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        # Calc diffs for row & col
        diff_r = self._pos[0] - end_pos[0]
        diff_c = self._pos[1] - end_pos[1]

        # Check if moving along row or column or diagonal
        # -Loop through all board positions between start and end
        # --Check to make sure no piece is there blocking movement
        if end_pos[0] == self._pos[0]:
            for i in range(self._pos[1], end_pos[1], 1 if end_pos[1] > self._pos[1] else -1)[1:]:
                check_piece = self._board[self._pos[0]][i]
                if check_piece is not None and not isinstance(check_piece, GhostPawn):
                    raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)
        elif end_pos[1] == self._pos[1]:
            for i in range(self._pos[0], end_pos[0], 1 if end_pos[0] > self._pos[0] else -1)[1:]:
                check_piece = self._board[i][self._pos[1]]
                if check_piece is not None and not isinstance(check_piece, GhostPawn):
                    raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)
        elif diff_r == diff_c:
            for i in range(0, diff_r, 1 if diff_r > 0 else -1)[1:]:
                check_piece = self._board[self._pos[0] + i][self._pos[1] + i]
                if check_piece is not None and not isinstance(check_piece, GhostPawn):
                    raise MoveError('Invalid Move', 'Another piece is in the way', self, self._pos, end_pos)
        else:
            raise MoveError('Invalid Move', 'Not a Valid Move for Selected Piece', self, self._pos, end_pos)


class King(Piece):
    def __str__(self):
        return '\u2654' if self._player.isWhite else '\u265a'

    def check_valid_move(self, end_pos):
        """Method to check if the passed move argument is a valid move.abs
        Inputs:
        endPos -- Tuple of final board coordinates for move
        """
        if end_pos[0] == 'CR':
            pass
        elif end_pos[1] == 'CL':
            pass
        else:
            r, c = self._pos
            moves = list(it.product((r - 1, r, r + 1), (c - 1, c, c + 1)))
            moves.remove((r, c))
            # Build a list of all valid moves,
            # with redundant bound check since that is scrubbed before this method is called
            all_valid_moves = [(x, y) for x, y in moves if 0 <= x < 8 and 0 <= y < 8]
            if end_pos not in all_valid_moves:
                raise MoveError('Invalid Move', 'Not a Valid Move for Selected Piece', self, self._pos, end_pos)
            if self._player.check_for_check(end_pos):
                raise MoveError('Invalid Move', 'Moving into check', self, self._pos, end_pos)


class GhostPawn(Piece):
    """
    Piece class used to enable En Passant rule when a pawn is moved by 2 spaces at the start.
    Puts a piece on the board that doesn't print or valid to move so attacking pawns can capture the
    jumping.
    Attributes:
    _parent_pawn -- The pawn that moved that caused this object to be made.
    """
    def __init__(self, parent_pawn, pos):
        Piece.__init__(self, None, pos)
        self._parent_pawn = parent_pawn

    def __str__(self):
        return ' '


class MoveError(Exception):
    """Exception raised for errors moving a piece.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
        piece -- piece being moved
        startPos -- starting position of the piece being moved
        endPos -- ending position of the move
    """

    def __init__(self, expression, message, piece, startPos, endPos):
        self.expression = expression
        self.message = message
        self.piece = piece
        self.startPos = startPos
        self.endPos = endPos
