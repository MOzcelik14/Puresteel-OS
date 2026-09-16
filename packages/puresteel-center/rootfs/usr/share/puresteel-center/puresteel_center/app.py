import sys
from pathlib import Path
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

def main():
    app=QApplication(sys.argv);app.setApplicationName("Puresteel Center");app.setOrganizationName("Puresteel")
    resource=Path(__file__).resolve().parent/"resources";app.setWindowIcon(QIcon(str(resource/"puresteel.png")))
    app.setStyleSheet((resource/"style.qss").read_text(encoding="utf-8"))
    settings=QSettings("Puresteel","Puresteel Center");lang=settings.value("language","tr")
    w=MainWindow(lang,settings);w.show();return app.exec()
