# main.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from PyQt6.QtCore import QTimer, QTime

from FR_login import LoginScreen
from FR_Data import DataEntryScreen
from FR_Timer import TimerDisplayScreen

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked = QStackedWidget()
        self.unit = None
        self.timer_screen = None
        self.login_screen = LoginScreen(self.to_data_entry)
        self.data_screen = None

        self.stacked.addWidget(self.login_screen)
        layout = QVBoxLayout()
        layout.addWidget(self.stacked)
        self.setLayout(layout)

    def to_data_entry(self, unit):
        self.unit = unit
        if self.timer_screen:
            self.timer_screen.close()

        self.timer_screen = TimerDisplayScreen(self.unit)
        self.timer_screen.show()

        self.data_screen = DataEntryScreen(
            self.handle_job, lambda: self.timer_screen.jobs, self.unit
        )

        if self.stacked.count() > 1:
            self.stacked.removeWidget(self.stacked.widget(1))
        self.stacked.addWidget(self.data_screen)
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
        max_jobs = 2 if self.unit == "E2X" else 3
        if count >= max_jobs:
            QMessageBox.warning(self, "Error", f"Maximum of {max_jobs} jobs allowed for {horno}.")
            return

        self.timer_screen.add_or_update_job(horno, job, salida)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
