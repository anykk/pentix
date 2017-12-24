#!/usr/bin/env python3
"""PyQt5 Pentix"""
import sys
import json

ERROR_PYTHON_VERSION = 1
ERROR_QT_IMPORT = 2
ERROR_MODULES_MISSING = 3

if sys.version_info < (3, 4):
    print('Use python >= 3.4', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

try:
    from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, \
        QInputDialog, QMessageBox, QVBoxLayout, QDialogButtonBox
    from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, pyqtSlot
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
        self.records_table = RecordsTable()
        self.game.player_data_msg[dict].connect(self.records_table.update_records)
        self.game.records_msg.connect(self.records_table.show_records)
        self.records_table.setWindowModality(Qt.WindowModal)

        self.setCentralWidget(self.game)

        self.status_bar = self.statusBar()
        self.game.status_bar_msg[str].connect(self.status_bar.showMessage)

        self.game.start()

        self.resize(200, 420)
        self.center()
        self.setWindowTitle('Pentix')
        self.show()

    def show_records(self):
        pass

    def center(self):
        """Центрируем окно"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)


class GameState(QFrame):
    """Игровая модель"""
    status_bar_msg = pyqtSignal(str)
    player_data_msg = pyqtSignal(dict)
    records_msg = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        """Начинаем игру"""
        self.game_board = Field(20, 10)
        self.shape = Shape()
        self.shape.new_shape(self.game_board)
        self.status_bar_msg.emit(str(self.game_board.score))
        self.timer.start(525, self)

    def send_player(self):
        name = QInputDialog.getText(None, "Get player name", "Player name:")
        if name[0]:
            self.player_data_msg.emit({name[0]: self.game_board.score})

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.game_board.score += 1
            self.status_bar_msg.emit(str(self.game_board.score))
            if self.game_board.is_game_over:
                self.timer.stop()
                self.status_bar_msg.emit("Game over!")
                self.send_player()
                self.records_msg.emit()
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


class RecordsTable(QMessageBox):
    """Класс таблицы рекордов"""
    def __init__(self):
        super().__init__()

    def show_records(self):
        """Показываем рекорды"""
        try:
            with open('records.json', 'r', encoding='utf-8') as file:
                records = json.load(file)
                temp = []
                for key in records:
                    temp.append((key, records[key]))
                temp.sort(key=lambda x: x[1], reverse=True)
                to_show = []
                for data in temp:
                    to_show.append(data[0])
                    to_show.append(': ')
                    to_show.append(data[1])
                    to_show.append('\r\n')
                result = ''.join(map(lambda x: str(x), to_show))
                self.information(None, "Records", result, QMessageBox.Ok)

        except FileNotFoundError:
            self.information(None, "Records", "Похоже, что отсутствует файл records.json в текущей директории. Он "
                                              "либо потерялся, "
                                              "либо рекорды не записывались. Без него, нечего вам показать ;'(",
                             QMessageBox.Ok)
        except Exception as e:
            self.critical(None, "Records", e)

    def update_records(self, data):
        """Обновляем таблицу рекордов"""
        try:
            file = open('records.json', 'r', encoding='utf-8')
            records = json.load(file)
            file.close()
            records.update(data)
            file = open('records.json', 'w', encoding='utf-8')
            json.dump(records, file, indent=4)
            file.close()
        except FileNotFoundError:
            file = open('records.json', 'w', encoding='utf-8')
            records = {}
            records.update(data)
            json.dump(records, file, indent=4)
            file.close()
        except Exception as e:
            self.critical(None, "Records", e)


if __name__ == '__main__':
    app = QApplication([])
    window = GameView()
    sys.exit(app.exec_())
