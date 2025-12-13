# Exam Practice System (EPS)

A robust, Flask-based Computer Based Test (CBT) practice application designed to simulate Nigerian examination environments (JAMB, WAEC, NECO). This system provides a realistic "War Room" exam interface for students and a comprehensive management panel for administrators.

## 🚀 Features

### For Students (Candidates)
* **"War Room" Exam Interface:** A distraction-free environment that mimics the actual JAMB CBT software.
    * **Zone A (Header):** User passport, active subject tabs, and a real-time countdown timer (turns red when < 5 mins left).
    * **Zone B (Main Stage):** Clear question display with large, Fitts's Law-compliant click targets for options.
    * **Zone C (Navigation Map):** A color-coded grid (Green=Answered, White=Unanswered) to jump between questions.
* **JAMB Simulator:** * Simultaneous testing of 4 subjects (e.g., English + 3 others).
    * 120-minute (2-hour) strict timer.
    * Built-in on-screen Calculator.
    * Keyboard Shortcuts: `N` for Next, `P` for Previous.
* **Detailed Results & Corrections:**
    * Performance score breakdown by subject.
    * Visual progress bars.
    * Correction mode showing user choice vs. correct answer with explanations.

### For Administrators
* **Secure Admin Panel:** Protected by password hashing and session authentication.
* **Content Management:**
    * **Subjects:** Create, Rename, and Delete subjects.
    * **Questions:** Full CRUD (Create, Read, Update, Delete) support.
* **Bulk Upload:** Upload hundreds of questions at once using CSV files.
* **User Management:** (Future feature) Manage student profiles.

## 🛠️ Technology Stack

* **Backend:** Python (Flask), SQLAlchemy (ORM).
* **Database:** SQLite (Auto-generated).
* **Frontend:** HTML5, CSS3, JavaScript.
    * **Framework:** Bootstrap 5.3 (Grid & Utilities).
    * **Custom CSS:** Modularized styles (`jamb.css`, `dashboard.css`, `results.css`) following *Refactoring UI* principles.
* **Security:** Flask-WTF (CSRF Protection), Werkzeug (Password Hashing).

## ⚙️ Installation & Setup

1.  **Clone or Download** this repository.
2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application:**
    ```bash
    python app.py
    ```
5.  **Access the System:**
    Open your browser and go to `http://127.0.0.1:5000`

## 🔐 Default Admin Credentials

* **Username:** `EPS`
* **Password:** `AdminEPS123`
* *(Note: You can change these in `exam_app/config.py`)*

## 📂 Project Structure

## 📝 CSV Upload Format

To bulk upload questions, create a `.csv` file with the following headers:
`question_text, option_a, option_b, option_c, option_d, correct_answer, explanation`

Example row:
`"What is 2+2?", "3", "4", "5", "6", "B", "Basic addition"`

## 🤝 Contributing

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/NewFeature`).
3.  Commit your changes (`git commit -m 'Add some NewFeature'`).
4.  Push to the branch (`git push origin feature/NewFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
