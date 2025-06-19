import sys
import requests
from config import API_KEY
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QKeyEvent

class WeatherAPI(QWidget):
    api_key = API_KEY
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q="

    def __init__(self):
        super().__init__()

        self.title_label: QLabel = QLabel("🌪️ CITY 🍃", self)
        self.city_input: QLineEdit = QLineEdit(self)
        self.enter_button: QPushButton = QPushButton("Get Weather", self)

        self.temp_label: QLabel = QLabel(self)
        self.emoji_desc: QLabel = QLabel(self)
        self.text_desc: QLabel = QLabel(self)

        self.initUI()

    def initUI(self):
        # Window edit
        self.setWindowTitle("Weather API")
        self.setWindowIcon(QIcon("weather_icon/sunny.png"))
        self.setStyleSheet("""
            background-color: #E6E9EB;
        """)

        # Set layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.title_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.enter_button)
        vbox.addWidget(self.temp_label)
        vbox.addWidget(self.emoji_desc)
        vbox.addWidget(self.text_desc)

        self.setLayout(vbox)

        # Label
        self.title_label.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]
        self.temp_label.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]

        self.emoji_desc.setAlignment(Qt.AlignCenter) # type: ignore[arg-type]
        self.text_desc.setAlignment(Qt.AlignCenter)  # type: ignore[arg-type]

        self.title_label.setStyleSheet("""
            font-size: 60px;
            font-weight: bold;
            color: #23B4C7;
            font-family: "Arial Black";
        """)

        self.temp_label.setStyleSheet("""
            font-size: 60px;
            font-family: calibri;
            font-weight: bold;
        """)

        self.emoji_desc.setStyleSheet("""
            font-size: 130px;
        """)

        self.text_desc.setStyleSheet("""
            font-size: 45px;
            font-family: "Arial Black";
        """)

        # Text box
        self.city_input.setStyleSheet("""
            font-family: "Helvetica";
            font-size: 40px;
            border-radius: 10px;
            border: 2px solid rgb(0, 0, 0);
            color: #387DC8;
            
        """)

        # Button
        self.enter_button.setStyleSheet("""
            QPushButton {
                font-size: 35px;
                background-color: lightblue;
                border: 2px solid rgb(0, 0, 0);
                border-radius: 10px;
                font-family: "Trebuchet MS";
            }
            
            QPushButton:hover {
                background-color: #75BAF6;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #5FB2F3;
                color: white;
            }
            
        """)

        # Install an event filter on the QLineEdit
        self.city_input.installEventFilter(self)

        # Connection
        self.enter_button.clicked.connect(self.enter_clicked)


    # user press enter
    def eventFilter(self, obj, event):
        if obj == self.city_input and event.type() == QKeyEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):  # Detect an Enter key
                self.enter_button.click()  # Simulate button click
                return True  # Stop event propagation
        return super().eventFilter(obj, event)


    def enter_clicked(self):
        data = self.get_api_info()


        if data:
            temp_celsius: float = round(data["main"]["temp"] - 273.15)
            description: str = data["weather"][0]["main"]

            weather_id: int = data["weather"][0]["id"]
            weather_icon = self.get_weather_icon(weather_id)
            icon: QPixmap = QPixmap(weather_icon)

            if icon.isNull():
                self.show_error(f"Failed to load {weather_icon}")

            self.temp_label.setText(f"{temp_celsius}°C")
            self.temp_label.setStyleSheet("""
                font-size: 60px;
                font-family: calibri;
                font-weight: bold;
            """)

            self.emoji_desc.setPixmap(icon.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # type: ignore[arg-type]
            self.text_desc.setText(description)

    def get_api_info(self):
        city = self.city_input.text().strip()
        url = f"{self.api_url}{city}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            return data

        # Network & Connection Errors (requests library)
        except requests.exceptions.HTTPError as http_error:
            status_code = http_error.response.status_code if http_error else "Unknown"

            # HTTP Status Code Error (API Response)
            match status_code:
                case 400: # Bad Request
                    print("Bad Request:\nCheck your input parameters.")
                    mes = "Bad Request:\nCheck your input parameters."
                    self.temp_label.setStyleSheet("font-size: 30px;")
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.setText(mes)

                case 401: #Unauthorized
                    print("Unauthorized: invalid API key.")
                    mes = "Unauthorized: invalid API key."
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 403: #Forbidden
                    print("Forbidden: access is denied.")
                    mes = "Forbidden: access is denied."
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 404: #Not Found
                    print("Not Found:\nCity not found.")
                    mes = "Not Found:\nCity not found."
                    self.temp_label.setStyleSheet("font-size: 30px;")
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.setText(mes)

                case 429: #Too Many Requests
                    print("Too many request. Please try again later!")
                    mes = "Too many request. Please try again later!"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 500: #Interal Sever Error
                    print("Sever error. Try again later")
                    mes = "Sever error. Try again later"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 502: #Bad Gateway
                    print("Bad Gateway:\nInvalid response from the server")
                    mes = f"Bad Gateway:\nInvalid response from the server"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 503:  # Service Unavailable
                    print("Service Unavailable:\nServer is down")
                    mes = f"Service Unavailable:\nServer is down"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case 504: #Gateway Timeout
                    print("Gateway Timeout:\nNo response from the server")
                    mes = f"Gateway Timeout:\nNo response from the server"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

                case _:
                    print(f"HTTP Error: {status_code}")
                    mes = f"HTTP Error: {status_code}"
                    self.emoji_desc.clear()
                    self.text_desc.clear()
                    self.temp_label.clear()
                    self.show_error(mes)

        except requests.ConnectionError:
            print("Error: Failed to connect to the server")
            mes = "Error: Failed to connect to the server"
            self.emoji_desc.clear()
            self.text_desc.clear()
            self.temp_label.clear()
            self.show_error(mes)

        except requests.Timeout:
            print("Error: The request timed out. Try again later.")
            mes = "Error: The request timed out. Try again later."
            self.emoji_desc.clear()
            self.text_desc.clear()
            self.temp_label.clear()
            self.show_error(mes)

        except requests.RequestException as e:
            print(f"Error: {e}")
            mes =f"Error: {e}"
            self.emoji_desc.clear()
            self.text_desc.clear()
            self.temp_label.clear()
            self.show_error(mes)

        except ValueError:
            print("Error: Failed to parse JSON response.")
            mes = "Error: Failed to parse JSON response."
            self.show_error(mes)

    @staticmethod
    def get_weather_icon(id: int):
        if 200 <= id <= 232:
            return "weather_icon/thunder.png"

        elif 300 <= id <= 321:
            return "weather_icon/drizzle.png"

        elif 500 <= id <= 531:
            return "weather_icon/rain.png"

        elif 600 <= id <= 622:
            return "weather_icon/snow.png"

        elif 701 <= id <= 741:
            return "weather_icon/mist.png"

        elif id == 762:
            return "weather_icon/volcano.png"

        elif id == 771:
            return "weather_icon/squall.png"

        elif id == 781:
            return "weather_icon/tornado.png"

        elif id == 800:
            return "weather_icon/sunny.png"

        elif 801 <= id <= 804:
            return "weather_icon/cloud.png"

        else:
            return ""

    @staticmethod
    def show_error(message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()

def main() -> None:
    app = QApplication(sys.argv)
    window = WeatherAPI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

