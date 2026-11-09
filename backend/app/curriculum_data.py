"""
Structured Python Curriculum Data (7 Modules)
Comprehensive textbook-grade notes, memory models, syntax specifications,
code walkthroughs, common pitfalls, and viva/interview cheat sheets.
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
                    "Introduction to Python & Dynamic Typing",
                    "Variables and Memory Pointer Reference Model",
                    "Primitive Data Types (int, float, str, bool)",
                    "Console Input and Output Formatting",
                    "Type Casting and Type Conversion Mechanics"
                ],
                "learning_objectives": [
                    "Understand how Python stores and manages variables in memory via reference pointers",
                    "Identify and utilize primitive data types: int, float, str, bool",
                    "Format console output using formatted strings (f-strings) and formatting flags",
                    "Safely cast values between types using int(), float(), and str() without data loss",
                    "Recognize and prevent common bugs such as floating point precision errors and type mismatches"
                ],
                "lesson_content": {
                    "introduction": "In Python, variables are not static memory containers or boxes with fixed sizes like in C, C++, or Java. Instead, variables are **symbolic names that act as references (pointers) to objects created on the heap**. Python uses dynamic typing, meaning a variable's type is determined by the object it references at runtime, not by a compile-time declaration.\n\nUnderstanding how Python binds names to objects, how memory identity works through `id()`, and how primitive types operate under the hood is the bedrock of mastering Python software engineering.",
                    "explanation": """### 1. Conceptual Architecture: Python's Name-Binding Memory Model
In languages like C or C++, when you write `int x = 10;`, the compiler allocates a 4-byte slot in stack memory labeled `x` and places the binary representation of `10` directly inside it.

In Python:
```python
x = 10
```
1. Python creates a **`PyObject`** representing integer `10` on the private heap. This object contains metadata: reference count, type descriptor (`<class 'int'>`), and the value `10`.
2. Python binds the identifier `x` in the local namespace (a hash table dictionary) to point to the address of that object.
3. If you subsequently write `y = x`, both `x` and `y` reference the **exact same memory address** (`id(x) == id(y)`).
4. If you write `x = 20`, `x` now points to a new integer object `20`. The original object `10` remains unchanged in memory.

---

### 2. The Four Built-in Primitive Types
Python provides four foundational primitive data types:

| Type | Full Name | Description & Storage | Example Values |
| :--- | :--- | :--- | :--- |
| **`int`** | Integer | Arbitrary precision whole numbers (limited only by RAM) | `-42`, `0`, `1_000_000` |
| **`float`** | Floating-Point | 64-bit double precision (IEEE 754 standard, 53 bits precision) | `3.14159`, `-0.005`, `1.5e3` |
| **`str`** | String | Immutable ordered sequence of Unicode codepoints (UTF-8) | `'hello'`, `"Python 3"` |
| **`bool`** | Boolean | Logical truth value (`True` or `False`), direct subclass of `int` | `True` (1), `False` (0) |

---

### 3. Type Inspection and Safe Conversion
Python is **dynamically typed** (types are determined at runtime), but **strongly typed** (Python will not silently convert incompatible types, e.g. `'5' + 5` raises `TypeError`).

- **`type(obj)`**: Returns the class type of an object.
- **`isinstance(obj, class_or_tuple)`**: Recommended for type checking in production code because it respects inheritance.
- **Type Conversion**:
  - `int("123")` -> `123`
  - `float("3.14")` -> `3.14`
  - `str(42)` -> `"42"`
  - `bool(0)` -> `False`, `bool("hello")` -> `True`

---

### 4. Common Traps & Pitfalls to Avoid
- **Floating Point Representation Quirks**: `0.1 + 0.2` evaluates to `0.30000000000000004` due to base-2 binary float approximations. Never compare floats with `==`; use `math.isclose(a, b)` or `round(val, 2)`.
- **Overwriting Built-in Names**: Never name a variable `str`, `int`, `list`, `type`, or `id`. Doing `str = "user"` will shadow the built-in `str()` function and cause subsequent conversions to crash!
- **Raw `input()` Always Returns String**: `user_age = input()` yields `"21"`, not `21`. Always wrap in `int(input())` when doing arithmetic.

---

### 5. Viva & Technical Interview Questions & Answers
- **Q1: What is the difference between `==` and `is` in Python?**
  - **Answer**: `==` checks for **value equality** (whether contents match, e.g. `[1, 2] == [1, 2]`). `is` checks for **identity equality** (whether both operands point to the exact same object in memory, `id(a) == id(b)`).
- **Q2: Does Python support integer overflow?**
  - **Answer**: In Python 3, integers have arbitrary precision. Unlike C++ or Java (which overflow at 32-bit or 64-bit limits), Python dynamically allocates more bytes as integers grow. You can compute `2 ** 1000` without any overflow error.
