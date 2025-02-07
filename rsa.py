import sys
import sqlite3
import time
import random
import math
from math import gcd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget, 
                             QTableWidget, QTextEdit, QTableWidgetItem, QComboBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

# Setup SQLite database
def setup_database():
    conn = sqlite3.connect('game_leaderboard.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        time INTEGER NOT NULL
    )''')
    conn.commit()
    conn.close()

# Function to apply hacker theme
def apply_hacker_theme(widget):
    widget.setStyleSheet("""
        QWidget {
            background-color: black;
            color: #33ff33;
            font-family: 'Courier New';
            background-image: url('background.jpg');
            background-repeat: no-repeat;
            background-position: center;
        }
        QPushButton {
            background-color: black;
            color: #33ff33;
            border: 2px solid #33ff33;
            font-size: 16px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #33ff33;
            color: white;
        }
        QLineEdit {
            background-color: black;
            color: #33ff33;
            border: 1px solid #33ff33;
            font-size: 16px;
        }
        QLabel {
            font-size: 18px;
        }
        QTableWidget {
            border: 1px solid #33ff33;
            gridline-color: #33ff33;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #33ff33;
            color: #000000;
        }    
        QHeaderView::section {
            background-color: transparent;
            color: #33ff33;
            padding: 4px;
            border: 1px solid #33ff33;
        }     
    """)

    # Create a QLabel to hold the animated GIF
    # label = QLabel(widget)
    # movie = QMovie("background.gif")
    # label.setMovie(movie)
    # movie.start()

    # # Resize the label to cover the entire widget
    # label.setGeometry(0, 0, widget.width(), widget.height())
    # label.lower()  # Ensure the label is behind other widgets

def add_score(player_name, difficulty, time_taken):
    conn = sqlite3.connect('game_leaderboard.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO leaderboard (player_name, difficulty, time)
    VALUES (?, ?, ?)
    ''', (player_name, difficulty, time_taken))
    conn.commit()
    conn.close()

def get_top_scores():
    conn = sqlite3.connect('game_leaderboard.db')
    c = conn.cursor()
    c.execute('''
    SELECT player_name, difficulty, time FROM leaderboard
    ORDER BY time ASC
    LIMIT 5
    ''')
    top_scores = c.fetchall()
    conn.close()
    return top_scores

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA: The Game")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        title = QLabel("Welcome to RSA: The Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        self.time_attack_btn = QPushButton("Time Attack Mode")
        self.time_attack_btn.clicked.connect(self.open_time_attack)
        
        self.rsa_game_btn = QPushButton("RSA Game")
        self.rsa_game_btn.clicked.connect(self.open_rsa_game)
                
        layout.addWidget(title)
        layout.addWidget(self.time_attack_btn)
        layout.addWidget(self.rsa_game_btn)
        
        widget = QWidget()
        widget.setLayout(layout)
        apply_hacker_theme(widget)
        self.setCentralWidget(widget)
    
    def open_time_attack(self):
        self.time_attack_window = TimeAttackGame()
        self.time_attack_window.show()
    
    def open_rsa_game(self):
        if not hasattr(self, 'rsa_game_window') or not self.rsa_game_window.isVisible():
            self.rsa_game_window = RSAGame()
            self.rsa_game_window.show()
    
    def open_leaderboard(self):
        self.leaderboard_window = Leaderboard()
        self.leaderboard_window.show()

