from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDateEdit,QVBoxLayout, QLabel, QWidget, QPushButton, QFormLayout, QLineEdit
from PyQt5.QtCore import QDate, pyqtSignal
from src.ui_elements.invoices_table import InvoicesTable
from src.ui_elements.documents_table import DocumentsTable

class DeliveryOrderDetailsPage(QMainWindow):
    data_saved = pyqtSignal()
    def __init__(self, delivery_order_id, database_connection):
        super().__init__()

        self.delivery_order_id = delivery_order_id
        self.database = database_connection

        # Set the window Title
        self.setWindowTitle(f"Delivery Order Details - {self.delivery_order_id}")

        layout = QVBoxLayout()

        # Create and add delivery order details form
        self.delivery_order_details_form = self.create_delivery_order_details_form()
        layout.addLayout(self.delivery_order_details_form)

        # TODO: Add Delivery Lots Table

        # Create and add the Invoices Table
        self.invoices_table = InvoicesTable(self.database, self.delivery_order_id)
        layout.addWidget(QLabel("Invoices"))
        layout.addWidget(self.invoices_table)
        layout.addWidget(self.invoices_table.get_button_widget())

        # Create and add the Documents Table
        self.documents_table = DocumentsTable(self.database, self.delivery_order_id)
        layout.addWidget(QLabel("Documents"))
        layout.addWidget(self.documents_table)
        layout.addWidget(self.documents_table.get_button_widget())

        # Add Save Button for all changes (including contract details and tables)
        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self.save_all_changes)
        layout.addWidget(save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_delivery_order_details_form(self):
        """Create and populate the form with the delivery order's details."""
        form_layout = QFormLayout()

        # Query delivery order details
        self.database.cursor.execute("""
            SELECT do_number, award_price, award, complete, producer, notes, mission_manager, poc, classification
            FROM delivery_orders
            WHERE id = %s
        """, (self.delivery_order_id,))
        delivery_order = self.database.cursor.fetchone()

        # Populate the form with fetched data
        if delivery_order:
            do_number, award_price, award, complete, producer, notes, mission_manager, poc, classification = delivery_order

            self.do_number_input = QLineEdit(str(do_number) if do_number is not None else "")
            self.award_price_input = QLineEdit(str(award_price) if award_price is not None else "")
            self.producer_input = QLineEdit(producer if producer is not None else "")
            self.mission_manager_input = QLineEdit(mission_manager if mission_manager is not None else "")
            self.poc_input = QLineEdit(poc if poc is not None else "")
            self.notes_input = QTextEdit(str(notes) if notes is not None else "")
            self.classification_input = QLineEdit(classification if classification is not None else "")

            # Handle QDateEdit for award and complete dates
            self.award_input = QDateEdit()
            self.complete_input = QDateEdit()

            # Set the date or leave empty if the value is None
            if award is not None:
                self.award_input.setDate(QDate.fromString(str(award), "yyyy-MM-dd"))

            if complete is not None:
                self.complete_input.setDate(QDate.fromString(str(complete), "yyyy-MM-dd"))


                # Add fields to the form layout
            form_layout.addRow("DO Number:", self.do_number_input)
            form_layout.addRow("Award Price:", self.award_price_input)
            form_layout.addRow("Award Date:", self.award_input)
            form_layout.addRow("Complete Date:", self.complete_input)
            form_layout.addRow("Producer:", self.producer_input)
            form_layout.addRow("Mission Manager:", self.mission_manager_input)
            form_layout.addRow("POC:", self.poc_input)
            form_layout.addRow("Notes:", self.notes_input)
            form_layout.addRow("Classification:", self.classification_input)

        return form_layout

    def save_all_changes(self):
        """Save all changes, including delivery order details, invoices, and documents."""
        self.save_do_details()  # Save delivery order details
        #self.invoices_table.save_data()  # Save invoices
        #self.documents_table.save_data()  # Save documents

        print("All changes saved to the database")

    def save_do_details(self):
        """Save the delivery order details to the database."""
        # Gather input values
        do_number = self.do_number_input.text() if self.do_number_input.text() else None
        award_price = self.award_price_input.text() if self.award_price_input.text() else None
        producer = self.producer_input.text() if self.producer_input.text() else None
        notes = self.notes_input.toPlainText() if self.notes_input.toPlainText() else None
        mission_manager = self.mission_manager_input.text() if self.mission_manager_input.text() else None
        poc = self.poc_input.text() if self.poc_input.text() else None
        classification = self.classification_input.text() if self.classification_input.text() else None

        # Handle QDateEdit for award and complete dates, ignore default date "01/01/2000"
        default_date = QDate(2000, 1, 1)

        # Award date handling: If it's different from the default date, use it; otherwise, set to None
        award_date = self.award_input.date()
        if award_date != default_date:
            award = award_date.toString("yyyy-MM-dd")
        else:
            award = None

        # Complete date handling: If it's different from the default date, use it; otherwise, set to None
        complete_date = self.complete_input.date()
        if complete_date != default_date:
            complete = complete_date.toString("yyyy-MM-dd")
        else:
            complete = None

        try:
            # Update the delivery order details in the database
            self.database.cursor.execute("""
                UPDATE delivery_orders
                SET do_number = %s, award_price = %s, award = %s, complete = %s, producer = %s, notes = %s,
                    mission_manager = %s, poc = %s, classification = %s
                WHERE id = %s
            """, (do_number, award_price, award, complete, producer, notes, mission_manager, poc, classification,
                  self.delivery_order_id))


            self.database.commit()
            self.data_saved.emit()
            # Commit the changes
            print("Delivery Order details updated")
        except Exception as e:
            print(f"Failed to save Delivery Order Details: {e}")