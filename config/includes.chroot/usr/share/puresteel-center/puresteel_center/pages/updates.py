\
from PySide6.QtCore import QObject,QThread,Signal
from PySide6.QtWidgets import QFrame,QHBoxLayout,QLabel,QListWidget,QMessageBox,QPushButton,QVBoxLayout,QWidget
from ..i18n import t
from ..services.update_service import apt_updates,flatpak_updates,install_all
from .base import page_header

class Worker(QObject):
    done=Signal(object,object,str)
    def run(self):
        a,ae=apt_updates(); f,fe=flatpak_updates()
        self.done.emit(a,f,"\\n".join(x for x in (ae,fe) if x))

class InstallWorker(QObject):
    done=Signal(int,str)
    def run(self):
        self.done.emit(*install_all())

class UpdatesPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__(); self.lang=lang; self.thread=None; self.setObjectName("ContentPage")
        l=QVBoxLayout(self); l.setContentsMargins(42,36,42,36); l.setSpacing(16)
        self.title,self.subtitle=page_header(l,"","")
        bar=QHBoxLayout()
        self.check=QPushButton(); self.check.setObjectName("PrimaryButton"); self.check.clicked.connect(self.check_updates)
        self.install=QPushButton(); self.install.setObjectName("SecondaryButton"); self.install.clicked.connect(self.install_updates)
        bar.addWidget(self.check); bar.addWidget(self.install); bar.addStretch(); l.addLayout(bar)
        self.status=QLabel(); self.status.setObjectName("StatusLabel"); l.addWidget(self.status)
        self.list=QListWidget(); self.list.setObjectName("DataList"); l.addWidget(self.list,1)
        note=QFrame(); note.setObjectName("Notice"); nb=QVBoxLayout(note); nb.setContentsMargins(14,12,14,12)
        self.note=QLabel(); self.note.setWordWrap(True); nb.addWidget(self.note); l.addWidget(note)
        self.set_language(lang)

    def set_language(self,lang):
        self.lang=lang; self.title.setText(t(lang,"updates_title")); self.subtitle.setText(t(lang,"updates_intro"))
        self.check.setText(t(lang,"check_now")); self.install.setText(t(lang,"install_all"))
        self.note.setText(t(lang,"updates_note"))

    def check_updates(self):
        self.status.setText(t(self.lang,"checking")); self.list.clear(); self.check.setEnabled(False)
        self.thread=QThread(self); w=Worker(); self.worker=w; w.moveToThread(self.thread)
        self.thread.started.connect(w.run); w.done.connect(self.show); w.done.connect(self.thread.quit)
        w.done.connect(w.deleteLater); self.thread.finished.connect(self.thread.deleteLater); self.thread.start()

    def show(self,a,f,err):
        total=len(a)+len(f)
        if a:
            self.list.addItem(t(self.lang,"apt_updates"))
            for n,v in a:self.list.addItem(f"  • {n}  {v}")
        if f:
            self.list.addItem(t(self.lang,"flatpak_updates"))
            for n,v in f:self.list.addItem(f"  • {n}  {v}")
        if total==0 and not err:self.list.addItem(t(self.lang,"up_to_date"))
        if err:self.list.addItem(err)
        self.status.setText(t(self.lang,"updates_found",count=total)); self.check.setEnabled(True)

    def install_updates(self):
        self.status.setText(t(self.lang,"installing")); self.install.setEnabled(False)
        self.thread=QThread(self); w=InstallWorker(); self.worker=w; w.moveToThread(self.thread)
        self.thread.started.connect(w.run); w.done.connect(self.install_done); w.done.connect(self.thread.quit)
        w.done.connect(w.deleteLater); self.thread.finished.connect(self.thread.deleteLater); self.thread.start()

    def install_done(self,code,out):
        self.install.setEnabled(True)
        QMessageBox.information(self,t(self.lang,"operation_done") if code==0 else t(self.lang,"operation_failed"),out[-5000:] or "OK")
        self.check_updates()
