from PyQt5.QtWidgets import QMainWindow, QDateEdit, QVBoxLayout, QLabel, QWidget, QPushButton, QFormLayout, QLineEdit
from PyQt5.QtCore import QDate
from src.pages.do_details import DeliveryOrderDetailsPage
from src.pages.documents_detials import DocumentDetailsPage
from src.pages.invoice_details import InvoiceDetailsPage
from src.ui_elements.delivery_orders_table import DeliveryOrdersTable
from src.ui_elements.invoices_table import InvoicesTable
from src.ui_elements.documents_table import DocumentsTable

class ContractDetailsPage(QMainWindow):
    def __init__(self, contract_id, database_connection):
        super().__init__()

        self.contract_id = contract_id
        self.database_connection = database_connection

        # Set the window title
        self.setWindowTitle(f"Contract Details - {self.contract_id}")

        # Main layout
        layout = QVBoxLayout()

        # Create an editable form for contract details
        self.contract_details_form = self.create_contract_details_form()
        layout.addLayout(self.contract_details_form)

        # Delivery Orders Table (pass self as the parent)
        self.delivery_orders_table = DeliveryOrdersTable(self.database_connection, self.contract_id, self)
        layout.addWidget(QLabel("Delivery Orders"))
        layout.addWidget(self.delivery_orders_table)

        # Add CRUD buttons and the Open Details button for Delivery Orders
        layout.addWidget(self.delivery_orders_table.get_button_widget())

        # Invoices Table
        self.invoices_table = InvoicesTable(self.database_connection, self.contract_id, parent=self)
        layout.addWidget(QLabel("Invoices"))
        layout.addWidget(self.invoices_table)

        # Add CRUD buttons for Invoices
        layout.addWidget(self.invoices_table.get_button_widget())

        # Documents Table
        self.documents_table = DocumentsTable(self.database_connection, self.contract_id, parent=self)
        layout.addWidget(QLabel("Documents"))
        layout.addWidget(self.documents_table)

        # Add CRUD buttons for Documents
        layout.addWidget(self.documents_table.get_button_widget())

        # Add Save Button for all changes (including contract details and tables)
        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self.save_all_changes)
        layout.addWidget(save_button)

        # Set the main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_contract_details_form(self):
        """Creates an editable form for the contract details."""
        form_layout = QFormLayout()

        # Fetch contract details from the database
        cursor = self.database_connection.cursor
        cursor.execute("SELECT name, type, funding_lines, spend_ceiling, spend_current, mission_manager, award, complete FROM management.contracts WHERE contract_id = %s", (self.contract_id,))
        contract = cursor.fetchone()

        if contract:
            name, contract_type, funding_lines, spend_ceiling, spend_current, mission_manager, award, complete = contract

            # Convert funding_lines from array to a comma-separated string (no quotes)
            funding_lines_str = ", ".join(map(lambda x: x.strip().replace("'", ""), funding_lines)) if funding_lines else ""

            # Create line edit fields for each contract detail
            self.name_input = QLineEdit(name)
            self.type_input = QLineEdit(contract_type)
            self.funding_lines_input = QLineEdit(funding_lines_str)  # Comma-separated format without quotes
            self.spend_ceiling_input = QLineEdit(str(spend_ceiling))
            self.spend_current_input = QLineEdit(str(spend_current))
            self.mission_manager_input = QLineEdit(mission_manager)

            self.award_date_input = QDateEdit()
            self.complete_date_input = QDateEdit()
            if award is not None:
                self.award_date_input.setDate(QDate.fromString(str(award), "yyyy-MM-dd"))

            if complete is not None:
                self.complete_date_input.setDate(QDate.fromString(str(complete), "yyyy-MM-dd"))


            # Add them to the form layout
            form_layout.addRow("Name:", self.name_input)
            form_layout.addRow("Type:", self.type_input)
            form_layout.addRow("Funding Lines:", self.funding_lines_input)
            form_layout.addRow("Spend Ceiling:", self.spend_ceiling_input)
            form_layout.addRow("Current Spend:", self.spend_current_input)
            form_layout.addRow("Mission Manager:", self.mission_manager_input)
            form_layout.addRow("Award Date:", self.award_date_input)
            form_layout.addRow("Completion Date:", self.complete_date_input)

        return form_layout

    def save_all_changes(self):
        """Save all changes, including contract details and the data in the tables."""
        # Save contract details
        self.save_contract_details()

        # Save changes for each table
        self.delivery_orders_table.save_data()
        self.invoices_table.save_data()
        self.documents_table.save_data()

        print("All changes saved to the database.")

    def save_contract_details(self):

        """Save the edited contract details to the database."""


        # Get the edited values from the form inputs
        name = self.name_input.text()
        contract_type = self.type_input.text()

        # Normalize funding lines (split by comma or space, remove extra whitespace)
        funding_lines = [line.strip() for line in self.funding_lines_input.text().replace(",", " ").split() if line.strip()]

        spend_ceiling = self.spend_ceiling_input.text()
        spend_current = self.spend_current_input.text()
        mission_manager = self.mission_manager_input.text()

        # Get dates from QDateEdit and convert to Python's date
        default_date = QDate(2000, 1, 1)
        award_date = self.award_date_input.date()
        if award_date != default_date:
            award_date = award_date.toString("yyyy-MM-dd")
        else:
            award_date = None
        complete_date = self.complete_date_input.date()
        if complete_date != default_date:
            complete_date = complete_date.toString("yyyy-MM-dd")
        else:
            complete_date = None

        try:
            # Update the contract details in the database
            self.database_connection.cursor.execute("""
                UPDATE management.contracts
                SET name = %s, type = %s, funding_lines = %s, spend_ceiling = %s, spend_current = %s, mission_manager = %s, award = %s, complete = %s
                WHERE contract_id = %s
            """, (name, contract_type, funding_lines, spend_ceiling, spend_current, mission_manager, award_date, complete_date, self.contract_id))

            self.database_connection.commit()
            print("Contract details updated.")
        except Exception as e:
            print(f"Failed saving Contract Details: {e}")

    def open_delivery_order_details(self, delivery_order_id,):
        try:
            self.do_details_page = DeliveryOrderDetailsPage(delivery_order_id, self.database_connection, parent=self)
            self.do_details_page.data_saved.connect(self.refresh_data)
            self.do_details_page.show()
        except Exception as e:
            print(f"Failed to open delivery order details: {e}")


    def open_invoice_details(self, invoice_id):
        try:
            self.invoice_details_page = InvoiceDetailsPage(invoice_id, self.database_connection)
            self.invoice_details_page.data_saved.connect(self.refresh_invoice_data)
            self.invoice_details_page.show()
        except Exception as e:
            print(f"Failed to open invoice details: {e}")


    def open_document_details(self, document_id):
        try:
            self.document_details_page = DocumentDetailsPage(document_id, self.database_connection)
            self.document_details_page.data_saved.connect(self.refresh_document_data)
            self.document_details_page.show()
        except Exception as e:
            print(f"Failed to open document details: {e}")

    def refresh_document_data(self):
        print("reloading document data")
        self.documents_table.load_data()
        self.documents_table.add_empty_row()

    def refresh_do_data(self):
        self.delivery_orders_table.load_data()
        self.delivery_orders_table.add_empty_row()

    def refresh_invoice_data(self):
        self.invoices_table.load_data()
        self.invoices_table.add_empty_row()

    def refresh_data(self):
        try:
            self.refresh_document_data()
            self.refresh_do_data()
            self.refresh_invoice_data()
        except Exception as e:
            print(e)