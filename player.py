#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Player class for the Chess Package
"""

import pieces as p


class Player:
    def __init__(self, is_white, opponent=None, king=None):
        self.pieces = []
        self.ghost_pawn = None
        self.isWhite = is_white
        self._opponent = opponent
        self._king = king

    def set_opponent(self, op):
        """Set the opponent attribute for the player to op"""
        self._opponent = op

    def get_opponent(self):
        """Return the player object stored as the opponent"""
        return self._opponent

    def clear(self):
        """Clears the attributes to start a new game"""
        self.pieces = []
        self.ghost_pawn = None

    def add_piece(self, piece):
        """Adds a piece to the piece list for the calling player"""
        self.pieces.append(piece)

    def is_checked(self):
        """Checks if player is checked and returns True or False"""
        return self.check_for_check(self._king.get_pos())

    def is_checkmate(self):
        """Checks if player is checkmated and returns True or False"""
        pass

    def check_for_check(self, king_pos=None):
        # TODO: Possibly change so it accepts an entire board state to cover moving other pieces when wanting to
        # check for a checkmate position.
        """Checks if player is checked based on passed king position"""
        if king_pos is None:
            king_pos = self._king.get_pos()
        # TODO: Logic to check if the king would be in check if in the location king_pos

    def set_king(self, king):
        """Sets the king object for the player object"""
        self._king = king

    def get_king(self):
        """Return the king piece object for this player"""
        return self._king
