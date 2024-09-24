from src.ui_elements.base_crud_table import BaseCRUDTable
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5.QtCore import  pyqtSignal

class ProductsTable(BaseCRUDTable):
    data_saved = pyqtSignal()
    def __init__(self, database_connection, lot_id, parent=None):
        self.lot_id = lot_id
        headers = ['ID', 'Cell ID', 'Site ID','Product Type','Version', 'Delivery Date','Status','Date','Classification']
        super().__init__(database_connection, headers, parent)
        self.init_crud_buttons()

        self.hideColumn(0)
        self.parent = parent
        self.open_details_button = QPushButton("Details")
        self.open_details_button.clicked.connect(self.open_selected_product)
        self.button_layout.addWidget(self.open_details_button)
        self.load_data()
        self.add_empty_row()


    def open_selected_product(self):
        selected_row = self.currentRow()
        if selected_row == -1:
            return
        product_id = self.item(selected_row, 0).text()
        try:
            self.parent.open_product_details(product_id)
        except Exception as e:
            print(e)

    def load_data(self):
        """Load products specific data from the database."""
        self.setRowCount(0)
        query = "SELECT id, cell_id, site_id, product_type, version, delivery_date, status, status_date, classification FROM public.products WHERE lot_id = %s"
