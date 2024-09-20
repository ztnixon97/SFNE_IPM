import os

from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QLabel, QWidget, QPushButton, QFormLayout, \
    QLineEdit, QSizePolicy
from PyQt5.QtCore import pyqtSignal

import fitz

class DocumentDetailsPage(QMainWindow):
    data_saved = pyqtSignal()
    def __init__(self, document_id, database_connection, parent=None):
        super().__init__()

        self.document_id = document_id
        self.database = database_connection
        self.parent= parent
        self.setWindowTitle(f"Document Details - {self.document_id}")

        self.layout = QVBoxLayout()

        self.document_details_form= self.create_document_details_form()
        self.layout.addLayout(self.document_details_form)

        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self.save_all_changes)
        self.layout.addWidget(save_button)

        open_button = QPushButton("Open Document")
        open_button.clicked.connect(self.open_document)
        self.layout.addWidget(open_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)


    def create_document_details_form(self):
        form_layout = QFormLayout()

        self.database.cursor.execute("""
            SELECT document_name, file_path, version, description, classification
            FROM documents
            where document_id = %s
        """, (self.document_id,))

        document = self.database.cursor.fetchone()
        if document:
            document_name, file_path, version, description, classification = document

            self.document_name_input = QLineEdit(str(document_name) if document_name is not None else "")
            self.file_path_input = QLineEdit(str(file_path) if file_path is not None else "")
            self.version_input = QLineEdit(str(version) if version is not None else "")
            self.description_input = QTextEdit(str(description) if description is not None else "")
            self.classification_input = QLineEdit(str(classification) if classification is not None else "")

            self.description_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.description_input.setMinimumHeight(100)
            form_layout.addRow("Document Name:", self.document_name_input)
            form_layout.addRow("File Path:", self.file_path_input)
            form_layout.addRow("Version:", self.version_input)
            form_layout.addRow("Description:", self.description_input)
            form_layout.addRow("Classification:", self.classification_input)

        return form_layout

    def save_all_changes(self):
        self.save_document_details()

    def save_document_details(self):
        document_name = self.document_name_input.text() if self.document_name_input.text() else None
        file_path = self.file_path_input.text() if self.file_path_input.text() else None
        version = self.version_input.text() if self.version_input.text() else None
        description = self.description_input.toPlainText() if self.description_input.toPlainText() else None
        classification = self.classification_input.text() if self.classification_input.text() else None

        try:
            self.database.cursor.execute("""
                UPDATE documents
                SET document_name = %s, file_path = %s, version = %s, description = %s, classification = %s
                WHERE document_id = %s
            """, (document_name, file_path, version, description, classification, self.document_id))

            self.database.commit()
            self.data_saved.emit()
            print("Document details updated")

        except Exception as e:
            self.database.rollback()
            print(f"Failed to save document details: {e}")

    def open_document(self):
        try:
            file_path = self.file_path_input.text()
            if not os.path.exists(file_path):
                print(f"File does not exist: {file_path}")
                return

            # Open Word document
            if file_path.endswith(('.doc', '.docx')):
                print("Opening Word document...")

                self.document = QAxWidget()
                self.document.setControl("Word.Application")
                self.document.dynamicCall('SetVisible (bool Visible)', 'false')
                self.document.setProperty('DisplayAlerts', 'false')
                self.document.setProperty('SetReadOnly (bool ReadOnly)', 'true')
                self.document.setControl(file_path)
                self.document.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.document.setMinimumSize(600, 400)  # Adjust minimum size as necessary

                self.layout.addWidget(self.document)


            # Open Excel document
            elif file_path.endswith(('.xls', '.xlsx')):
                print("Opening Excel document...")
                self.document = QAxWidget()
                self.document.setControl("Excel.Application")
                self.document.dynamicCall('SetVisible (bool Visible)', 'false')
                self.document.setProperty('DisplayAlerts', 'false')
                self.document.setControl(file_path)
                self.document.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.document.setMinimumSize(600, 400)  # Adjust minimum size as necessary

                self.layout.addWidget(self.document)
                self.layout.addWidget(self.document)
            # Open PDF document
            elif file_path.endswith('.pdf'):
                print("Opening PDF document...")
                self.open_pdf(file_path)

            else:
                print(f"Unsupported file type: {file_path}")


        except Exception as e:
            print(e)

        self.showMaximized()




    def open_pdf(self, file_path):
        """Open and display PDF files."""
        pdf_document = fitz.open(file_path)

        pdf_layout = QVBoxLayout()

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()

            # Convert the PyMuPDF pixmap to a Qt image
            image = pix.tobytes("ppm")
            label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(image)
            label.setPixmap(pixmap)
            pdf_layout.addWidget(label)

        # Add the PDF to the layout
        pdf_widget = QWidget()
        pdf_widget.setLayout(pdf_layout)
        self.layout.addWidget(pdf_widget)