from pathlib import Path
import shutil, subprocess
from PySide6.QtCore import QSize,QUrl
from PySide6.QtGui import QDesktopServices,QIcon
from PySide6.QtWidgets import QLabel,QMessageBox,QPushButton,QVBoxLayout,QWidget
from ..i18n import t
from .base import page_header

PROJECT_URL="https://github.com/MOzcelik14/Puresteel-OS"

def open_url(url):
    if QDesktopServices.openUrl(QUrl(url)):
        return True
    for cmd in (["gio","open",url],["xdg-open",url],["flatpak","run","app.zen_browser.zen",url]):
        if shutil.which(cmd[0]):
            try:
                p=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=8,check=False)
                if p.returncode==0:return True
            except (OSError,subprocess.TimeoutExpired):
                pass
    return False

class AboutPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(16)
        self.title,self.subtitle=page_header(l,"","")
        logo=QLabel();logo.setPixmap(QIcon(str(Path(__file__).resolve().parents[1]/"resources"/"puresteel.png")).pixmap(QSize(180,180)))
        l.addWidget(logo)
        self.body=QLabel();self.body.setObjectName("Lead");self.body.setWordWrap(True);l.addWidget(self.body)
        self.git=QPushButton();self.git.setObjectName("PrimaryButton");self.git.clicked.connect(self.open_project)
        l.addWidget(self.git);l.addStretch();self.set_language(lang)

    def open_project(self):
        if not open_url(PROJECT_URL):
            QMessageBox.warning(self,"Puresteel",PROJECT_URL)

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"about_title"))
        self.subtitle.setText("Puresteel, Debian 13 tabanı üzerinde Cinnamon kullanan bağımsız bir Linux dağıtımıdır." if lang=="tr" else "Puresteel is an independent Debian 13 based Linux distribution using Cinnamon.")
        self.body.setText("Puresteel Center; güncellemeler, uygulamalar, GPU/sürücüler, profiller, kaynaklar, yedekleme ve tanılamayı tek yerde toplar." if lang=="tr" else "Puresteel Center brings updates, applications, GPU/drivers, profiles, sources, backup and diagnostics together in one place.")
        self.git.setText(t(lang,"github"))