# RSA Game Class (from test.py)
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
        apply_hacker_theme(widget)
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
        apply_hacker_theme(widget)
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
        apply_hacker_theme(widget)
        return widget
    
    def generate_keys(self):
        if self.p is None or self.q is None:
            QMessageBox.warning(self, "Error", "Prime numbers are not set properly.")
            return
        
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)

        selected_e = self.e_combo.currentText()
        if not selected_e.isdigit():
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid e value!")
            return
        
        self.e = int(selected_e)
        try:
            self.d = self.mod_inverse(self.e, self.phi)
            if self.d is None:
                raise ValueError("No modular inverse found.")
        except Exception as ex:
            QMessageBox.warning(self, "Key Generation Error", f"Failed to generate keys: {ex}")
            return
        
        #QMessageBox.information(self, "Key Generated", f"Your Private Key (d) is: {self.d}")
        QMessageBox.information(self, "Key Generated", f"Your Private Key (d) is: {self.d}\nPublic Key (e) is: {self.e}\nPhi(n) is: {self.phi}\nModulus (n) is: {self.n}")
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
        apply_hacker_theme(widget)
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
        apply_hacker_theme(widget)
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
        if self.stage2_widget is None:
            QMessageBox.warning(self, "Error", "Stage 2 UI was not initialized.")
            return
        self.stack.setCurrentWidget(self.stage2_widget)
    
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
        print(f"[DEBUG] Timer running: {minutes}:{seconds}")  # Check if this prints endlessly
        self.setWindowTitle(f"RSA Game - Time: {minutes:02}:{seconds:02}")

