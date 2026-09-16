\
from PySide6.QtWidgets import QFrame,QHBoxLayout,QLabel,QLineEdit,QListWidget,QMessageBox,QPushButton,QTabWidget,QTextEdit,QVBoxLayout,QWidget
from ..i18n import t
from ..services.source_service import apt_sources,flatpak_remotes,add_flatpak_remote,remove_flatpak_remote
from .base import page_header

class SourcesPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(15)
        self.title,self.subtitle=page_header(l,"","")
        self.tabs=QTabWidget();self.tabs.setObjectName("Tabs");l.addWidget(self.tabs,1)

        aptw=QWidget();ab=QVBoxLayout(aptw);self.aptlist=QListWidget();self.apttext=QTextEdit();self.apttext.setReadOnly(True)
        self.aptlist.currentRowChanged.connect(self.show_apt);ab.addWidget(self.aptlist);ab.addWidget(self.apttext,1)
        self.tabs.addTab(aptw,"APT")

        fw=QWidget();fb=QVBoxLayout(fw);self.flat=QListWidget();fb.addWidget(self.flat,1)
        row=QHBoxLayout();self.name=QLineEdit();self.url=QLineEdit();self.add_btn=QPushButton();self.remove_btn=QPushButton()
        self.add_btn.clicked.connect(self.add_remote);self.remove_btn.clicked.connect(self.remove_remote)
        row.addWidget(self.name);row.addWidget(self.url);row.addWidget(self.add_btn);row.addWidget(self.remove_btn);fb.addLayout(row)
        self.tabs.addTab(fw,"Flatpak")
        self.note=QLabel();self.note.setObjectName("StatusLabel");self.note.setWordWrap(True);l.addWidget(self.note)
        self.files=[];self.set_language(lang);self.refresh()

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"sources_title"));self.subtitle.setText(t(lang,"sources_intro"))
        self.tabs.setTabText(0,t(lang,"apt_sources"));self.tabs.setTabText(1,t(lang,"flatpak_remotes"))
        self.name.setPlaceholderText(t(lang,"remote_name"));self.url.setPlaceholderText(t(lang,"remote_url"))
        self.add_btn.setText(t(lang,"add"));self.remove_btn.setText(t(lang,"remove_selected"));self.note.setText(t(lang,"sources_note"))

    def refresh(self):
        self.files=apt_sources();self.aptlist.clear()
        for p,_ in self.files:self.aptlist.addItem(p)
        self.flat.clear()
        for n,u in flatpak_remotes():self.flat.addItem(f"{n}\\t{u}")

    def show_apt(self,row):
        if 0<=row<len(self.files):self.apttext.setPlainText(self.files[row][1])

    def add_remote(self):
        n=self.name.text().strip();u=self.url.text().strip()
        if not n or not u:return
        code,out=add_flatpak_remote(n,u);QMessageBox.information(self,t(self.lang,"operation_done") if code==0 else t(self.lang,"operation_failed"),out or "OK")
        self.refresh()

    def remove_remote(self):
        item=self.flat.currentItem()
        if not item:return
        n=item.text().split("\\t",1)[0]
        code,out=remove_flatpak_remote(n);QMessageBox.information(self,t(self.lang,"operation_done") if code==0 else t(self.lang,"operation_failed"),out or "OK")
        self.refresh()
