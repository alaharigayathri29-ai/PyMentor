"""
Seed initial platform data: topics, assessment questions, practice problems, admin user.
Safe to run multiple times — skips if already seeded.

Usage:
    cd backend
    python -m app.seed_data
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.models import (
    Base, User, Topic, Question, PracticeProblem,
    LearningPath, AssessmentAttempt, StudentKnowledge,
    PracticeSubmission, MentorSession, MentorMessage,
)
from app.services.auth_service import get_password_hash
from app.config import settings


from app.curriculum_data import CURRICULUM_MODULES

def sync_curriculum_data(db):
    """Ensure all 7 curriculum modules and topics have complete structured content."""
    for mod in CURRICULUM_MODULES:
        mod_num = mod["module_number"]
        mod_name = mod["module_name"]
        for top_data in mod["topics"]:
            slug = top_data["slug"]
            existing = db.query(Topic).filter(Topic.slug == slug).first()
            if existing:
                existing.module_number = mod_num
                existing.module_name = mod_name
                existing.subtopics = top_data.get("subtopics", [])
                existing.learning_objectives = top_data.get("learning_objectives", [])
                existing.lesson_content = top_data.get("lesson_content", {})
                if not existing.description:
                    existing.description = top_data.get("description", "")
            else:
                new_topic = Topic(
                    name=top_data["name"],
                    slug=slug,
                    description=top_data.get("description", f"Master {top_data['name']} in Python."),
                    order=top_data["order"],
                    difficulty=top_data["difficulty"],
                    icon=top_data["icon"],
                    module_number=mod_num,
                    module_name=mod_name,
                    subtopics=top_data.get("subtopics", []),
                    learning_objectives=top_data.get("learning_objectives", []),
                    lesson_content=top_data.get("lesson_content", {}),
                    prerequisites=[],
                )
                db.add(new_topic)
    db.commit()

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Topic).count() > 0:
            print("[SEED] Topics already exist. Syncing structured curriculum content...")
            sync_curriculum_data(db)
            if db.query(User).filter(User.role == "student").count() == 0:
                print("[SEED] Seeding demo student accounts...")
                seed_demo_students(db)
            return

        # ── Topics ────────────────────────────────────────────────────────────
        topics_data = [
            {"name": "Variables & Data Types",      "slug": "variables",      "description": "Learn to store and work with different kinds of data in Python.", "order": 1,  "difficulty": "beginner",     "icon": "📦"},
            {"name": "Operators & Expressions",      "slug": "operators",      "description": "Master arithmetic, comparison, and logical operators.",            "order": 2,  "difficulty": "beginner",     "icon": "🧮"},
            {"name": "Conditional Statements",       "slug": "conditions",     "description": "Control program flow with if, elif, and else.",                   "order": 3,  "difficulty": "beginner",     "icon": "🔀"},
            {"name": "Loops",                        "slug": "loops",          "description": "Repeat code efficiently with for and while loops.",               "order": 4,  "difficulty": "beginner",     "icon": "🔄"},
            {"name": "Functions",                    "slug": "functions",      "description": "Create reusable code blocks with parameters and return values.",   "order": 5,  "difficulty": "beginner",     "icon": "🧩"},
            {"name": "Lists & Tuples",               "slug": "lists",          "description": "Work with ordered collections of data.",                          "order": 6,  "difficulty": "beginner",     "icon": "📝"},
            {"name": "Dictionaries & Sets",          "slug": "dictionaries",   "description": "Store and access data with key-value pairs.",                     "order": 7,  "difficulty": "intermediate", "icon": "🗄️"},
            {"name": "String Operations",            "slug": "strings",        "description": "Manipulate and format text data effectively.",                    "order": 8,  "difficulty": "intermediate", "icon": "✍️"},
            {"name": "List Comprehensions",          "slug": "comprehensions",  "description": "Write concise, Pythonic list and dictionary operations.",        "order": 9,  "difficulty": "intermediate", "icon": "⚡"},
            {"name": "Error Handling",               "slug": "error-handling", "description": "Handle exceptions gracefully with try/except.",                  "order": 10, "difficulty": "intermediate", "icon": "🛡️"},
            {"name": "File I/O",                     "slug": "file-io",        "description": "Read from and write to files.",                                   "order": 11, "difficulty": "intermediate", "icon": "📁"},
            {"name": "Object-Oriented Programming",  "slug": "oop",            "description": "Model real-world concepts with classes and objects.",             "order": 12, "difficulty": "advanced",     "icon": "🏗️"},
            {"name": "Modules & Packages",           "slug": "modules",        "description": "Organise code into reusable modules and packages.",               "order": 13, "difficulty": "advanced",     "icon": "📦"},
        ]

        topics: dict[str, Topic] = {}
        for td in topics_data:
            t = Topic(**td)
            db.add(t)
            db.flush()
            topics[td["slug"]] = t

        # ── Assessment Questions ───────────────────────────────────────────────
        qs = [
            # --- Variables & Data Types (3 q) ---
            {"slug": "variables", "text": "Which of the following is a valid Python variable name?",
             "opts": ["2fast", "my-var", "_speed", "class"], "ans": "2", "diff": "easy",
             "exp": "_speed is valid. Names must start with a letter or underscore; 'class' is a keyword."},
            {"slug": "variables", "text": "What is the data type of `x = 3.14`?",
             "opts": ["int", "float", "str", "double"], "ans": "1", "diff": "easy",
             "exp": "3.14 has a decimal point, making it a float."},
            {"slug": "variables", "text": "What does `type(True)` return?",
             "opts": ["<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'boolean'>"], "ans": "0", "diff": "easy",
             "exp": "True/False are booleans. Python's boolean type is 'bool'."},

            # --- Operators (3 q) ---
            {"slug": "operators", "text": "What is the result of `10 % 3`?",
             "opts": ["3", "1", "3.33", "0"], "ans": "1", "diff": "easy",
             "exp": "% is modulo (remainder). 10 ÷ 3 = 3 remainder 1."},
            {"slug": "operators", "text": "What does `2 ** 3` evaluate to?",
             "opts": ["6", "8", "9", "5"], "ans": "1", "diff": "easy",
             "exp": "** is exponentiation. 2³ = 8."},
            {"slug": "operators", "text": "Which operator checks 'not equal' in Python?",
             "opts": ["<>", "!=", "=/=", "not =="], "ans": "1", "diff": "easy",
             "exp": "!= is the not-equal operator. <> was removed in Python 3."},

            # --- Conditions (3 q) ---
            {"slug": "conditions",
             "text": "What will print?\n```python\nx = 10\nif x > 5:\n    print('A')\nelif x > 8:\n    print('B')\nelse:\n    print('C')\n```",
             "opts": ["A", "B", "C", "AB"], "ans": "0", "diff": "easy",
             "exp": "Python stops at the first True condition. x > 5 is True, so 'A' prints and elif is skipped."},
            {"slug": "conditions", "text": "Which keyword is Python's 'else if'?",
             "opts": ["else if", "elseif", "elif", "or if"], "ans": "2", "diff": "easy",
             "exp": "Python uses 'elif' (not 'else if') for additional conditions."},
            {"slug": "conditions", "text": "What does `True and False` evaluate to?",
             "opts": ["True", "False", "None", "Error"], "ans": "1", "diff": "easy",
             "exp": "'and' requires BOTH sides to be True. True and False = False."},

            # --- Loops (3 q) ---
            {"slug": "loops",
             "text": "How many times does this loop execute?\n```python\nfor i in range(3, 10, 2):\n    pass\n```",
             "opts": ["7", "4", "3", "5"], "ans": "1", "diff": "medium",
             "exp": "range(3, 10, 2) generates 3, 5, 7, 9 — four values."},
            {"slug": "loops", "text": "Which keyword skips the rest of the current loop iteration?",
             "opts": ["skip", "break", "continue", "pass"], "ans": "2", "diff": "easy",
             "exp": "'continue' moves to the next iteration. 'break' exits the loop entirely."},
            {"slug": "loops",
             "text": "What will this print?\n```python\nfor i in range(4):\n    if i == 2:\n        break\n    print(i)\n```",
             "opts": ["0 1 2 3", "0 1", "0 1 3", "1 2"], "ans": "1", "diff": "medium",
             "exp": "0 and 1 are printed; when i==2, break exits the loop before printing 2."},

            # --- Functions (3 q) ---
            {"slug": "functions", "text": "What does a function return if it has no `return` statement?",
             "opts": ["0", "False", "None", "Error"], "ans": "2", "diff": "easy",
             "exp": "Functions without a return statement implicitly return None."},
            {"slug": "functions",
             "text": "What is the output?\n```python\ndef add(a, b=10):\n    return a + b\nprint(add(5))\n```",
             "opts": ["5", "10", "15", "Error"], "ans": "2", "diff": "medium",
             "exp": "b defaults to 10. add(5) → 5 + 10 = 15."},
            {"slug": "functions", "text": "Which keyword defines a function in Python?",
             "opts": ["func", "function", "define", "def"], "ans": "3", "diff": "easy",
             "exp": "Python uses 'def' to define functions."},

            # --- Lists (3 q) ---
            {"slug": "lists",
             "text": "What does this print?\n```python\nmy_list = [1, 2, 3, 4, 5]\nprint(my_list[-2])\n```",
             "opts": ["4", "5", "2", "Error"], "ans": "0", "diff": "medium",
             "exp": "Negative indexing counts from the end. -1=5, -2=4."},
            {"slug": "lists", "text": "Which method adds an element to the END of a list?",
             "opts": ["list.add()", "list.insert()", "list.append()", "list.push()"], "ans": "2", "diff": "easy",
             "exp": ".append() adds to the end. .insert(index, val) adds at a specific position."},
            {"slug": "lists", "text": "What does `[1, 2, 3][1:3]` return?",
             "opts": ["[1, 2]", "[2, 3]", "[1, 2, 3]", "[2]"], "ans": "1", "diff": "medium",
             "exp": "Slicing [1:3] returns index 1 and 2 (not including 3): [2, 3]."},

            # --- OOP (3 q) ---
            {"slug": "oop", "text": "What is the purpose of `__init__` in a Python class?",
             "opts": ["To delete the object", "To initialise the object's attributes when it's created",
                      "To define class methods", "To inherit from another class"], "ans": "1", "diff": "medium",
             "exp": "__init__ is the constructor — runs automatically when an instance is created."},
            {"slug": "oop", "text": "What does `self` refer to in a class method?",
             "opts": ["The class itself", "The current instance (object)", "The parent class", "A static variable"],
             "ans": "1", "diff": "medium",
             "exp": "'self' refers to the specific instance calling the method."},
            {"slug": "oop", "text": "Which OOP concept allows a class to use properties/methods of another class?",
             "opts": ["Polymorphism", "Encapsulation", "Inheritance", "Abstraction"], "ans": "2", "diff": "medium",
             "exp": "Inheritance lets a child class reuse attributes and methods from a parent class."},

            # --- Error Handling (2 q) ---
            {"slug": "error-handling", "text": "Which block always executes regardless of whether an exception occurred?",
             "opts": ["try", "except", "else", "finally"], "ans": "3", "diff": "medium",
             "exp": "The 'finally' block always runs — used for cleanup (e.g., closing files)."},
            {"slug": "error-handling", "text": "What exception is raised when accessing a missing dictionary key?",
             "opts": ["ValueError", "IndexError", "KeyError", "TypeError"], "ans": "2", "diff": "medium",
             "exp": "KeyError is raised for missing dict keys. Use .get() to avoid it."},

            # --- Dictionaries (1 q) ---
            {"slug": "dictionaries",
             "text": "What is the output?\n```python\nd = {'a': 1, 'b': 2}\nprint(d.get('c', 0))\n```",
             "opts": ["None", "Error", "0", "c"], "ans": "2", "diff": "medium",
             "exp": ".get(key, default) returns default (0) when key 'c' doesn't exist."},

            # --- Comprehensions (1 q) ---
            {"slug": "comprehensions", "text": "What does `[x**2 for x in range(4)]` evaluate to?",
             "opts": ["[1, 4, 9, 16]", "[0, 1, 4, 9]", "[0, 2, 4, 6]", "[0, 1, 2, 3]"], "ans": "1", "diff": "medium",
             "exp": "range(4) → 0,1,2,3. Squaring: 0,1,4,9."},
        ]

        for qd in qs:
            topic = topics.get(qd["slug"])
            if not topic:
                continue
            db.add(Question(
                topic_id=topic.id,
                text=qd["text"],
                question_type="mcq",
                options=qd["opts"],
                correct_answer=qd["ans"],
                difficulty=qd["diff"],
                explanation=qd["exp"],
            ))

        # ── Practice Problems ─────────────────────────────────────────────────
        problems = [
            {
                "slug": "variables",
                "title": "Temperature Converter",
                "desc": """Write a function `celsius_to_fahrenheit(celsius)` that converts Celsius to Fahrenheit.

