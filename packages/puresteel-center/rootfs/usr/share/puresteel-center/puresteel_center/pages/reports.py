from PySide6.QtWidgets import QFileDialog,QHBoxLayout,QMessageBox,QPushButton,QTextEdit,QVBoxLayout,QWidget
from ..i18n import t
from ..services.report_service import create_support_bundle, generate
from .base import page_header

class ReportsPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(14)
        self.title,self.subtitle=page_header(l,"","")
        row=QHBoxLayout();self.gen=QPushButton();self.gen.setObjectName("PrimaryButton");self.save=QPushButton();self.save.setObjectName("SecondaryButton")
        self.bundle=QPushButton();self.bundle.setObjectName("SecondaryButton")
        self.gen.clicked.connect(self.generate);self.save.clicked.connect(self.save_report);self.bundle.clicked.connect(self.export_bundle)
        row.addWidget(self.gen);row.addWidget(self.save);row.addWidget(self.bundle);row.addStretch();l.addLayout(row)
        self.text=QTextEdit();self.text.setReadOnly(True);self.text.setObjectName("ReportText");l.addWidget(self.text,1)
        self.set_language(lang)

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"reports_title"));self.subtitle.setText(t(lang,"reports_intro"))
        self.gen.setText(t(lang,"generate_report"));self.save.setText(t(lang,"save_report"));self.bundle.setText(t(lang,"export_bundle"))

    def generate(self):
        self.text.setPlainText(generate())

    def save_report(self):
        if not self.text.toPlainText():self.generate()
        p,_=QFileDialog.getSaveFileName(self,t(self.lang,"save_report"),"puresteel-system-report.txt","Text (*.txt)")
        if p:
            open(p,"w",encoding="utf-8").write(self.text.toPlainText())

    def export_bundle(self):
        p,_=QFileDialog.getSaveFileName(self,t(self.lang,"export_bundle"),"puresteel-support-bundle.tar.gz","Gzipped Tar (*.tar.gz)")
        if p:
            create_support_bundle(p)
            QMessageBox.information(self,t(self.lang,"app_title"),t(self.lang,"bundle_saved").format(path=p))
