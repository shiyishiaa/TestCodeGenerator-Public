from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy


class QPager(QWidget):
    def __init__(self, title="", /, parent=None):
        super().__init__(parent)
        self.stacked_widget = QStackedWidget()
        self.title_label = QLabel(title)
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")

        self._init_ui()
        self._connect_signals()
        self._update_button_states()

    def _init_ui(self):
        # Header row with title and buttons
        header_row = QHBoxLayout()

        # Title label configuration
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Button container
        button_container = QHBoxLayout()
        button_container.addWidget(self.btn_prev)
        button_container.addWidget(self.btn_next)

        # Combine elements in single row
        header_row.addWidget(self.title_label)
        header_row.addLayout(button_container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(header_row)
        main_layout.addWidget(self.stacked_widget)

        # Style adjustments
        self._apply_styles()

    def _apply_styles(self):
        self.title_label.setStyleSheet("""
            QLabel {
                font: italic bold;
                padding-left: 5px;
            }
        """)

        button_style = """
            QPushButton {
                min-width: 32px;
                max-width: 32px;
                height: 28px;
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: white;
            }
            QPushButton:hover { background: #3fa3e6; }
            QPushButton:disabled { background: #95a5a6; }
        """
        self.btn_prev.setStyleSheet(button_style)
        self.btn_next.setStyleSheet(button_style)

    def _connect_signals(self):
        self.btn_prev.clicked.connect(self.previous_page)
        self.btn_next.clicked.connect(self.next_page)
        self.stacked_widget.currentChanged.connect(self._update_button_states)

    def add_page(self, widget, title=None):
        """Add a new page with optional title"""
        self.stacked_widget.addWidget(widget)
        if title:
            self.current_title = title
        self._update_button_states()

    def previous_page(self):
        """Navigate to the previous page"""
        if self.stacked_widget.currentIndex() > 0:
            self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() - 1)

    def next_page(self):
        """Navigate to next page"""
        if self.stacked_widget.currentIndex() < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(self.stacked_widget.currentIndex() + 1)

    def _update_button_states(self):
        """Update button availability and title"""
        current_idx = self.stacked_widget.currentIndex()
        self.btn_prev.setEnabled(current_idx > 0)
        self.btn_next.setEnabled(current_idx < self.stacked_widget.count() - 1)

    def clear_pages(self):
        """Clear all pages"""
        while self.stacked_widget.count() > 0:
            self.stacked_widget.removeWidget(self.stacked_widget.widget(0))
        self.title_label.clear()
        self._update_button_states()

    def pages(self) -> List[Tuple[str, QWidget]]:
        """
        Get a list of all pages
        """
        return [(self.title_label.text(), self.stacked_widget.widget(i)) for i in range(self.stacked_widget.count())]

    def count(self) -> int:
        """
        Get the number of pages
        """
        return self.stacked_widget.count()

    @property
    def current_index(self) -> int:
        """
        Get the index of the current widget

        Returns:
            int: The index of the current widget
        """
        return self.stacked_widget.currentIndex()

    @current_index.setter
    def current_index(self, index: int):
        """
        Set the index of the current widget

        Args:
            index: The index of the widget to show
        """
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)

    @property
    def current_title(self) -> str:
        """
        Get the title of the current widget

        Returns:
            str: The title of the current widget
        """
        return self.title_label.text()

    @current_title.setter
    def current_title(self, title: str):
        """
        Set the title of the current widget

        Args:
            title: The title of the widget to show
        """
        self.title_label.setText(title)