**Formula:** `F = (C × 9/5) + 32`

**Examples:**
- `celsius_to_fahrenheit(0)` → `32.0`
- `celsius_to_fahrenheit(100)` → `212.0`
- `celsius_to_fahrenheit(-40)` → `-40.0`""",
                "diff": "easy",
                "starter": "def celsius_to_fahrenheit(celsius):\n    # Write your formula here\n    pass",
                "cases": [
                    {"call": "celsius_to_fahrenheit(0)",   "expected_output": "32.0",  "description": "0°C = 32°F"},
                    {"call": "celsius_to_fahrenheit(100)", "expected_output": "212.0", "description": "100°C = 212°F"},
                    {"call": "celsius_to_fahrenheit(-40)", "expected_output": "-40.0", "description": "-40°C = -40°F"},
                ],
                "hints": ["Use the formula: F = (C * 9/5) + 32", "Make sure to return a float", "Multiply by 9 then divide by 5"],
            },
            {
                "slug": "conditions",
                "title": "Grade Calculator",
                "desc": """Write a function `get_grade(score)` that returns the letter grade:
- 90–100 → `'A'`
- 80–89  → `'B'`
- 70–79  → `'C'`
- 60–69  → `'D'`
- Below 60 → `'F'`""",
                "diff": "easy",
                "starter": "def get_grade(score):\n    # Use if/elif/else\n    pass",
                "cases": [
                    {"call": "get_grade(95)", "expected_output": "A", "description": "95 → A"},
                    {"call": "get_grade(85)", "expected_output": "B", "description": "85 → B"},
                    {"call": "get_grade(72)", "expected_output": "C", "description": "72 → C"},
                    {"call": "get_grade(55)", "expected_output": "F", "description": "55 → F"},
                ],
                "hints": ["Check from highest to lowest", "Use if score >= 90:", "Return the letter as a string 'A'"],
            },
            {
                "slug": "loops",
                "title": "FizzBuzz",
                "desc": """Write a function `fizzbuzz(n)` that returns a list of strings from 1 to n:
- Divisible by 3 → `"Fizz"`
- Divisible by 5 → `"Buzz"`
- Divisible by both 3 and 5 → `"FizzBuzz"`
- Otherwise → the number as a string

**Example:** `fizzbuzz(5)` → `['1', '2', 'Fizz', '4', 'Buzz']`""",
                "diff": "easy",
                "starter": "def fizzbuzz(n):\n    result = []\n    for i in range(1, n + 1):\n        # Add your logic here\n        pass\n    return result",
                "cases": [
                    {"call": "fizzbuzz(5)",  "expected_output": "['1', '2', 'Fizz', '4', 'Buzz']", "description": "FizzBuzz to 5"},
                    {"call": "fizzbuzz(15)", "expected_output": "['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']", "description": "FizzBuzz to 15"},
                ],
                "hints": ["Check divisibility by 15 (3 and 5) FIRST", "Use % (modulo) for divisibility", "Append strings to result list"],
            },
            {
                "slug": "functions",
                "title": "Palindrome Checker",
                "desc": """Write a function `is_palindrome(text)` that returns `True` if the text reads the same forwards and backwards (ignore case and spaces), `False` otherwise.

**Examples:**
- `is_palindrome("racecar")` → `True`
- `is_palindrome("hello")` → `False`
- `is_palindrome("A man a plan a canal Panama")` → `True`""",
                "diff": "easy",
                "starter": "def is_palindrome(text):\n    # Hint: clean the text, then compare with its reverse\n    pass",
                "cases": [
                    {"call": "is_palindrome('racecar')", "expected_output": "True",  "description": "Simple palindrome"},
                    {"call": "is_palindrome('hello')",   "expected_output": "False", "description": "Not a palindrome"},
                    {"call": "is_palindrome('A man a plan a canal Panama')", "expected_output": "True", "description": "Palindrome with spaces"},
                ],
                "hints": ["Use .lower() then .replace(' ', '')", "Python reverses strings with [::-1]", "Compare cleaned == cleaned[::-1]"],
            },
            {
                "slug": "lists",
                "title": "List Statistics",
                "desc": """Write a function `list_stats(numbers)` that returns a dictionary:
- `"min"`: minimum value
- `"max"`: maximum value
- `"sum"`: sum of all values
- `"avg"`: average rounded to 2 decimal places

**Example:** `list_stats([1, 2, 3, 4, 5])` → `{'min': 1, 'max': 5, 'sum': 15, 'avg': 3.0}`""",
                "diff": "medium",
                "starter": "def list_stats(numbers):\n    # Return a dict with min, max, sum, avg\n    pass",
                "cases": [
                    {"call": "list_stats([1, 2, 3, 4, 5])", "expected_output": "{'min': 1, 'max': 5, 'sum': 15, 'avg': 3.0}", "description": "Basic stats"},
                    {"call": "list_stats([10, 20, 30])",     "expected_output": "{'min': 10, 'max': 30, 'sum': 60, 'avg': 20.0}", "description": "Three numbers"},
                ],
                "hints": ["Use built-ins: min(), max(), sum(), len()", "avg = sum / len", "round(value, 2) for 2 decimal places"],
            },
            {
                "slug": "dictionaries",
                "title": "Word Frequency Counter",
                "desc": """Write a function `word_frequency(text)` that counts how often each word appears (case-insensitive, split by spaces).

**Example:** `word_frequency("the cat sat on the mat")` → `{'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}`""",
                "diff": "medium",
                "starter": "def word_frequency(text):\n    # Count word occurrences\n    pass",
                "cases": [
                    {"call": "word_frequency('the cat sat on the mat')", "expected_output": "{'the': 2, 'cat': 1, 'sat': 1, 'on': 1, 'mat': 1}", "description": "Basic word count"},
                    {"call": "word_frequency('hello hello hello')",       "expected_output": "{'hello': 3}", "description": "Repeated word"},
                ],
                "hints": ["Use .lower() and .split()", "Loop and use dict.get(word, 0) + 1", "Build result dict incrementally"],
            },
            {
                "slug": "comprehensions",
                "title": "Even Squares",
                "desc": """Write a function `even_squares(n)` that returns a list of squares of even numbers from 0 to n (inclusive).