- **Q3: What is Small Integer Caching (Interning)?**
  - **Answer**: CPython pre-allocates and caches integer objects in the range `-5` to `256` upon startup. Any variable assigned an integer in this range will point to the same cached singleton object.""",
                    "code_examples": [
                        {
                            "title": "Declaring Variables & Memory Identity Verification",
                            "code": "a = 250\nb = 250\n\nprint(f'a value: {a}, type: {type(a).__name__}, id: {id(a)}')\nprint(f'b value: {b}, type: {type(b).__name__}, id: {id(b)}')\nprint(f'a == b (Values match): {a == b}')\nprint(f'a is b (Same memory address): {a is b}')",
                            "explanation": "Demonstrates variable assignment, f-string formatting, runtime type reflection, and memory pointer equivalence.",
                            "expected_output": "a value: 250, type: int, id: [heap_address]\nb value: 250, type: int, id: [heap_address]\na == b (Values match): True\na is b (Same memory address): True"
                        },
                        {
                            "title": "Type Casting & Defensive Floating-Point Comparisons",
                            "code": "import math\n\nprice_str = '19.99'\nqty_str = '3'\n\nprice = float(price_str)\nqty = int(qty_str)\ntotal = price * qty\n\nprint(f'Total: ${total:.2f}')\n\n# Float comparison demonstration\nx = 0.1 + 0.2\nprint(f'Raw 0.1 + 0.2 = {x}')\nprint(f'Direct comparison (x == 0.3): {x == 0.3}')\nprint(f'Safe comparison (math.isclose): {math.isclose(x, 0.3)}')",
                            "explanation": "Shows proper string-to-numeric casting and how to defensively handle IEEE 754 floating-point precision differences using math.isclose.",
                            "expected_output": "Total: $59.97\nRaw 0.1 + 0.2 = 0.30000000000000004\nDirect comparison (x == 0.3): False\nSafe comparison (math.isclose): True"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the return type of the expression 15 / 3 in Python 3?",
                            "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "<class 'long'>"],
                            "correct_answer": 1,
                            "explanation": "In Python 3, single slash (/) always performs true float division, returning 5.0. To obtain integer division without fractions, use the double slash (//) floor division operator."
                        },
                        {
                            "id": 2,
                            "question": "Which of the following variable names is illegal according to Python syntax?",
                            "options": ["_student_score", "studentScore2", "2nd_student", "MAX_BUFFER_SIZE"],
                            "correct_answer": 2,
                            "explanation": "Python identifier names must start with a letter (a-z, A-Z) or an underscore (_). Starting with a numeric digit causes a SyntaxError."
                        }
                    ],
                    "practical_challenge": {
                        "prompt": "Write a function that calculates total cost including tax and formats it cleanly to 2 decimal places.",
                        "starter_code": "def calculate_bill(subtotal, tax_rate):\n    # Calculate total and return float rounded to 2 decimal places\n    pass",
                        "test_call": "calculate_bill(100.0, 0.08)",
                        "expected": "108.0"
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
                    "Comparison Operators & Chained Comparisons",
                    "Logical Operators (and, or, not) & Short-Circuit Evaluation",
                    "Bitwise and Assignment Operators",
                    "Operator Precedence Hierarchy (PEMDAS)"
                ],
                "learning_objectives": [
                    "Distinguish between true division (/), floor division (//), and modulo (%) across positive and negative values",
                    "Construct clear logical expressions with short-circuit evaluation without unnecessary overhead",
                    "Utilize chained comparisons (e.g. 10 <= x <= 100) for clean mathematical readability",
                    "Apply operator precedence rules to eliminate ambiguous code expressions"
                ],
                "lesson_content": {
                    "introduction": "Operators are specialized tokens in Python that perform computational transformations on one or more operands. Python features rich operator support spanning arithmetic, relational comparison, boolean logic, bitwise manipulation, membership, and identity testing.\n\nWriting bug-free code requires a clear understanding of operator precedence, floor division semantics, and how Python handles short-circuit evaluation.",
                    "explanation": """### 1. Arithmetic Operators Breakdown
- **`+`, `-`, `*`**: Standard mathematical addition, subtraction, multiplication.
- **`/` (True Division)**: Always returns a float, even if both operands are integers (e.g. `8 / 2 = 4.0`).
- **`//` (Floor Division)**: Divides and rounds *down* towards negative infinity. Notice: `7 // 2 = 3`, but `-7 // 2 = -4`!
- **`%` (Modulo)**: Computes the remainder. Satisfies the identity: `a = (a // b) * b + (a % b)`.
- **`**` (Exponentiation)**: Computes power. `2 ** 8 = 256`. Note: `**` binds right-to-left: `2 ** 3 ** 2 = 2 ** 9 = 512`.

---

### 2. Logical Operators & Short-Circuit Evaluation
Python uses readable English keywords: `and`, `or`, `not`.

**Short-Circuit Evaluation Rules**:
- **`a and b`**: Evaluates `a`. If `a` is false, returns `a` immediately without evaluating `b`. If `a` is true, returns `b`.
- **`a or b`**: Evaluates `a`. If `a` is true, returns `a` immediately without evaluating `b`. If `a` is false, returns `b`.
- **`not a`**: Reverses the boolean truth value of `a`.

*Why does this matter?* It allows safe guard conditions:
```python
if user is not None and user.is_active:
    # user.is_active will NEVER be called if user is None, avoiding AttributeError!
    process_user(user)
```

---

### 3. Chained Comparison Magic
In C or Java, checking if `x` is between `1` and `10` requires `x >= 1 && x <= 10`.
In Python, you can chain comparisons naturally:
```python
if 1 <= score <= 100:
    print("Valid score range")
```
Python evaluates this as `(1 <= score) and (score <= 100)`, evaluating `score` only once.

---

### 4. Operator Precedence Hierarchy Table (Highest to Lowest)
1. Parentheses: `()`
2. Exponentiation: `**` (Right-to-Left)
3. Unary signs: `+x`, `-x`, `~x`
4. Multiplication, Division, Floor, Modulo: `*`, `/`, `//`, `%`
5. Addition, Subtraction: `+`, `-`
6. Bitwise Shifts: `<<`, `>>`
7. Bitwise AND: `&`
8. Bitwise XOR: `^`
9. Bitwise OR: `|`
10. Comparisons, Identity, Membership: `==`, `!=`, `<`, `>`, `<=`, `>=`, `is`, `is not`, `in`, `not in`
11. Boolean NOT: `not`
12. Boolean AND: `and`
13. Boolean OR: `or`

---

### 5. Viva & Technical Interview Questions & Answers
- **Q1: What does `-11 // 3` evaluate to in Python?**
  - **Answer**: It evaluates to `-4`. In Python, floor division rounds towards negative infinity. $-11 / 3 = -3.666...$, and the floor of $-3.666...$ is $-4$.
- **Q2: What does `'python' and 0 or [1, 2]` return?**
  - **Answer**: `[1, 2]`. First, `'python' and 0` evaluates: since `'python'` is truthy, it returns `0`. Then `0 or [1, 2]` evaluates: since `0` is falsy, it returns `[1, 2]`.""",
                    "code_examples": [
                        {
                            "title": "Arithmetic & Floor Division Corner Cases",
                            "code": "print(f'10 / 3 = {10 / 3:.4f}')\nprint(f'10 // 3 = {10 // 3}')\nprint(f'-10 // 3 = {-10 // 3}')\nprint(f'10 % 3 = {10 % 3}')\nprint(f'2 ** 3 ** 2 = {2 ** 3 ** 2} (Right-to-left associativity)')",
                            "explanation": "Illustrates division mechanics, negative number rounding semantics, and exponentiation associativity.",
                            "expected_output": "10 / 3 = 3.3333\n10 // 3 = 3\n-10 // 3 = -4\n10 % 3 = 1\n2 ** 3 ** 2 = 512 (Right-to-left associativity)"
                        },
                        {
                            "title": "Short-Circuit Guard Patterns & Chained Comparisons",
                            "code": "user = {'role': 'admin', 'authenticated': True}\nage = 24\n\n# Chained comparison\nis_eligible = 18 <= age <= 65\nprint(f'Age eligibility check: {is_eligible}')\n\n# Safe short-circuit check\nis_admin = user and user.get('authenticated') and user.get('role') == 'admin'\nprint(f'Authorized Admin: {is_admin}')",
                            "explanation": "Demonstrates practical production-grade logical chaining and short-circuit protection.",
                            "expected_output": "Age eligibility check: True\nAuthorized Admin: True"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the result of 2 + 3 * 2 ** 3 in Python?",
                            "options": ["40", "26", "200", "256"],
                            "correct_answer": 1,
                            "explanation": "Following precedence: 2 ** 3 = 8 first. Then 3 * 8 = 24. Finally 2 + 24 = 26."
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
                    "Nested Conditions vs Guard Clauses",
                    "Ternary Conditional Expressions",
                    "Truthiness and Falsiness of Python Objects"
                ],
                "learning_objectives": [
                    "Construct branched decision trees using if, elif, and else structures",
                    "Refactor deeply nested conditional blocks into clean guard clauses with early returns",
                    "Master Python truth value testing rules across containers, numbers, and None",
                    "Utilize concise ternary expressions for inline assignments"
                ],
                "lesson_content": {
                    "introduction": "Conditional execution is what gives software the capability to make intelligent decisions. A program evaluates boolean expressions and directs control flow along divergent execution branches. Clean control flow avoids 'arrowhead anti-patterns' (deeply nested ifs) through the use of guard clauses and declarative conditions.",
                    "explanation": """### 1. The Anatomy of if-elif-else
