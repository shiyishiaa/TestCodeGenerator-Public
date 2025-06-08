from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class QJavaScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keywords = [
            'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while',
            'return', 'break', 'continue', 'switch', 'case', 'default', 'true',
            'false', 'null', 'undefined', 'this', 'new', 'typeof', 'instanceof',
            'try', 'catch', 'throw', 'delete', 'class', 'extends', 'super',
            'import', 'export', 'async', 'await', 'yield', 'void', 'debugger'
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
            QRegularExpression(r'`[^`\\]*(\\.[^`\\]*)*`')  # Backticks (template literals)
        ]
        for pattern in string_patterns:
            self.highlighting_rules.append((pattern, string_format))

        # Single-line comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gray
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression(r'//[^\n]*'), comment_format
        ))

        # Multi-line comments
        self.multi_line_comment_format = comment_format
        self.comment_start = QRegularExpression(r'/\*')
        self.comment_end = QRegularExpression(r'\*/')

    def highlightBlock(self, text):
        # Apply all non-multi-line rules
        for pattern, fmt in self.highlighting_rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_match = self.comment_start.match(text)
            start_index = start_match.capturedStart()

        while start_index >= 0:
            end_match = self.comment_end.match(text, start_index)
            if end_match.hasMatch():
                end_index = end_match.capturedEnd()
                comment_length = end_index - start_index
                self.setCurrentBlockState(0)
            else:
                comment_length = len(text) - start_index
                self.setCurrentBlockState(1)

            self.setFormat(start_index, comment_length, self.multi_line_comment_format)

            # Find next comment start
            start_match = self.comment_start.match(text, start_index + comment_length)
            start_index = start_match.capturedStart() if start_match.hasMatch() else -1
