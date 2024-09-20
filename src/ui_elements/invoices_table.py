# src/ui_elements/invoices_table.py
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton

from src.ui_elements.base_crud_table import BaseCRUDTable

class InvoicesTable(BaseCRUDTable):
    def __init__(self, database_connection, contract_id = None, do_id = None, parent=None):
        headers = ['Invoice ID', 'Invoice Number', 'Issue Date', 'Total Amount', 'Status']
        self.contract_id = contract_id
        self.do_id = do_id
        super().__init__(database_connection, headers, parent)
        self.hideColumn(0)
        self.parent = parent
        self.open_details_button = QPushButton("Details")
        self.open_details_button.clicked.connect(self.open_selected_invoice)
        self.button_layout.addWidget(self.open_details_button)

    def open_selected_invoice(self):
        select_row = self.currentRow()
        invoice_id = self.item(select_row, 0).text()
        try:
            self.parent.open_invoice_details(invoice_id)
        except Exception as e:
            print(e)

    def load_data(self):
        """Load invoices specific data from the database."""
        self.setRowCount(0)
        cursor = self.database_connection.cursor
        query = "SELECT invoice_id, invoice_number, issue_date, cost, status FROM management.invoices WHERE contract_id = %s"
        cursor.execute(query, (self.contract_id,))
        invoices = cursor.fetchall()

        # Populate the table with data
        for invoice in invoices:
            print(invoice)
            self.add_row(invoice)


    def load_date_do(self):
        """Load Data for Delivery Orders"""
        self.setRowCount(0)
        cursor = self.database_connection.cursor
        query = "SELECT invoice_id, issue_date, cost, status FROM management.invoices WHERE delivery_order_id = %s"
        cursor.execute(query, (self.do_id,))
        invoices = cursor.fetchall()
        # Populate the table with data
        for invoice in invoices:
            self.add_row(invoice)


    def save_data(self):
            """Save invoices specific data to the database."""
            for row in range(self.rowCount()):
                row_data = self.parse_row_data(row)

                if row_data is None:
                    continue

                id, invoice_number, issue_date, total_amount, status = row_data

                try:
                    total_amount = float(total_amount) if total_amount is not None else None
                except ValueError:
                    total_amount = None

                try:
                    if id is None or id == "":
                        # Insert a new invoice
                        self.database_connection.cursor.execute("""
                                            INSERT INTO management.invoices (invoice_number, issue_date, cost, contract_id, delivery_order_id, status)
                                            VALUES (%s, %s, %s, %s, %s, %s) RETURNING invoice_id;
                                        """, (invoice_number, issue_date, total_amount, self.contract_id, self.do_id, status))
                        new_id = self.database_connection.cursor.fetchone()[0]
                        self.setItem(row, 0, QTableWidgetItem(str(new_id)))
                    else:
                        # Set the new invoice ID
                        self.database_connection.cursor.execute("""
                            UPDATE management.invoices
                            set invoice_number = %s, issue_date = %s, cost = %s, status = %s
                            where invoice_id = %s;
                        """, (invoice_number, issue_date, total_amount, status, id))

                except Exception as e:
                    print(f"Failed to save invoice: {e}")
            try:
                self.database_connection.commit()
                print("Invoices saved.")
            except Exception as e:
                self.database_connection.rollback()
                print(f"Failed to save Invoices: {e}")

    def delete_selected_row(self):
        """Delete the currently selected row."""
        selected_row = self.currentRow()
        invoice_id = self.item(self.currentRow(), 0).text()
        self.database_connection.cursor.execute("""DELETE FROM management.invoices WHERE invoice_id = %s;""", (invoice_id,))
        self.removeRow(selected_row)