Python structures branches using indentation blocks (4 spaces):
```python
if condition_1:
    # Executed if condition_1 is truthy
elif condition_2:
    # Executed only if condition_1 was falsy AND condition_2 is truthy
else:
    # Fallback: executed if all preceding conditions were falsy
```

---

### 2. Complete Truthiness & Falsiness Table
In Python, every object has an inherent boolean truth value. You do NOT need to write `if len(items) > 0:` or `if flag == True:`.

**The Falsy Objects in Python**:
- Constants: `None`, `False`
- Numeric zeros: `0`, `0.0`, `0j`, `Decimal(0)`
- Empty sequences: `""` (empty string), `()` (empty tuple), `[]` (empty list)
- Empty mappings / sets: `{}` (empty dict), `set()`
- Custom classes defining `__bool__()` or `__len__()` returning `False` or `0`.

*All other objects evaluate to `True`!*

---

### 3. Guard Clauses & Early Return Pattern
Deeply nested if-statements create cognitive overload and make unit testing difficult. **Guard clauses** validate error conditions upfront and return early:

```python
# Anti-pattern: Deep Arrowhead Nesting
def process_order(order):
    if order is not None:
        if order.is_paid:
            if order.in_stock:
                return ship(order)
            else:
                return "Out of stock"
        else:
            return "Payment required"
    return "Invalid order"

# Clean Code: Guard Clause Refactoring
def process_order(order):
    if not order:
        return "Invalid order"
    if not order.is_paid:
        return "Payment required"
    if not order.in_stock:
        return "Out of stock"
    return ship(order)
```

---

### 4. Ternary Conditional Expression
For concise assignments based on a single condition:
```python
access_level = "Administrator" if user.is_admin else "Standard User"
```

---

### 5. Viva & Technical Interview Questions & Answers
- **Q1: Why is checking `if my_list:` preferred over `if len(my_list) > 0:`?**
  - **Answer**: It is both more Pythonic (PEP 8) and computationally cleaner. Python directly queries `bool(my_list)` which delegates to the C-level `tp_as_sequence->sq_length` without invoking python-level function dispatch.
- **Q2: What is the difference between `if condition:` and `elif condition:`?**
  - **Answer**: `if` initiates an independent conditional check. `elif` is mutually exclusive with prior `if`/`elif` checks in the chain; it is only tested if every preceding condition was falsy.""",
                    "code_examples": [
                        {
                            "title": "Guard Clause Pattern in Action",
                            "code": "def withdraw(balance, amount):\n    if amount <= 0:\n        return 'Error: Invalid withdrawal amount.'\n    if amount > balance:\n        return 'Error: Insufficient funds.'\n    remaining = balance - amount\n    return f'Success! Dispensed: ${amount:.2f}, Balance: ${remaining:.2f}'\n\nprint(withdraw(500, 150))\nprint(withdraw(500, 600))\nprint(withdraw(500, -20))",
                            "explanation": "Illustrates guard clauses preventing invalid operations with early exits.",
                            "expected_output": "Success! Dispensed: $150.00, Balance: $350.00\nError: Insufficient funds.\nError: Invalid withdrawal amount."
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Which of the following objects evaluates to True in a boolean context?",
                            "options": ["[]", "0.0", "'0'", "None"],
                            "correct_answer": 2,
                            "explanation": "The string '0' is non-empty, so it evaluates to True. Empty containers [], numeric zero 0.0, and None are falsy."
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
                    "for Loops and the range() Function",
                    "Iterating Over Collections (Strings, Lists, Dictionaries)",
                    "while Loops and Loop Termination Invariants",
                    "Control Flow: break, continue, and pass",
                    "The Unique for-else and while-else Construct"
                ],
                "learning_objectives": [
                    "Understand Python's iterator protocol: iterable objects vs iterator instances",
                    "Control loop execution dynamically with break and continue",
                    "Utilize enumerate() and zip() for expressive, bug-free parallel looping",
                    "Apply the for-else search pattern without flag variables"
                ],
                "lesson_content": {
                    "introduction": "Repetition is fundamental to automated computation. Python features two loop constructs: `for` loops (which perform definite iteration over iterable sequences using the iterator protocol) and `while` loops (which perform indefinite iteration based on a dynamic boolean condition).\n\nMastering loop idioms like `enumerate()`, `zip()`, and the `for-else` construct allows you to write elegant, fast, and idiomatic Python algorithms.",
                    "explanation": """### 1. The Iterator Protocol Under the Hood
In Python, `for item in collection:` does not use indexed counter lookups. Instead:
1. Python calls `iter(collection)` to request an iterator object.
2. Inside a loop, it repeatedly calls `next(iterator)`.
3. When elements are exhausted, the iterator raises `StopIteration`, which the `for` loop catches and exits cleanly.

---

### 2. Range Function Anatomy: `range(start, stop, step)`
- `range(5)` -> `0, 1, 2, 3, 4` (starts at 0, exclusive of 5)
- `range(2, 8)` -> `2, 3, 4, 5, 6, 7`
- `range(10, 0, -2)` -> `10, 8, 6, 4, 2` (counting backwards)
*In Python 3, `range` is a lazy sequence type consuming O(1) memory regardless of size.*

