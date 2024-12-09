from PyQt5.QtWidgets import (
    QTableView, QMessageBox, QComboBox,
    QDialog, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton
)
from PyQt5.QtSql import QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt, pyqtSlot

class Model(QSqlTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTable('tests')
        self.select()


class View(QTableView):
    def __init__(self, conn, parent=None):
        super().__init__(parent)
        self.conn = conn
        model = Model(parent=self)
        self.setModel(model)
        model.setHeaderData(1, Qt.Horizontal, "Название")
        model.setHeaderData(2, Qt.Horizontal, "Содержание")
        model.setHeaderData(3, Qt.Horizontal, "Автор")
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        #self.hideColumn(0)
        vh = self.verticalHeader()
        vh.setSectionResizeMode(vh.Fixed)
        hh = self.horizontalHeader()
        hh.setSectionResizeMode(hh.ResizeToContents)
        hh.setSectionResizeMode(2, hh.Stretch)
        self.selectAuthors()

    def add(self):
        dialog = Dialog(self)
        if dialog.exec():
            rec = self.conn.record('tests')
            rec.setValue('tname', dialog.tname)
            rec.setValue('tcontent', dialog.tcontent)
            rec.setValue('teacher_id', None if dialog.teacher == "" else self.__authors[dialog.teacher])
            print(rec.value(0), rec.value(1), rec.value(2), rec.value(3))
            print(self.model().insertRecord(-1, rec))
            self.model().select()

    def delete(self):
        ans = QMessageBox.question(self, 'Задача', 'Вы уверены?')
        if ans == QMessageBox.Yes:
            self.model().removeRow(self.currentIndex().row())
            self.model().select()

    def selectAuthors(self):
        sel_query = QSqlQuery()
        SELECT = '''
            select id_teacher, fio
                from teachers ;
        '''
        sel_query.exec_(SELECT)
        if sel_query.isActive():
            sel_query.first()
            self.__authors = {}
            while sel_query.isValid():
                self.__authors[sel_query.value('fio')] = sel_query.value('id_teacher')
                sel_query.next()
            print(self.__authors)

    @property
    def authors(self):
        return self.__authors.keys()

class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Задача')

        tname_lbl = QLabel('&Название', parent=self)
        self.__tname_edit = QLineEdit(parent=self)
        tname_lbl.setBuddy(self.__tname_edit)

        tcontent_lbl = QLabel('&Содержание', parent=self)
        self.__tcontent_edit = QTextEdit(parent=self)
        tcontent_lbl.setBuddy(self.__tcontent_edit)

        teacher_lbl = QLabel('&Автор', parent=self)
        self.__teacher_cmb = QComboBox(parent=self)
        teacher_lbl.setBuddy(self.__teacher_cmb)
        self.__teacher_cmb.addItem("")
        self.__teacher_cmb.addItems(parent.authors)

        ok_btn = QPushButton('OK', parent=self)
        cancel_btn = QPushButton('Отмена', parent=self)

        lay = QVBoxLayout(self)
        lay.addWidget(tname_lbl)
        lay.addWidget(self.__tname_edit)
        lay.addWidget(tcontent_lbl)
        lay.addWidget(self.__tcontent_edit)
        lay.addWidget(teacher_lbl)
        lay.addWidget(self.__teacher_cmb)

        hlay = QHBoxLayout()
        hlay.addStretch()
        hlay.addWidget(ok_btn)
        hlay.addWidget(cancel_btn)
        lay.addLayout(hlay)
        self.setLayout(lay)

        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.finish)

    @pyqtSlot()
    def finish(self):
        if self.tcontent is None:
            return
        self.accept()

    @property
    def tname(self):
        result = self.__tname_edit.text().strip()
        if result == '':
            return None
        return result

    @property
    def tcontent(self):
        result = self.__tcontent_edit.toPlainText().strip()
        if result == '':
            return None
        return result

    @property
    def teacher(self):
        return self.__teacher_cmb.currentText()


