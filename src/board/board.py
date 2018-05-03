import copy
import logging

from src.colors import colors
from src.randomizer.randomizer import Randomizer
from src.renderer.renderer import Renderer
from src.tetromino.tetromino import Tetromino

log = logging.getLogger(__name__)


class Board:
    """Board contains all the tetrominos in the current game."""

    def __init__(self, width, height):
        """
        Initialize a Board object.

        Args:
            width (int): The board's width in number of units.
            height (int): The board's height in number of units.
        """
        log.info(
            "Initializing board (width={}, height={})".format(width, height)
        )
        self.width = width
        self.height = height
        self.random_tetrominos = Randomizer()
        self.current_tetromino = self.random_tetrominos.next()
        self.current_tetromino_matrix = [
            [0 for y in range(height)] for x in range(width)]
        self.next_tetromino = self.random_tetrominos.next()
        self.board_tetrominos = []
        self.board_tetrominos_matrix = [
            [0 for y in range(height)] for x in range(width)]
        self.ghost_tetromino = self.get_ghost_tetromino()
        self.holdable = True
        self.held_tetromino = None

    def render_board(self):
        """Render the contents of the board to the screen."""
        self.update_matrices()

        # Render the background
        self.render_background()

        # Render pieces except current one
        for tetromino in self.board_tetrominos:
            tetromino.render_tetromino()

        # Render the ghost tetromino
        self.ghost_tetromino.render_tetromino()

        # Render current playable tetromino
        self.current_tetromino.render_tetromino()

    def update_matrices(self):
        """Update the matrices to match the tetrominos in the board."""
        self.clear_matrix(self.current_tetromino_matrix)
        self.clear_matrix(self.board_tetrominos_matrix)
        for tetromino in self.board_tetrominos:
            for square in tetromino.squares:
                self.fill_matrix(self.board_tetrominos_matrix, square)
        for square in self.current_tetromino.squares:
            self.fill_matrix(self.current_tetromino_matrix, square)

    def get_ghost_tetromino(self):
        """
        Return a gray clone of the current tetromino and moves it down by the maximum amount.

        Returns:
            Tetromino: The ghost tetromino

        """
        self.update_matrices()
        ghost = copy.deepcopy(self.current_tetromino)
        ghost.color = colors.ASH
        for i in range(self.height):
            ghost.offset(0, -1)
            for square in ghost.squares:
                if square.y < 0 or self.board_tetrominos_matrix[square.x][square.y] == 1:
                    ghost.offset(0, 1)
                    break
        return ghost

    def switch_current_tetromino(self):
        """Replace the current tetromino with the next tetromino."""
        self.current_tetromino = self.next_tetromino
        self.ghost_tetromino = self.get_ghost_tetromino()
        self.next_tetromino = self.random_tetrominos.next()

    def render_ghost(self):
        """Render the ghost of the current tetromino."""
        ghost = Tetromino(
            self.current_tetromino.id,
            self.current_tetromino.origin,
            colors.ASH
        )
        for i in range(self.current_tetromino.state.value):
            ghost.rotate_cw()
        for i in range(self.height):
            ghost.offset(0, -1)
            for square in ghost.squares:
                if square.y < 0 or self.board_tetrominos_matrix[square.x][square.y] == 1:
                    ghost.offset(0, 1)
                    break
        ghost.render_tetromino()

    def fill_matrix(self, matrix, square):
        """
        Fill the given matrix at the given square's indices with a 1.

        Args:
            matrix ([][]int): The matrix with the index to be filled.
            square (Square): The square with the coordinates to fill the matrix.
        """
        if square.x >= self.width or square.y >= self.height:
            log.warning(
                "Position exceeds boundaries: [{}][{}]".format(square.x, square.y))
            return
        matrix[square.x][square.y] = 1

    def unfill_matrix(self, matrix, square):
        """
        Fill the given matrix at the given square's indices with a 0.

        Args:
            matrix ([][]int): The matrix with the index to be unfilled.
            square (Square): The square with the coordinates to unfill the matrix.
        """
        if square.x >= self.width or square.y >= self.height:
            log.error(
                "Position exceeds boundaries: [{}][{}]".format(square.x, square.y))
            return
        matrix[square.x][square.y] = 0

    def clear_matrix(self, matrix):
        """
        Set every element of the given matrix to 0.

        Args:
            matrix ([][]int): The matrix to be cleared.
        """
        for i in range(self.width):
            for j in range(self.height):
                matrix[i][j] = 0

    def render_background(self):
        """Render the background squares."""
        for i in range(self.width):
            for j in range(self.height):
                if (i % 2 is 0 and j % 2 is 0) or \
                        ((i + 1) % 2 is 0 and (j + 1) % 2 is 0):
                    s = Renderer(i, j, colors.CHARCOAL)
                else:
                    s = Renderer(i, j, colors.JET)
                s.draw()

    def hold_current_tetromino(self):
        """Put the current tetromino on hold to be retrieved later."""
        if self.holdable is False:
            log.info("Hold slot is already occupied by {}".format(
                self.held_tetromino.id))
            return
        self.holdable = False
        if self.held_tetromino is None:
            log.info("Putting tetromino {} on hold".format(
                self.current_tetromino.id))
            self.held_tetromino = copy.deepcopy(self.current_tetromino)
            self.held_tetromino.reset_position()
            self.switch_current_tetromino()
        else:
            log.info("Putting tetromino {} out of hold".format(
                self.held_tetromino.id))
            tmp = self.current_tetromino
            self.current_tetromino = self.held_tetromino
            log.info("Putting tetromino {} on hold".format(tmp.id))
            self.held_tetromino = copy.deepcopy(tmp)
            self.held_tetromino.reset_position()
        self.ghost_tetromino = self.get_ghost_tetromino()

    def get_combined_matrix_string(self):
        """
        Combine the board and piece matrices as a string for debugging.

        Returns:
            string: The combined matrix.

        """
        combined_matrix = "Matrix:\n"
        for j in reversed(range(self.height)):
            for i in range(self.width):
                combined_matrix += str(self.board_tetrominos_matrix[i]
                                       [j] or self.current_tetromino_matrix[i][j]) + " "
            combined_matrix += "\n"
        return combined_matrix
