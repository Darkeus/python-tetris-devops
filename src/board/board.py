import copy
import logging

from src.colors import colors
from src.randomizer.randomizer import Randomizer
from src.renderer.renderer import Renderer

log = logging.getLogger(__name__)


class Board:
    """Board contains all the tetrominos in the current game"""

    def __init__(self, width, height):
        log.info("Initializing board (width={}, height={})".format(width, height))
        self.width = width
        self.height = height
        self.random_tetrominos = Randomizer()
        self.current_tetromino = self.random_tetrominos.next()
        self.current_tetromino_matrix = [
            [0 for y in range(height)] for x in range(width)]
        self.next_tetromino = self.random_tetrominos.next()
        self.board_tetrominos_squares = []
        self.board_tetrominos_matrix = [
            [0 for y in range(height)] for x in range(width)]
        self.ghost_tetromino = self.get_ghost_tetromino()
        self.holdable = True
        self.held_tetromino = None

    def render_board(self):
        """Renders the board to the screen and updates matrices"""
        self.update_matrices()

        # Render the background
        self.render_background()

        # Render pieces except current one
        for square in self.board_tetrominos_squares:
            square.render_square()

        # Render the ghost tetromino
        self.ghost_tetromino.render_tetromino()

        # Render current playable tetromino
        self.current_tetromino.render_tetromino()

    def get_filled_indices(self):
        """Returns the number of lines filled"""
        filled_indices = []
        for j in range(self.height):
            is_filled = True
            for i in range(self.width):
                if self.board_tetrominos_matrix[i][j] == 0:
                    is_filled = False
            if is_filled:
                filled_indices.append(j)
        return filled_indices

    def clear_lines(self, indices):
        """Takes in a list of indices that are full and removes all the
        squares in the row"""

        #  Needs a copy of the list so it doesn't mutate the original list
        board_tetrominos_squares_copy = self.board_tetrominos_squares[:]
        for index in indices:
            for sqr in self.board_tetrominos_squares:
                if sqr.y == index:
                    board_tetrominos_squares_copy.remove(sqr)

        self.board_tetrominos_squares = board_tetrominos_squares_copy

    def drop_lines(self, indices):
        lines_dropped = 0
        cond = False
        for index in indices:
            log.debug("Current loop index: {}".format(index))
            for square in self.board_tetrominos_squares:
                if square.y > index - lines_dropped:
                    square.y = square.y - 1
                    cond = True
            if cond:
                lines_dropped += 1

    def update_matrices(self):
        self.clear_matrix(self.current_tetromino_matrix)
        self.clear_matrix(self.board_tetrominos_matrix)
        for square in self.board_tetrominos_squares:
            self.fill_matrix(self.board_tetrominos_matrix, square)
        for sqaure in self.current_tetromino.squares:
            self.fill_matrix(self.current_tetromino_matrix, square)

    def get_ghost_tetromino(self):
        """Returns a gray clone of the current tetromino and moves it down by the maximum amount"""
        self.update_matrices()
        ghost = copy.deepcopy(self.current_tetromino)
        for i in range(self.height):
            ghost.offset(0, -1)
            for square in ghost.squares:
                if square.y < 0 or self.board_tetrominos_matrix[square.x][square.y] == 1:
                    ghost.offset(0, 1)
                    break
                square.color = colors.ASH
        return ghost

    def switch_current_tetromino(self):
        """Assigns a new current piece"""
        self.current_tetromino = self.next_tetromino
        self.ghost_tetromino = self.get_ghost_tetromino()
        self.next_tetromino = self.random_tetrominos.next()

    def fill_matrix(self, matrix, square):
        """Fills the given matrix at the given indices with a 1"""
        if square.x >= self.width or square.y >= self.height:
            log.warning(
                "Position exceeds boundaries: {}".format(square.tuple()))
            return
        matrix[square.x][square.y] = 1

    def unfill_matrix(self, matrix, square):
        """Fills the given matrix at the given indices with a 0"""
        if square.x >= self.width or square.y >= self.height:
            log.error(
                "Position exceeds boundaries: {}".format(square.tuple()))
            return
        matrix[square.x][square.y] = 0

    def clear_matrix(self, matrix):
        """Sets every element of the given matrix to 0"""
        for i in range(self.width):
            for j in range(self.height):
                matrix[i][j] = 0

    def render_background(self):
        """Renders the background squares"""
        for i in range(self.width):
            for j in range(self.height):
                if (i % 2 is 0 and j % 2 is 0) or \
                        ((i + 1) % 2 is 0 and (j + 1) % 2 is 0):
                    s = Renderer(i, j, colors.CHARCOAL)
                else:
                    s = Renderer(i, j, colors.JET)
                s.draw()

    def hold_current_tetromino(self):
        """Holds the current tetromino and switches to another one"""
        if self.holdable is False:
            log.info("Hold slot is already occupied by {}".format(
                self.held_tetromino.id))
            return
        self.holdable = False
        if self.held_tetromino is None:
            log.info("Putting tetromino {} on hold".format(
                self.current_tetromino.id))
            self.held_tetromino = copy.deepcopy(self.current_tetromino)
            self.switch_current_tetromino()
        else:
            log.info("Putting tetromino {} out of hold".format(
                self.held_tetromino.id))
            tmp = self.current_tetromino
            self.current_tetromino = self.held_tetromino
            log.info("Putting tetromino {} on hold".format(tmp.id))
            self.held_tetromino = copy.deepcopy(tmp)
        self.ghost_tetromino = self.get_ghost_tetromino()

    def get_combined_matrix_string(self):
        """Combines the board and piece matrices as a string for debugging"""
        combined_matrix = "Matrix:\n"
        for j in reversed(range(self.height)):
            for i in range(self.width):
                combined_matrix += str(self.board_tetrominos_matrix[i][j] or
                                       self.current_tetromino_matrix[i][j]) + " "
            combined_matrix += "\n"
        return combined_matrix
