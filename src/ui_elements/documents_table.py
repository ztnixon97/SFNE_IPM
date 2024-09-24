# src/ui_elements/documents_table.py
from PyQt5.QtWidgets import QPushButton, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal
from setuptools.dist import sequence

from src.ui_elements.base_crud_table import BaseCRUDTable

class DocumentsTable(BaseCRUDTable):
    data_saved = pyqtSignal()
    def __init__(self, database_connection, contract_id=None,do_id=None, parent=None):
        headers = ['Document ID','Document Name', 'File Path', 'Version', 'Description', 'Classification']
        self.contract_id = contract_id
        self.do_id = do_id
        super().__init__(database_connection, headers, parent)

        self.hideColumn(0)
        self.parent = parent
        self.open_details_button = QPushButton("Details")
        self.open_details_button.clicked.connect(self.open_selected_document)
        self.button_layout.addWidget(self.open_details_button)
        if do_id is not None:
            self.load_data = self.load_data_do
        self.load_data()
        self.add_empty_row()

    def open_selected_document(self):
        selected_row = self.currentRow()
        if selected_row == -1:
            return
        document_id = self.item(selected_row, 0).text()
        self.parent.open_document_details(document_id)
        try:
            self.parent.open_document_details(document_id)
        except Exception as e:
            print(e)

    def load_data(self):
        """Load documents specific data from the database."""
        self.setRowCount(0)
        cursor = self.database_connection.cursor
        query = """
            SELECT document_id, document_name, file_path, version, description, classification
            FROM public.documents
            WHERE document_id IN (
                SELECT document_id FROM documents WHERE contract_id = %s
            )
        """
        cursor.execute(query, (self.contract_id,))
        documents = cursor.fetchall()

        # Populate the table with data
        for document in documents:
            self.add_row(document)
    def load_data_do(self):
        self.setRowCount(0)
        cursor = self.database_connection.cursor
        query = """
            SELECT document_id, document_name, file_path, version, description, classification
            from public.documents
            where do_id = %s
        """

        cursor.execute(query, (self.do_id,))
        documents = cursor.fetchall()
        for document in documents:
            self.add_row(document)
    def save_data(self):
        """Save documents specific data to the database."""
        for row in range(self.rowCount()):
            row_date = self.parse_row_data(row)

            if row_date is None:
                continue

            document_id, document_name, file_path, version, description, classification = row_date

            try:
                print("id {}".format(document_id))
                print("do_id".format(self.do_id))
                print("contract_id".format(self.contract_id))
                if document_id is None or document_id == "":
                    print("new doc")
                    self.database_connection.cursor.execute("""
                        INSERT into documents (document_name, file_path, version, description, classification,do_id, contract_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING document_id; 
                    """, (document_name, file_path, version, description, classification, self.do_id, self.contract_id))
                    new_id = self.database_connection.cursor.fetchone()[0]
                    self.setItem(row, 0, QTableWidgetItem(str(new_id)))
                else:
                    print("update doc")
                    self.database_connection.cursor.execute("""
                        UPDATE documents
                        set document_name = %s, file_path = %s, version = %s, description = %s, classification = %s
                        where document_id = %s;
                    """,(document_name, file_path, version, description, classification, document_id))

            except Exception as e:
                print(f"Failed to save document: {e}")

        try:
            self.database_connection.commit()
            self.data_saved.emit()
            print("Documents saved.")
        except Exception as e:
            self.database_connection.rollback()
            print(f"Failed to save Documents: {e}")

    def delete_selected_row(self):
        selected_row = self.currentRow()
        document_id = self.item(selected_row, 0).text()
        self.database_connection.cursor.execute("DELETE FROM documents WHERE document_id = %s", (document_id,))
        self.removeRow(selected_row)
