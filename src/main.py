import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtCore import Qt

from utils.database import SFNEIpmDatabase
from ui_elements.clickable_card import ClickableCard
from pages.contract_details import ContractDetailsPage

# Management View with Card Based Navigation
class ManagementView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = SFNEIpmDatabase()
        self.database.connect()

        self.setWindowTitle("Contract Management")

        # Create the central widget and layout
        self.central_widget = QWidget()
        self.grid_layout = QGridLayout(self.central_widget)
        self.grid_layout.setSpacing(10)  # Space between cards
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align cards to top-left
        self.setCentralWidget(self.central_widget)

        # Load contract cards
        self.load_contract_cards()

        # Call resize event to adjust the grid dynamically when the window resizes
        self.resizeEvent = self.adjust_grid_layout

    def load_contract_cards(self):
        cursor = self.database.cursor
        cursor.execute("SELECT contract_id, name, spend_ceiling, spend_current, mission_manager FROM management.contracts")
        contracts = cursor.fetchall()

        self.cards = []
        for contract in contracts:
            contract_id, name, spend_ceiling, spend_current, mission_manager = contract

            # Create a clickable card for each contract
            card = ClickableCard(contract_id, name, spend_ceiling, spend_current, mission_manager)
            card.clicked.connect(lambda _, id=contract_id: self.open_contract(id))

            # Add the card to the list of cards
            self.cards.append(card)

        # Adjust the layout to add cards in grid
        self.adjust_grid_layout()

    def adjust_grid_layout(self, event=None):
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

        # Get the number of columns based on the current width
        window_width = self.central_widget.width()
        card_width = 250  # Fixed width for each card
        num_columns = max(1, window_width // (card_width + self.grid_layout.spacing()))  # Ensure at least 1 column

        # Populate the grid layout dynamically based on the number of columns
        row = 0
        col = 0
        for i, card in enumerate(self.cards):
            self.grid_layout.addWidget(card, row, col)

            # Move to the next row if we've reached the column limit
            col += 1
            if col >= num_columns:
                col = 0
                row += 1

    def open_contract(self, contract_id):
        """Open the ContractDetailsPage when a contract is clicked."""
        try:
            self.contract_details_page = ContractDetailsPage(contract_id, self.database)
            self.contract_details_page.show()
        except Exception as e:
            print(f"Error opening contract: {e}")

if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Create and show the management view
    window = ManagementView()
    window.show()

    sys.exit(app.exec_())