---

### 3. Essential Iteration Helpers
- **`enumerate(iterable, start=0)`**: Yields pairs `(index, item)`. Eliminates manual counter variables (`i += 1`).
- **`zip(list_a, list_b)`**: Pairs corresponding elements from multiple iterables.

---

### 4. The Unique `for-else` Pattern
Python loops feature an optional `else:` clause.
**Rule**: The `else:` block executes **ONLY if the loop completed normally without encountering a `break` statement**.
This is ideal for search algorithms:
```python
for item in database:
    if item.id == target_id:
        print("Found:", item)
        break
else:
    print("Item not found in entire database!")
```

---

### 5. Viva & Technical Interview Questions & Answers
- **Q1: Why should you NEVER modify a list while iterating over it?**
  - **Answer**: Modifying a list (deleting or inserting items) while iterating shifts the internal array indices, causing elements to be skipped or evaluated twice. If you must filter items, iterate over a shallow copy (`for item in list_a[:]:`) or use a list comprehension.
- **Q2: What is the memory footprint of `range(1_000_000_000)` in Python 3?**
  - **Answer**: Approximately 48 bytes. In Python 3, `range` is an immutable lazy sequence object that computes elements on demand via integer arithmetic rather than creating a billion integers in RAM.""",
                    "code_examples": [
                        {
                            "title": "Clean Iteration with enumerate and for-else Search",
                            "code": "primes = [2, 3, 5, 7, 11, 13]\nsearch_target = 7\n\n# 1. Enumerate demonstration\nfor idx, val in enumerate(primes, 1):\n    print(f'Prime #{idx}: {val}')\n\n# 2. for-else search pattern\nfor p in primes:\n    if p == search_target:\n        print(f'Target {search_target} verified in prime registry!')\n        break\nelse:\n    print(f'Target {search_target} not found.')",
                            "explanation": "Shows 1-indexed enumeration and declarative for-else search without temporary boolean flags.",
                            "expected_output": "Prime #1: 2\nPrime #2: 3\nPrime #3: 5\nPrime #4: 7\nPrime #5: 11\nPrime #6: 13\nTarget 7 verified in prime registry!"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "When does the else block of a Python while loop execute?",
                            "options": [
                                "Whenever the while loop runs at least once",
                                "Only when the loop terminates because its condition became False (no break)",
                                "Whenever an exception occurs inside the loop",
                                "Every single iteration"
                            ],
                            "correct_answer": 1,
                            "explanation": "The else block on a loop executes only if the loop naturally finished all iterations without a break statement."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 3,
        "module_name": "Data Structures",
        "description": "Harness Python's versatile collection types: strings, lists, tuples, dictionaries, and sets.",
        "icon": "📚",
        "topics": [
            {
                "slug": "strings",
                "name": "String Operations",
                "order": 5,
                "difficulty": "beginner",
                "icon": "✍️",
                "subtopics": [
                    "String Immutability and Memory Interning",
                    "Indexing and Extended Slicing [start:stop:step]",
                    "15+ Core String Methods (strip, split, join, replace)",
                    "Modern f-strings Formatting and Alignment Specs"
                ],
                "learning_objectives": [
                    "Understand string immutability and memory optimization in CPython",
                    "Slice strings forwards and backwards with negative strides",
                    "Perform efficient tokenization and concatenation using split() and join()",
                    "Format financial values, decimal padding, and tables using f-strings"
                ],
                "lesson_content": {
                    "introduction": "Strings in Python are immutable sequences of Unicode characters. Immutability guarantees that once a string object is instantiated in memory, its contents cannot be altered in-place. Any string method that appears to modify text actually constructs and returns a new string object.",
                    "explanation": """### 1. Extended Slicing Mechanics: `s[start:stop:step]`
- `s[0]` -> First character
- `s[-1]` -> Last character
- `s[1:5]` -> Characters from index 1 up to index 4 (stop index is exclusive)
- `s[::-1]` -> Reverses the entire string with negative step
- `s[::2]` -> Every second character

---

### 2. High-Performance String Methods
- **`s.strip()`, `s.lstrip()`, `s.rstrip()`**: Strips whitespace or specified characters.
- **`s.split(sep)`**: Splits string into a list of tokens based on separator.
- **`sep.join(list_of_strings)`**: High-performance concatenation. **Crucial tip**: Never build long strings with `+=` inside loops (which has $O(N^2)$ time complexity due to creating $N$ temporary objects). Always append tokens to a list and call `''.join(tokens)` ($O(N)$ linear time).
- **`s.replace(old, new)`**: Replaces occurrences.
- **`s.startswith(prefix)` / `s.endswith(suffix)`**: Clean boolean checks.

---

### 3. Advanced f-string Specifications
```python
pi = 3.14159265
val = 42
print(f"{pi:.2f}")       # '3.14' (2 decimals)
print(f"{val:>8}")        # '      42' (Right aligned, width 8)
print(f"{val:0>8}")       # '00000042' (Zero padded)
print(f"{val=}")          # 'val=42' (Self-documenting debug print)
```""",
                    "code_examples": [
                        {
                            "title": "String Processing & High-Performance Join",
                            "code": "raw = '   alex, 95, engineering, active   '\ntokens = [t.strip().capitalize() for t in raw.split(',')]\nformatted = ' | '.join(tokens)\nprint('Parsed record:', formatted)\n\nrev = tokens[0][::-1]\nprint(f'Reversed name: {tokens[0]} -> {rev}')",
                            "explanation": "Cleaning messy CSV strings, transforming cases, and joining cleanly.",
                            "expected_output": "Parsed record: Alex | 95 | Engineering | Active\nReversed name: Alex -> xelA"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What does 'PyMentor'[1:6:2] produce?",
                            "options": ["'yM'", "'yeo'", "'yMt'", "'Pye'"],
                            "correct_answer": 1,
                            "explanation": "Indices considered from 1 to 5 with step 2: index 1 ('y'), index 3 ('e'), index 5 ('o'). Result: 'yeo'."
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
                    "Dynamic Array Architecture & Amortized Growth",
                    "List Methods (append, extend, pop, insert, sort)",
                    "Tuples: Immutability, Memory Benefits & Unpacking",
                    "Shallow vs Deep Copying in Nested Collections"
                ],
                "learning_objectives": [
                    "Understand how Python lists resize dynamically under the hood",
                    "Differentiate when to use mutable lists vs immutable tuples",
                    "Unpack tuples and lists using the starred (*) operator",
                    "Safely clone nested data structures using copy.deepcopy"
                ],
                "lesson_content": {
                    "introduction": "Lists and tuples are ordered collections of arbitrary Python objects. Lists are mutable dynamic arrays, allowing insertions, deletions, and replacements in-place. Tuples are immutable sequences, guaranteeing data integrity and serving as safe dictionary keys.",
                    "explanation": """### 1. Dynamic Array Growth Mechanics
