import sys
import sqlite3
import time
import random
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, 
                             QComboBox)
from PyQt5.QtCore import QTimer

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

class RSAGame(QMainWindow):
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

        layout.addWidget(QLabel("RSA Game - Time Attack Mode"))
        layout.addWidget(QLabel("Enter your name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Select Difficulty:"))
        layout.addWidget(self.difficulty_combo)
        layout.addWidget(start_btn)
        layout.addWidget(leaderboard_btn)

        widget.setLayout(layout)
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

if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    game = RSAGame()
    game.show()
    sys.exit(app.exec_())
