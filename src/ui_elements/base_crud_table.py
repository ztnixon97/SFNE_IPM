# src/ui_elements/base_crud_table.py
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QWidget

class BaseCRUDTable(QTableWidget):
    def __init__(self, database_connection, headers, parent=None):
        super().__init__(parent)
        self.database_connection = database_connection
        self.headers = headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # Enable cell editing
        self.setEditTriggers(QTableWidget.DoubleClicked)

        # Add CRUD buttons for each table
        self.init_crud_buttons()


    def init_crud_buttons(self):
        """Initialize CRUD buttons (Add, Edit, Delete)."""
        self.button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Row")
        self.add_button.clicked.connect(self.add_row)

        self.delete_button = QPushButton("Delete Selected Row")
        self.delete_button.clicked.connect(self.delete_selected_row)

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_data)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.save_button)

    def handle_cell_change(self, row, column):
        """Automatically save data when the user edits a row."""
        if row == self.rowCount() - 1:  # If user is editing the last (empty) row
            self.add_empty_row()  # Append a new empty row
        self.save_data()  # Save data after the cell is changed

    def add_empty_row(self):
        """Append an empty row at the bottom for user to input new data."""
        row_position = self.rowCount()
        self.insertRow(row_position)
        for col in range(self.columnCount()):
            self.setItem(row_position, col, QTableWidgetItem(""))

    def add_row(self, row_data=None):
        """
        Add a new row to the table. If row_data is provided, populate the row with that data.
        If row_data is None, add an empty row.
        """
        row_position = self.rowCount()
        self.insertRow(row_position)

        if row_data:
            # Populate the row with the provided data
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data)) if data is not None else QTableWidgetItem("")
                self.setItem(row_position, col, item)
        else:
            # Insert empty row for creating new data
            for col in range(self.columnCount()):
                self.setItem(row_position, col, QTableWidgetItem(""))

    def delete_selected_row(self):
        """Delete the currently selected row."""
        selected_row = self.currentRow()
        if selected_row >= 0:
            self.removeRow(selected_row)

    def save_data(self):
        """Override this method in derived classes to save data to the database."""
        pass

    def load_data(self):
        """Override this method in derived classes to load data from the database."""
        pass

    def get_button_widget(self):
        """Return a widget that contains the CRUD buttons."""
        button_widget = QWidget()
        button_widget.setLayout(self.button_layout)
        return button_widget

    def parse_row_data(self, row):
        """Parse the row data, replacing empty strings with None, but only for non-empty rows."""
        row_data = []
        is_row_empty = True

        for col in range(self.columnCount()):
            item = self.item(row, col)
            value = item.text() if item is not None else None

            if value and value.strip():
                is_row_empty = False

            value = value if value and value.strip() else None
            row_data.append(value)

        if is_row_empty:
            return None

        return row_data