In CPython, a list is an array of pointers to `PyObject` items. When you append items to a full list, Python over-allocates extra capacity (roughly $1.125 \\times$ current size $+ 6$ items).
- **`append()`**: Amortized $O(1)$ constant time.
- **`pop()`**: $O(1)$ removing from the end.
- **`insert(0, val)` or `pop(0)`**: $O(N)$ linear time because all remaining elements must shift in memory!

---

### 2. Tuples & Tuple Unpacking
Tuples are defined with parentheses `(1, 2, 3)` or simply commas `1, 2, 3`.
Because tuples are immutable:
- They consume less memory than lists.
- They are hashable (can be used as dictionary keys or set members if their contents are hashable).

**Advanced Unpacking**:
```python
first, *middle, last = [10, 20, 30, 40, 50]
# first = 10, middle = [20, 30, 40], last = 50
```

---

### 3. Shallow vs Deep Copy Trap
```python
import copy
a = [[1, 2], [3, 4]]
b = a.copy()       # Shallow copy: b references same inner sublists!
b[0][0] = 999
print(a[0][0])     # 999! a was modified!

c = copy.deepcopy(a)  # Truly independent clone
```""",
                    "code_examples": [
                        {
                            "title": "Tuple Unpacking & Sorting",
                            "code": "students = [('Alice', 88), ('Bob', 95), ('Charlie', 78)]\n\n# Sort by grade descending\nsorted_students = sorted(students, key=lambda s: s[1], reverse=True)\nfor rank, (name, score) in enumerate(sorted_students, 1):\n    print(f'Rank {rank}: {name} ({score}%)')",
                            "explanation": "Demonstrates tuple unpacking inside enumerate loop and custom key sorting.",
                            "expected_output": "Rank 1: Bob (95%)\nRank 2: Alice (88%)\nRank 3: Charlie (78%)"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the time complexity of list.pop(0) in Python?",
                            "options": ["O(1)", "O(log N)", "O(N)", "O(N^2)"],
                            "correct_answer": 2,
                            "explanation": "Removing the first item from a list forces all remaining N-1 elements to shift one memory slot to the left, taking linear O(N) time. Use collections.deque for O(1) double-ended queues."
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
                    "Hash Tables Under the Hood & O(1) Amortized Lookups",
                    "Dictionary Methods (get, items, keys, setdefault)",
                    "Dictionary Merging and Unpacking Operators",
                    "Set Operations: Union, Intersection, Difference"
                ],
                "learning_objectives": [
                    "Understand hash tables, hash functions, and key collision resolution",
                    "Access dictionary keys safely with get() and default fallbacks",
                    "Perform high-speed membership testing using sets",
                    "Execute mathematical set operations: union, intersection, and symmetric difference"
                ],
                "lesson_content": {
                    "introduction": "Dictionaries and sets are Python's high-speed hash-table data structures. Dictionaries map unique hashable keys to arbitrary values, providing near-instantaneous $O(1)$ average time lookups, insertions, and deletions.",
                    "explanation": """### 1. Hash Tables Under the Hood
When you write `d['key'] = value`:
1. Python calls `hash('key')` to compute a 64-bit integer hash code.
2. It masks this hash to find an index into an internal sparse table.
3. If two different keys produce the same table index (a collision), Python uses open addressing with perturbation to find the next available slot.
4. **Requirement**: Keys must be immutable and hashable (e.g. `str`, `int`, `tuple`). A `list` cannot be a dictionary key!

---

### 2. Safe Dictionary Access & Defaults
```python
user = {"name": "Alice"}
# Dangerous: user["email"] raises KeyError
# Safe:
email = user.get("email", "no-email@example.com")
```

---

### 3. Set Operations
Sets store unique, unordered elements:
- Union: `a | b`
- Intersection: `a & b`
- Difference: `a - b`
- Symmetric Difference: `a ^ b`
- Membership testing (`item in my_set`) is $O(1)$, compared to $O(N)$ for lists!""",
                    "code_examples": [
                        {
                            "title": "Dictionary Aggregation & Set Intersection",
                            "code": "backend_skills = {'Python', 'FastAPI', 'PostgreSQL', 'Docker'}\nstudent_skills = {'Python', 'JavaScript', 'HTML', 'PostgreSQL'}\n\nmatched = student_skills & backend_skills\nmissing = backend_skills - student_skills\n\nprint('Qualified skills:', matched)\nprint('Skills to learn:', missing)",
                            "explanation": "Using set intersection and difference for automated skill gap analysis.",
                            "expected_output": "Qualified skills: {'PostgreSQL', 'Python'}\nSkills to learn: {'Docker', 'FastAPI'}"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Which of the following can be used as a key in a Python dictionary?",
                            "options": ["['admin', 1]", "{'id': 1}", "('admin', 1)", "set([1, 2])"],
                            "correct_answer": 2,
                            "explanation": "Only immutable, hashable objects can be dictionary keys. Tuples containing immutable items are hashable. Lists, dicts, and sets are mutable and unhashable."
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
                    "List, Dict, and Set Comprehension Syntax",
                    "Filtering with Conditional if Clauses",
                    "Nested Comprehensions and Matrix Operations",
                    "Generator Expressions vs Memory Efficiency"
                ],
                "learning_objectives": [
                    "Transform and filter collections with expressive one-line comprehensions",
                    "Construct dictionary comprehensions for key-value inversion and indexing",
                    "Use generator expressions to process massive streams with O(1) memory footprint"
                ],
                "lesson_content": {
                    "introduction": "Comprehensions provide a concise, declarative syntax for generating new collections from existing iterables. They are faster than traditional `for` loops with `.append()` because the loop is executed at optimized C-speed inside the Python interpreter.",
                    "explanation": """### 1. Comprehension Syntax Patterns
- **List Comprehension**: `[expr for item in iterable if condition]`
- **Dict Comprehension**: `{key_expr: val_expr for item in iterable if condition}`
- **Set Comprehension**: `{expr for item in iterable if condition}`
- **Generator Expression**: `(expr for item in iterable if condition)` (Lazy, $O(1)$ memory!)

---

