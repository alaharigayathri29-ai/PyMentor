"""
Structured Python Curriculum Data (7 Modules)
Inspired by BYJU'S (engaging, visual, step-by-step) and ByteXL (rigorous, industry-oriented).

Module 1: Python Fundamentals
Module 2: Control Flow
Module 3: Data Structures
Module 4: Functions
Module 5: Object-Oriented Programming
Module 6: Advanced Python
Module 7: Practical Python
"""

CURRICULUM_MODULES = [
    {
        "module_number": 1,
        "module_name": "Python Fundamentals",
        "description": "Master core syntax, variables, data types, console I/O, type conversion, and operators.",
        "icon": "🌱",
        "topics": [
            {
                "slug": "variables",
                "name": "Variables & Data Types",
                "order": 1,
                "difficulty": "beginner",
                "icon": "📦",
                "subtopics": [
                    "Introduction to Python",
                    "Variables and Memory Allocation",
                    "Primitive Data Types (int, float, str, bool)",
                    "Console Input and Output",
                    "Type Casting and Type Conversion"
                ],
                "learning_objectives": [
                    "Understand how Python stores and manages variables in memory",
                    "Identify and utilize primitive data types: int, float, str, bool",
                    "Use input() and print() with formatted strings (f-strings)",
                    "Safely cast values between types using int(), float(), and str()"
                ],
                "lesson_content": {
                    "introduction": "In Python, variables are symbolic names that act as references or pointers to objects stored in memory. Unlike statically typed languages like C++ or Java, Python is dynamically typed—you do not need to explicitly declare data types.",
                    "explanation": "### 1. Variables and Assignment\nA variable is created the moment you first assign a value to it using the assignment operator (`=`):\n\n```python\nstudent_name = 'Alex'\nstudent_age = 20\ngpa = 3.85\nis_enrolled = True\n```\n\n### 2. Built-in Primitive Types\n- **int**: Whole numbers like `42`, `-7`, `0`\n- **float**: Numbers with fractional parts like `3.14159`, `-0.01`\n- **str**: Ordered sequence of Unicode characters enclosed in single or double quotes\n- **bool**: Boolean truth values: `True` or `False`\n\n### 3. Dynamic Typing & Inspection\nYou can check any variable's data type at runtime using `type()` and its memory identity using `id()`.",
                    "code_examples": [
                        {
                            "title": "Declaring Variables and Checking Types",
                            "code": "name = 'PyMentor'\nage = 5\nrating = 4.9\nis_awesome = True\n\nprint(f'{name} is {type(name).__name__}')\nprint(f'{age} is {type(age).__name__}')\nprint(f'{rating} is {type(rating).__name__}')\nprint(f'{is_awesome} is {type(is_awesome).__name__}')",
                            "explanation": "Using f-strings (formatted string literals) to dynamically interpolate expressions and display their runtime type names.",
                            "expected_output": "PyMentor is str\n5 is int\n4.9 is float\nTrue is bool"
                        },
                        {
                            "title": "Type Casting and User Input",
                            "code": "raw_input = '42'\nnumber = int(raw_input)\npi_val = float('3.14')\n\nprint(f'Converted int: {number}, double: {number * 2}')\nprint(f'Converted float: {pi_val}, squared: {round(pi_val ** 2, 4)}')",
                            "explanation": "Converting strings into numeric types for mathematical calculations.",
                            "expected_output": "Converted int: 42, double: 84\nConverted float: 3.14, squared: 9.8596"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the output of type(10 / 2) in Python 3?",
                            "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'number'>"],
                            "correct_answer": 1,
                            "explanation": "In Python 3, division (/) always returns a float, even if the division is exact (10 / 2 = 5.0). Use // for integer floor division."
                        },
                        {
                            "id": 2,
                            "question": "Which of the following is an invalid variable name in Python?",
                            "options": ["_counter", "student_2", "2nd_student", "studentName"],
                            "correct_answer": 2,
                            "explanation": "Variable names cannot start with a digit. They must start with a letter or an underscore."
                        }
                    ],
                    "practical_challenge": {
                        "prompt": "Create a program that calculates the area and perimeter of a rectangle given its width and height.",
                        "starter_code": "def rectangle_properties(width, height):\n    # Return a dictionary with 'area' and 'perimeter'\n    pass",
                        "test_call": "rectangle_properties(5, 10)",
                        "expected": "{'area': 50, 'perimeter': 30}"
                    }
                }
            },
            {
                "slug": "operators",
                "name": "Operators & Expressions",
                "order": 2,
                "difficulty": "beginner",
                "icon": "🧮",
                "subtopics": [
                    "Arithmetic Operators (+, -, *, /, //, %, **)",
                    "Comparison Operators (==, !=, <, >, <=, >=)",
                    "Logical Operators (and, or, not)",
                    "Bitwise and Assignment Operators",
                    "Operator Precedence (PEMDAS)"
                ],
                "learning_objectives": [
                    "Master all arithmetic operators including floor division and exponentiation",
                    "Evaluate complex logical expressions using short-circuit evaluation",
                    "Understand operator precedence to write unambiguous expressions"
                ],
                "lesson_content": {
                    "introduction": "Operators are special tokens that represent computations like addition, multiplication, and comparison. Values that an operator acts on are called operands.",
                    "explanation": "### 1. Arithmetic Operators\n- `+`, `-`, `*`: Basic math\n- `/`: True float division (e.g. `7 / 2 = 3.5`)\n- `//`: Floor division, rounds towards negative infinity (e.g. `7 // 2 = 3`)\n- `%`: Modulo (remainder, e.g. `7 % 2 = 1`)\n- `**`: Exponentiation (e.g. `2 ** 4 = 16`)\n\n### 2. Logical Operators & Short-circuiting\nPython uses words: `and`, `or`, `not`.\n- `a and b`: Evaluates `b` only if `a` is truthy.\n- `a or b`: Evaluates `b` only if `a` is falsy.",
                    "code_examples": [
                        {
                            "title": "Arithmetic & Floor Division",
                            "code": "a = 17\nb = 5\nprint(f'{a} / {b} = {a / b}')\nprint(f'{a} // {b} = {a // b}')\nprint(f'{a} % {b} = {a % b}')\nprint(f'2 ** 5 = {2 ** 5}')",
                            "explanation": "Demonstrates true division, integer floor division, remainder, and exponentiation.",
                            "expected_output": "17 / 5 = 3.4\n17 // 5 = 3\n17 % 5 = 2\n2 ** 5 = 32"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the value of 3 + 2 * 2 ** 2?",
                            "options": ["20", "11", "19", "16"],
                            "correct_answer": 1,
                            "explanation": "By precedence: 2 ** 2 = 4, then 2 * 4 = 8, then 3 + 8 = 11."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 2,
        "module_name": "Control Flow",
        "description": "Direct program execution using decisions, branching, and iterative loops.",
        "icon": "🔄",
        "topics": [
            {
                "slug": "conditions",
                "name": "Conditional Statements",
                "order": 3,
                "difficulty": "beginner",
                "icon": "🔀",
                "subtopics": [
                    "if, elif, and else statements",
                    "Nested conditions",
                    "Ternary conditional expressions",
                    "Truthiness and falsiness of objects"
                ],
                "learning_objectives": [
                    "Construct branched decision trees with if/elif/else",
                    "Avoid deep nesting using guard clauses",
                    "Leverage Python's truth value testing (falsy: 0, None, '', [], {})"
                ],
                "lesson_content": {
                    "introduction": "Conditional statements allow your program to make decisions and execute different blocks of code depending on whether a given boolean condition evaluates to True or False.",
                    "explanation": "### Conditional Syntax\n```python\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelse:\n    grade = 'C'\n```\n\n### Ternary Expression\n`status = 'Adult' if age >= 18 else 'Minor'`",
                    "code_examples": [
                        {
                            "title": "Guard Clause Example",
                            "code": "def process_payment(amount, balance):\n    if amount <= 0:\n        return 'Error: Invalid amount'\n    if amount > balance:\n        return 'Error: Insufficient funds'\n    return f'Success! Remaining: ${balance - amount}'\n\nprint(process_payment(50, 120))\nprint(process_payment(200, 120))",
                            "explanation": "Using early returns (guard clauses) to cleanly handle invalid states before main business logic.",
                            "expected_output": "Success! Remaining: $70\nError: Insufficient funds"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Which of these evaluates to False in a boolean context?",
                            "options": ["'False'", "[]", "[-1]", "0.1"],
                            "correct_answer": 1,
                            "explanation": "An empty list [] is falsy in Python. Non-empty collections and strings are truthy."
                        }
                    ]
                }
            },
            {
                "slug": "loops",
                "name": "Loops & Iterations",
                "order": 4,
                "difficulty": "beginner",
                "icon": "🔁",
                "subtopics": [
                    "for loops with range()",
                    "Iterating over sequences",
                    "while loops and loop conditions",
                    "break and continue control flow",
                    "for-else and while-else construct"
                ],
                "learning_objectives": [
                    "Iterate over numeric ranges with range(start, stop, step)",
                    "Control loop execution with break and continue",
                    "Understand loop invariants and avoid infinite while loops"
                ],
                "lesson_content": {
                    "introduction": "Loops allow repeated execution of statements. Python features `for` loops (for definite iteration over iterables) and `while` loops (for indefinite iteration until a condition becomes false).",
                    "explanation": "### 1. The for loop\nIterates over elements in any iterable (list, string, range, etc.):\n```python\nfor i in range(1, 6, 2):  # start=1, stop=6, step=2\n    print(i)             # prints 1, 3, 5\n```\n\n### 2. The while loop\nRepeats as long as its condition remains True:\n```python\ncount = 3\nwhile count > 0:\n    print(count)\n    count -= 1\n```",
                    "code_examples": [
                        {
                            "title": "Break and Continue in Action",
                            "code": "evens = []\nfor n in range(1, 10):\n    if n % 2 != 0:\n        continue\n    evens.append(n)\nprint('Even numbers:', evens)",
                            "explanation": "Skipping odd numbers using continue.",
                            "expected_output": "Even numbers: [2, 4, 6, 8]"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "How many numbers are produced by range(2, 10, 3)?",
                            "options": ["3", "4", "2", "8"],
                            "correct_answer": 0,
                            "explanation": "range(2, 10, 3) produces 2, 5, 8. That is exactly 3 numbers."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 3,
        "module_name": "Data Structures",
        "description": "Harness Python's versatile collection types: lists, tuples, sets, and dictionaries.",
        "icon": "📚",
        "topics": [
            {
                "slug": "strings",
                "name": "String Operations",
                "order": 5,
                "difficulty": "beginner",
                "icon": "✍️",
                "subtopics": [
                    "String indexing and slicing [start:stop:step]",
                    "String immutability and memory",
                    "Useful methods: split(), join(), strip(), replace()",
                    "Formatted string literals (f-strings)"
                ],
                "learning_objectives": [
                    "Slice strings forwards and backwards using negative indices",
                    "Perform efficient tokenization and concatenation using split() and join()",
                    "Format dates, floats, and alignments with f-strings"
                ],
                "lesson_content": {
                    "introduction": "Strings in Python are immutable sequences of characters. Once created, they cannot be modified in-place; all operations return a new string.",
                    "explanation": "### Slicing Syntax\n`s[start:stop:step]`\n- `s[::-1]` reverses a string.\n- `s[2:6]` gets characters from index 2 up to 5.",
                    "code_examples": [
                        {
                            "title": "String Slicing and Methods",
                            "code": "msg = '  python programming is fun!  '\ncleaned = msg.strip().title()\nprint('Cleaned:', cleaned)\nwords = cleaned.split()\nprint('Reversed words:', ' '.join(reversed(words)))",
                            "explanation": "Combining string cleaning, splitting into lists, and joining back with delimiters.",
                            "expected_output": "Cleaned: Python Programming Is Fun!\nReversed words: Fun! Is Programming Python"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the output of 'Python'[1:4]?",
                            "options": ["'Pyt'", "'yth'", "'ytho'", "'Pyth'"],
                            "correct_answer": 1,
                            "explanation": "Index 1 is 'y', 2 is 't', 3 is 'h'. Index 4 ('o') is exclusive, resulting in 'yth'."
                        }
                    ]
                }
            },
            {
                "slug": "lists",
                "name": "Lists & Tuples",
                "order": 6,
                "difficulty": "beginner",
                "icon": "📝",
                "subtopics": [
                    "List creation, indexing, appending, inserting",
                    "List mutations vs shallow copies",
                    "Tuples: immutable collections and unpacking",
                    "Sorting: list.sort() vs sorted()"
                ],
                "learning_objectives": [
                    "Differentiate between mutable lists and immutable tuples",
                    "Safely copy lists without unwanted side effects",
                    "Perform tuple unpacking and multiple variable assignment"
                ],
                "lesson_content": {
                    "introduction": "Lists are ordered, mutable sequences that can store arbitrary objects. Tuples are ordered, immutable sequences commonly used for fixed records and dictionary keys.",
                    "explanation": "### Mutability\nLists can be modified: `lst.append(x)`, `lst.pop()`, `lst[0] = val`.\nTuples cannot be changed after creation: `t = (1, 2, 3)`.",
                    "code_examples": [
                        {
                            "title": "Tuple Unpacking & List Manipulation",
                            "code": "coords = (10, 20, 30)\nx, y, z = coords\n\nnums = [5, 2, 8, 1]\nnums.sort()\nprint(f'Unpacked: x={x}, y={y}, z={z}')\nprint(f'Sorted list: {nums}')",
                            "explanation": "Tuple unpacking and in-place list sorting.",
                            "expected_output": "Unpacked: x=10, y=20, z=30\nSorted list: [1, 2, 5, 8]"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Which operation will raise an error on a tuple t = (1, 2, 3)?",
                            "options": ["len(t)", "t[0]", "t[0] = 99", "3 in t"],
                            "correct_answer": 2,
                            "explanation": "Tuples are immutable; item assignment t[0] = 99 raises TypeError: 'tuple' object does not support item assignment."
                        }
                    ]
                }
            },
            {
                "slug": "dictionaries",
                "name": "Dictionaries & Sets",
                "order": 7,
                "difficulty": "intermediate",
                "icon": "🗄️",
                "subtopics": [
                    "Key-value mappings and hashing mechanism",
                    "Dictionary lookup, get(), keys(), values(), items()",
                    "Sets: unique elements and mathematical operations (union, intersection)",
                    "Dictionary merges and default values"
                ],
                "learning_objectives": [
                    "Leverage O(1) average-time complexity lookups using hashable keys",
                    "Use dict.get(key, default) to prevent KeyErrors",
                    "Perform set union, intersection, and difference operations"
                ],
                "lesson_content": {
                    "introduction": "Dictionaries (dict) store associative key-value pairs backed by high-performance hash tables. Sets are unordered collections of unique hashable elements.",
                    "explanation": "### Dictionary Access\n`student = {'name': 'Sara', 'score': 95}`\n`score = student.get('score', 0)` (avoids KeyError if key missing)\n\n### Set Operations\n`a | b` (union), `a & b` (intersection), `a - b` (difference)",
                    "code_examples": [
                        {
                            "title": "Word Frequency Counting with Dict",
                            "code": "words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']\ncounts = {}\nfor w in words:\n    counts[w] = counts.get(w, 0) + 1\nprint('Frequencies:', counts)",
                            "explanation": "Using dict.get() to count frequencies cleanly.",
                            "expected_output": "Frequencies: {'apple': 3, 'banana': 2, 'orange': 1}"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the result of len(set([1, 2, 2, 3, 3, 3]))?",
                            "options": ["6", "3", "1", "Error"],
                            "correct_answer": 1,
                            "explanation": "A set discards duplicates, leaving {1, 2, 3}, which has length 3."
                        }
                    ]
                }
            },
            {
                "slug": "comprehensions",
                "name": "List Comprehensions",
                "order": 8,
                "difficulty": "intermediate",
                "icon": "⚡",
                "subtopics": [
                    "List comprehension syntax [expr for item in iterable if cond]",
                    "Dictionary comprehensions {k: v for ...}",
                    "Set comprehensions",
                    "Nested comprehensions and readability guidelines"
                ],
                "learning_objectives": [
                    "Write concise, idiomatic Python transformations",
                    "Filter data efficiently inside comprehensions",
                    "Know when to use a comprehension vs a standard for-loop"
                ],
                "lesson_content": {
                    "introduction": "Comprehensions provide a concise, declarative way to construct new collections from existing iterables with optional filtering.",
                    "explanation": "### Formula\n`[expression for item in iterable if condition]`\n\nEquivalent to:\n```python\nres = []\nfor item in iterable:\n    if condition:\n        res.append(expression)\n```",
                    "code_examples": [
                        {
                            "title": "Filtering and Transforming Squares",
                            "code": "numbers = [1, 2, 3, 4, 5, 6]\neven_squares = [n ** 2 for n in numbers if n % 2 == 0]\nprint('Even squares:', even_squares)",
                            "explanation": "Constructing squares of even numbers in a single readable line.",
                            "expected_output": "Even squares: [4, 16, 36]"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What does [x * 2 for x in [1, 2, 3] if x > 1] produce?",
                            "options": ["[2, 4, 6]", "[4, 6]", "[2, 4]", "[6]"],
                            "correct_answer": 1,
                            "explanation": "Only 2 and 3 satisfy x > 1. Multiplying by 2 gives [4, 6]."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 4,
        "module_name": "Functions",
        "description": "Build reusable, modular, and maintainable software components.",
        "icon": "🧩",
        "topics": [
            {
                "slug": "functions",
                "name": "Functions & Scope",
                "order": 9,
                "difficulty": "beginner",
                "icon": "🧩",
                "subtopics": [
                    "def statement, parameters, and arguments",
                    "Positional, keyword, and default parameters",
                    "*args and **kwargs variable argument unpacking",
                    "Variable scope: LEGB rule (Local, Enclosing, Global, Built-in)",
                    "Anonymous functions: lambda expressions"
                ],
                "learning_objectives": [
                    "Design clean functions adhering to the Single Responsibility Principle",
                    "Utilize default arguments and variable-length arguments (*args, **kwargs)",
                    "Distinguish between local, enclosing, global, and built-in scopes",
                    "Write inline lambda functions for callbacks and sorting keys"
                ],
                "lesson_content": {
                    "introduction": "Functions are self-contained blocks of code that execute when called. They accept input arguments, perform calculations, and return results.",
                    "explanation": "### Defining Functions\n```python\ndef greet(name, greeting='Hello'):\n    return f'{greeting}, {name}!'\n```\n\n### The LEGB Rule\nWhen resolving a variable name, Python searches:\n1. **L**ocal (inside current function)\n2. **E**nclosing (enclosing outer functions)\n3. **G**lobal (module level)\n4. **B**uilt-in (`len`, `range`, `print`)",
                    "code_examples": [
                        {
                            "title": "Flexible Arguments with *args and **kwargs",
                            "code": "def make_summary(*items, **metadata):\n    total_count = len(items)\n    print(f'Category: {metadata.get(\"category\", \"General\")}')\n    print(f'Items ({total_count}): {list(items)}')\n\nmake_summary('Python', 'FastAPI', 'SQLite', category='Backend Tech')",
                            "explanation": "Accepting arbitrary positional items and keyword metadata.",
                            "expected_output": "Category: Backend Tech\nItems (3): ['Python', 'FastAPI', 'SQLite']"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the return value of a Python function that does not include a return statement?",
                            "options": ["0", "False", "None", "''"],
                            "correct_answer": 2,
                            "explanation": "Functions without an explicit return statement implicitly return None."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 5,
        "module_name": "Object-Oriented Programming",
        "description": "Model complex domains using classes, inheritance, encapsulation, and polymorphism.",
        "icon": "🏗️",
        "topics": [
            {
                "slug": "oop",
                "name": "Classes & Objects",
                "order": 10,
                "difficulty": "advanced",
                "icon": "🏗️",
                "subtopics": [
                    "Classes, instances, and the __init__ constructor",
                    "Instance attributes vs class attributes",
                    "Inheritance and the super() function",
                    "Encapsulation and private attributes (_single, __double underscore)",
                    "Polymorphism and dunder methods (__str__, __repr__, __len__)"
                ],
                "learning_objectives": [
                    "Define custom classes with instance initialization",
                    "Implement class hierarchies through inheritance",
                    "Override magic/dunder methods to give objects Pythonic behavior"
                ],
                "lesson_content": {
                    "introduction": "Object-Oriented Programming (OOP) is a paradigm based on the concept of 'objects' that bundle state (attributes) and behavior (methods).",
                    "explanation": "### Class Anatomy\n```python\nclass BankAccount:\n    def __init__(self, owner, balance=0.0):\n        self.owner = owner\n        self._balance = balance\n        \n    def deposit(self, amount):\n        self._balance += amount\n        return self._balance\n```",
                    "code_examples": [
                        {
                            "title": "Inheritance and Polymorphism",
                            "code": "class Animal:\n    def speak(self):\n        return 'Some sound'\n\nclass Dog(Animal):\n    def speak(self):\n        return 'Woof!'\n\nclass Cat(Animal):\n    def speak(self):\n        return 'Meow!'\n\npets = [Dog(), Cat()]\nfor p in pets:\n    print(f'{type(p).__name__}: {p.speak()}')",
                            "explanation": "Demonstrates runtime polymorphism where each subclass defines its own implementation of speak().",
                            "expected_output": "Dog: Woof!\nCat: Meow!"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What does the first parameter 'self' represent in a method?",
                            "options": ["The class definition", "The current instance of the class", "The parent class", "A global variable"],
                            "correct_answer": 1,
                            "explanation": "'self' explicitly refers to the specific instance of the class invoking the method."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 6,
        "module_name": "Advanced Python",
        "description": "Master robust error handling, file I/O operations, modular packages, and decorators.",
        "icon": "🛡️",
        "topics": [
            {
                "slug": "error-handling",
                "name": "Exception Handling",
                "order": 11,
                "difficulty": "intermediate",
                "icon": "🛡️",
                "subtopics": [
                    "try, except, else, finally blocks",
                    "Catching specific exception hierarchies",
                    "Raising exceptions with raise",
                    "Custom Exception classes"
                ],
                "learning_objectives": [
                    "Handle runtime exceptions gracefully without terminating the program",
                    "Use finally for deterministic cleanup and resource release",
                    "Define custom exception classes for domain-specific errors"
                ],
                "lesson_content": {
                    "introduction": "Errors that occur during execution are called exceptions. Exception handling allows a program to deal with unexpected events cleanly.",
                    "explanation": "### Syntax\n```python\ntry:\n    val = int('abc')\nexcept ValueError as err:\n    print('Conversion failed:', err)\nfinally:\n    print('Cleanup complete')\n```",
                    "code_examples": [
                        {
                            "title": "Robust Safe Division",
                            "code": "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 'Error: Division by zero is undefined'\n    except TypeError:\n        return 'Error: Operands must be numeric'\n\nprint(safe_divide(10, 2))\nprint(safe_divide(10, 0))\nprint(safe_divide(10, 'x'))",
                            "explanation": "Targeting specific exception types for precise diagnostics.",
                            "expected_output": "5.0\nError: Division by zero is undefined\nError: Operands must be numeric"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Which block always executes in a try/except structure?",
                            "options": ["else", "except", "finally", "catch"],
                            "correct_answer": 2,
                            "explanation": "The 'finally' block is guaranteed to execute whether an exception occurred, was caught, or was not caught."
                        }
                    ]
                }
            },
            {
                "slug": "file-io",
                "name": "File Handling",
                "order": 12,
                "difficulty": "intermediate",
                "icon": "📁",
                "subtopics": [
                    "File modes ('r', 'w', 'a', 'b')",
                    "Context managers (with statement)",
                    "Reading lines and handling large files",
                    "JSON data serialization and deserialization"
                ],
                "learning_objectives": [
                    "Safely open, read, and write files using context managers",
                    "Avoid resource leaks by ensuring file descriptors close automatically",
                    "Serialize and deserialize Python dictionaries to JSON"
                ],
                "lesson_content": {
                    "introduction": "File handling allows persistent storage of data across program executions.",
                    "explanation": "### Context Manager\n`with open('data.txt', 'r') as f:` automatically closes the file even if exceptions occur.",
                    "code_examples": [
                        {
                            "title": "JSON Serialization in Memory",
                            "code": "import json\ndata = {'student': 'Priya', 'modules_completed': 4, 'passed': True}\njson_str = json.dumps(data, indent=2)\nprint('Serialized JSON:\\n' + json_str)",
                            "explanation": "Encoding Python dictionaries into standard JSON strings.",
                            "expected_output": 'Serialized JSON:\n{\n  "student": "Priya",\n  "modules_completed": 4,\n  "passed": true\n}'
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the primary benefit of using 'with open(...) as f:'?",
                            "options": ["Files open 10x faster", "The file is automatically closed when the block exits", "Files become encrypted", "Enables multithreading"],
                            "correct_answer": 1,
                            "explanation": "The context manager protocol ensures __exit__ is called, closing the file descriptor reliably."
                        }
                    ]
                }
            },
            {
                "slug": "modules",
                "name": "Modules & Packages",
                "order": 13,
                "difficulty": "advanced",
                "icon": "📦",
                "subtopics": [
                    "import, from ... import ..., as aliases",
                    "Standard library highlights (math, random, datetime)",
                    "Creating reusable local modules and __name__ == '__main__'",
                    "Package structure and __init__.py"
                ],
                "learning_objectives": [
                    "Organize multi-file Python applications into packages",
                    "Use the __name__ guard for script vs module behavior",
                    "Explore essential standard library utilities"
                ],
                "lesson_content": {
                    "introduction": "Modules are Python files (.py) containing functions, classes, and variables. Packages are directories containing multiple modules.",
                    "explanation": "### The __name__ Guard\n`if __name__ == '__main__':` ensures test or setup code only executes when the file is run directly, not when imported.",
                    "code_examples": [
                        {
                            "title": "Using the math Standard Library Module",
                            "code": "import math\n\nradius = 5\narea = math.pi * math.pow(radius, 2)\nprint(f'Circle area with radius {radius}: {round(area, 2)}')",
                            "explanation": "Importing math and using constants and mathematical functions.",
                            "expected_output": "Circle area with radius 5: 78.54"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What does __name__ evaluate to when a Python script is executed directly?",
                            "options": ["'__script__'", "'__main__'", "'root'", "'__init__'"],
                            "correct_answer": 1,
                            "explanation": "When executed directly, Python sets the top-level script's __name__ to '__main__'."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 7,
        "module_name": "Practical Python",
        "description": "Apply all skills to solve real-world coding challenges and build capstone projects.",
        "icon": "🚀",
        "topics": [
            {
                "slug": "practical-python",
                "name": "Problem Solving & Projects",
                "order": 14,
                "difficulty": "advanced",
                "icon": "🎯",
                "subtopics": [
                    "Algorithmic thinking and computational complexity",
                    "Two-pointer techniques and hash-map optimization",
                    "Building a command-line inventory system",
                    "Final Capstone Assessment & Certificate of Completion"
                ],
                "learning_objectives": [
                    "Synthesize data structures, functions, and OOP to build robust mini-projects",
                    "Analyze time and space complexity of solutions",
                    "Complete capstone programming assessments"
                ],
                "lesson_content": {
                    "introduction": "Practical programming combines syntax mastery with algorithmic problem-solving. This capstone module focuses on industry-grade coding exercises and architectural mini-projects.",
                    "explanation": "### Problem-Solving Framework\n1. **Understand:** Identify inputs, outputs, and edge cases.\n2. **Plan:** Write pseudocode and trace manually.\n3. **Implement:** Write modular, testable functions.\n4. **Optimize:** Check time and space complexity.",
                    "code_examples": [
                        {
                            "title": "Palindrome Checker Algorithm",
                            "code": "def is_palindrome(s):\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    return cleaned == cleaned[::-1]\n\nprint('Racecar:', is_palindrome('Race car'))\nprint('Python:', is_palindrome('Python'))",
                            "explanation": "Filtering alphanumeric characters and verifying symmetrical strings.",
                            "expected_output": "Racecar: True\nPython: False"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the time complexity of checking membership in a Python set of size N on average?",
                            "options": ["O(N)", "O(log N)", "O(1)", "O(N^2)"],
                            "correct_answer": 2,
                            "explanation": "Sets in Python use hash tables; average lookup time is O(1) constant time."
                        }
                    ]
                }
            }
        ]
    }
]

