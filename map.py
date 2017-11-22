import config
import point
import randomizer
import renderer
import tetromino


class Map:
    """Map contains all the tetrominos in the current game"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map_matrix = [[0 for y in range(height)] for x in range(width)]
        self.piece_matrix = [[0 for y in range(height)] for x in range(width)]
        self.random_list = randomizer.Randomizer()
        next_piece = self.random_list.next()
        self.current_tetromino = tetromino.Tetromino(
            next_piece, point.Point(config.SPAWN[next_piece]), config.COLORS[next_piece])
        self.other_tetrominos = []

    def render_map(self):
        """Renders the map to the screen and updates matrices"""
        self.clear_matrix(self.piece_matrix)
        self.clear_matrix(self.map_matrix)

        self.render_background()

        # Render current playable piece
        self.current_tetromino.render_tetromino()
        for s in self.current_tetromino.sqrs:
            self.fill_matrix(self.piece_matrix, s)

        # Render the rest of the map
        for t in self.other_tetrominos:
            t.render_tetromino()
            for s in t.sqrs:
                self.fill_matrix(self.map_matrix, s)

    def switch_piece(self):
        """Appends the current piece to the map and assigns a new current piece"""
        next_piece = self.random_list.next()
        self.current_tetromino = tetromino.Tetromino(
            next_piece, point.Point(config.SPAWN[next_piece]), config.COLORS[next_piece])

    def fill_matrix(self, matrix, square):
        """Fills the matrix at the given indices with a 1"""
        if square.x >= self.width or square.y >= self.height:
            print(
                "Warning: position exceeds boundaries: [{:d}][{:d}]".format(square.x, square.y))
            return
        matrix[square.x][square.y] = 1

    def unfill_matrix(self, matrix, square):
        """Fills the matrix at the given indices with a 0"""
        if square.x >= self.width or square.y >= self.height:
            print(
                "Warning: position exceeds boundaries: [{:d}][{:d}]".format(square.x, square.y))
            return
        matrix[square.x][square.y] = 0

    def clear_matrix(self, matrix):
        """Clears the current matrix"""
        for i in range(self.width):
            for j in range(self.height):
                matrix[i][j] = 0

    def render_background(self):
        """Renders the background squares"""
        for i in range(self.width):
            for j in range(self.height):
                s = renderer.Renderer(i, j, config.COLORS["BACKGROUND"])
                s.draw()

    def print_matrix(self):
        """Prints the current matrix for debugging purposes"""
        for i in reversed(range(self.height)):
            for j in range(self.width):
                if self.map_matrix[j][i] or self.piece_matrix[j][i] == 1:
                    print(1, end=" ")
                else:
                    print(0, end=" ")
            print()
        print()
