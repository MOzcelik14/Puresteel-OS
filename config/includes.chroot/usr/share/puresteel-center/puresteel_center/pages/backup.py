\
from pathlib import Path
from PySide6.QtWidgets import QCheckBox,QFileDialog,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QVBoxLayout,QWidget
from ..i18n import t
from ..services.backup_service import create_backup
from .base import page_header

class BackupPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(14)
        self.title,self.subtitle=page_header(l,"","")
        self.boxes={}
        for key in ("documents","pictures","music","config","packages"):
            cb=QCheckBox();cb.setChecked(key in ("documents","pictures","config","packages"));self.boxes[key]=cb;l.addWidget(cb)
        row=QHBoxLayout();self.dest=QLineEdit(str(Path.home()));self.browse=QPushButton();self.browse.clicked.connect(self.choose)
        row.addWidget(self.dest,1);row.addWidget(self.browse);l.addLayout(row)
        self.create=QPushButton();self.create.setObjectName("PrimaryButton");self.create.clicked.connect(self.make);l.addWidget(self.create)
        self.status=QLabel();self.status.setObjectName("StatusLabel");self.status.setWordWrap(True);l.addWidget(self.status);l.addStretch()
        self.set_language(lang)

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"backup_title"));self.subtitle.setText(t(lang,"backup_intro"))
        labels={"documents":"backup_documents","pictures":"backup_pictures","music":"backup_music","config":"backup_config","packages":"backup_packages"}
        for k,cb in self.boxes.items():cb.setText(t(lang,labels[k]))
        self.browse.setText(t(lang,"browse"));self.create.setText(t(lang,"create_backup"))

    def choose(self):
        d=QFileDialog.getExistingDirectory(self,t(self.lang,"choose_folder"),self.dest.text())
        if d:self.dest.setText(d)

    def make(self):
        try:
            path=create_backup(self.dest.text(),{k:b.isChecked() for k,b in self.boxes.items()})
            self.status.setText(t(self.lang,"backup_done",path=path))
        except Exception as e:
            self.status.setText(t(self.lang,"backup_error",error=str(e)))
