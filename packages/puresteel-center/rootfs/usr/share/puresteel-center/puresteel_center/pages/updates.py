from PySide6.QtCore import QObject,QThread,Signal,QTimer
from PySide6.QtWidgets import QFrame,QHBoxLayout,QLabel,QListWidget,QMessageBox,QPushButton,QVBoxLayout,QWidget
from ..i18n import t
from ..services.update_service import apt_updates,classify_apt,flatpak_updates,install_all
from .base import page_header

class Worker(QObject):
    done=Signal(object,object,str)
    def run(self):
        a,ae=apt_updates(); f,fe=flatpak_updates()
        self.done.emit(a,f,"\n".join(x for x in (ae,fe) if x))

class InstallWorker(QObject):
    done=Signal(int,str)
    def run(self):
        self.done.emit(*install_all(safe=True))

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
        self.lang=lang
        self.title.setText(t(lang,"updates_title"))
        self.subtitle.setText("Kernel, sürücü ve firmware güncellemelerini diğer paketlerden ayırarak göster." if lang=="tr" else "Separate kernel, driver and firmware updates from regular packages.")
        self.check.setText(t(lang,"check_now"))
        self.install.setText("Güvenli güncelle" if lang=="tr" else "Safe update")
        self.note.setText("Timeshift snapshot'ı oluşturulamaz veya doğrulanamazsa güncelleme başlamaz. Kernel/NVIDIA/firmware paketleri kritik işaretlenir." if lang=="tr" else "Updates stop if a Timeshift snapshot cannot be created and verified. Kernel/NVIDIA/firmware packages are marked as critical.")

    def check_updates(self):
        if self.thread is not None: return
        self.status.setText(t(self.lang,"checking")); self.list.clear()
        self.check.setEnabled(False); self.install.setEnabled(False)
        self.thread=QThread(self); w=Worker(); self.worker=w; w.moveToThread(self.thread)
        self.thread.started.connect(w.run); w.done.connect(self.show); w.done.connect(self.thread.quit)
        w.done.connect(w.deleteLater); self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.finish_thread(False))
        self.thread.start()

    def add_group(self,title,items):
        if not items:return
        self.list.addItem(title)
        for n,v in items:self.list.addItem(f"  • {n}  {v}")

    def show(self,a,f,err):
        critical,normal=classify_apt(a)
        total=len(a)+len(f)
        tr=self.lang=="tr"
        self.add_group("⚠ Kritik sistem güncellemeleri" if tr else "⚠ Critical system updates",critical)
        self.add_group("APT paketleri" if tr else "APT packages",normal)
        self.add_group(t(self.lang,"flatpak_updates"),f)
        if total==0 and not err:self.list.addItem(t(self.lang,"up_to_date"))
        if err:self.list.addItem(err)
        self.status.setText(t(self.lang,"updates_found",count=total))

    def install_updates(self):
        if self.thread is not None: return
        if QMessageBox.question(self, "Puresteel Safe Update",
            "Snapshot oluşturulamazsa güncelleme iptal edilecek. Devam edilsin mi?" if self.lang=="tr" else
            "Updates stop if a snapshot cannot be verified. Continue?") != QMessageBox.Yes: return
        self.status.setText("Snapshot + güncelleme hazırlanıyor…" if self.lang=="tr" else "Preparing snapshot + update…")
        self.check.setEnabled(False); self.install.setEnabled(False)
        self.thread=QThread(self); w=InstallWorker(); self.worker=w; w.moveToThread(self.thread)
        self.thread.started.connect(w.run); w.done.connect(self.install_done); w.done.connect(self.thread.quit)
        w.done.connect(w.deleteLater); self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(lambda: self.finish_thread(True))
        self.thread.start()

    def install_done(self,code,out):
        box = QMessageBox.information if code==0 else QMessageBox.warning
        box(self,t(self.lang,"operation_done") if code==0 else t(self.lang,"operation_failed"),out[-5000:] or "OK")

    def finish_thread(self,refresh):
        self.thread=None; self.worker=None
        self.check.setEnabled(True); self.install.setEnabled(True)
        if refresh: QTimer.singleShot(0,self.check_updates)
