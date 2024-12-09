import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTableView,
    QPushButton,
    QLineEdit,
    QFormLayout,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import pyqtSlot


class TeacherModel(QSqlTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTable("teachers")
        self.setEditStrategy(
            QSqlTableModel.OnFieldChange
        )
        self.select()


class TeacherDialog(QDialog):
    def __init__(self, parent=None, teacher_id=None):
        super().__init__(parent)
        self.teacher_id = teacher_id
        self.setWindowTitle("Добавить/Редактировать Учителя")

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.subject_input = QLineEdit()
        self.group_input = QLineEdit()

        layout.addRow("ФИО:", self.name_input)
        layout.addRow("Предмет:", self.subject_input)
        layout.addRow("Группа:", self.group_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        if self.teacher_id is not None:
            self.load_data()

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def load_data(self):
        query = QSqlQuery()
        query.prepare("SELECT name, subject, group_name FROM teachers WHERE id = :id")
        query.bindValue(":id", self.teacher_id)
        query.exec_()
        if query.next():
            self.name_input.setText(query.value(0))
            self.subject_input.setText(query.value(1))
            self.group_input.setText(query.value(2))

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "subject": self.subject_input.text().strip(),
            "group": self.group_input.text().strip(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление Учителями")
        self.setGeometry(100, 100, 800, 600)

        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName("teachers.db")
        if not self.database.open():
            QMessageBox.critical(
                self, "Ошибка базы данных", "Не удалось подключиться к базе данных."
            )
            sys.exit(1)

        self.create_table()

        self.teacher_model = TeacherModel(self)
        self.teacher_model.dataChanged.connect(
            self.auto_save
        )

        self.teacher_view = QTableView()
        self.teacher_view.setModel(self.teacher_model)
        self.teacher_view.setSelectionBehavior(self.teacher_view.SelectRows)
        self.teacher_view.setSelectionMode(self.teacher_view.SingleSelection)
        self.teacher_view.horizontalHeader().setStretchLastSection(True)

        self.add_teacher_button = QPushButton("Добавить Учителя")
        self.edit_teacher_button = QPushButton("Редактировать Учителя")
        self.delete_teacher_button = QPushButton("Удалить Учителя")
        self.save_changes_button = QPushButton("Сохранить изменения")

        self.add_teacher_button.clicked.connect(self.add_teacher)
        self.edit_teacher_button.clicked.connect(self.edit_teacher)
        self.delete_teacher_button.clicked.connect(self.delete_teacher)
        self.save_changes_button.clicked.connect(self.save_changes)

        layout = QVBoxLayout()
        layout.addWidget(self.teacher_view)
        layout.addWidget(self.add_teacher_button)
        layout.addWidget(self.edit_teacher_button)
        layout.addWidget(self.delete_teacher_button)
        layout.addWidget(self.save_changes_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_table(self):
        query = QSqlQuery()
        query.exec_(
            """CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            group_name TEXT NOT NULL
        )"""
        )

    def add_teacher(self):
        dialog = TeacherDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data["name"] and data["subject"] and data["group"]:
                query = QSqlQuery()
                query.prepare(
                    "INSERT INTO teachers (name, subject, group_name) VALUES (:name, :subject, :group)"
                )
                query.bindValue(":name", data["name"])
                query.bindValue(":subject", data["subject"])
                query.bindValue(":group", data["group"])
                if query.exec_():
                    self.teacher_model.select()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить учителя.")

    def edit_teacher(self):
        index = self.teacher_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите учителя для редактирования."
            )
            return

        teacher_id = self.teacher_model.data(self.teacher_model.index(index.row(), 0))
        dialog = TeacherDialog(self, teacher_id)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data["name"] and data["subject"] and data["group"]:
                query = QSqlQuery()
                query.prepare(
                    """UPDATE teachers SET name = :name, subject = :subject, group_name = :group
                                WHERE id = :id"""
                )
                query.bindValue(":name", data["name"])
                query.bindValue(":subject", data["subject"])
                query.bindValue(":group", data["group"])
                query.bindValue(":id", teacher_id)
                if query.exec_():
                    self.teacher_model.select()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить учителя.")

    def delete_teacher(self):
        index = self.teacher_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите учителя для удаления."
            )
            return

        teacher_id = self.teacher_model.data(self.teacher_model.index(index.row(), 0))
        reply = QMessageBox.question(
            self,
            "Удалить учителя",
            "Вы уверены, что хотите удалить учителя?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM teachers WHERE id = :id")
            query.bindValue(":id", teacher_id)
            if query.exec_():
                self.teacher_model.select()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось удалить учителя.")

    @pyqtSlot()
    def auto_save(self):
        if not self.teacher_model.submitAll():
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить изменения.")
            self.teacher_model.revertAll()

    def save_changes(self):
        if self.teacher_model.submitAll():
            QMessageBox.information(self, "Сохранено", "Изменения успешно сохранены.")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить изменения.")
            self.teacher_model.revertAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