**Example:** `even_squares(10)` → `[0, 4, 16, 36, 64, 100]`""",
                "diff": "medium",
                "starter": "def even_squares(n):\n    # Use a list comprehension with a condition\n    pass",
                "cases": [
                    {"call": "even_squares(10)", "expected_output": "[0, 4, 16, 36, 64, 100]", "description": "Even squares to 10"},
                    {"call": "even_squares(6)",  "expected_output": "[0, 4, 16, 36]",           "description": "Even squares to 6"},
                ],
                "hints": ["[expr for x in range(...) if condition]", "Even check: x % 2 == 0", "Square: x ** 2"],
            },
            {
                "slug": "error-handling",
                "title": "Safe Division",
                "desc": """Write a function `safe_divide(a, b)` that:
- Returns `a / b` as a float if valid
- Returns `"Cannot divide by zero"` if b is 0
- Returns `"Invalid input"` if inputs are not numbers""",
                "diff": "medium",
                "starter": "def safe_divide(a, b):\n    # Use try/except\n    pass",
                "cases": [
                    {"call": "safe_divide(10, 2)",   "expected_output": "5.0",                   "description": "Normal division"},
                    {"call": "safe_divide(10, 0)",   "expected_output": "Cannot divide by zero", "description": "Division by zero"},
                    {"call": "safe_divide('x', 2)", "expected_output": "Invalid input",          "description": "Invalid input"},
                ],
                "hints": ["Catch ZeroDivisionError for zero", "Catch TypeError for non-numbers", "Use try/except/except"],
            },
            {
                "slug": "oop",
                "title": "Bank Account Class",
                "desc": """Create a `BankAccount` class with:
- Constructor: `__init__(self, owner, balance=0)`
- `deposit(amount)`: add to balance, return new balance
- `withdraw(amount)`: subtract if sufficient funds, else return `"Insufficient funds"`
- `get_balance()`: return current balance""",
                "diff": "medium",
                "starter": "class BankAccount:\n    def __init__(self, owner, balance=0):\n        pass\n\n    def deposit(self, amount):\n        pass\n\n    def withdraw(self, amount):\n        pass\n\n    def get_balance(self):\n        pass",
                "cases": [
                    {"call": "BankAccount('Alice', 100).deposit(50)",   "expected_output": "150",                  "description": "Deposit"},
                    {"call": "BankAccount('Bob', 200).withdraw(200)",   "expected_output": "0",                    "description": "Withdraw full"},
                    {"call": "BankAccount('Carol', 50).withdraw(100)",  "expected_output": "Insufficient funds",   "description": "Insufficient funds"},
                    {"call": "BankAccount('Dave', 300).get_balance()",  "expected_output": "300",                  "description": "Get balance"},
                ],
                "hints": ["Store balance with self.balance", "Check amount <= self.balance before withdrawing", "Return the new balance from deposit/withdraw"],
            },
        ]

        for pd in problems:
            topic = topics.get(pd["slug"])
            if not topic:
                continue
            db.add(PracticeProblem(
                topic_id=topic.id,
                title=pd["title"],
                description=pd["desc"],
                difficulty=pd["diff"],
                starter_code=pd["starter"],
                test_cases=pd["cases"],
                hints=pd["hints"],
            ))

        # ── Admin user ────────────────────────────────────────────────────────
        if not db.query(User).filter(User.role == "admin").first():
            db.add(User(
                username="admin",
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin",
            ))
            print(f"[SEED] Admin created  -->  username: admin  |  password: {settings.ADMIN_PASSWORD}")

        db.commit()
        print(f"[SEED] DONE: Seeded {len(topics_data)} topics, {len(qs)} questions, {len(problems)} problems.")

        # Seed demo students
        seed_demo_students(db)

    except Exception as exc:
        db.rollback()
        print(f"[SEED] ERROR: {exc}")
        raise
    finally:
        db.close()


def seed_demo_students(db=None):
    """Seed realistic student accounts with assessment, practice submissions and chat history."""
    close_when_done = False
    if db is None:
        db = SessionLocal()
        close_when_done = True

    try:
        topics = {t.slug: t for t in db.query(Topic).all()}
        all_topics_ordered = db.query(Topic).order_by(Topic.order).all()
        problems = {p.title: p for p in db.query(PracticeProblem).all()}
        default_pwd = get_password_hash("student123")

        demo_students = [
            {
                "username": "priya_beginner",
                "email": "priya@example.com",
                "skill_level": "beginner",
                "score": 42.0,
                "topic_scores": {"variables": 80.0, "operators": 60.0, "conditions": 40.0, "loops": 20.0},
                "submissions": [
                    {
                        "title": "Sum of Two Numbers",
                        "code": "def add(a, b):\n    return a + b\n",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "All test cases passed! Clean and correct.",
                    },
                    {
                        "title": "Even or Odd",
                        "code": "def is_even(n):\n    if n % 2 == 0:\n        return True\n    return False\n",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Great job! Clean conditional logic.",
                    },
                ],
                "chat": {
                    "title": "Help with Variables & Types",
                    "messages": [
                        ("user", "Hi PyMentor! I am confused about the difference between integer and float in Python."),
                        ("assistant", "Hello Priya! Great question.\n\nAn **integer (`int`)** represents a whole number without any fractional or decimal parts (e.g., `5`, `-12`, `0`).\nA **float (`float`)** represents a real number that includes a decimal point (e.g., `3.14`, `0.5`, `-2.0`).\n\n```python\nx = 10     # int\ny = 10.0   # float\nprint(type(x), type(y))\n```\nTry checking what happens when you divide `7 / 2` in Python!"),
                        ("user", "It gave me 3.5 which is a float! Thank you!"),
                        ("assistant", "Spot on! That's Python's true division operator `/`. Keep up the curious mindset!"),
                    ],
                },
            },
            {
                "username": "rahul_intermediate",
                "email": "rahul@example.com",
                "skill_level": "intermediate",
                "score": 68.0,
                "topic_scores": {"variables": 90.0, "operators": 85.0, "conditions": 80.0, "loops": 70.0, "functions": 65.0, "lists": 60.0},
                "submissions": [
                    {
                        "title": "Sum of Two Numbers",
                        "code": "def add(a, b):\n    return a + b",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Perfect solution.",
                    },
                    {
                        "title": "Find Maximum of Three",
                        "code": "def max_of_three(a, b, c):\n    return max(a, b, c)",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Pythonic and clean use of max()!",
                    },
                    {
                        "title": "Count Vowels",
                        "code": "def count_vowels(s):\n    vowels = 'aeiouAEIOU'\n    count = 0\n    for char in s:\n        if char in vowels:\n            count += 1\n    return count",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Excellent iteration and condition checking.",
                    },
                    {
                        "title": "Reverse a String",
                        "code": "def reverse_string(s):\n    return s[::-1]",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Masterful slice notation!",
                    },
                ],
                "chat": {
                    "title": "List Comprehensions Optimization",
                    "messages": [
                        ("user", "Can you explain how list comprehensions are faster than regular for loops?"),
                        ("assistant", "Hi Rahul! List comprehensions are often faster because their loop bytecode is executed at C speed inside the Python interpreter without repeatedly calling the `list.append()` method bytecode overhead.\n\nCompare:\n```python\n# Traditional loop\nsquares = []\nfor x in range(10):\n    squares.append(x * x)\n\n# List comprehension\nsquares = [x * x for x in range(10)]\n```\nBeyond speed, they make your intentions expressive and compact when transforming data!"),
                    ],
                },
            },
            {
                "username": "ananya_advanced",
                "email": "ananya@example.com",
                "skill_level": "advanced",
                "score": 92.0,
                "topic_scores": {"variables": 100.0, "operators": 100.0, "conditions": 100.0, "loops": 95.0, "functions": 95.0, "lists": 90.0, "dictionaries": 90.0, "strings": 85.0},
                "submissions": [
                    {
                        "title": "Sum of Two Numbers",
                        "code": "def add(a: int, b: int) -> int:\n    return a + b",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Excellent with type annotations.",
                    },
                    {
                        "title": "Find Maximum of Three",
                        "code": "def max_of_three(a, b, c):\n    return max(a, b, c)",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Optimal.",
                    },
                    {
                        "title": "Count Vowels",
                        "code": "def count_vowels(s: str) -> int:\n    return sum(1 for c in s.lower() if c in 'aeiou')",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Superb generator comprehension!",
                    },
                    {
                        "title": "Reverse a String",
                        "code": "def reverse_string(s):\n    return s[::-1]",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Perfect.",
                    },
                    {
                        "title": "Bank Account Class",
                        "code": "class BankAccount:\n    def __init__(self, owner: str, balance: float = 0.0):\n        self.owner = owner\n        self.balance = balance\n\n    def deposit(self, amount: float):\n        self.balance += amount\n        return self.balance\n\n    def withdraw(self, amount: float):\n        if amount > self.balance:\n            return 'Insufficient funds'\n        self.balance -= amount\n        return self.balance\n\n    def get_balance(self):\n        return self.balance",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Flawless OOP implementation with state encapsulation.",
                    },
                ],
                "chat": {
                    "title": "Clean OOP Encapsulation",
                    "messages": [
                        ("user", "How should private variables and getters/setters be designed in Pythonic code?"),
                        ("assistant", "Hello Ananya! In Python, we adhere to 'we are all consenting adults here'. Rather than traditional Java-style getters/setters, the standard approach is the `@property` decorator:\n\n```python\nclass Student:\n    def __init__(self, score: float):\n        self._score = score  # internal convention\n\n    @property\n    def score(self) -> float:\n        return self._score\n\n    @score.setter\n    def score(self, value: float):\n        if not 0 <= value <= 100:\n            raise ValueError('Score must be between 0 and 100')\n        self._score = value\n```\nThis preserves clean dot notation (`student.score = 95`) while providing encapsulation!"),
                    ],
                },
            },
            {
                "username": "vikram_code",
                "email": "vikram@example.com",
                "skill_level": "beginner",
                "score": 46.0,
                "topic_scores": {"variables": 65.0, "operators": 55.0, "conditions": 40.0, "loops": 25.0},
                "submissions": [
                    {
                        "title": "Sum of Two Numbers",
                        "code": "def add(a, b):\n    return a + b\n",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "Passed all test cases.",
                    },
                    {
                        "title": "Even or Odd",
                        "code": "def is_even(n):\n    # bug: flipped return values\n    if n % 2 != 0:\n        return True\n    return False",
                        "score": 0.0,
                        "passed": 0,
                        "total": 4,
                        "feedback": "Test cases failed. Odd numbers are returning True.",
                    },
                    {
                        "title": "Countdown Timer",
                        "code": "def countdown(n):\n    res = []\n    while n > 0:\n        res.append(n)\n        n -= 1\n    return res",
                        "score": 100.0,
                        "passed": 4,
                        "total": 4,
                        "feedback": "All test cases passed after fixing decrement.",
                    },
                ],
                "chat": {
                    "title": "Debugging Infinite Loops",
                    "messages": [
                        ("user", "My while loop keeps freezing the browser or timing out. How do I fix it?"),
                        ("assistant", "Hey Vikram! A while loop runs continuously as long as its condition evaluates to `True`. If your loop condition is `while n > 0:`, but you never decrease `n` inside the loop body, `n` will stay positive forever!\n\nChecklist to prevent infinite loops:\n1. Make sure the variable tested in the condition changes inside the loop body (e.g. `n -= 1`).\n2. Have a clear exit condition.\n3. Test with small numbers first!"),
                    ],
                },
            },
        ]

        created_count = 0
        for s in demo_students:
            existing = db.query(User).filter(User.username == s["username"]).first()
            if existing:
                continue

            user = User(
                username=s["username"],
                email=s["email"],
                hashed_password=default_pwd,
                role="student",
                is_active=True,
            )
            db.add(user)
            db.flush()

            attempt = AssessmentAttempt(
                user_id=user.id,
                score=s["score"],
                skill_level=s["skill_level"],
                topic_scores=s["topic_scores"],
                answers={},
            )
            db.add(attempt)

            topic_ids = [t.id for t in all_topics_ordered]
            lp = LearningPath(
                user_id=user.id,
                skill_level=s["skill_level"],
                topic_order=topic_ids,
                current_topic_id=topic_ids[0] if topic_ids else None,
            )
            db.add(lp)

            for t in all_topics_ordered:
                mastery = s["topic_scores"].get(t.slug, 30.0 if s["skill_level"] == "advanced" else 0.0)
                status = "completed" if mastery >= 70.0 else ("available" if mastery > 0 else "locked")
                db.add(StudentKnowledge(
                    user_id=user.id,
                    topic_id=t.id,
                    mastery_score=mastery,
                    attempts=2 if mastery > 0 else 0,
                    correct_count=1 if mastery >= 50 else 0,
                    status=status,
                ))

            for sub_data in s["submissions"]:
                prob = problems.get(sub_data["title"])
                if prob:
                    sub = PracticeSubmission(
                        user_id=user.id,
                        problem_id=prob.id,
                        code=sub_data["code"],
                        passed_cases=sub_data["passed"],
                        total_cases=sub_data["total"],
                        score=sub_data["score"],
                        feedback=sub_data["feedback"],
                    )
                    db.add(sub)

            chat_data = s["chat"]
            session = MentorSession(user_id=user.id, title=chat_data["title"])
            db.add(session)
            db.flush()

            for role, content in chat_data["messages"]:
                db.add(MentorMessage(session_id=session.id, role=role, content=content))

            created_count += 1

        db.commit()
        print(f"[SEED] Successfully seeded {created_count} demo student accounts!")
        return created_count

    except Exception as e:
        db.rollback()
        print(f"[SEED] Error seeding demo students: {e}")
        return 0
    finally:
        if close_when_done:
            db.close()


if __name__ == "__main__":
    seed()

