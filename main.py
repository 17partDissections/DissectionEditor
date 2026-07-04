import sys, webbrowser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QIcon
from dissection_handler import pack, unpack
from localization import languages
import resources_rc

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.version = 1.0
        self.language = "english"
        self.current_file = None
        self.is_dissection = False
        self.font_family = "Consolas"
        self.font_size = 12

        self.setWindowTitle("Dissection Editor")
        self.setWindowIcon(QIcon(":/icon.ico"))
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 800) // 2
        y = (screen.height() - 600) // 2
        self.setGeometry(x, y, 800, 600)
        self.textEdit = QTextEdit()
        font = QFont(self.font_family, self.font_size)
        self.textEdit.setFont(font)
        self.textEdit.setTabStopDistance(30)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.setCentralWidget(self.textEdit)
        self.status_bar = self.statusBar()
        self.cursor_label = QLabel(f"{languages[self.language]['line']}: 1, {languages[self.language]['column']}: 1")
        self.status_bar.addPermanentWidget(self.cursor_label)
        self.rightLabel = QLabel(f"{languages[self.language]['version']} {self.version}")
        self.status_bar.addPermanentWidget(self.rightLabel)
        self.textEdit.cursorPositionChanged.connect(self.update_status_bar)
        self.create_menu()
        self.show()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(languages[self.language]["file"])

        new = QAction(languages[self.language]["new"], self)
        new.setShortcut("Ctrl+N")
        new.triggered.connect(self.new)

        open_file = QAction(languages[self.language]["open"], self)
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)

        save = QAction(languages[self.language]["save"], self)
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self.save)

        save_as = QAction(languages[self.language]["save_as"], self)
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        export = QAction(languages[self.language]["export"], self)
        export.setShortcut("Ctrl+E")
        export.triggered.connect(self.export)

        exitAction = QAction(languages[self.language]["exit"], self)
        exitAction.setShortcut("Alt+F4")
        exitAction.triggered.connect(self.close)

        options_menu = menu_bar.addMenu(languages[self.language]["options"])

        zoom = QMenu(languages[self.language]["zoom"], self)

        zoom_in = QAction(languages[self.language]["zoom_in"], self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(self.zoom_in)

        zoom_out = QAction(languages[self.language]["zoom_out"], self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(self.zoom_out)

        font = QAction(languages[self.language]["font"], self)
        font.triggered.connect(self.set_font)

        language = QMenu(languages[self.language]["language"], self)
        lang_en = QAction("English", self)
        lang_en.triggered.connect(lambda: self.set_language("english"))
        lang_ru = QAction("Русский", self)
        lang_ru.triggered.connect(lambda: self.set_language("russian"))

        help_menu = menu_bar.addMenu(languages[self.language]["help"])
        about = QAction(languages[self.language]["about"], self)
        about.setShortcut("F1")
        about.triggered.connect(self.about)
        update = QAction(languages[self.language]["check_updates"], self)
        update.setShortcut("F2")
        update.triggered.connect(self.check_updates)

        file_menu.addAction(new)
        file_menu.addAction(open_file)
        file_menu.addSeparator()
        file_menu.addAction(save)
        file_menu.addAction(save_as)
        file_menu.addSeparator()
        file_menu.addAction(export)
        file_menu.addSeparator()
        file_menu.addAction(exitAction)

        options_menu.addMenu(zoom)
        zoom.addAction(zoom_in)
        zoom.addAction(zoom_out)
        options_menu.addAction(font)
        options_menu.addMenu(language)
        language.addAction(lang_en)
        language.addAction(lang_ru)

        help_menu.addAction(about)
        help_menu.addAction(update)
    def zoom_in(self):
        if self.font_size < 120:
            self.font_size += 1
            self.apply_font_size()
    def zoom_out(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.apply_font_size()
    def apply_font_size(self):
        font = QFont(self.font_family, self.font_size)
        self.textEdit.setFont(font)
        self.status_bar.showMessage(f"{languages[self.language]['zoom']}: {self.font_size}pt", 3000)
    def wheelEvent(self, event): #cuz why not
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0: self.zoom_in()
            elif delta < 0: self.zoom_out()
            event.accept()
        else: super().wheelEvent(event)
    def set_font(self):
        font, ok = QFontDialog.getFont(self.textEdit.font(), self, "Font")
        if ok:
            self.textEdit.setFont(font)
            self.font_family = font.family()
            self.font_size = font.pointSize()
            self.status_bar.showMessage(f"{languages[self.language]['font']}: {self.font_family}; {languages[self.language]['font_size']}: {self.font_size}", 3000)
    def set_language(self, language):
        self.language = language
        self.menuBar().clear()
        self.create_menu()
        self.rightLabel.setText(f"{languages[self.language]['version']} {self.version}")
        self.status_bar.showMessage(f"{languages[self.language]['language']}: {self.language}", 3000)
    def new(self):
        if (self.check_unsaved_changes() == 1): return
        self.textEdit.clear()
        self.current_file = None
        self.is_dissection = False
        self.setWindowTitle("Dissection Editor")
        self.status_bar.showMessage(f"{languages[self.language]['new_status']}", 3000)
    def open_file(self):
        if (self.check_unsaved_changes() == 1): return
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "All Supported (*.dissection *.txt *.md *.py *.cpp *.c *.cs *.java *.js *.html *.css *.xml *.yaml *.yml *.php *.json);;"
            "DISSECTION Files (*.dissection);;"
            "Text Files (*.txt *.md);;"
            "Python (*.py);;"
            "C/C++ (*.cpp *.c);;"
            "C# (*.cs);;"
            "Java (*.java);;"
            "Web (*.js *.html *.css *.xml);;"
            "PHP (*.php);;"
            "Data (*.json *.yaml *.yml);;"
            "All Files (*)"
        )
        if not filepath: return
        try:
            with open(filepath, 'rb') as f: data = f.read()
            text = unpack(data)
            if text is not None:
                self.textEdit.setPlainText(text)
                self.is_dissection = True
                self.current_file = filepath
                self.setWindowTitle(f"Dissection Editor - {filepath}")
                self.status_bar.showMessage(f"{languages[self.language]['opened_file']}: {filepath}", 3000)
                return
            with open(filepath, 'r', encoding='utf-8') as f: self.textEdit.setPlainText(f.read())
            self.is_dissection = False
            self.current_file = filepath
            self.setWindowTitle(f"Dissection Editor - {filepath}")
            self.status_bar.showMessage(f"{languages[self.language]['opened_file']}: {filepath}", 3000)
        except Exception as e: QMessageBox.critical(self, "Error", f"Cannot open file:\n{str(e)}")
    def save(self):
        if self.current_file and not self.is_dissection:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f: f.write(self.textEdit.toPlainText())
                self.status_bar.showMessage(f"{languages[self.language]['file_saved']}", 3000)
            except Exception as e: QMessageBox.critical(self, "Error", f"Cannot save file:\n{str(e)}")
        else: self.save_as()
    def save_as(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(self.textEdit.toPlainText())
            self.current_file = filepath
            self.is_dissection = False
            self.setWindowTitle(f"Dissection Editor - {filepath}")
            self.status_bar.showMessage(f"{languages[self.language]['file_saved_as']} {filepath}", 3000)
        except Exception as e: QMessageBox.critical(self, "Error", f"Cannot save file:\n{str(e)}")

    def export(self):
        packed = pack(self.textEdit.toPlainText())
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export as DISSECTION", "",
            "DISSECTION Files (*.dissection);;All Files (*)"
        )
        if not filepath: return
        try:
            with open(filepath, 'wb') as f: f.write(packed)
            self.current_file = filepath
            self.is_dissection = True
            self.setWindowTitle(f"Dissection Editor - {filepath}")
            self.status_bar.showMessage(f"{languages[self.language]['file_exported_as']} {filepath}", 3000)
        except Exception as e: QMessageBox.critical(self, "Error", f"Cannot export file:\n{str(e)}")

    def check_updates(self):
        webbrowser.open("https://github.com/17partDissections/DissectionEditor/releases")
    def about(self):
        about_message = QMessageBox(self)
        about_message.setIcon(QMessageBox.Information)
        about_message.setWindowTitle("About")
        about_message.setText(
            "<b>Dissection Editor</b>"
            f"<br>{languages[self.language]['version']} {self.version}<br>"
            f"{languages[self.language]['about_message']}"
        )
        about_message.exec_()

    def check_unsaved_changes(self):
        if self.textEdit.toPlainText() != "":
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                languages[self.language]["unsaved_changes"],
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save: self.save()
            elif reply == QMessageBox.Cancel: return 1
    def update_status_bar(self):
        cursor = self.textEdit.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_label.setText(f"{languages[self.language]['line']}: {line}, {languages[self.language]['column']}: {column}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = Window()
    sys.exit(app.exec())