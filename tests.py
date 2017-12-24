import unittest
from game_classes import Field, Shape


class TestClasses(unittest.TestCase):
    def setUp(self):
        self.game_board = Field(20, 10)
        self.shape = Shape()

    def test_del_rows(self):
        self.game_board.grid[19] = [1] * 5 + [0] * 5
        self.game_board.grid[18] = [1] * self.game_board.columns
        self.game_board.grid[17] = [0] * 5 + [1] * 5

        self.game_board.del_full_rows()

        self.assertEqual(self.game_board.grid[19], [1] * 5 + [0] * 5)
        self.assertEqual(self.game_board.grid[18], [0] * 5 + [1] * 5)

    def test_land_shape(self):
        self.shape.new_shape(self.game_board)
        old = self.shape.shape
        self.game_board.land_shape(self.shape)
        self.assertEqual(self.game_board.grid[0][4], old[0][0])

    def test_move_down(self):
        self.shape.new_shape(self.game_board)

        self.shape.move_down(self.game_board)

        self.assertEqual((self.shape.y, self.shape.x), (1, 4))

    def test_move_shape(self):
        self.shape.new_shape(self.game_board)

        self.shape.try_move(self.game_board, 5, 15)

        self.assertEqual((self.shape.y, self.shape.x), (15, 5))
        self.assertEqual(self.game_board.grid[15][5], 0)
        self.assertEqual(self.game_board.grid[15][6], 0)
        self.assertEqual(self.game_board.grid[16][5], 0)
        self.assertEqual(self.game_board.grid[16][6], 0)


if __name__ == '__main__':
    unittest.main()