from src.ui_elements.base_crud_table import BaseCRUDTable
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5.QtCore import  pyqtSignal
class DeliveryLotsTable(BaseCRUDTable):
    data_saved = pyqtSignal()
    def __init__(self, database_connection, do_id, contract_id = None, parent=None):
        self.do_id = do_id
        self.contract_id = contract_id
        headers = ['ID','Lot Number','Due Date','Notes','Classification']
        super().__init__(database_connection, headers, parent)
        self.init_crud_buttons()

        # Hide the ID column
        self.hideColumn(0)
        self.parent = parent
        self.open_details_button = QPushButton("Details")
        self.open_details_button.clicked.connect(self.open_selected_delivery_lot)
        self.button_layout.addWidget(self.open_details_button)
        self.load_data()
        self.add_empty_row()


    def open_selected_delivery_lot(self):
        selected_row = self.currentRow()
        if selected_row == -1:
            return
        delivery_lot_id = self.item(selected_row, 0).text()
        try:
            self.parent.open_delivery_lot_details(delivery_lot_id)
        except Exception as e:
            print(e)

    def load_data(self):
        """Load delivery lots specific data from the database."""
        self.setRowCount(0)
        query = "SELECT id, lot_number, due_date, notes, classification FROM public.delivery_lots WHERE do_id = %s"
        self.database_connection.cursor.execute(query, (self.do_id,))
        delivery_lots = self.database_connection.cursor.fetchall()

        # Populate the table with data
        for lot in delivery_lots:
            self.add_row(lot)

    def save_data(self):
        """Save the data from the table to the database."""
        for row in range(self.rowCount()):
            row_data = self.parse_row_data(row)
            #skip empty rows
            if row_data is None:
                continue

            id, lot_number, due_date, notes, classification = row_data

            try:
                if id is None:
                    self.database_connection.cursor.execute("""
                        INSERT INTO public.delivery_lots (lot_number, due_date, notes, classification, do_id)
                        VALUES  (%s, %s, %s, %s, %s) RETURNING id;
                    """, (lot_number, due_date, notes, classification, self.do_id))
                    new_id = self.database_connection.cursor.fetchone()[0]
                    self.setItem(row, 0, QTableWidgetItem(str(new_id)))
                else:
                    self.database_connection.cursor.execute("""
                        UPDATE public.delivery_lots
                        set lot_number = %s, due_date = %s, notes = %s, classification = %s
                        WHERE id = %s;
                    """, (lot_number, due_date, notes, classification, id))
            except Exception as e:
                print(f"Failed to save delivery lot: {e}")
                self.database_connection.rollback()
        try:
            self.database_connection.commit()
            print("Delivery Lots saved.")
        except Exception as e:
            print(f"Failed to save Delivery Lots: {e}")
            self.database_connection.rollback()