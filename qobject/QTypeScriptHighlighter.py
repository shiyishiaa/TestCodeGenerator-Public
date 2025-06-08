from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class QTypeScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Keywords
        keywords = [
            'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while',
            'return', 'break', 'continue', 'switch', 'case', 'default', 'true',
            'false', 'null', 'undefined', 'this', 'new', 'typeof', 'instanceof',
            'try', 'catch', 'throw', 'delete', 'class', 'extends', 'super',
            'import', 'export', 'async', 'await', 'yield', 'void', 'debugger',
            'interface', 'type', 'enum', 'implements', 'declare', 'namespace',
            'abstract', 'as', 'is', 'keyof', 'readonly', 'private', 'protected',
            'public', 'static', 'package', 'module'
        ]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)
        for keyword in keywords:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))

        # Types
        type_format = QTextCharFormat()
        type_format.setForeground(QColor(128, 0, 128))  # Purple
        type_format.setFontWeight(QFont.Weight.Bold)
        types = [
            'string', 'number', 'boolean', 'any', 'void', 'never', 'object',
            'array', 'unknown', 'undefined', 'null', 'bigint', 'symbol'
        ]
        for type_name in types:
            pattern = QRegularExpression(r'\b' + type_name + r'\b')
            self.highlighting_rules.append((pattern, type_format))

        # Type annotations
        type_annotation_format = QTextCharFormat()
        type_annotation_format.setForeground(QColor(128, 0, 128))  # Purple
        self.highlighting_rules.append((
            QRegularExpression(r':\s*([A-Za-z0-9_<>[\],\s|&]+)(?=[,);={])'),
            type_annotation_format
        ))

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
        start_index = -1

        start_match = self.comment_start.match(text)
        if start_match.hasMatch():
            start_index = start_match.capturedStart()
        elif self.previousBlockState() == 1:
            start_index = 0

        while start_index >= 0:
            end_match = self.comment_end.match(text, start_index)

            if end_match.hasMatch():
                comment_length = end_match.capturedEnd() - start_index
                self.setCurrentBlockState(0)

                # Find next comment start
                start_match = self.comment_start.match(text, start_index + comment_length)
                start_index = start_match.capturedStart() if start_match.hasMatch() else -1
            else:
                comment_length = len(text) - start_index
                self.setCurrentBlockState(1)
                start_index = -1

            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
