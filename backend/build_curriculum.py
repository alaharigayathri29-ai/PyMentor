"""
Full Curriculum Generator
Generates textbook-grade, 5+ page equivalent chapters for all 14 curriculum topics.
Deep low-level systems theory, CPython vs JVM vs Native C/C++ memory models,
Polyglot comparison tables, enterprise fullstack & data engineering design patterns,
subtle edge-case anti-patterns, and 10 detailed interview questions with model answers per topic.
"""
import json
import sys
import os

OUTPUT_FILE = r"D:\ch work\ai-mentor\backend\app\curriculum_data.py"

def get_module_1():
    return {
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
                    "Memory Pointer Reference Model & CPython PyObject Layout",
                    "Stack vs Heap: Dynamic Binding in Python vs Static Allocation in C/C++/Java",
                    "Built-in Primitives: int, float, str, bool & Small Integer Caching",
                    "Type Casting, Duck Typing, and Type Safety in Enterprise Systems",
                    "Memory Optimization, Pointer Chasing, and Cache Locality in Data Engineering"
                ],
                "learning_objectives": [
                    "Understand how Python manages heap memory references via PyObject pointers rather than fixed-size memory slots",
                    "Compare Python's dynamic typing with C/C++ scalar variables and Java primitive/reference types",
                    "Analyze memory overhead of PyObject pointers compared to contiguous native memory",
                    "Safely cast values between types using defensive validation without data truncation or precision loss",
                    "Identify subtle production bugs including IEEE 754 floating-point inaccuracies, object aliasing, and variable shadowing"
                ],
                "lesson_content": {
                    "introduction": "In Python, variables are fundamentally different from compiled languages like C, C++, or Java. Variables are **symbolic pointer references (names)** bound to dynamic **objects allocated on the heap**, rather than named memory containers of fixed size.\n\nTo build scalable software as a Fullstack or Data Engineer, you must master how CPython represents objects internally (`PyObject`), how reference counting and generational garbage collection reclaim unused memory, how integer caching works under the hood, and how data structures scale across the memory hierarchy.",
                    "explanation": """### 1. Conceptual Architecture & Low-Level Memory Mechanics

#### 1.1 The CPython `PyObject` Structure
Every entity in Python—whether an integer, string, function, or class—is represented internally in CPython as a C struct called `PyObject` (or `PyVarObject` for variable-length items like strings and lists).

In the CPython source code (`Include/object.h`), `PyObject` is defined as:
```c
struct _object {
    _PyObject_HEAD_EXTRA // Double-linked list pointers for debug tracing
    Py_ssize_t ob_refcnt; // Reference count (64-bit integer on 64-bit OS = 8 bytes)
    struct _typeobject *ob_type; // Pointer to the type descriptor object = 8 bytes
};
```

When you declare an integer in Python:
```python
x = 42
```
Python allocates a `PyLongObject` on the private heap:
1. `ob_refcnt`: Initialized to `1` (or incremented if already cached).
2. `ob_type`: Points to `<class 'int'>`.
3. `ob_size`: Stores the number of 30-bit digits (or sign flag).
4. `ob_digit[1]`: Array containing the actual value `42`.

**Total Memory Cost:** A native C `int32_t` requires exactly **4 bytes** of memory. In contrast, a Python integer requires **28 bytes** on a 64-bit machine!
- 8 bytes for `ob_refcnt`
- 8 bytes for `ob_type` pointer
- 8 bytes for `ob_size`
- 4 bytes for the actual digit representation

#### 1.2 Stack vs. Heap Allocation Comparison
- **C / C++**: Local variables like `int x = 42;` reside directly inside the thread's **Stack Frame**. When the enclosing function scope exits, the stack pointer increments (`SP + 4`), and the memory is instantaneously reclaimed in $O(1)$ time with zero garbage collection overhead.
- **Java**: Primitive types (`int`, `double`, `boolean`) reside on the stack. Objects (`Integer`, `String`, custom classes) reside on the JVM Heap. References (4 or 8 bytes) reside on the stack pointing to heap headers.
- **Python**: **Everything resides on the Heap**. The local stack frame contains only a hash table (or fast local array of pointers `fastlocals` in the evaluation loop) storing pointers to `PyObject` structures on the heap.

```
       PYTHON MEMORY MODEL                   NATIVE C MEMORY MODEL
┌─────────────────────────────────┐      ┌─────────────────────────┐
│ STACK: Local Namespace Pointer  │      │ STACK: Direct Storage   │
│ x ───► [ 0x7ffd9820a100 ]       │      │ x: [ 0000000000101010 ] │ (4 bytes)
└──────────────┬──────────────────┘      └─────────────────────────┘
               │ (Points to Heap)
┌──────────────▼──────────────────┐
│ HEAP: PyLongObject (28 bytes)   │
│ ├─ ob_refcnt: 1                 │
│ ├─ ob_type: <class 'int'>       │
│ ├─ ob_size: 1                   │
│ └─ ob_digit: 42                 │
└─────────────────────────────────┘
```

#### 1.3 Small Integer Caching & String Interning
To prevent constant heap allocation and deallocation for ubiquitous numbers, CPython implements an optimization called **Small Integer Caching**:
- CPython pre-allocates an array of `PyLongObject` singletons for all integers in the range **`[-5, 256]`** during interpreter initialization.
- When any code creates an integer in this range, Python returns the existing singleton pointer:
```python
a = 100
b = 100
print(a is b)  # True — Identical pointer address in memory!

c = 1000
d = 1000
print(c is d)  # False — Independent heap allocations (id(c) != id(d))
```

---

### 2. Polyglot Comparative Syntax & Performance Matrix

| Dimension | Python 3.12+ | ANSI C (C99/C11) | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- | :--- |
| **Type System** | Dynamic, Strong | Static, Weak | Static, Strong | Static, Strong |
| **Variable Declaration** | `x = 100` | `int x = 100;` | `int x = 100;` or `auto x = 100;` | `int x = 100;` or `var x = 100;` |
| **Memory Allocation** | Heap (`PyObject`) | Stack (or `malloc`) | Stack (or `new` / RAII) | Stack (primitives) / Heap (objects) |
| **Memory Size of int** | 28 bytes | 4 bytes | 4 bytes | 4 bytes (primitive `int`) |
| **Integer Overflow** | Unlimited (Arbitrary Precision) | Undefined Behavior | Undefined Behavior | Wraps around ($2^{31}-1 \to -2^{31}$) |
| **Garbage Collection** | Ref Counting + Generational GC | Manual (`free()`) | RAII (`std::unique_ptr`) | Automatic Tracing GC (G1GC/ZGC) |
| **Constant Declaration** | `FINAL_VAR: Final[int] = 10` | `const int x = 10;` | `constexpr int x = 10;` | `final int x = 10;` |
| **Null / Nil Sentinel** | `None` (Singleton) | `NULL` / `0` | `nullptr` | `null` |

---

### 3. Comprehensive Language Specification & Built-in Primitives

#### 3.1 Primitive Types Breakdown
1. **`int` (Arbitrary-Precision Integer)**:
   - There is no 32-bit or 64-bit integer ceiling in Python 3. Integers automatically grow to consume available RAM.
   - Example: `2 ** 128` computes instantaneously without overflow errors.
2. **`float` (IEEE 754 Double Precision)**:
   - Stored as a 64-bit double precision float (53 bits of mantissa, 11 bits of exponent, 1 sign bit).
   - Precision: ~15 to 17 significant decimal digits.
   - Special sentinels: `float('inf')`, `float('-inf')`, `float('nan')`.
3. **`str` (Immutable Unicode Sequence)**:
   - Optimized via PEP 393: Python uses Latin-1 (1 byte/char), UCS-2 (2 bytes/char), or UCS-4 (4 bytes/char) based on the highest codepoint in the string to conserve RAM.
4. **`bool` (Boolean Truth Values)**:
   - Direct subclass of `int`. `True == 1` and `False == 0`.
   - Singletons: Only two boolean instances exist in the entire Python runtime.

#### 3.2 Type Inspection & Defensive Casting
```python
# Safe type checking respecting inheritance:
if isinstance(payload_value, (int, float)):
    processed = float(payload_value)
else:
    raise TypeError(f"Expected numeric payload, got {type(payload_value).__name__}")
```

---

### 4. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 4.1 Data Engineering: The "Pointer Chasing" Problem
When processing 10 million rows in an ETL pipeline:
- A standard Python `list[int]` creates a contiguous array of **pointers** (`PyObject*`), each pointing to an isolated 28-byte `PyLongObject` scattered randomly across the heap.
- **Cache Invalidation**: The CPU cannot prefetch these scattered memory blocks into L1/L2 CPU cache. Every element lookup causes a CPU cache miss, taking ~200 CPU cycles.
- **Engineering Solution**: Use contiguous native memory arrays like NumPy `ndarray`, PyArrow, or Polars:
```python
import numpy as np

# Native contiguous C memory buffer: exactly 4 bytes per integer!
# Direct SIMD vectorized CPU execution with zero cache misses.
sensor_readings = np.zeros(10_000_000, dtype=np.int32)
```

#### 4.2 Fullstack Pattern: Immutable Config DTOs
In enterprise microservices, mutable global variables lead to race conditions. Use frozen dataclasses or typed dictionaries:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    host: str
    port: int
    pool_size: int = 20
    timeout_seconds: float = 5.0
```

---

### 5. Common Production Pitfalls & Undefined Behaviors

#### Anti-Pattern 1: Floating-Point Equality Checks
```python
# ❌ BUG: Base-2 binary floating point approximation error
def is_account_balanced(credit: float, debit: float) -> bool:
    return (credit - debit) == 0.0  # Fails when 0.1 + 0.2 != 0.3!

# ✅ PRODUCTION FIX: Use math.isclose or decimal.Decimal for monetary calculations
from decimal import Decimal
import math

def is_account_balanced_safe(credit: float, debit: float) -> bool:
    return math.isclose(credit, debit, rel_tol=1e-9)

# For financial and banking transactions:
from decimal import Decimal
price = Decimal('19.99')
tax = Decimal('0.0825')
total = price * (Decimal('1') + tax)  # Exact decimal arithmetic
```

#### Anti-Pattern 2: Overriding Built-in Type Names
```python
# ❌ PRODUCTION HAZARD: Shadows built-in type
def process_data(list, str):
    return str(list)  # Crashes with TypeError: 'str' object is not callable!

# ✅ PRODUCTION FIX: Use descriptive domain-specific names
def process_data_safe(items: list, serializer_label: str):
    return f"{serializer_label}: {len(items)} records"
```

---

### 6. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What is the exact difference between `==` and `is` in Python?
- **Answer**: `==` checks for **value equality** by invoking the left operand's `__eq__()` method (e.g. comparing if two separate lists contain the same items). In contrast, `is` checks for **identity equality** by comparing the memory addresses of the two object pointers (`id(a) == id(b)`). In C terms, `a is b` translates directly to `pointer_a == pointer_b`.

#### Q2: Why does `0.1 + 0.2 == 0.3` evaluate to `False` in Python, C++, and Java?
- **Answer**: Floating-point numbers are stored in hardware conforming to IEEE 754 binary floating-point representation. Fractions like $0.1$ ($1/10$) and $0.2$ ($1/5$) cannot be represented as finite terminating binary fractions in base 2 (just as $1/3$ cannot be represented as a finite decimal in base 10). They become repeating binary expansions rounded to 53 bits of precision. The sum `0.1 + 0.2` produces `0.30000000000000004440892098500626...`, which does not match the binary encoding of `0.3`.

#### Q3: How does CPython's Memory Manager optimize integer memory allocation?
- **Answer**: CPython employs small integer caching (`small_ints` array) pre-allocated for integers between $-5$ and $256$ inclusive. Whenever an integer in this range is created, CPython bypasses `PyObject_Malloc()` and returns an existing reference from this static table, saving memory allocations and improving cache hit rates.

#### Q4: What is the GIL (Global Interpreter Lock) and how does it relate to variable reference counting?
- **Answer**: CPython manages object lifetimes using reference counting (`ob_refcnt`). In a multi-threaded application, concurrent modifications to `ob_refcnt` could trigger race conditions, resulting in memory leaks or premature deallocation (dangling pointers). The GIL is a mutual-exclusion lock that guarantees only one native OS thread executes Python bytecode at any given moment, protecting reference counts from thread race conditions without needing granular per-object locks.

#### Q5: How do `__slots__` optimize class memory layout?
- **Answer**: By default, each Python object instance stores its attributes in a dynamic dictionary (`__dict__`). A dictionary has substantial memory overhead (minimum 100+ bytes due to hash table buckets). Defining `__slots__ = ('name', 'age')` removes `__dict__` and allocates a fixed-size C array of pointers for instance attributes directly within the object struct, reducing instance memory by ~60-70% and accelerating attribute access.

#### Q6: Explain Python's Type System: Is Python Strong or Weak? Static or Dynamic?
- **Answer**: Python is **Dynamically Typed** because types are associated with values (objects) at runtime, not with variable names during compilation. However, Python is **Strongly Typed** because it enforces strict type discipline: the interpreter will not silently coerce types into invalid operations (e.g., `'10' + 5` raises `TypeError`, whereas in weakly typed JavaScript it produces `'105'`).

#### Q7: Does Python support integer overflow? How does it handle massive numbers like $2^{1000}$?
- **Answer**: In Python 3, `int` is of arbitrary precision. Unlike C/C++ (where `int32` overflows beyond $2,147,483,647$) or Java (where `long` overflows at $2^{63}-1$), CPython represents large integers as variable-length arrays of 30-bit digits (`ob_digit[]`). As numbers grow, Python dynamically reallocates more digit chunks, bounded only by system RAM.

#### Q8: What is Variable Shadowing and how can linters detect it?
- **Answer**: Variable shadowing occurs when a variable declared in an inner scope (such as a local function variable or loop variable) has the same name as a variable in an outer scope (such as global namespace or built-in functions). This makes the outer variable inaccessible within the inner scope. Linters like Flake8, Ruff, or PyLint flag this with warnings like `redefined-builtin` or `shadowed-variable`.

#### Q9: What happens under the hood when you execute `a = b = []`?
- **Answer**: Both identifiers `a` and `b` are bound to the **exact same mutable list object** in heap memory (`id(a) == id(b)`). Mutating `a` via `a.append(1)` will immediately reflect in `b` (`b == [1]`), because neither variable owns a unique copy; they are two pointers referencing the same memory block. To create distinct objects, use `a = []; b = []` or `b = a.copy()`.

#### Q10: How does Python's Garbage Collector resolve circular references that reference counting cannot reclaim?
- **Answer**: Reference counting handles 99% of deallocations in $O(1)$ time when `ob_refcnt` hits zero. However, circular references (e.g. object A points to B, and B points back to A) prevent `ob_refcnt` from ever reaching zero. CPython solves this using a **Cyclic Generational Garbage Collector** (`gc` module) that divides objects into three generations (Gen 0, 1, 2). It periodically inspects container objects, subtracts internal references, identifies unreachable isolated reference cycles, and reclaims their memory."""
                },
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
        ]
    }