### 2. Matrix Transpose Example
```python
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in matrix] for i in range(3)]
# [[1, 4], [2, 5], [3, 6]]
```""",
                    "code_examples": [
                        {
                            "title": "Comprehensions in Real-World Filtering",
                            "code": "users = [\n    {'name': 'Alex', 'active': True, 'score': 92},\n    {'name': 'Beth', 'active': False, 'score': 85},\n    {'name': 'Carl', 'active': True, 'score': 74}\n]\n\nhigh_scorers = [u['name'] for u in users if u['active'] and u['score'] >= 80]\nscore_map = {u['name']: u['score'] for u in users if u['active']}\n\nprint('High Scorers:', high_scorers)\nprint('Active Score Map:', score_map)",
                            "explanation": "Filtering active users and mapping scores into a dictionary using comprehension syntax.",
                            "expected_output": "High Scorers: ['Alex']\nActive Score Map: {'Alex': 92, 'Carl': 74}"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the difference between [x*2 for x in range(10)] and (x*2 for x in range(10))?",
                            "options": [
                                "The second is invalid syntax",
                                "The first creates a list in memory; the second creates a lazy generator iterator",
                                "The second creates a tuple",
                                "They are identical"
                            ],
                            "correct_answer": 1,
                            "explanation": "Parentheses create a generator expression which produces items on demand via the iterator protocol without allocating all elements in memory."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 4,
        "module_name": "Functions",
        "description": "Construct modular, reusable code architectures with functions, arguments, and scopes.",
        "icon": "🧩",
        "topics": [
            {
                "slug": "functions",
                "name": "Functions & Scope",
                "order": 9,
                "difficulty": "beginner",
                "icon": "🧩",
                "subtopics": [
                    "Function Definition (def) and Return Values",
                    "Positional, Keyword, and Default Arguments",
                    "*args and **kwargs Variable Argument Lists",
                    "Variable Scope & The LEGB Rule (Local, Enclosing, Global, Built-in)",
                    "First-Class Functions, Closures, and Lambda Expressions"
                ],
                "learning_objectives": [
                    "Write modular, decoupled functions adhering to Single Responsibility Principle",
                    "Harness *args and **kwargs to construct flexible, extensible APIs",
                    "Understand Python scope resolution using the LEGB hierarchy",
                    "Avoid the notorious mutable default argument trap"
                ],
                "lesson_content": {
                    "introduction": "Functions are the fundamental building blocks of reusable software. In Python, functions are first-class citizens: they can be assigned to variables, passed as arguments to other functions, and returned from functions.",
                    "explanation": """### 1. Flexible Argument Handling: `*args` and `**kwargs`
- **`*args`**: Captures any number of positional arguments into a **tuple**.
- **`**kwargs`**: Captures any number of keyword arguments into a **dictionary**.

---

### 2. The LEGB Scope Resolution Rule
When a variable is accessed inside a function, Python searches scopes in this exact order:
1. **L (Local)**: Defined within the current function body.
2. **E (Enclosing)**: Defined in outer nested function wrappers (closures).
3. **G (Global)**: Defined at top-level of the module.
4. **B (Built-in)**: Python's pre-loaded symbols (`len`, `range`, `print`).

---

### 3. THE NOTORIOUS TRAP: Mutable Default Arguments
```python
# BUG: The default list [] is evaluated ONCE when function is defined!
def append_to(item, target=[]):
    target.append(item)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2] -- UNEXPECTED! Shares same list!

# CORRECT PRODUCTION PATTERN:
def append_to_safe(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```""",
                    "code_examples": [
                        {
                            "title": "Flexible Decorator-Style Function with *args and **kwargs",
                            "code": "def log_execution(func, *args, **kwargs):\n    print(f'Invoking {func.__name__} with args={args}, kwargs={kwargs}')\n    result = func(*args, **kwargs)\n    print(f'Finished {func.__name__} -> Result: {result}')\n    return result\n\ndef calculate_total(subtotal, tax=0.08, discount=0):\n    return round(subtotal * (1 + tax) - discount, 2)\n\nres = log_execution(calculate_total, 100, tax=0.10, discount=5)",
                            "explanation": "Passing arbitrary positional and keyword parameters dynamically to a wrapped target function.",
                            "expected_output": "Invoking calculate_total with args=(100,), kwargs={'tax': 0.1, 'discount': 5}\nFinished calculate_total -> Result: 105.0"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "Why is using def func(data=[]) considered dangerous in Python?",
                            "options": [
                                "It causes a SyntaxError",
                                "The default list is created only once at function definition time and mutated across subsequent calls",
                                "Python cannot serialize default lists",
                                "Lists are restricted inside functions"
                            ],
                            "correct_answer": 1,
                            "explanation": "Default arguments are evaluated once when the function definition is executed, so a mutable default object retains mutations across calls."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 5,
        "module_name": "Object-Oriented Programming",
        "description": "Model complex software entities with classes, inheritance, encapsulation, and polymorphism.",
        "icon": "🏛️",
        "topics": [
            {
                "slug": "oop",
                "name": "Classes & Objects",
                "order": 10,
                "difficulty": "intermediate",
                "icon": "🏛️",
                "subtopics": [
                    "Class Definitions, Instantiation, and the __init__ Constructor",
                    "Instance Attributes vs Class-Level Attributes",
                    "Encapsulation: Public, Protected (_), and Private (__) Name Mangling",
                    "Inheritance, super(), and Method Resolution Order (MRO)",
                    "Polymorphism and Special Dunder Methods (__str__, __repr__, __len__)"
                ],
                "learning_objectives": [
                    "Design object-oriented classes encapsulating state and domain behaviors",
                    "Distinguish class-level state from instance-level state",
                    "Construct clean inheritance hierarchies with super() initialization",
                    "Implement dunder methods for operator overloading and custom string representations"
                ],
                "lesson_content": {
                    "introduction": "Object-Oriented Programming (OOP) is a paradigm that organizes software design around data entities (objects) rather than functions alone. An object bundles state (attributes) and behavior (methods) into a cohesive, reusable software entity.",
                    "explanation": """### 1. Anatomy of a Python Class
- `self`: Explicit reference to the current instance object.
- `__init__(self, ...)`: The initializer method called automatically when creating instances.
- Class Attributes: Shared by all instances of the class.
- Instance Attributes: Unique to each individual object.

---

### 2. Encapsulation & Name Mangling
- `public_var`: Accessible from anywhere.
- `_protected_var`: Convention indicating internal use (PEP 8 courtesy).
- `__private_var`: Python applies **Name Mangling**, transforming the name to `_ClassName__private_var` to prevent accidental overwriting in subclasses.

