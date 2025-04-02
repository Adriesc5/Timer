# FR_login.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

LOGIN_USER = "Admin"
LOGIN_PASS = "Admin"

class LoginScreen(QWidget):
    def __init__(self, switch_to_data):
        super().__init__()
        self.switch_to_data = switch_to_data

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        logo = QLabel()
        logo.setPixmap(QPixmap("TMCDL-removebg-preview.png").scaledToHeight(100))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Login")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #112D4E;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("background-color: #3F72AF; color: white; font-size: 16px;")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        if self.user_input.text() == LOGIN_USER and self.pass_input.text() == LOGIN_PASS:
            self.switch_to_data()
        else:
            QMessageBox.warning(self, "Error", "Incorrect credentials")