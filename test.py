import sys
import random
from math import gcd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget, 
                            QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                            QMessageBox, QTextEdit, QComboBox)
from PyQt5.QtCore import Qt, QTimer

class RSAGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive RSA Game")
        self.setGeometry(100, 100, 800, 600)
        
        # Game state variables
        self.difficulty = "easy"
        self.stage = 0
        self.p = self.q = self.n = self.phi = self.e = self.d = None
        self.plaintext = ""
        self.ciphertext = []
        self.time_elapsed = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        # Create main stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create screens
        self.main_menu = self.create_main_menu()
        self.stage1_widget = self.create_stage1()
        self.stage2_widget = self.create_stage2()
        self.stage3_widget = self.create_stage3()
        self.stage4_widget = self.create_stage4()
        
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.stage1_widget)
        self.stack.addWidget(self.stage2_widget)
        self.stack.addWidget(self.stage3_widget)
        self.stack.addWidget(self.stage4_widget)
        
    def create_main_menu(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("RSA Crypto Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        
        start_btn = QPushButton("Start Game")
        start_btn.clicked.connect(self.start_game)
        
        layout.addWidget(title)
        layout.addWidget(QLabel("Select Difficulty:"))
        layout.addWidget(self.difficulty_combo)
        layout.addWidget(start_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_stage1(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stage1_title = QLabel("Stage 1: Prime Number Selection")
        self.stage1_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("Enter first prime number (p)")
        
        self.q_input = QLineEdit()
        self.q_input.setPlaceholderText("Enter second prime number (q)")
        
        validate_btn = QPushButton("Validate Primes")
        validate_btn.clicked.connect(self.validate_primes)
        
        layout.addWidget(self.stage1_title)
        layout.addWidget(QLabel("Enter two prime numbers:"))
        layout.addWidget(self.p_input)
        layout.addWidget(self.q_input)
        layout.addWidget(validate_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def validate_primes(self):
        p = self.p_input.text()
        q = self.q_input.text()
        
        try:
            p = int(p)
            q = int(q)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid integers")
            return
            
        if not (self.is_prime(p) and self.is_prime(q)):
            QMessageBox.warning(self, "Invalid Primes", "Both numbers must be prime!")
            return
        
        if p < 11 or q < 11:  # Require larger prime numbers
            QMessageBox.warning(self, "Prime Too Small", "Choose prime numbers greater than 10!")
            return

        self.p = p
        self.q = q
        self.show_stage2()

    
    def create_stage2(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stage2_title = QLabel("Stage 2: Key Generation")
        self.stage2_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.n_label = QLabel()
        self.phi_label = QLabel()
        
        self.e_combo = QComboBox()
        self.e_combo.addItem("Select public exponent (e)")  # Placeholder alternative
        
        generate_btn = QPushButton("Generate Private Key")
        generate_btn.clicked.connect(self.generate_keys)
        
        layout.addWidget(self.stage2_title)
        layout.addWidget(self.n_label)
        layout.addWidget(self.phi_label)
        layout.addWidget(QLabel("Select public exponent:"))
        layout.addWidget(self.e_combo)
        layout.addWidget(generate_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def generate_keys(self):
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        selected_e = self.e_combo.currentText()
        
        if not selected_e.isdigit():
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid e value!")
            return

        self.e = int(selected_e)

        self.d = self.mod_inverse(self.e, self.phi)
        
        if self.d is None:
            QMessageBox.warning(self, "Invalid Selection", "No modular inverse exists for selected e")
            return

        print(f"Debug: Generated Keys -> e: {self.e}, phi(n): {self.phi}, d: {self.d}, n: {self.n}")  # Debugging

        QMessageBox.information(self, "Key Generated", f"Your Private Key (d) is: {self.d}")
        
        self.show_stage3()

    def create_stage3(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stage3_title = QLabel("Stage 3: Encryption")
        self.stage3_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.plaintext_input = QLineEdit()
        self.plaintext_input.setPlaceholderText("Enter message to encrypt")
        
        encrypt_btn = QPushButton("Encrypt")
        encrypt_btn.clicked.connect(self.encrypt_message)
        
        self.ciphertext_display = QTextEdit()
        self.ciphertext_display.setReadOnly(True)
        
        layout.addWidget(self.stage3_title)
        layout.addWidget(QLabel("Enter plaintext message:"))
        layout.addWidget(self.plaintext_input)
        layout.addWidget(encrypt_btn)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def encrypt_message(self):
        if self.e is None or self.n is None:
            QMessageBox.warning(self, "Encryption Error", "Public key (e, n) is not set properly!")
            return

        self.plaintext = self.plaintext_input.text()
        if not self.plaintext:
            QMessageBox.warning(self, "Empty Message", "Please enter a message to encrypt")
            return

        print(f"Debug: e={self.e}, n={self.n}")  # Debugging line

        # Convert to ASCII values and encrypt
        try:
            self.ciphertext = [pow(ord(c), self.e, self.n) for c in self.plaintext]
        except TypeError as ex:
            print(f"Encryption Error: {ex}")
            QMessageBox.warning(self, "Encryption Failed", "An error occurred during encryption.")
            return

        # Display results
        result = f"Encrypted: {self.ciphertext}"
        self.ciphertext_display.setPlainText(result)
        self.show_stage4()

    def create_stage4(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stage4_title = QLabel("Stage 4: Decryption")
        self.stage4_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.d_input = QLineEdit()
        self.d_input.setPlaceholderText("Enter private key (d)")
        
        decrypt_btn = QPushButton("Decrypt")
        decrypt_btn.clicked.connect(self.decrypt_message)
        
        self.decrypted_display = QTextEdit()
        self.decrypted_display.setReadOnly(True)
        
        layout.addWidget(self.stage4_title)
        layout.addWidget(QLabel("Enter private key:"))
        layout.addWidget(self.d_input)
        layout.addWidget(decrypt_btn)
        layout.addWidget(QLabel("Ciphertext:"))
        layout.addWidget(self.ciphertext_display)
        layout.addWidget(QLabel("Decrypted Message:"))
        layout.addWidget(self.decrypted_display)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def decrypt_message(self):
        try:
            d = int(self.d_input.text())
            print(f"Debug: Entered Private Key (d) = {d}")  # Debugging
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer for d")
            return

        print(f"Debug: Decrypting with d={d}, n={self.n}")  # Debugging

        try:
            decrypted = [chr(pow(c, d, self.n)) for c in self.ciphertext]
            decrypted_text = ''.join(decrypted)
        except Exception as ex:
            print(f"Decryption Error: {ex}")
            QMessageBox.warning(self, "Decryption Failed", "An error occurred during decryption.")
            return

        print(f"Debug: Decrypted ASCII: {[ord(c) for c in decrypted_text]}")
        print(f"Debug: Decrypted Message: {decrypted_text}")

        self.decrypted_display.setPlainText(f"Decrypted Message: {decrypted_text}")

        if decrypted_text == self.plaintext:
            # Stop Timer and Calculate Time Taken
            self.timer.stop()
            minutes = self.time_elapsed // 60
            seconds = self.time_elapsed % 60
            time_taken_str = f"{minutes} minute(s) {seconds} second(s)"

            QMessageBox.information(self, "Success!", f"Decryption successful!\nTime taken: {time_taken_str}")
        else:
            QMessageBox.warning(self, "Failure", "Decryption failed!")


    
    # Helper functions
    def is_prime(self, n, k=5):
        if n <= 1:
            return False
        for p in [2,3,5,7,11,13,17,19,23,29]:
            if n % p == 0:
                return n == p
        d = n-1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        for _ in range(k):
            a = random.randint(2, min(n-2, 1<<20))
            x = pow(a, d, n)
            if x == 1 or x == n-1:
                continue
            for __ in range(s-1):
                x = pow(x, 2, n)
                if x == n-1:
                    break
            else:
                return False
        return True
    
    def mod_inverse(self, e, phi):
        try:
            return pow(e, -1, phi)
        except ValueError:
            print(f"Error: No modular inverse for e={e}, phi={phi}")
            return None

    
    # Navigation functions
    def start_game(self):
        self.difficulty = self.difficulty_combo.currentText().lower()
        self.time_elapsed = 0  # Reset timer
        self.timer.start(1000)  # Start timer with 1-second intervals
        self.stack.setCurrentIndex(1)

    
    def show_stage2(self):
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        self.n_label.setText(f"n = p * q = {self.n}")
        self.phi_label.setText(f"φ(n) = (p-1)(q-1) = {self.phi}")

        # Generate valid e values
        self.e_combo.clear()
        valid_es = [e for e in range(3, self.phi) if gcd(e, self.phi) == 1 and e < self.phi][:10]
        self.e_combo.addItems(map(str, valid_es))

        print(f"Debug: Valid e values = {valid_es}")  # Debugging

        self.stack.setCurrentIndex(2)

    
    def show_stage3(self):
        self.stack.setCurrentIndex(3)
    
    def show_stage4(self):
        self.stack.setCurrentIndex(4)
    
    def update_timer(self):
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.setWindowTitle(f"RSA Game - Time: {minutes:02}:{seconds:02}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RSAGame()
    window.show()
    sys.exit(app.exec_())