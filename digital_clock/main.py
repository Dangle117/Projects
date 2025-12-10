import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QTime, Qt, QDate
from PyQt5.QtGui import QIcon, QFontDatabase, QFont


class DigitalClock(QWidget):
    def __init__(self):
        super().__init__()
        self.date_label: QLabel = QLabel(self)
        self.time_label: QLabel = QLabel(self)

        self.timer: QTimer = QTimer(self)

        self.initUI()

    def initUI(self):
        # WINDOW
        self.setWindowTitle("Digital Clock")
        self.setGeometry(700, 500, 600, 200)
        self.setWindowIcon(QIcon("logo_imagine/digital-clock.png"))

        # SET LAYOUT
        vbox = QVBoxLayout()
        vbox.addWidget(self.time_label)
        vbox.addWidget(self.date_label)
        self.setLayout(vbox)

        # Label
        self.time_label.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]
        self.date_label.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]

        self.time_label.setStyleSheet("""
            font-size: 150px;
            font-weight: bold;
            color: purple;
        
        """)

        self.date_label.setStyleSheet("""
            font-size: 50px;
            font-weight: bold;
            color: purple;
            font-family: calibri;

        """)

        # Set specific font
        font_id = QFontDatabase.addApplicationFont("Font/technology.bold.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.time_label.setFont(QFont(font_family))

        # Connection
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()


    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        current_date = QDate.currentDate().toString("dddd, MMMM d, yyyy")
        self.time_label.setText(current_time)
        self.date_label.setText(current_date)


def main() -> None:
    app = QApplication(sys.argv)
    clock = DigitalClock()
    clock.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
