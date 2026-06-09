from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtGui import QPainter, QPen, QColor, QIcon
from PySide6.QtCore import Qt, QPoint, QSize  # noqa F401


class HandWritingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("手写板")
        self.setMinimumSize(400, 400)
        # self.setMaximumSize(1080, 720)
        self.paths = []  # store paths
        self.current_path = []  # current path being drawn

        # set background color
        self.backgroundColor = QColor(240, 240, 240)  # a bit pale white background

        # clear_button
        self.clear_btn = QPushButton(self)
        self.clear_btn.setIcon(QIcon("./assets/clear.png"))
        self.clear_btn.setIconSize(QSize(30, 30))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: none; border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.clear_btn.clicked.connect(self.clear_board)

        # undo_button
        self.undo_btn = QPushButton(self)
        self.undo_btn.setIcon(QIcon("./assets/undo.png"))
        self.undo_btn.setIconSize(QSize(30, 30))
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: none; border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.undo_btn.clicked.connect(self.undo_last)

    def resizeEvent(self, event):
        # position buttons at bottom-left, bottom-right corner
        margin = 10
        btn_size = 30
        self.clear_btn.move(margin, self.height() - btn_size - margin)
        self.undo_btn.move(self.width() - btn_size - margin, self.height() - btn_size - margin)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.current_path = [event.position()]  # start a new path
            self.update()
        if event.button() == Qt.RightButton:
            self.undo_last()  # undo last path
        if event.button() == Qt.MiddleButton:
            self.clear_board()  # clear all paths

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.current_path.append(event.position())  # add to current path
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.paths.append(self.current_path)  # save the completed path
            self.current_path = []  # reset current path
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.Antialiasing
        )  # enable anti-aliasing for smoother lines
        pen = QPen(QColor(0, 0, 0), 2)  # black pen with width 2
        painter.setPen(pen)

        # draw all saved paths
        for path in self.paths:
            for i in range(1, len(path)):
                painter.drawLine(path[i - 1], path[i])

        # draw current path
        for i in range(1, len(self.current_path)):
            painter.drawLine(self.current_path[i - 1], self.current_path[i])
    
    def clear_board(self):
        self.paths = []
        self.current_path = []
        self.update()
    
    def undo_last(self):
        if self.paths:
            self.paths.pop()
            self.update()



def main():
    app = QApplication([])
    window = HandWritingWidget()
    window.show()
    app.exec()

    

if __name__ == "__main__":
    main()
