# main.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from PyQt6.QtCore import QTimer, QDateTime, QTime

from FR_login import LoginScreen
from FR_Data import DataEntryScreen
from FR_Timer import TimerDisplayScreen

MAX_JOBS_PER_HORNO = 2

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked = QStackedWidget()
        self.login_expiration = QDateTime.currentDateTime()

        self.timer_screen = TimerDisplayScreen(self.show_login_or_data)
        self.login_screen = LoginScreen(self.to_data_entry)
        self.data_screen = DataEntryScreen(self.handle_job, lambda: self.timer_screen.jobs)

        self.stacked.addWidget(self.login_screen)
        self.stacked.addWidget(self.data_screen)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stacked)
        self.setLayout(self.layout)

    def to_data_entry(self):
        self.stacked.setCurrentWidget(self.data_screen)
        self.login_expiration = QDateTime.currentDateTime().addSecs(600)  # 10 min
        QTimer.singleShot(10 * 60 * 1000, lambda: self.stacked.setCurrentWidget(self.login_screen))

    def show_login_or_data(self):
        if QDateTime.currentDateTime() > self.login_expiration:
            self.stacked.setCurrentWidget(self.login_screen)
        else:
            self.stacked.setCurrentWidget(self.data_screen)

    def handle_job(self, horno, job, salida, finish=False):
        job = job.strip().upper()
        key = (horno, job)

        if not finish:
            if not isinstance(salida, QTime):
                QMessageBox.warning(self, "Error", "Invalid exit time.")
                return
            if key in self.timer_screen.jobs:
                QMessageBox.warning(self, "Duplicate", f"Job '{job}' is already registered in {horno}.")
                return
            count = sum(1 for (h, _) in self.timer_screen.jobs if h == horno)
            if count >= MAX_JOBS_PER_HORNO:
                QMessageBox.warning(self, "Limit Reached", f"Only {MAX_JOBS_PER_HORNO} jobs are allowed per oven: {horno}")
                return

        self.timer_screen.add_or_update_job(horno, job, salida, finish)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    window.timer_screen.show()
    sys.exit(app.exec())
