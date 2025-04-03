# main.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from PyQt6.QtCore import QTimer, QTime

from FR_login import LoginScreen
from FR_Data import DataEntryScreen
from FR_Timer import TimerDisplayScreen

MAX_JOBS_PER_HORNO = 2

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked = QStackedWidget()
        self.timer_screen = TimerDisplayScreen()
        self.login_screen = LoginScreen(self.to_data_entry)
        self.data_screen = DataEntryScreen(self.handle_job, lambda: self.timer_screen.jobs)

        self.stacked.addWidget(self.login_screen)
        self.stacked.addWidget(self.data_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def to_data_entry(self):
        self.stacked.setCurrentWidget(self.data_screen)
        QTimer.singleShot(10 * 60 * 1000, lambda: self.stacked.setCurrentWidget(self.login_screen))

    def handle_job(self, horno, job, salida, finish=False, pause=False):
        job = job.strip().upper()
        key = (horno, job)

        if finish:
            self.timer_screen.add_or_update_job(horno, job, None, finish=True)
            return

        if pause:
            self.timer_screen.toggle_pause(horno, job)
            return

        if not isinstance(salida, QTime):
            QMessageBox.warning(self, "Error", "Invalid exit time.")
            return

        if key in self.timer_screen.jobs:
            QMessageBox.warning(self, "Duplicate", f"Job '{job}' is already registered in {horno}.")
            return

        count = sum(1 for (h, _) in self.timer_screen.jobs if h == horno)
        if count >= MAX_JOBS_PER_HORNO:
            QMessageBox.warning(self, "Error", f"Maximum of {MAX_JOBS_PER_HORNO} jobs permited per {horno}.")
            return

        self.timer_screen.add_or_update_job(horno, job, salida)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    window.timer_screen.show()
    sys.exit(app.exec())
