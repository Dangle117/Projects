import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QListWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QTime, Qt


class StopWatch(QWidget):
    def __init__(self):
        super().__init__()

        # Widgets
        self.time_label: QLabel = QLabel("00:00:00.00")
        self.toggle_button: QPushButton = QPushButton("Start", self)
        self.lap_button: QPushButton = QPushButton("lap", self)
        self.reset_button: QPushButton = QPushButton("Reset", self)
        self.lap_list: QListWidget = QListWidget(self)

        self.is_running: bool = False

        # Timer
        self.timer: QTimer = QTimer()
        self.time: QTime = QTime(0, 0, 0, 0)

        self.initUI()

    def initUI(self):
        # window
        self.setWindowTitle("Stop watch")
        self.setWindowIcon(QIcon("app_logo/StopwatchIcon.png"))
        self.setGeometry(700, 400, 700, 300)

        # CSS style
        self.setStyleSheet("""
            QLabel {
                font-size: 150px;
                background-color: #F9DBDE;
                border-radius: 10px;
                padding: 10px;
            }

            QPushButton {
                font-size: 50px;
                padding: 10px;
                border: 2px solid rgb(0, 0, 0);  
                border-radius: 8px;
            }

            QPushButton:hover {
                color: white;
                background-color: #E5CDE8;
            }

            QPushButton:pressed {
                color: white;
                background-color: #E2C7E7;
            }

            QListWidget {
                font-size: 20px;
                font-weight: bold;
                background-color: #F5FFFA;
                border: 1px solid #E2C7E7;
                border-radius: 8px;
                padding: 5px;
            }
            
            QListWidget::item:selected {
                background-color: #E5CDE8;
                color: black;
            }
            
            QListWidget::item:hover {
                background-color: #EDE7F6;
            }
            
        """)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.time_label)
        vbox.addWidget(self.toggle_button)
        vbox.addWidget(self.reset_button)
        vbox.addWidget(self.lap_button)
        vbox.addWidget(self.lap_list)
        self.setLayout(vbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.toggle_button)
        hbox.addWidget(self.reset_button)
        hbox.addWidget(self.lap_button)

        vbox.addLayout(hbox)

        # Label
        self.time_label.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]

        # connect to function
        self.toggle_button.clicked.connect(self.toggle_timer)
        self.lap_button.clicked.connect(self.record_lap)
        self.reset_button.clicked.connect(self.reset_time)
        self.timer.timeout.connect(self.update_display)

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.toggle_button.setText("start")

        else:
            self.timer.start(10)
            self.toggle_button.setText("stop")

        self.is_running = not self.is_running

    def record_lap(self):
        current_time = self.format_time(self.time)
        self.lap_list.addItem(f"Lap {self.lap_list.count() + 1}: {current_time}")

        latest_item = self.lap_list.item(self.lap_list.count() - 2)
        self.lap_list.scrollToItem(latest_item, QListWidget.PositionAtBottom) # type: ignore[arg-type]

    def reset_time(self):
        self.timer.stop()
        self.time = QTime(0, 0, 0, 0)

        self.time_label.setText("00:00:00.00")
        self.lap_list.clear()

        self.is_running = False
        self.toggle_button.setText("start")


    def update_display(self):
        self.time = self.time.addMSecs(10)
        self.time_label.setText(self.format_time(self.time))

    @staticmethod
    def format_time(time):
        return time.toString("hh:mm:ss.zzz")[:-1]


def main() -> None:
    app = QApplication(sys.argv)
    watch = StopWatch()
    watch.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()