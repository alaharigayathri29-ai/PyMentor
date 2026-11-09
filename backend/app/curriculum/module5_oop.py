# -*- coding: utf-8 -*-
"""
Module 5: Object-Oriented Programming (OOP) Architecture
5+ Pages In-Depth Systems Knowledge, Metaclasses, MRO (C3 Linearization),
Vtables, Design Patterns (Factory, Strategy, Repository), and 10 Viva Q&As.
"""

MODULE_5 = {
    "module_number": 5,
    "module_name": "Object-Oriented Programming",
    "description": "Master object-oriented design, dynamic dispatch, class internals (__slots__), and production design patterns.",
    "icon": "🏛️",
    "topics": [
        {
            "slug": "oop",
            "name": "Object-Oriented Architecture & Design Patterns",
            "order": 1,
            "difficulty": "intermediate",
            "icon": "🏗️",
            "subtopics": [
                "Object Memory Architecture: __dict__ Overhead vs __slots__ C-Level Structs",
                "Multiple Inheritance & Method Resolution Order (C3 Linearization Algorithm)",
                "Dunder / Magic Protocols (__init__, __repr__, __eq__, __hash__, __enter__)",
                "Polyglot Comparison: Python Dynamic Dispatch vs C++ Vtables vs Java Interfaces",
                "Enterprise Fullstack & Data Engineering Design Patterns (Factory, Repository, Strategy)"
            ],
            "learning_objectives": [
                "Understand Python's object model and contrast instance __dict__ with memory-efficient __slots__",
                "Trace method resolution in multiple inheritance hierarchies using the C3 Linearization Algorithm (mro())",
                "Implement key object protocols including equality (__eq__), hashability (__hash__), and string representation",
                "Compare Python's duck typing and dynamic dispatch with C++ virtual method tables (vtables) and Java interfaces",
                "Apply enterprise OOP patterns (Repository, Factory, Strategy) in fullstack microservice architectures"
            ],
            "lesson_content": {
                "introduction": "Object-Oriented Programming (OOP) is a paradigm for modeling complex business domains through encapsulated state and behaviors. In Python, OOP is radically dynamic: classes are themselves first-class objects created at runtime by metaclasses (`type`), attributes are resolved through dynamic hash tables, and polymorphism is governed by **Duck Typing**.\n\nIn this comprehensive module, we dissect CPython's object layout, explain how `__slots__` eliminates 70% of instance memory, calculate Method Resolution Order (MRO) using C3 Linearization, compare dynamic dispatch with C++ virtual method tables and Java bytecode `invokevirtual`, and implement enterprise software design patterns.",
                "explanation": """### 1. Conceptual Architecture: CPython Object Model Internals

#### 1.1 The Default Instance: `__dict__` Memory Overhead
By default, every instance of a standard Python class allocates a dynamic dictionary (`__dict__`) to store its attributes:
```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s = Student("Gayatri", 21)
print(s.__dict__)  # {'name': 'Gayatri', 'age': 21}
```
**The Problem**: A dictionary is a complex hash table. On a 64-bit OS, each instance dictionary consumes **104+ bytes** of RAM, plus the object header (16 bytes). If your system instantiates 1,000,000 student records in memory, you waste over **120MB of RAM** solely on hash table overhead!

#### 1.2 The Production Solution: `__slots__`
By defining `__slots__`, you instruct CPython **NOT** to create an instance `__dict__`. Instead, CPython allocates a fixed-size C array of pointers directly inside the object's memory struct:
```python
class StudentOptimized:
    __slots__ = ('name', 'age')  # Directly inlines pointer slots!
    def __init__(self, name, age):
        self.name = name
        self.age = age
```
**Benefits**:
1. **Memory Reduction**: Cuts memory from ~152 bytes per instance down to **48 bytes** (a 68% RAM reduction!).
2. **Speed**: Attribute access (`LOAD_ATTR`) bypasses dictionary hashing and reads from fixed memory offsets, executing ~20% faster.
3. **Safety**: Prevents accidental dynamic attribute typos (`s.ag = 22` raises `AttributeError`).

#### 1.3 Multiple Inheritance & C3 Linearization Algorithm (MRO)
Python supports multiple inheritance. When multiple parent classes define the same method, Python determines search order using the **C3 Linearization Algorithm** (invoked via `Class.mro()`):
- **Monotonicity**: If class A precedes class B in parent class list, A precedes B in all subclasses.
- **Local Precedence**: Direct parents are checked from left to right.
- **Single Inheritance Root**: All classes inherit from `object`.

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.mro())
# [D, B, C, A, object]
# Python guarantees B and C are searched before their common ancestor A!
```

---

### 2. Polyglot Comparative Syntax & OOP Matrix

| Dimension | Python 3.12+ | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- |
| **Dispatch Mechanism** | Dynamic Duck Typing | Virtual Method Table (Vtable) | `invokevirtual` / `invokeinterface` |
| **Multiple Inheritance** | Full (C3 Linearization) | Full (Virtual Base classes) | Single Class + Multiple Interfaces |
| **Encapsulation** | Public / Name Mangling (`__var`) | `public`, `protected`, `private` | `public`, `protected`, `private`, package |
| **Abstract Classes** | `abc.ABC` & `@abstractmethod` | Pure Virtual (`= 0`) | `abstract class` / `interface` |
| **Memory Layout** | Heap `PyObject` + `__dict__` or slots | Inline Memory (Stack or Heap) | Heap `Object` Header (12-16 bytes) |
| **Metaprogramming** | Metaclasses (`type`), `__init_subclass__` | Template Metaprogramming | Reflection / Bytecode Agents |
| **Value Objects** | `@dataclass(frozen=True)` | Structs / Constexpr | `record Point(int x, int y)` |

---

### 3. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 3.1 The Repository Pattern for Database Abstraction
In enterprise microservices, never couple SQL/ORM queries directly into API endpoints. Use the **Repository Pattern**:
```python
from abc import ABC, abstractmethod

class StudentRepository(ABC):
    @abstractmethod
    def get_by_id(self, student_id: int):
        pass

    @abstractmethod
    def save(self, student: dict):
        pass

# Production Implementation with Postgres / SQLAlchemy:
class PostgresStudentRepository(StudentRepository):
    def __init__(self, db_session):
        self.session = db_session

    def get_by_id(self, student_id: int):
        return self.session.query(StudentModel).filter_by(id=student_id).first()

    def save(self, student: dict):
        self.session.add(StudentModel(**student))
        self.session.commit()
```

#### 3.2 The Strategy Pattern for Dynamic Billing & Algorithms
```python
class TaxCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, subtotal: float) -> float:
        pass

class DomesticTax(TaxCalculationStrategy):
    def calculate(self, subtotal: float) -> float:
        return subtotal * 0.0825

class InternationalTax(TaxCalculationStrategy):
    def calculate(self, subtotal: float) -> float:
        return subtotal * 0.15

class InvoiceContext:
    def __init__(self, strategy: TaxCalculationStrategy):
        self.strategy = strategy

    def compute_total(self, subtotal: float) -> float:
        return subtotal + self.strategy.calculate(subtotal)
```

---

### 4. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What is the purpose of `self` in Python class methods? Why is it explicit?
- **Answer**: `self` is a reference to the specific instance of the class upon which a method is invoked. In C++ and Java, this pointer is passed implicitly (`this`). In Python, `self` is explicitly declared as the first parameter of instance methods to adhere to the Zen of Python ("Explicit is better than implicit"). When calling `s.study()`, CPython translates this syntactically to `Student.study(s)`.

#### Q2: What is the difference between `@classmethod`, `@staticmethod`, and standard instance methods?
- **Answer**:
  - **Instance Method**: Receives the instance `self` as its first argument; can read and mutate both instance and class state.
  - **Class Method (`@classmethod`)**: Receives the class `cls` as its first argument; used for alternative constructors and factory methods (e.g. `Student.from_json(data)`).
  - **Static Method (`@staticmethod`)**: Receives neither `self` nor `cls`; behaves like an ordinary function placed within the class's namespace for logical grouping.

#### Q3: What is Name Mangling in Python? Is private state strictly protected?
- **Answer**: In Python, prefixing an attribute with two leading underscores (e.g. `__secret`) triggers **name mangling**. CPython automatically rewrites the attribute name to `_ClassName__secret` to prevent accidental name collisions in subclasses. However, it does NOT enforce strict security: calling `instance._ClassName__secret` still accesses the value. Python operates on the philosophy of "We are all consenting adults here."

#### Q4: What is the C3 Linearization Algorithm and how does it prevent the "Diamond Problem"?
- **Answer**: The Diamond Problem occurs when class D inherits from B and C, which both inherit from base class A. If both B and C override a method from A, which one should D inherit? Python resolves this using the **C3 Linearization Algorithm**, which produces a monotonic order preserving the relative precedence of parent classes from left to right while ensuring no class is visited before its children.

#### Q5: How do `__slots__` optimize memory and attribute access speed?
- **Answer**: `__slots__` replaces the instance `__dict__` with a fixed-size C array of pointers stored directly inside the object's struct. This eliminates the 100+ byte hash table overhead per instance, reducing memory by ~60-70%. It also accelerates attribute access because CPython reads from a known memory offset (`ob_item[offset]`) rather than performing hash table lookups.

#### Q6: What is Duck Typing and how does it relate to Python's Protocol architecture?
- **Answer**: Duck Typing comes from the adage: "If it walks like a duck and quacks like a duck, it's a duck." In Python, code does not verify whether an object belongs to a specific class hierarchy (`isinstance`). Instead, it checks whether the object implements the required methods or behaviors. For example, any object implementing `read()` can be treated as a file, regardless of whether it inherits from `io.IOBase`.

#### Q7: What are Dunder (Magic) Methods and how do they enable operator overloading?
- **Answer**: Dunder (Double Underscore) methods are special methods defined by the Python language protocol that allow user-defined classes to hook into core language features: `__add__` for `+`, `__getitem__` for indexing `obj[key]`, `__len__` for `len()`, `__enter__`/`__exit__` for context managers (`with`), and `__call__` to make instances callable like functions.

#### Q8: What is the difference between `__repr__()` and `__str__()`?
- **Answer**:
  - `__repr__()`: Aims to be unambiguous, detailed, and ideally reproducible code (e.g., `Point(x=10, y=20)`). Designed for developers and debugging.
  - `__str__()`: Aims to be readable, concise, and user-friendly (e.g., `"Point at (10, 20)"`). Invoked by `print()` and `str()`. If `__str__` is not defined, Python falls back to `__repr__`.

#### Q9: What is a Metaclass in Python? How does it differ from a standard class?
- **Answer**: A class defines how an instance of that class behaves. A **Metaclass** defines how a **class itself** behaves. In Python, classes are instances of metaclasses. The default metaclass in Python is `type`. Metaclasses can intercept class creation (`__new__`, `__init__`), validate class attributes, register classes in global registries, and generate boilerplate methods (as used in ORMs like SQLAlchemy and Django).

#### Q10: How does Python's `@dataclass` work and what boilerplate does it automate?
- **Answer**: Introduced in Python 3.7 (PEP 557), `@dataclass` inspects class type annotations and automatically generates standard boilerplate methods: `__init__()`, `__repr__()`, `__eq__()`, and optionally `__hash__()` and comparison operators. Using `@dataclass(slots=True, frozen=True)` generates an immutable, memory-efficient data transfer object with $O(1)$ attribute access."""
            },
            "code_examples": [
                {
                    "title": "Slots Optimization vs Standard Dict Memory Footprint",
                    "code": "import sys\n\nclass RegularStudent:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\nclass SlottedStudent:\n    __slots__ = ('name', 'age')\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\nreg = RegularStudent('Alice', 20)\nslot = SlottedStudent('Alice', 20)\n\nprint(f'Regular Student Object RAM: {sys.getsizeof(reg)} + {sys.getsizeof(reg.__dict__)} bytes')\nprint(f'Slotted Student Object RAM: {sys.getsizeof(slot)} bytes (No __dict__!)')",
                    "explanation": "Illustrates how __slots__ eliminates the instance dictionary and saves massive RAM.",
                    "expected_output": "Regular Student Object RAM: 48 + 104 bytes\nSlotted Student Object RAM: 48 bytes (No __dict__!)"
                },
                {
                    "title": "Multiple Inheritance & Method Resolution Order (MRO)",
                    "code": "class BaseService:\n    def execute(self):\n        return 'Base'\n\nclass LoggingMixin(BaseService):\n    def execute(self):\n        return f'[LOG] {super().execute()}'\n\nclass MetricsMixin(BaseService):\n    def execute(self):\n        return f'[METRIC] {super().execute()}'\n\nclass UserApplication(LoggingMixin, MetricsMixin):\n    pass\n\napp = UserApplication()\nprint('Resolved Output:', app.execute())\nprint('Class MRO Sequence:', [c.__name__ for c in UserApplication.mro()])",
                    "explanation": "Demonstrates C3 Linearization and cooperative multiple inheritance with super().",
                    "expected_output": "Resolved Output: [LOG] [METRIC] Base\nClass MRO Sequence: ['UserApplication', 'LoggingMixin', 'MetricsMixin', 'BaseService', 'object']"
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "Which attribute on a Python class displays the computed C3 Linearization method search order?",
                    "options": ["__order__", "__mro__", "__hierarchy__", "__path__"],
                    "correct_answer": 1,
                    "explanation": "The __mro__ (Method Resolution Order) attribute or .mro() method displays the inheritance search path."
                },
                {
                    "id": 2,
                    "question": "What is the primary architectural benefit of defining __slots__ in a Python class?",
                    "options": [
                        "Prevents the class from being inherited",
                        "Eliminates the instance __dict__ to reduce memory footprint by ~60-70%",
                        "Forces all methods to execute asynchronously",
                        "Enables automatic encryption of instance attributes"
                    ],
                    "correct_answer": 1,
                    "explanation": "__slots__ eliminates the per-instance __dict__ hash table, saving significant memory and speeding up attribute access."
                }
            ],
            "practical_challenge": {
                "prompt": "Create a class Vector2D(x, y) with __slots__ = ('x', 'y') implementing __add__(self, other) to return a new Vector2D with summed coordinates.",
                "starter_code": "class Vector2D:\n    __slots__ = ('x', 'y')\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n    # Implement __add__\n    pass",
                "test_call": "(Vector2D(10, 20) + Vector2D(5, 5)).x",
                "expected": "15"
            }
        }
    ]
}

