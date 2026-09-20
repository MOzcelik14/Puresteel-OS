from pathlib import Path
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QButtonGroup,QFrame,QHBoxLayout,QLabel,QListWidget,QListWidgetItem,QMainWindow,QPushButton,QStackedWidget,QVBoxLayout,QWidget
from .i18n import t
from .pages.home import HomePage
from .pages.puresteel import PuresteelPage
from .pages.updates import UpdatesPage
from .pages.applications import ApplicationsPage
from .pages.drivers import DriversPage
from .pages.profiles import ProfilesPage
from .pages.sources import SourcesPage
from .pages.backup import BackupPage
from .pages.reports import ReportsPage
from .pages.about import AboutPage

class MainWindow(QMainWindow):
    def __init__(self,language="tr",settings=None):
        super().__init__();self.language=language if language in ("tr","en") else "tr";self.settings=settings
        self.resource=Path(__file__).resolve().parent/"resources"
        self.resize(1220,780);self.setMinimumSize(1000,650)
        root=QWidget();root.setObjectName("Root");rb=QHBoxLayout(root);rb.setContentsMargins(0,0,0,0);rb.setSpacing(0)

        side=QFrame();side.setObjectName("Sidebar");side.setFixedWidth(265);sb=QVBoxLayout(side);sb.setContentsMargins(18,22,18,18);sb.setSpacing(16)
        brand=QHBoxLayout();logo=QLabel();logo.setPixmap(QIcon(str(self.resource/"puresteel.png")).pixmap(QSize(42,42)));txt=QLabel("Puresteel Center");txt.setObjectName("BrandText")
        brand.addWidget(logo);brand.addWidget(txt);brand.addStretch();sb.addLayout(brand)
        self.nav=QListWidget();self.nav.setObjectName("Navigation");self.nav.setFocusPolicy(Qt.NoFocus);self.nav.setSpacing(3);sb.addWidget(self.nav,1)

        langbox=QFrame();langbox.setObjectName("LanguageBox");lb=QVBoxLayout(langbox);lb.setContentsMargins(10,9,10,9)
        self.lang_label=QLabel();self.lang_label.setObjectName("SidebarCaption");lb.addWidget(self.lang_label)
        row=QHBoxLayout();self.trb=QPushButton("TR");self.enb=QPushButton("EN")
        for b in (self.trb,self.enb):b.setCheckable(True);b.setObjectName("LanguageButton");row.addWidget(b)
        grp=QButtonGroup(self);grp.setExclusive(True);grp.addButton(self.trb);grp.addButton(self.enb)
        self.trb.clicked.connect(lambda:self.set_language("tr"));self.enb.clicked.connect(lambda:self.set_language("en"));lb.addLayout(row);sb.addWidget(langbox)
        self.ver=QLabel();self.ver.setObjectName("VersionLabel");sb.addWidget(self.ver)

        self.pages=QStackedWidget();self.pages.setObjectName("Pages")
        self.page_objects=[
            HomePage(self.language),PuresteelPage(self.language),UpdatesPage(self.language),ApplicationsPage(self.language),DriversPage(self.language),
            ProfilesPage(self.language),SourcesPage(self.language),BackupPage(self.language),ReportsPage(self.language),AboutPage(self.language)
        ]
        for p in self.page_objects:self.pages.addWidget(p)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        rb.addWidget(side);rb.addWidget(self.pages,1);self.setCentralWidget(root)
        self.apply_language();self.nav.setCurrentRow(0)

    def set_language(self,lang):
        self.language=lang
        if self.settings:self.settings.setValue("language",lang)
        self.apply_language()

    def apply_language(self):
        self.setWindowTitle(t(self.language,"app_title"));self.lang_label.setText(t(self.language,"language"));self.ver.setText("Puresteel Center 1.4.0")
        self.trb.setChecked(self.language=="tr");self.enb.setChecked(self.language=="en")
        keys=["home","puresteel","updates","applications","drivers","profiles","sources","backup","reports","about"];cur=self.nav.currentRow();self.nav.clear()
        for k in keys:
            if k=="puresteel": text="Puresteel"
            elif k=="profiles": text="Profiller" if self.language=="tr" else "Profiles"
            else: text=t(self.language,k)
            it=QListWidgetItem(text);it.setSizeHint(QSize(0,44));self.nav.addItem(it)
        self.nav.setCurrentRow(max(cur,0))
        for p in self.page_objects:
            if hasattr(p,"set_language"):p.set_language(self.language)