---

### 3. Inheritance and `super()`
Subclasses inherit attributes and methods from parent classes. Using `super().__init__(...)` delegates initialization upwards cleanly.

---

### 4. Magic Dunder Methods
- **`__str__(self)`**: User-friendly representation (`print(obj)`).
- **`__repr__(self)`**: Developer representation (`repr(obj)`).
- **`__eq__(self, other)`**: Equality operator `==`.
- **`__len__(self)`**: Enables `len(obj)`.

---

### 5. Viva & Technical Interview Questions & Answers
- **Q1: What is Method Resolution Order (MRO)?**
  - **Answer**: MRO is the order in which Python searches for a method in a class hierarchy, especially with multiple inheritance. Python uses the **C3 Superclass Linearization algorithm**. You can inspect any class's MRO using `Class.mro()`.
- **Q2: Does Python support true private variables?**
  - **Answer**: No. Python follows the philosophy 'We are all consenting adults here.' Prefixing with `__` triggers name mangling (`_Class__attr`), but the attribute is still accessible if referenced with its mangled name.""",
                    "code_examples": [
                        {
                            "title": "Inheritance, Encapsulation, and Dunder Methods",
                            "code": "class BankAccount:\n    interest_rate = 0.04  # Class attribute\n\n    def __init__(self, owner, balance=0.0):\n        self.owner = owner\n        self._balance = balance  # Protected attribute\n\n    def deposit(self, amount):\n        if amount > 0:\n            self._balance += amount\n            return True\n        return False\n\n    def __str__(self):\n        return f'BankAccount({self.owner}: ${self._balance:.2f})'\n\nclass SavingsAccount(BankAccount):\n    def apply_interest(self):\n        interest = self._balance * self.interest_rate\n        self._balance += interest\n        return interest\n\nacct = SavingsAccount('Sarah', 1000.0)\nacct.apply_interest()\nprint(acct)",
                            "explanation": "Illustrates class attributes, subclassing, superclass delegation, and custom string dunder representation.",
                            "expected_output": "BankAccount(Sarah: $1040.00)"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the purpose of the self parameter in Python class methods?",
                            "options": [
                                "It is a keyword that imports standard methods",
                                "It refers to the specific instance of the class calling the method",
                                "It specifies the superclass",
                                "It allocates stack memory"
                            ],
                            "correct_answer": 1,
                            "explanation": "self represents the instance of the class. By using self, you can access the attributes and methods of the specific object."
                        }
                    ]
                }
            }
        ]
    },
    {
        "module_number": 6,
        "module_name": "Advanced Python",
        "description": "Professional engineering: exceptions, context managers, file I/O, and modular packaging.",
        "icon": "⚡",
        "topics": [
            {
                "slug": "error-handling",
                "name": "Exception Handling",
                "order": 11,
                "difficulty": "intermediate",
                "icon": "🛡️",
                "subtopics": [
                    "The try, except, else, and finally Lifecycle",
                    "Catching Specific Exceptions vs Anti-pattern Bare except",
                    "Raising Exceptions and Exception Chaining (raise ... from)",
                    "Defining Custom Domain Exception Hierarchies"
                ],
                "learning_objectives": [
                    "Defend programs against runtime failures with structured try-except blocks",
                    "Understand the specific roles of else (runs if no exception) and finally (always runs)",
                    "Create domain-specific custom exceptions inheriting from Exception"
                ],
                "lesson_content": {
                    "introduction": "Robust software must anticipate and gracefully recover from unexpected runtime anomalies. Python uses exceptions rather than error return codes. Understanding how to structure try-except-else-finally blocks is essential for writing resilient systems.",
                    "explanation": """### 1. The Full Exception Lifecycle
- **`try`**: Code that might raise an error.
- **`except SpecificError as e`**: Runs if that specific error occurs.
- **`else`**: Runs ONLY if NO exceptions were raised in the `try` block.
- **`finally`**: Runs ALWAYS, even if an exception occurred or `return` was called. Perfect for closing database connections, sockets, and files.

---

### 2. The Bare Except Anti-Pattern
Never write `except:`. This catches `KeyboardInterrupt` (Ctrl+C) and `SystemExit`, preventing users from terminating the program! Always catch specific exceptions: `except (ValueError, KeyError) as e:`.""",
                    "code_examples": [
                        {
                            "title": "Graceful File & Conversion Handling",
                            "code": "def parse_integer(val):\n    try:\n        num = int(val)\n    except (ValueError, TypeError) as err:\n        return f'Parse Error: Cannot convert {val!r} to int.'\n    else:\n        return f'Success: Parsed integer is {num}'\n    finally:\n        pass\n\nprint(parse_integer('42'))\nprint(parse_integer('invalid_abc'))",
                            "explanation": "Illustrates targeted multi-exception catching and the else block.",
                            "expected_output": "Success: Parsed integer is 42\nParse Error: Cannot convert 'invalid_abc' to int."
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "When does the else block in a try-except structure execute?",
                            "options": [
                                "Only if an unhandled exception occurred",
                                "Only if no exception was raised in the try block",
                                "Always right before the finally block",
                                "Only when an except block executed"
                            ],
                            "correct_answer": 1,
                            "explanation": "The else block in a try statement executes only if the try block completed successfully without raising any exceptions."
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
                        "Context Managers (with statement) & Safe File Descriptors",
                        "File Modes ('r', 'w', 'a', 'rb', 'wb')",
                        "Reading Files Line-by-Line to Conserve Memory",
                        "Working with JSON and CSV Structured Formats"
                    ],
                    "learning_objectives": [
                        "Always use context managers (with) to guarantee automatic file closure",
                        "Differentiate between text modes and binary modes",
                        "Stream massive files line-by-line with O(1) memory consumption",
                        "Serialize and deserialize JSON data with json.dumps and json.loads"
                    ],
                    "lesson_content": {
                        "introduction": "File handling allows software to interact with the host filesystem. In modern Python, the `with` statement (Context Manager) is mandatory: it guarantees file descriptors are closed immediately, even if unhandled exceptions occur.",
                        "explanation": """### 1. The Context Manager Pattern
```python
with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:  # Memory efficient streaming!
        process(line.strip())
# File is automatically closed here!
```

---

