# src/ui_elements/delivery_orders_table.py

from src.ui_elements.base_crud_table import BaseCRUDTable
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton

class DeliveryOrdersTable(BaseCRUDTable):
    def __init__(self, database_connection, contract_id, parent=None):
        self.contract_id = contract_id
        headers = ['ID', 'DO Number', 'Award Price', 'Award Date', 'Completion Date', 'Producer']  # Include 'ID'
        super().__init__(database_connection, headers, parent)
        self.init_crud_buttons()

        # Hide the ID column after initializing the table
        self.hideColumn(0)  # Column 0 is the 'ID' column
        self.parent = parent
        self.open_details_button = QPushButton("Details")
        self.open_details_button.clicked.connect(self.open_selected_delivery_order)
        self.button_layout.addWidget(self.open_details_button)
        self.load_data()
        self.add_empty_row()

    def open_selected_delivery_order(self):
        select_row = self.currentRow()
        if select_row == -1:
            return
        delivery_order_id = self.item(select_row, 0).text()
        try:
            self.parent.open_delivery_order_details(delivery_order_id)
        except Exception as e:
            print(e)
    def load_data(self):
        """Load delivery orders specific data from the database."""
        self.setRowCount(0)
        query = "SELECT id, do_number, award_price, award, complete, producer FROM public.delivery_orders WHERE contract_id = %s"
        self.database_connection.cursor.execute(query, (self.contract_id,))
        delivery_orders =  self.database_connection.cursor.fetchall()

        # Populate the table with data
        for order in delivery_orders:
            self.add_row(order)

    def save_data(self):
        """Save the data from the table to the database."""
        for row in range(self.rowCount()):  # Iterate over all rows
            row_data = self.parse_row_data(row)

            # Skip completely empty rows
            if row_data is None:
                continue

            id, do_number, award_price, award_date, complete_date, producer = row_data

            # Convert numeric fields to the correct type
            try:
                award_price = float(award_price) if award_price is not None else None
            except ValueError:
                award_price = None  # Handle non-convertible values gracefully

            try:
                # Update or insert the data into the database based on `id`
                if id is None:
                    # If `id` is None, insert a new record
                    self.database_connection.cursor.execute("""
                        INSERT INTO public.delivery_orders (do_number, award_price, award, complete, producer, contract_id)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
                    """, (do_number, award_price, award_date, complete_date, producer, str(self.contract_id)))
                    # Get the new `id` from the database and update the table
                    new_id =  self.database_connection.cursor.fetchone()[0]
                    self.setItem(row, 0, QTableWidgetItem(str(new_id)))  # Set the new `id` in the hidden column
                else:
                    # If `id` exists, update the existing record
                    self.database_connection.cursor.execute("""
                        UPDATE public.delivery_orders
                        SET do_number = %s, award_price = %s, award = %s, complete = %s, producer = %s
                        WHERE id = %s;
                    """, (do_number, award_price, award_date, complete_date, producer, id))
            except Exception as e:
                print(f"Failed to save delivery order: {e}")
                self.database_connection.rollback()

        try:
            self.database_connection.commit()  # Commit the changes
            print("Delivery Orders saved.")
        except Exception as e:
            print(f"Failed to save Delivery Orders: {e}")
            self.database_connection.rollback()

    def delete_selected_row(self):
        """Delete the currently selected row."""
        select_row = self.currentRow()

        id = self.item(select_row, 0).text()
        self.database_connection.cursor.execute("DELETE FROM public.delivery_orders WHERE id = %s", (id,))
        self.removeRow(select_row)

    def open_delivery_lots_details(self, delivery_lot_id):
        pass