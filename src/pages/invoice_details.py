from PyQt5.QtWidgets import QMainWindow, QDateEdit,QVBoxLayout, QWidget, QPushButton, QFormLayout, QLineEdit
from PyQt5.QtCore import QDate, pyqtSignal

class InvoiceDetailsPage(QMainWindow):
    data_saved = pyqtSignal()
    def __init__(self, invoice_id, database_connection):
        super().__init__()

        self.invoice_id = invoice_id
        self.database = database_connection

        #Set the Window Title
        self.setWindowTitle(f"Invoice Details - {self.invoice_id}")

        layout = QVBoxLayout()

        #create and add invoice detailks from

        self.invoice_details_form = self.create_invoice_details_form()
        layout.addLayout(self.invoice_details_form)

        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self.save_all_changes)
        layout.addWidget(save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_invoice_details_form(self):
        form_layout = QFormLayout()

        #Query for Invoice Details

        self.database.cursor.execute("""
            SELECT invoice_number, issue_date, cost, status, classification
            FROM management.invoices
            WHERE invoice_id = %s
        """, (self.invoice_id,))
        invoice = self.database.cursor.fetchone()

        if invoice:
            invoice_number, issue_date, total_amount, status, classification = invoice

            self.invoice_number_input = QLineEdit(str(invoice_number) if invoice_number is not None else "")
            self.status = QLineEdit(str(status) if status is not None else "")
            self.total_amount = QLineEdit(str(total_amount) if total_amount is not None else "")
            self.classification = QLineEdit(str(classification) if classification is not None else "")

            self.issue_date_input = QDateEdit()
            if issue_date is not None:
                self.issue_date_input.setDate(QDate.fromString(str(issue_date), "yyyy-MM-dd"))


            form_layout.addRow("Invoice Number:", self.invoice_number_input)
            form_layout.addRow("Issue Date:", self.issue_date_input)
            form_layout.addRow("Total Amount:", self.total_amount)
            form_layout.addRow("Status:", self.status)
            form_layout.addRow("Classification:", self.classification)
        return form_layout

    def save_all_changes(self):
        self.save_invoice_details()

    def save_invoice_details(self):
        invoice_number = self.invoice_number_input.text() if self.invoice_number_input.text() else None
        total_amount = self.total_amount.text() if self.total_amount.text() else None
        status = self.status.text() if self.status.text() else None
        classification = self.classification.text() if self.classification.text() else None

        default_date = QDate(2000, 1, 1)
        issue_date = self.issue_date_input.date()
        if issue_date != default_date:
            issue_date = issue_date.toString("yyyy-MM-dd")
        else:
            issue_date = None

        try:
            self.database.cursor.execute("""
                UPDATE management.invoices
                SET invoice_number = %s, cost = %s, status = %s, classification = %s, issue_date = %s
                where invoice_id = %s
            """, (invoice_number, total_amount, status, classification, issue_date, self.invoice_id))

            self.database.commit()
            self.data_saved.emit()
            print("Invoice details updated")
        except Exception as e:
            print(f"Failed to save invoice details: {e}")