### 2. Common Modes
- `'r'`: Read only (file must exist).
- `'w'`: Write (truncates/overwrites existing file or creates new).
- `'a'`: Append (writes to end of existing file).
- `'b'`: Binary mode (e.g. `'rb'` for images, audio, zip files).""",
                        "code_examples": [
                            {
                                "title": "JSON Serialization and Deserialization",
                                "code": "import json\n\nstudent_data = {'id': 101, 'name': 'Gayathri', 'skills': ['Python', 'SQL']}\njson_str = json.dumps(student_data, indent=2)\nprint('Serialized JSON:\\n' + json_str)\n\nparsed = json.loads(json_str)\nprint('Parsed back:', parsed['name'], parsed['skills'])",
                                "explanation": "Demonstrates serialization of in-memory data structures to JSON strings and parsing back.",
                                "expected_output": 'Serialized JSON:\n{\n  "id": 101,\n  "name": "Gayathri",\n  "skills": [\n    "Python",\n    "SQL"\n  ]\n}\nParsed back: Gayathri [\'Python\', \'SQL\']'
                            }
                        ],
                        "practice_questions": [
                            {
                                "id": 1,
                                "question": "Why is 'with open(...) as f:' preferred over manually calling f.close()?",
                                "options": [
                                    "It executes faster",
                                    "It automatically closes the file descriptor even if an error is raised inside the block",
                                    "It enables multi-threading",
                                    "It compresses the file"
                                ],
                                "correct_answer": 1,
                                "explanation": "Context managers guarantee that the file descriptor is released upon exiting the block, preventing file descriptor leaks."
                            }
                        ]
                    }
                },
                {
                    "slug": "modules",
                    "name": "Modules & Packages",
                    "order": 13,
                    "difficulty": "intermediate",
                    "icon": "📦",
                    "subtopics": [
                        "Importing Modules and Namespace Isolation",
                        "The if __name__ == '__main__' Execution Idiom",
                        "Package Structure (__init__.py)",
                        "Python Standard Library Highlights (os, sys, math, datetime)"
                    ],
                    "learning_objectives": [
                        "Organize Python projects into modular packages and namespaces",
                        "Use if __name__ == '__main__' to write dual-purpose testable scripts",
                        "Navigate standard library utilities efficiently"
                    ],
                    "lesson_content": {
                        "introduction": "A module is a file containing Python definitions and statements. A package is a collection of modules under a directory namespace. Modular design enables clean separation of concerns and maintainability in large-scale applications.",
                        "explanation": """### The `if __name__ == '__main__'` Idiom
When a Python file is run directly: `__name__` is set to `'__main__'`.
When imported by another module: `__name__` is set to the module's file name.

```python
def calculate():
    return 42

if __name__ == '__main__':
    # Only executes when run directly via CLI, not when imported!
    print("Self-test result:", calculate())
```""",
                        "code_examples": [
                            {
                                "title": "Standard Library Datetime & Math Utilities",
                                "code": "import math\nfrom datetime import datetime, timedelta\n\nnow = datetime.now()\nfuture = now + timedelta(days=7)\nprint(f\"Current date: {now.strftime('%Y-%m-%d')}\")\nprint(f\"7 days ahead: {future.strftime('%Y-%m-%d')}\")\nprint(f'Factorial of 6: {math.factorial(6)}')",
                                "explanation": "Demonstrates date manipulation and mathematical standard libraries.",
                                "expected_output": "Current date: [YYYY-MM-DD]\n7 days ahead: [YYYY-MM-DD]\nFactorial of 6: 720"
                            }
                        ],
                        "practice_questions": [
                            {
                                "id": 1,
                                "question": "What is the value of __name__ when a Python file is imported into another script?",
                                "options": ["'__main__'", "The module's actual filename/name", "'__import__'", "None"],
                                "correct_answer": 1,
                                "explanation": "When imported, __name__ is assigned the module's name. When executed directly as the script entry point, it equals '__main__'."
                            }
                        ]
                    }
                }
            ]
        },
        {
        "module_number": 7,
        "module_name": "Practical Python",
        "description": "Real-world engineering: algorithmic problem solving, clean code architecture, and software projects.",
        "icon": "🚀",
        "topics": [
            {
                "slug": "practical-python",
                "name": "Problem Solving & Projects",
                "order": 14,
                "difficulty": "advanced",
                "icon": "🚀",
                "subtopics": [
                    "Algorithmic Problem Deconstruction & Big-O Complexity",
                    "Defensive Programming and Input Validation",
                    "Testing with Doctest and Assert Statements",
                    "Full-Stack Project Development: CLI to Web Integration"
                ],
                "learning_objectives": [
                    "Deconstruct real-world business requirements into clean algorithmic workflows",
                    "Evaluate space and time complexity using Big-O notation",
                    "Build full-featured software projects combining Python backend and Web interfaces"
                ],
                "lesson_content": {
                    "introduction": "Programming mastery culminates in the ability to solve non-trivial software engineering problems and build robust, user-facing applications. This module integrates concepts across data structures, algorithms, error handling, and clean code principles.",
                    "explanation": """### Engineering Best Practices:
1. **DRY (Don't Repeat Yourself)**: Extract duplicated logic into reusable functions or classes.
2. **KISS (Keep It Simple, Stupid)**: Favor readable, explicit implementations over cryptic one-liners.
3. **PEP 8**: Follow standard Python conventions (snake_case functions, PascalCase classes, 4 spaces indentation).
4. **Defensive Validation**: Validate untrusted inputs at boundaries before executing core business logic.""",
                    "code_examples": [
                        {
                            "title": "Algorithmic Two-Sum Solution in O(N) Time",
                            "code": "def two_sum(numbers, target):\n    seen = {}  # val -> index\n    for idx, num in enumerate(numbers):\n        complement = target - num\n        if complement in seen:\n            return (seen[complement], idx)\n        seen[num] = idx\n    return None\n\nnums = [2, 7, 11, 15]\nres = two_sum(nums, 9)\nprint(f'Indices adding to 9 in {nums}: {res} (Values: {nums[res[0]]} + {nums[res[1]]})')",
                            "explanation": "High-efficiency hash map lookup finding two numbers summing to target in single pass O(N) time.",
                            "expected_output": "Indices adding to 9 in [2, 7, 11, 15]: (0, 1) (Values: 2 + 7)"
                        }
                    ],
                    "practice_questions": [
                        {
                            "id": 1,
                            "question": "What is the time complexity of searching for an element in a Python dictionary of size N?",
                            "options": ["O(N)", "O(log N)", "O(1) average", "O(N^2)"],
                            "correct_answer": 2,
                            "explanation": "Dictionaries use hash tables, giving O(1) constant average lookup time."
                        }
                    ]
                }
            }
        ]
    }
]
