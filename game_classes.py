from random import choice
from shapes import shapes


class Field:

    def __init__(self, rows, columns):
        """Инициализируем игровую доску"""
        self.rows = rows
        self.columns = columns
        self.grid = [[0] * columns for _ in range(rows)]
        self.grid_color = 0x69af69
        self.score = 0
        self.want_new_shape = True
        self.is_game_over = False

    def land_shape(self, Shape):
        """Записываем фигуру на карту (складываем как матрицы, только по тем индексам, где в фигуре 1)"""
        for y, row in enumerate(Shape.shape):
            for x, col in enumerate(row):
                if Shape.shape[y][x]:
                    self.grid[y + Shape.y][x + Shape.x] = col

        self.del_full_rows()

        if self.want_new_shape:
            Shape.new_shape(self)

    def del_full_rows(self):
        """Удаляем полные ряды"""
        for y, row in enumerate(self.grid):
            if 0 not in row:
                del self.grid[y]
                self.grid = [[0] * self.columns] + self.grid
                self.score += 10
        self.want_new_shape = True


class Shape:
    def new_shape(self, GameBoard):
        """Спауним новую фигуру и проверяем, может ли она двигаться"""
        self.shape = choice(shapes)
        self.shape_color = 0x252d25
        self.y, self.x = 0, 4
        GameBoard.want_new_shape = False

        if not self.try_move(GameBoard, self.x, self.y):
            GameBoard.is_game_over = True

    def try_move(self, GameBoard, dx, dy):
        """Проверка на возможность движения фигуры (на местах, где в фигуре 1,
         смотрим столкновения с картой или с другими 1, т.е. фигурами)"""
        for y, row in enumerate(self.shape):
            for x, col in enumerate(row):
                if self.shape[y][x]:
                    if x + dx < 0 or x + dx >= 10 or y + dy < 0 or y + dy >= 20:
                        return False
                    if GameBoard.grid[y + dy][x + dx]:
                        return False
        self.x, self.y = dx, dy
        return True

    def move_down(self, GameBoard):
        """Движение фигуры вниз"""
        if not self.try_move(GameBoard, self.x, self.y + 1):
            GameBoard.land_shape(self)

    def drop_down(self, GameBoard):
        """Ускоренное падение"""
        new_y = self.y

        while self.try_move(GameBoard, self.x, new_y + 1):
            new_y += 1
        GameBoard.land_shape(self)

    def rotate_shape(self, GameBoard, dx, dy):
        """Поворот фигуры по часовой стрелке"""
        old = self.shape
        self.shape = list(map(lambda *l: list(l), *self.shape[::-1]))
        if not self.try_move(GameBoard, dx, dy):
            self.shape = old
