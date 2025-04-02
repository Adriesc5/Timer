from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path

base_path = Path(__file__).parent

LOGIN_USER = "Tanking"
LOGIN_PASS = "Tan123!"

class LoginScreen(QWidget):
    def __init__(self, switch_to_data):
        super().__init__()
        self.switch_to_data = switch_to_data

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)

        logo = QLabel()
        logo.setPixmap(
            QPixmap(str(base_path / "TMCDL-removebg-preview.png")).scaled(
                200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        )
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
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3F72AF;
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #365f91;
            }
            QPushButton:pressed {
                background-color: #2f4e73;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        form.setLayout(layout)
        form.setMaximumWidth(300)
        outer_layout.addWidget(form)
        self.setLayout(outer_layout)

    def handle_login(self):
        if self.user_input.text() == LOGIN_USER and self.pass_input.text() == LOGIN_PASS:
            self.switch_to_data()
        else:
            QMessageBox.warning(self, "Error", "Incorrect credentials")
