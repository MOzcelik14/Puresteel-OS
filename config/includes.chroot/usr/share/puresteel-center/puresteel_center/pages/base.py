\
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

def page_header(layout, title, subtitle):
    panel = QFrame()
    panel.setObjectName("HeroPanel")
    box = QVBoxLayout(panel)
    box.setContentsMargins(28,24,28,24)
    box.setSpacing(8)
    title_label = QLabel(title)
    title_label.setObjectName("PageTitle")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("Lead")
    subtitle_label.setWordWrap(True)
    box.addWidget(title_label)
    box.addWidget(subtitle_label)
    layout.addWidget(panel)
    return title_label, subtitle_label
