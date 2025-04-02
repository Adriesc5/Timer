# FR_login.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

LOGIN_USER = "Admin"
LOGIN_PASS = "Admin"

class LoginScreen(QWidget):
    def __init__(self, switch_to_data):
        super().__init__()
        self.switch_to_data = switch_to_data

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo TMCDL centrado
        logo = QLabel()
        logo.setPixmap(QPixmap("TMCDL-removebg-preview.png").scaledToHeight(80))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Título estilizado
        self.label = QLabel("User Login")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.label.setStyleSheet("color: #112D4E;")  


        # Inputs de login
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("User")
        self.user_input.setFixedHeight(40)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setFixedHeight(40)

        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setStyleSheet("background-color: #3F72AF; color: white; font-size: 18px;")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addSpacing(20)
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_btn)
        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        if self.user_input.text() == LOGIN_USER and self.pass_input.text() == LOGIN_PASS:
            self.switch_to_data()
        else:
            QMessageBox.warning(self, "Error", "Incorrect credentials")