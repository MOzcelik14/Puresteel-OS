from PySide6.QtCore import QObject,QThread,Signal
from PySide6.QtWidgets import QComboBox,QHBoxLayout,QLabel,QLineEdit,QMessageBox,QPushButton,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget
from ..i18n import t
from ..services.app_service import apt_search,flatpak_search,apt_installed,flatpak_installed,install,remove
from .base import page_header

class SearchWorker(QObject):
    done=Signal(list)
    def __init__(self,q):super().__init__();self.q=q
    def run(self):
        self.done.emit(apt_search(self.q)+flatpak_search(self.q))

class ApplicationsPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.thread=None;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(15)
        self.title,self.subtitle=page_header(l,"","")
        row=QHBoxLayout();self.query=QLineEdit();self.search_btn=QPushButton();self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self.search);self.query.returnPressed.connect(self.search)
        row.addWidget(self.query,1);row.addWidget(self.search_btn);l.addLayout(row)
        self.table=QTableWidget(0,4);self.table.setObjectName("DataTable");self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers);self.table.horizontalHeader().setStretchLastSection(True)
        l.addWidget(self.table,1)
        actions=QHBoxLayout();self.install_btn=QPushButton();self.remove_btn=QPushButton()
        self.install_btn.setObjectName("PrimaryButton");self.remove_btn.setObjectName("SecondaryButton")
        self.install_btn.clicked.connect(lambda:self.act(True));self.remove_btn.clicked.connect(lambda:self.act(False))
        actions.addWidget(self.install_btn);actions.addWidget(self.remove_btn);actions.addStretch();l.addLayout(actions)
        self.set_language(lang)

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"apps_title"));self.subtitle.setText(t(lang,"apps_intro"))
        self.query.setPlaceholderText(t(lang,"search_placeholder"));self.search_btn.setText(t(lang,"search"))
        self.install_btn.setText(t(lang,"install"));self.remove_btn.setText(t(lang,"remove"))
        self.table.setHorizontalHeaderLabels([t(lang,"source"),t(lang,"package"),"Description",t(lang,"installed")])

    def search(self):
        q=self.query.text().strip()
        if len(q)<2:return
        self.search_btn.setEnabled(False);self.table.setRowCount(0)
        self.thread=QThread(self);w=SearchWorker(q);self.worker=w;w.moveToThread(self.thread)
        self.thread.started.connect(w.run);w.done.connect(self.show);w.done.connect(self.thread.quit)
        w.done.connect(w.deleteLater);self.thread.finished.connect(self.thread.deleteLater);self.thread.start()

    def show(self,rows):
        for src,name,desc in rows[:120]:
            r=self.table.rowCount();self.table.insertRow(r)
            inst=apt_installed(name) if src=="APT" else flatpak_installed(name)
            for c,val in enumerate((src,name,desc,t(self.lang,"installed") if inst else t(self.lang,"not_installed"))):
                self.table.setItem(r,c,QTableWidgetItem(val))
        if not rows:
            r=self.table.rowCount();self.table.insertRow(r);self.table.setItem(r,1,QTableWidgetItem(t(self.lang,"no_results")))
        self.search_btn.setEnabled(True);self.table.resizeColumnsToContents()

    def selected(self):
        r=self.table.currentRow()
        if r<0:return None
        s=self.table.item(r,0);n=self.table.item(r,1)
        if not s or not n:return None
        return s.text(),n.text()

    def act(self,do_install):
        sel=self.selected()
        if not sel:return
        code,out=(install(*sel) if do_install else remove(*sel))
        QMessageBox.information(self,t(self.lang,"operation_done") if code==0 else t(self.lang,"operation_failed"),out[-5000:] or "OK")
        self.search()
