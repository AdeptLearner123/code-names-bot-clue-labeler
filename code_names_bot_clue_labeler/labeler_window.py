from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt

class LabelerWindow(QtWidgets.QWidget):
    next_signal = Signal()
    prev_signal = Signal()
    label_signal = Signal(int)

    INPUT_KEYS = "012"

    def __init__(self):
        super().__init__()
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        self._add_title()
        self._add_text()
    
    def _add_title(self):
        self._title = QtWidgets.QLabel()
        self._layout.addWidget(self._title)
    
    def _add_text(self):
        text = QtWidgets.QLabel()
        self._layout.addWidget(text)
        self._text = text

    def _get_annotation(self, color):
        return f"<b style=\"color:{color}\">", f"</b>"

    def _render_text(self, text, source_start, source_end, target_start, target_end):
        source_start_tag, source_end_tag = self._get_annotation("red")
        target_start_tag, target_end_tag = self._get_annotation("green")
        styled_text = text[:source_start] + source_start_tag + text[source_start:source_end] + source_end_tag + text[source_end:target_start] + target_start_tag + text[target_start:target_end] + target_end_tag
        self._text.setText(styled_text)
    
    def keyPressEvent(self, event):
        if event.key() == 16777234:  # Left
            self.prev_signal.emit()
        elif event.key() == 16777236:  # Right
            self.next_signal.emit()
        elif event.text() in self.INPUT_KEYS:
            input_index = self.INPUT_KEYS.index(event.text())
            self.label_signal.emit(input_index)
        self._render()