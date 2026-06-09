# Copyright 2026, ShiningZec. All rights reserved.

import os
import sys
import random
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QPixmap


from src import HandWritingWidget, Quiz, QuizLoader, QuizLoaderAI, QuizRequest


class QuizGenerateWorker(QObject):
    finished = Signal(str)  # file path
    error = Signal(str)

    def __init__(self, quiz_request: QuizRequest):
        super().__init__()
        self.quiz_request = quiz_request
        base_path = os.path.dirname(__file__)
        self.dataset_dir = os.path.join(base_path, "dataset")

    @Slot()
    def run(self):
        try:
            loader = QuizLoaderAI()

            # 获取题目
            loader.get_quizzes(self.quiz_request)

            # 自动生成文件名
            filename = (
                f"{self.quiz_request.category}_"
                f"{self.quiz_request.topic}_"
                f"{self.quiz_request.difficulty}.json"
            )

            actual_file = loader.dump_and_drop_quizzes(
                os.path.join(self.dataset_dir, filename)
            )

            self.finished.emit(actual_file)

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz-Monde")
        self.resize(1080, 720)

        base_path = os.path.dirname(__file__)
        self.dataset_dir = os.path.join(base_path, "dataset")
        self.assets_dir = os.path.join(base_path, "assets")

        self.loader = QuizLoader(self.dataset_dir)
        self.categories = self.loader.load_categories()

        # 题目库
        self.quiz_storage = []
        self.remained_quizzes = len(self.quiz_storage)
        self.correct_count = 0
        self.total_count = 0

        # 标签页
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # 页 1：答题界面
        tab1 = QWidget()
        tabs.addTab(tab1, "答题")
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(0, 0, 0, 0)

        # 页 2：题库管理界面（待实现）
        tab2 = QWidget()
        tabs.addTab(tab2, "题库管理")
        tab2_layout = QVBoxLayout(tab2)
        # tab2_layout.addWidget(QLabel("题库管理界面（待实现）"))

        # 题库管理: tab2
        top_layout = QHBoxLayout()
        tab2_layout.addLayout(top_layout)
        self.category_group = QGroupBox("题库管理")
        top_layout.addWidget(self.category_group)
        cat_layout = QVBoxLayout(self.category_group)
        self.category_checkboxes = []
        for cat in self.categories:
            cb = QCheckBox(cat)
            cb.setChecked(True)
            cat_layout.addWidget(cb)
            self.category_checkboxes.append(cb)
        # 刷新按钮
        btn_refresh = QPushButton("刷新")
        btn_refresh.clicked.connect(self.refresh_categories)
        cat_layout.addWidget(btn_refresh)

        # tab2:bottom
        self.bottom_group = QGroupBox("让AI生成题目吧!")
        bottom_layout = QVBoxLayout(self.bottom_group)
        form_layout = QFormLayout()
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(10)
        self.category_edit = QLineEdit()
        self.topic_edit = QLineEdit()
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["easy", "medium", "hard"])
        form_layout.addRow("数量", self.count_spin)
        form_layout.addRow("分类", self.category_edit)
        form_layout.addRow("主题", self.topic_edit)
        form_layout.addRow("难度", self.difficulty_combo)
        bottom_layout.addLayout(form_layout)
        self.generate_btn = QPushButton("生成并保存")
        self.generate_btn.clicked.connect(self.generate_quizzes)
        bottom_layout.addWidget(self.generate_btn)
        self.ai_log = QTextEdit()
        self.ai_log.setReadOnly(True)
        bottom_layout.addWidget(self.ai_log)
        tab2_layout.addWidget(self.bottom_group)

        # tab1 上部显示包装
        self.wrapper_widget = QWidget()
        wrapper_layout = QHBoxLayout(self.wrapper_widget)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        tab1_layout.addWidget(self.wrapper_widget)
        # 剩余题目数、分数显示标签
        self.remain_label = QLabel("剩余题数: 0")
        wrapper_layout.addWidget(self.remain_label, alignment=Qt.AlignLeft)
        self.score_label = QLabel("分数: 0/0")
        wrapper_layout.addWidget(self.score_label, alignment=Qt.AlignRight)
        # 重置分数按钮、重置题库按钮
        btn_reset = QPushButton("重置分数")
        btn_reset.clicked.connect(self.reset_score)
        wrapper_layout.addWidget(btn_reset)
        btn_reload = QPushButton("重置题库")
        btn_reload.clicked.connect(
            lambda: (self.refresh_question_storage(), self.next_question(reload=True))
        )
        wrapper_layout.addWidget(btn_reload)

        # 中部：题目内容区（可滚动）
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setMinimumHeight(150)
        self.content_widget = QWidget()
        self.content_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout(self.content_widget)
        tab1_layout.addWidget(self.content_area)

        # 显示单选项的区域和组件(滚动)
        self.options_area = QScrollArea()
        self.options_area.setWidgetResizable(True)
        self.options_area.setMinimumHeight(150)
        self.options_layout = QVBoxLayout()
        self.options_widget = QWidget()
        self.options_widget.setLayout(self.options_layout)
        self.options_area.setWidget(self.options_widget)
        tab1_layout.addWidget(self.options_area)
        self.round_widgets = []

        # 作答区：手写区。永久显示
        self.answer_group = QGroupBox("作答")
        self.answer_layout = QVBoxLayout(self.answer_group)
        self.answer_layout.addWidget(HandWritingWidget(self))
        # 外边框
        self.answer_group.setStyleSheet(
            """QGroupBox{
                border: 10px solid #CED4DA;
                border-radius: 5px;
                margin-top: 10px;
            }
            """
        )
        tab1_layout.addWidget(self.answer_group)
        self.answer_group.show()

        # “Show Answer” 按钮
        self.btn_show_answer = QPushButton("显示答案")
        self.btn_show_answer.clicked.connect(self.show_answer)
        tab1_layout.addWidget(self.btn_show_answer)

        # 标准答案显示区(区域永久显示)
        self.answer_label = QLabel("")
        self.answer_label.setWordWrap(True)
        self.answer_label.setStyleSheet(
            """
            color: black;
            font-size: 18px;
            font-weight: bold;
            background-color: #E9ECEF; border: 1px solid #CED4DA; padding: 4px;
            """
        )
        tab1_layout.addWidget(self.answer_label)

        # “正确/错误”按钮
        self.btn_correct = QPushButton("✔ 正确")
        self.btn_correct.clicked.connect(
            lambda: (self.record_result(True), self.next_question())
        )
        self.btn_correct.setStyleSheet("background-color: #4DABF7; color: #FFFFFF;")
        self.btn_correct.show()
        self.btn_wrong = QPushButton("✘ 错误")
        self.btn_wrong.clicked.connect(
            lambda: (self.record_result(False), self.next_question())
        )
        self.btn_wrong.setStyleSheet("background-color: #FF6B6B; color: #FFFFFF;")
        self.btn_wrong.show()
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_correct)
        btn_layout.addWidget(self.btn_wrong)
        tab1_layout.addLayout(btn_layout)

        # “Skip”按钮
        self.btn_next = QPushButton("Skip")
        self.btn_next.clicked.connect(self.next_question)
        tab1_layout.addWidget(self.btn_next)

        # self.answer_label.show()
        self.btn_correct.show()
        self.btn_wrong.show()

        # 载入第一题
        self.next_question(reload=True)

        # 标签页的样式
        tabs.setStyleSheet(
            """QTabWidget::pane { border: 1px solid #CED4DA; }
               QTabBar::tab { background: #E9ECEF; border: 1px solid #CED4DA; padding: 6px; }
               QTabBar::tab:selected { background: #4DABF7; color: #FFFFFF; }
            """
        )

    def refresh_categories(self):
        # 重新扫描题库目录并更新复选框
        self.categories = self.loader.load_categories()
        for cb in self.category_checkboxes:
            cb.deleteLater()
        self.category_checkboxes.clear()
        layout = self.category_group.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                widget.deleteLater()
        for cat in self.categories:
            cb = QCheckBox(cat)
            cb.setChecked(True)
            layout.insertWidget(layout.count() - 1, cb)  # 插入到刷新、重置按钮之前
            self.category_checkboxes.append(cb)

    def reset_score(self):
        # 重置计分
        self.correct_count = 0
        self.total_count = 0
        self.update_score_label()

    def update_score_label(self):
        self.score_label.setText(f"分数: {self.correct_count}/{self.total_count}")

    def clear_layout(self, layout):
        # 删除布局中所有部件
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def show_answer(self):
        # 显示标准答案并显示判题按钮
        if self.current_quiz:
            self.answer_label.setText(f"标准答案：{self.current_quiz.answer}")
            self.answer_label.show()
            self.btn_correct.show()
            self.btn_wrong.show()

    def record_result(self, correct: bool):
        # 用户判题后的记录
        self.total_count += 1
        if correct:
            self.correct_count += 1
        self.update_score_label()
        self.btn_next.setEnabled(True)

    def next_question(self, reload: bool = False):
        # 加载下一题
        # 如果题目库已经为空，则根据选中分类加载题目列表
        if reload:
            selected = [cb.text() for cb in self.category_checkboxes if cb.isChecked()]
            self.quiz_storage = self.loader.load_quizzes(selected)
        if not self.quiz_storage:
            self.current_quiz: Optional[Quiz] = None
            # destroy old widgets
            for w in self.round_widgets:
                w.deleteLater()
            self.round_widgets.clear()
            self.clear_layout(self.options_layout)
            self.clear_layout(self.content_layout)

            label = QLabel("恭喜！题目已回答完毕！")
            label.setWordWrap(True)
            label.setStyleSheet(
                """QLabel{
                    color: black;
                    font-size: 16px;
                    font-weight: bold;
                }"""
            )
            self.content_layout.addWidget(label)
            self.remained_quizzes = 0
            self.remain_label.setText(f"剩余题数: {self.remained_quizzes}")
            return

        # 清除答案显示区和选项区等等
        self.clear_layout(self.content_layout)
        self.answer_label.setText("")

        # 选择一题并显示
        self.current_quiz: Optional[Quiz] = random.choice(self.quiz_storage)
        self.quiz_storage.remove(self.current_quiz)
        self.answer_group.show()
        self.btn_show_answer.setEnabled(True)
        # self.btn_next.setEnabled(False)

        # 渲染题目内容块
        for block in self.current_quiz.content_blocks:
            if block.type == "text":
                label = QLabel(block.content)
                label.setWordWrap(True)
                label.setStyleSheet(
                    """QLabel{
                        color: black;
                        font-size: 16px;
                        font-weight: bold;
                    }"""
                )
                self.content_layout.addWidget(label)
            elif block.type == "image":
                img_label = QLabel()
                img_label.setAlignment(Qt.AlignCenter)
                img_path = os.path.join(
                    self.dataset_dir, self.current_quiz.category, block.content
                )
                if not os.path.exists(img_path):
                    img_path = os.path.join(self.assets_dir, block.content)
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    if not pixmap.isNull():
                        # 按宽度 600 缩放，保持宽高比
                        pixmap = pixmap.scaledToWidth(600, Qt.SmoothTransformation)
                        img_label.setPixmap(pixmap)
                self.content_layout.addWidget(img_label)

        # 渲染单选题的选项
        if self.current_quiz.type == "single_choice":
            self.show_single_choices(self.current_quiz.options)
        else:
            # destroy old widgets
            for w in self.round_widgets:
                w.deleteLater()
            self.round_widgets.clear()
            self.clear_layout(self.options_layout)

        # 清理手写区
        self.answer_group.findChild(HandWritingWidget).clear_board()

        # 更新剩余题数
        self.remained_quizzes = len(self.quiz_storage) + 1  # +1 = current quiz
        self.remain_label.setText(f"剩余题数: {self.remained_quizzes}")

    def refresh_question_storage(self):
        # 根据选中分类刷新题目列表
        selected = [cb.text() for cb in self.category_checkboxes if cb.isChecked()]
        self.quiz_storage = self.loader.load_quizzes(selected)
        self.remained_quizzes = len(self.quiz_storage)
        self.remain_label.setText(f"剩余题数: {self.remained_quizzes}")

    def show_single_choices(self, options: list[str]):
        # destroy old widgets
        for w in self.round_widgets:
            w.deleteLater()
        self.round_widgets.clear()
        self.clear_layout(self.options_layout)

        box_width = 200
        box_height = 40
        for opt in options:
            label = QLabel(opt, self.content_widget)
            label.setFixedSize(box_width, box_height)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                """QLabel{
                    color: black;
                    border: 1px solid #CED4DA;
                    border-radius: 10px;
                    background-color: #A6D4E3;
                    font-size: 16px;
                    font-weight: bold;
                }"""
            )
            self.options_layout.addWidget(label)
            self.round_widgets.append(label)

    def generate_quizzes(self):
        request = QuizRequest(
            count=self.count_spin.value(),
            category=self.category_edit.text().strip(),
            topic=self.topic_edit.text().strip(),
            difficulty=self.difficulty_combo.currentText(),
        )
        self.generate_btn.setEnabled(False)

        self.ai_log.append("开始生成题目...")
        self.thread = QThread()
        self.worker = QuizGenerateWorker(request)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_generate_success)
        self.worker.error.connect(self.on_generate_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_generate_success(self, file_path: str):
        self.ai_log.append(f"生成成功，已保存到：{file_path}")
        self.generate_btn.setEnabled(True)

    def on_generate_error(self, msg: str):
        self.ai_log.append(f"生成失败：{msg}")
        self.generate_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    # 设置全局样式（颜色主题）
    app.setStyleSheet("""
        QWidget { background-color: #F8F9FA; color: #212529; }
        QPushButton { background-color: #4DABF7; color: #FFFFFF; border:none; padding:6px; }
        QPushButton:disabled { background-color: #CCCCCC; }
        QLineEdit { padding:4px; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
