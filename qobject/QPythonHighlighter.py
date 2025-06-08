from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class QPythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keywords = [
            'def', 'if', 'else', 'for', 'while', 'return', 'break',
            'continue', 'match', 'case', 'default', 'True',
            'False', 'None', 'self', 'class', 'import', 'from', 'as',
            'try', 'except', 'finally', 'raise', 'async', 'await',
            'yield', 'lambda', 'pass', 'assert', 'with', 'global',
            'nonlocal', 'and', 'or', 'not', 'is', 'in', 'del'
        ]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)
        for keyword in keywords:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(0, 128, 0))  # Dark Green
        string_patterns = [
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'),  # Double quotes
            QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"),  # Single quotes
            QRegularExpression(r'"""[\s\S]*?"""'),  # Triple double quotes
            QRegularExpression(r"'''[\s\S]*?'''")  # Triple single quotes
        ]
        for pattern in string_patterns:
            self.highlighting_rules.append((pattern, string_format))

        # Single-line comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gray
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r'#[^\n]*'), comment_format
        ))

        # Multi-line comments (using the same format as single-line)
        self.multi_line_comment_format = comment_format

    def highlightBlock(self, text):
        # Apply all highlighting rules
        for pattern, fmt in self.highlighting_rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
