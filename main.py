#!/usr/bin/env python3
"""PyQt5 Pentix"""

ERROR_PYTHON_VERSION = 1
ERROR_QT_IMPORT = 2
ERROR_MODULES_MISSING = 3

import sys

if sys.version_info < (3, 4):
    print('Use python >= 3.4', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

try:
    from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
    from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
    from PyQt5.QtGui import QPainter, QColor
except Exception as e:
    print('PyQt5 not found: "{}."'.format(e),
          file=sys.stderr)
    sys.exit(ERROR_QT_IMPORT)

try:
    from game_classes import Field, Shape
except Exception as e:
    print('Game modules not found: "{}"'.format(e), file=sys.stderr)
    sys.exit(ERROR_MODULES_MISSING)


__version__ = '0'
__author__ = 'Yuldashev Kirill'
__email__ = 'kirill.yuldashev@mail.ru'


class GameView(QMainWindow):
    """Отрисовка"""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.game = GameState(self)

        self.setCentralWidget(self.game)

        self.status_bar = self.statusBar()
        self.game.status_bar_msg[str].connect(self.status_bar.showMessage)

        self.game.start()

        self.resize(200, 425)
        self.center()
        self.setWindowTitle('Pentix')
        self.show()

    def center(self):
        """Центрируем окно"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)


class GameState(QFrame):
    """Игровая модель"""
    status_bar_msg = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        """Начинаем игру"""
        self.game_board = Field(20, 10)
        self.shape = Shape()
        self.shape.new_shape(self.game_board)
        self.status_bar_msg.emit(str(self.game_board.cnt_full_rows))
        self.timer.start(525, self)

    def timerEvent(self, event):

        if event.timerId() == self.timer.timerId():
            self.status_bar_msg.emit(str(self.game_board.cnt_full_rows))
            if self.game_board.is_game_over:
                self.timer.stop()
                self.status_bar_msg.emit("Game over!")
            elif self.game_board.want_new_shape:
                self.shape.new_shape(self.game_board)
                self.update()
            else:
                self.shape.move_down(self.game_board)
                self.update()
        else:
            super(GameState, self).timerEvent(event)

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw_block(self, qp, x, y, color):
        """Рисуем отдельный блок"""
        color = QColor(color)
        col = QColor(self.game_board.grid_color)
        qp.setPen(col)

        qp.setBrush(color)
        qp.drawRect(x, y, 20, 20)

    def draw(self, qp):
        """Рисуем карту, рисуем фигуру (по блокам)"""
        for y in range(self.game_board.rows):
            for x in range(self.game_board.columns):
                if self.game_board.grid[y][x]:
                    self.draw_block(qp, x * 20, y * 20, self.shape.shape_color)
                else:
                    self.draw_block(qp, x * 20, y * 20, self.game_board.grid_color)

        for y in range(len(self.shape.shape)):
            for x in range(len(self.shape.shape[y])):
                if self.shape.shape[y][x]:
                    self.draw_block(qp, (x + self.shape.x) * 20, (y + self.shape.y) * 20, self.shape.shape_color)

    def keyPressEvent(self, event):

        if self.game_board.is_game_over:
            super(GameState, self).keyPressEvent(event)
            return
        # if event.key() == Qt.Key_P:
            # self.pause()
            # return
        if event.key() == Qt.Key_Left:
            self.shape.try_move(self.game_board, self.shape.x - 1, self.shape.y)
            self.update()
        elif event.key() == Qt.Key_Right:
            self.shape.try_move(self.game_board, self.shape.x + 1, self.shape.y)
            self.update()
        elif event.key() == Qt.Key_Down:
            self.shape.move_down(self.game_board)
            self.update()
        elif event.key() == Qt.Key_Space:
            self.shape.drop_down(self.game_board)
            self.update()
        elif event.key() == Qt.Key_Up:
            self.shape.rotate_shape(self.game_board, self.shape.x, self.shape.y)
            self.shape.try_move(self.game_board, self.shape.x, self.shape.y)
            self.update()
        else:
            super(GameState, self).keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = GameView()
    sys.exit(app.exec_())
