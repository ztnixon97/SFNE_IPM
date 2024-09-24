from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDateEdit,QVBoxLayout, QLabel, QWidget, QPushButton, QFormLayout, QLineEdit
from PyQt5.QtCore import QDate, pyqtSignal

class DeliveryLotDetailsPage(QMainWindow):
    data_saved = pyqtSignal()
    def __init__(self, delivery_lot_id, database_connection):
        super().__init__()

        self.delivery_lot_id = delivery_lot_id
        self.database = database_connection

        self.setWindowTitle(f"Delivery Lot Details - {self.delivery_lot_id}")
        layout = QVBoxLayout()

        self.delivery_lot_details_form = self.create_delivery_lot_details_form()
        layout.addLayout(self.delivery_lot_details_form)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_delivery_lot_details_form(self):
        form_layout = QFormLayout()
        self.database.cursor.execute("""
            SELECT lot_number, due_date, notes, classification
            FROM delivery_lots
            where id = %s
        """, (self.delivery_lot_id,))
        delivery_lot = self.database.cursor.fetchone()

        if delivery_lot:
            lot_number, due_date, notes, classification = delivery_lot
            self.lot_number_input = QLineEdit(str(lot_number) if lot_number is not None else "")
            self.due_date_input = QDateEdit()
            if due_date is not None:
                self.due_date_input.setDate(QDate.fromString(str(due_date), "yyyy-MM-dd"))
            self.notes_input = QTextEdit(str(notes) if notes is not None else "")
            self.classification_input = QLineEdit(str(classification) if classification is not None else "")
            form_layout.addRow("Lot Number:", self.lot_number_input)
            form_layout.addRow("Due Date:", self.due_date_input)
            form_layout.addRow("Notes:", self.notes_input)
            form_layout.addRow("Classification:", self.classification_input)

        return form_layout

    def save_all_changes(self):
        self.save_delivery_lot_details()

        print("Saved all changes")

    def save_delivery_lot_details(self):
        lot_number = self.lot_number_input.text() if self.lot_number_input.text() else None
        notes = self.notes_input.toPlainText() if self.notes_input.toPlainText() else None
        classification = self.classification_input.text() if self.classification_input.text() else None
        due_date = self.due_date_input.date()
        default_date = QDate(2000, 1, 1)
        if due_date != default_date:
            due_date = due_date.toString("yyyy-MM-dd")
        else:
            due_date = None

        try:
            self.database.cursor.exectue("""
                UPDATE delivery_lots
                SET lot_number = %s, notes = %s, classification = %s, due_date = %s
                where id = %s
            """, (lot_number, notes, classification, due_date, self.delivery_lot_id))

            self.database.commit()
            self.data_saved.emit()
            print("Delivery lot details updated")
        except Exception as e:
            print(f"Failed to save delivery lot details: {e}")
            self.database.rollback()
