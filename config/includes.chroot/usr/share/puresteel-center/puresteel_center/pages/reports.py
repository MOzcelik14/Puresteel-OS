\
from PySide6.QtWidgets import QFileDialog,QHBoxLayout,QPushButton,QTextEdit,QVBoxLayout,QWidget
from ..i18n import t
from ..services.report_service import generate
from .base import page_header

class ReportsPage(QWidget):
    def __init__(self,lang="tr"):
        super().__init__();self.lang=lang;self.setObjectName("ContentPage")
        l=QVBoxLayout(self);l.setContentsMargins(42,36,42,36);l.setSpacing(14)
        self.title,self.subtitle=page_header(l,"","")
        row=QHBoxLayout();self.gen=QPushButton();self.gen.setObjectName("PrimaryButton");self.save=QPushButton();self.save.setObjectName("SecondaryButton")
        self.gen.clicked.connect(self.generate);self.save.clicked.connect(self.save_report);row.addWidget(self.gen);row.addWidget(self.save);row.addStretch();l.addLayout(row)
        self.text=QTextEdit();self.text.setReadOnly(True);self.text.setObjectName("ReportText");l.addWidget(self.text,1)
        self.set_language(lang)

    def set_language(self,lang):
        self.lang=lang;self.title.setText(t(lang,"reports_title"));self.subtitle.setText(t(lang,"reports_intro"))
        self.gen.setText(t(lang,"generate_report"));self.save.setText(t(lang,"save_report"))

    def generate(self):
        self.text.setPlainText(generate())

    def save_report(self):
        if not self.text.toPlainText():self.generate()
        p,_=QFileDialog.getSaveFileName(self,t(self.lang,"save_report"),"puresteel-system-report.txt","Text (*.txt)")
        if p:
            open(p,"w",encoding="utf-8").write(self.text.toPlainText())
