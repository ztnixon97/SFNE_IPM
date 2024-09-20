from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt
from PyQt5 import QtCore


class ClickableCard(QFrame):
    clicked = QtCore.pyqtSignal(int)  # Custom signal that will carry the contract ID

    def __init__(self, contract_id, contract_name, spend_ceiling, spend_current, mission_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.contract_id = contract_id

        # Set the appearance of the card
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("""
            background-color: lightgrey;
            padding: 10px;
            border-radius: 10px;
            font-size: 20px;  /* Increase font size */
        """)
        self.setCursor(Qt.PointingHandCursor)

        # Set fixed size for each card
        self.setFixedSize(500, 250)  # Adjust the width and height as needed

        # Create layout for the card's content
        layout = QVBoxLayout()

        # Add contract details as labels
        layout.addWidget(QLabel(f"Contract Name: {contract_name}"))
        layout.addWidget(QLabel(f"Spend Ceiling: {spend_ceiling}"))
        layout.addWidget(QLabel(f"Current Spend: {spend_current}"))
        layout.addWidget(QLabel(f"Mission Manager: {mission_manager}"))

        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Emit signal when the card is clicked
        self.clicked.emit(self.contract_id)