# Time Attack Game Class (from ui.py)
class TimeAttackGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA Game - Time Attack Mode")
        self.setGeometry(100, 100, 600, 400)        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.start_time = None
        self.time_taken = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Game variables
        self.p = self.q = self.n = 0
        self.phi = self.e = self.d = 0
        self.player_name = ""
        self.difficulty = ""
        self.current_question = 0  

        # Pages
        self.start_page = self.create_start_page()
        self.game_page = self.create_game_page()
        self.leaderboard_page = self.create_leaderboard_page()
        
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.game_page)
        self.stack.addWidget(self.leaderboard_page)
    
    def create_start_page(self):
        """Create the start page UI"""
        widget = QWidget()
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])

        start_btn = QPushButton("Start Game")
        start_btn.clicked.connect(self.start_game)

        leaderboard_btn = QPushButton("View Leaderboard")
        leaderboard_btn.clicked.connect(self.show_leaderboard)

        #layout.addWidget(QLabel("RSA Game - Time Attack Mode"))

        title = QLabel("RSA Game - Time Attack Mode")
        title.setAlignment(Qt.AlignCenter)  # Center the text
        title.setStyleSheet("font-size: 24px; font-weight: bold;")  # Bold and larger font
        layout.addWidget(title)
        layout.addWidget(QLabel("Enter your name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Select Difficulty:"))
        layout.addWidget(self.difficulty_combo)
        layout.addWidget(start_btn)
        layout.addWidget(leaderboard_btn)

        widget.setLayout(layout)
        apply_hacker_theme(widget)
        return widget
    
    def create_game_page(self):
        """Create the game page UI"""
        widget = QWidget()
        layout = QVBoxLayout()

        self.question_label = QLabel("")
        self.time_label = QLabel("Time: 0 seconds")

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Enter your answer")

        submit_btn = QPushButton("Submit Answer")
        submit_btn.clicked.connect(self.submit_answer)

        layout.addWidget(self.question_label)
        layout.addWidget(self.time_label)
        layout.addWidget(QLabel("Enter your answer:"))
        layout.addWidget(self.answer_input)
        layout.addWidget(submit_btn)

        widget.setLayout(layout)
        apply_hacker_theme(widget)
        return widget

    def create_leaderboard_page(self):
        """Create the leaderboard page UI"""
        widget = QWidget()
        layout = QVBoxLayout()

        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Player", "Difficulty", "Time (s)"])

        back_btn = QPushButton("Back to Menu")
        back_btn.clicked.connect(self.reset_game)

        layout.addWidget(QLabel("Leaderboard - Top 5 Scores"))
        layout.addWidget(self.leaderboard_table)
        layout.addWidget(back_btn)

        widget.setLayout(layout)
        apply_hacker_theme(widget)
        return widget

    def start_game(self):
        """Start the game and initialize variables"""
        self.player_name = self.name_input.text()
        self.difficulty = self.difficulty_combo.currentText().lower()

        if not self.player_name:
            QMessageBox.warning(self, "Input Error", "Please enter your name.")
            return

        self.generate_challenge()
        self.start_time = time.time()
        self.timer.start(1000)
        self.current_question = 0
        self.ask_question()

        self.stack.setCurrentWidget(self.game_page)

    def generate_challenge(self):
        """Generate RSA parameters"""
        if self.difficulty == "easy":
            self.p, self.q = 5, 7
        elif self.difficulty == "medium":
            self.p, self.q = 11, 13
        elif self.difficulty == "hard":
            self.p, self.q = 17, 19

        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = self.find_coprime(self.phi)
        self.d = pow(self.e, -1, self.phi)

    def update_timer(self):
        """Update the timer every second"""
        elapsed_time = int(time.time() - self.start_time)
        self.time_label.setText(f"Time: {elapsed_time} seconds")


    def find_coprime(self, phi):
        """Find a small prime number e that is coprime to φ(n)"""
        for e in range(3, phi, 2):
            if math.gcd(e, phi) == 1:
                return e
        return 3  

    def ask_question(self):
        """Ask the next question"""
        questions = [
            f"If p = {self.p} and q = {self.q}, find n (n = p * q):",
            f"Find e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1. (φ(n) = {self.phi})",
            f"Find d such that d = e⁻¹ mod φ(n). (e = {self.e}, φ(n) = {self.phi})"
        ]
        self.question_label.setText(questions[self.current_question])

    def submit_answer(self):
        """Check answer and proceed to next question"""
        correct_answers = [self.n, self.e, self.d]
        
        try:
            user_answer = int(self.answer_input.text())
            if user_answer == correct_answers[self.current_question]:
                self.current_question += 1
                if self.current_question < 3:
                    self.ask_question()
                    self.answer_input.clear()
                else:
                    self.time_taken = int(time.time() - self.start_time)
                    self.timer.stop()
                    add_score(self.player_name, self.difficulty, self.time_taken)
                    QMessageBox.information(self, "Success!", f"You completed all questions in {self.time_taken} seconds.")
                    self.reset_game()
            else:
                QMessageBox.warning(self, "Incorrect!", "Try again!")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number.")

    def show_leaderboard(self):
        """Display leaderboard"""
        scores = get_top_scores()
        self.leaderboard_table.setRowCount(len(scores))

        for row, (name, difficulty, time) in enumerate(scores):
            self.leaderboard_table.setItem(row, 0, QTableWidgetItem(name))
            self.leaderboard_table.setItem(row, 1, QTableWidgetItem(difficulty))
            self.leaderboard_table.setItem(row, 2, QTableWidgetItem(str(time)))

        self.stack.setCurrentWidget(self.leaderboard_page)

    def reset_game(self):
        """Reset game to the start page"""
        self.name_input.clear()
        self.answer_input.clear()
        self.stack.setCurrentWidget(self.start_page)

# Leaderboard Class
class Leaderboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Leaderboard")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(3)
        self.leaderboard_table.setHorizontalHeaderLabels(["Player", "Difficulty", "Time (s)"])
        
        scores = get_top_scores()
        self.leaderboard_table.setRowCount(len(scores))
        
        for row, (name, difficulty, time) in enumerate(scores):
            self.leaderboard_table.setItem(row, 0, QTableWidgetItem(name))
            self.leaderboard_table.setItem(row, 1, QTableWidgetItem(difficulty))
            self.leaderboard_table.setItem(row, 2, QTableWidgetItem(str(time)))
        
        layout.addWidget(self.leaderboard_table)
        widget = QWidget()
        widget.setLayout(layout)
        apply_hacker_theme(widget)
        self.setCentralWidget(widget)

if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec_())
