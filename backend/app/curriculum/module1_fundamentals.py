# -*- coding: utf-8 -*-
"""
Module 1: Python Fundamentals (Variables & Operators)
5+ Pages In-Depth Systems Knowledge, Memory Layouts, Polyglot Comparisons,
Fullstack / Data Engineering Design Patterns, Edge Cases, and 10 Viva Q&As.
"""

MODULE_1 = {
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
        },
        {
            "slug": "operators",
            "name": "Operators & Expressions",
            "order": 2,
            "difficulty": "beginner",
            "icon": "🧮",
            "subtopics": [
                "Arithmetic Operators & Floor Division vs Truncation",
                "Short-Circuit Evaluation in Logical Expressions & Bytecode Mechanics",
                "Chained Comparisons & Mathematical Optimization",
                "Bitwise Operators, Bitmasks & Bloom Filters in Data Engineering",
                "Operator Precedence Hierarchy & Defensive Parenthesization"
            ],
            "learning_objectives": [
                "Analyze the exact differences between floor division (//), true division (/), and modulo (%) across positive and negative integers",
                "Master short-circuit evaluation semantics and inspect Python bytecode (JUMP_IF_FALSE_OR_POP)",
                "Apply chained comparisons for clean, idiomatic range validation",
                "Implement bitwise operators for high-throughput flag management and bitmask filters",
                "Eliminate precedence ambiguities in complex enterprise business logic"
            ],
            "lesson_content": {
                "introduction": "Operators are computational instructions that execute transformations upon operands. In Python, operators go far beyond elementary arithmetic: they encompass boolean short-circuit evaluation, bitwise memory manipulations, chained relational assertions, and dynamic protocol overloads via dunder methods like `__add__` and `__eq__`.\n\nIn this comprehensive module, we dissect operator precedence, explore how floor division differs from C and Java, analyze how Python's bytecode optimizes boolean expressions, and demonstrate how Data Engineers leverage bitwise masks for ultra-fast filtering.",
                "explanation": """### 1. Conceptual Architecture & Bytecode Mechanics

#### 1.1 Floor Division (`//`) vs. Truncation: Python vs C/C++/Java
In languages like C, C++, and Java, integer division performs **truncation towards zero**:
- C / Java: `7 / 2 = 3` and `-7 / 2 = -3` (the fractional part is discarded towards zero).
- In Python, `//` performs **floor division (rounding down towards negative infinity)**:
  - `7 // 2 = 3`
  - `-7 // 2 = -4` (because $-3.5$ rounded towards negative infinity is $-4$)

**Modulo Operator (`%`) Identity**:
Python guarantees the fundamental mathematical identity:
$$a = (a // b) \times b + (a \% b)$$

For $a = -7$ and $b = 2$:
$$-7 = (-7 // 2) \times 2 + (-7 \% 2) \implies -7 = (-4 \times 2) + 1 = -8 + 1 = -7$$
Therefore, in Python, `-7 % 2` produces `1` (always maintaining the sign of the divisor $b$), whereas in C and Java, `-7 % 2` produces `-1`!

#### 1.2 Bytecode Mechanics of Short-Circuit Evaluation
Python's `and` and `or` operators do not return `True` or `False`; they return the **actual operand value** that decided the expression!
- `a and b`: If `a` is falsy, returns `a`; otherwise evaluates and returns `b`.
- `a or b`: If `a` is truthy, returns `a`; otherwise evaluates and returns `b`.

Let's inspect the compiled bytecode using Python's `dis` module:
```python
import dis

def check(user):
    return user is not None and user.is_active

dis.dis(check)
```
Output:
```
  2           0 LOAD_FAST                0 (user)
              2 LOAD_CONST               0 (None)
              4 IS_OP                    1 (is not)
              6 JUMP_IF_FALSE_OR_POP     12
              8 LOAD_FAST                0 (user)
             10 LOAD_ATTR                0 (is_active)
        >>   12 RETURN_VALUE
```
Notice instruction `6 JUMP_IF_FALSE_OR_POP 12`: If `user is not None` evaluates to `False`, the virtual machine jumps immediately to line `12` (`RETURN_VALUE`), completely skipping `LOAD_ATTR (is_active)`. This prevents `AttributeError: 'NoneType' object has no attribute 'is_active'` at the hardware level!

---

### 2. Polyglot Comparative Operator Matrix

| Operator Category | Python 3.12+ | ANSI C (C99/C11) | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- | :--- |
| **True Division** | `/` (Always Float) | `(double)a / b` | `static_cast<double>(a) / b` | `(double)a / b` |
| **Integer Division** | `//` (Floor towards $-\infty$) | `/` (Truncates towards 0) | `/` (Truncates towards 0) | `/` (Truncates towards 0) |
| **Modulo (`-7 % 2`)** | `1` (Sign of divisor) | `-1` (Sign of dividend) | `-1` (Sign of dividend) | `-1` (Sign of dividend) |
| **Exponentiation** | `a ** b` | `pow(a, b)` (math.h) | `std::pow(a, b)` | `Math.pow(a, b)` |
| **Logical AND / OR** | `and`, `or` | `&&`, `\|\|` | `&&`, `\|\|` | `&&`, `\|\|` |
| **Bitwise Unsigned Shift** | Manual mask `& 0xFFFFFFFF` | `(unsigned)x >> n` | `static_cast<uint32_t>(x) >> n` | `>>>` (Triple Shift) |
| **Identity Comparison** | `is`, `is not` | `ptr1 == ptr2` | `ptr1 == ptr2` | `obj1 == obj2` |
| **Value Equality** | `==`, `!=` | `strcmp()` for strings | `==` (overloadable) | `.equals()` for objects |
| **Chained Comparison** | `1 <= x <= 10` | `1 <= x && x <= 10` | `1 <= x && x <= 10` | `1 <= x && x <= 10` |
| **Walrus Assignment** | `:=` (PEP 572) | Direct assignment in expr | Direct assignment in expr | Direct assignment in expr |

---

### 3. Comprehensive Operator Precedence Table

When Python evaluates expressions without explicit parentheses, it follows strict precedence rules:

| Rank | Operators | Description | Associativity |
| :---: | :--- | :--- | :---: |
| **1** | `()` | Parentheses (Grouping), Function Calls, Subscripts | Left-to-Right |
| **2** | `**` | Exponentiation | **Right-to-Left** |
| **3** | `+x`, `-x`, `~x` | Unary positive, negative, bitwise NOT | Right-to-Left |
| **4** | `*`, `/`, `//`, `%` | Multiplication, Division, Floor Div, Modulo | Left-to-Right |
| **5** | `+`, `-` | Addition, Subtraction | Left-to-Right |
| **6** | `<<`, `>>` | Bitwise Shifts | Left-to-Right |
| **7** | `&` | Bitwise AND | Left-to-Right |
| **8** | `^` | Bitwise XOR | Left-to-Right |
| **9** | `\|` | Bitwise OR | Left-to-Right |
| **10** | `==`, `!=`, `<`, `<=`, `>`, `>=`, `is`, `in` | Comparisons, Identity, Membership | Left-to-Right |
| **11** | `not` | Boolean NOT | Right-to-Left |
| **12** | `and` | Boolean AND | Left-to-Right |
| **13** | `or` | Boolean OR | Left-to-Right |
| **14** | `:=` | Walrus Assignment Expression | Right-to-Left |

> [!WARNING]
> **Right-to-Left Exponentiation**: `2 ** 3 ** 2` is evaluated as `2 ** (3 ** 2) = 2 ** 9 = 512`, NOT `(2 ** 3) ** 2 = 64`! Always use explicit parentheses for clarity.

---

### 4. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 4.1 Data Engineering: Bitmasks & Flags for Ultra-Fast Filtering
In high-throughput event processing (e.g. ad-tech or financial telemetry), storing statuses as string tags in database rows wastes immense memory and bandwidth. Senior engineers use **Bitwise Flags**:
```python
# Permission flags represented as bit positions (powers of 2):
READ_PRIVILEGE    = 1 << 0  # 0001 (1)
WRITE_PRIVILEGE   = 1 << 1  # 0010 (2)
EXECUTE_PRIVILEGE = 1 << 2  # 0100 (4)
ADMIN_PRIVILEGE   = 1 << 3  # 1000 (8)

# Grant READ and WRITE in a single 1-byte integer:
user_mask = READ_PRIVILEGE | WRITE_PRIVILEGE  # 0011 (3)

# O(1) Check if user has WRITE_PRIVILEGE:
has_write = bool(user_mask & WRITE_PRIVILEGE)  # True

# Revoke WRITE_PRIVILEGE:
user_mask &= ~WRITE_PRIVILEGE  # 0001 (1)
```

#### 4.2 Fullstack Pattern: The Walrus Operator in Streaming APIs
Introduced in PEP 572, the Walrus Operator (`:=`) allows assigning variables within expressions, eliminating duplicate function evaluations:
```python
# Streaming chunked upload handler:
def process_upload_stream(socket_reader):
    # Reads chunks and stops immediately when chunk is empty:
    while (chunk := socket_reader.read(4096)):
        process_chunk_buffer(chunk)
```

---

### 5. Common Production Pitfalls & Anti-Patterns

#### Anti-Pattern 1: Bitwise vs. Logical Operators Confusion
```python
# ❌ DANGEROUS BUG: Using bitwise '&' instead of logical 'and'
def validate_access(user, token):
    # If user is None, 'user is not None & user.has_token(token)' will STILL evaluate
    # the right-hand side because bitwise '&' has HIGHER precedence than comparison '!==',
    # triggering an immediate AttributeError crash!
    return user is not None & user.has_token(token)

# ✅ PRODUCTION FIX: Always use boolean 'and' with short-circuit evaluation
def validate_access_safe(user, token):
    return user is not None and user.has_token(token)
```

#### Anti-Pattern 2: Chained Comparisons with Function Call Side Effects
```python
# ❌ PERFORMANCE / BUG RISK:
if 0 < fetch_sensor_reading() < 100:
    # Notice: Python evaluates the middle expression ONLY ONCE, which is safe,
    # but in C/C++ this is a critical logic error: (0 < x) returns 1, then checks (1 < 100) -> always True!
    pass
```

---

### 6. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: Why does `-13 // 5` return `-3` in Python, while in C++ and Java it returns `-2`?
- **Answer**: Python adheres to mathematical floor division, which rounds down towards negative infinity: $-13 / 5 = -2.6 \to \lfloor -2.6 \rfloor = -3$. C++ and Java perform truncating division (rounding towards zero): $-2.6 \to -2$. Python's choice ensures that the modulo $a \% b$ always preserves the sign of the divisor $b$.

#### Q2: What is the exact difference between `and` and `&` in Python?
- **Answer**: `and` is a **short-circuit boolean logical operator** that operates on truth values. If the left operand is falsy, the right operand is never evaluated. `&` is a **bitwise AND operator** that performs bit-by-bit conjunction on integers or set intersection on sets. It evaluates both operands eagerly and does not short-circuit.

#### Q3: How does the Walrus Operator (`:=`) differ from standard assignment (`=`)?
- **Answer**: Standard assignment (`=`) is a statement in Python syntax; it does not yield a value and cannot be placed inside expressions (e.g. `if (x = 10):` causes `SyntaxError`). The Walrus operator (`:=`) is an **assignment expression** that assigns the variable and simultaneously evaluates to that assigned value, permitting assignment inside `if` conditions, `while` loops, and list comprehensions.

#### Q4: What does the expression `[] or {} or "default"` return and why?
- **Answer**: It returns `"default"`. Python's `or` operator inspects each operand from left to right. `[]` is falsy, so it moves to `{}`. `{}` is falsy, so it evaluates `"default"`, which is truthy, returning the string value directly rather than boolean `True`.

#### Q5: How do bitwise operators enable Bloom Filters in high-scale Data Engineering?
- **Answer**: A Bloom Filter is a space-efficient probabilistic data structure that tests set membership. It uses a bit array of size $m$ initialized to all zeros. When an item is inserted, $k$ independent hash functions compute bit indices, which are turned on using the bitwise OR operator (`bit_array |= (1 << hash_val)`). Checking membership uses bitwise AND (`bit_array & (1 << hash_val)`). If any bit is 0, the element is definitely not in the set.

#### Q6: Explain operator overloading in Python: What dunder methods correspond to `+`, `-`, and `*`?
- **Answer**: `+` invokes `__add__(self, other)` (or `__radd__` for reflected addition), `-` invokes `__sub__(self, other)`, and `*` invokes `__mul__(self, other)`. If the left operand does not support the operation with the right operand's type, it returns `NotImplemented`, causing Python to try the right operand's reflected method (`__radd__`).

#### Q7: Why is `x = x + [1]` significantly slower than `x += [1]` for a large list?
- **Answer**: `x = x + [1]` invokes `__add__`, which allocates a completely new list in memory, copies all existing elements from `x`, appends `1`, and rebinds `x` (an $O(N)$ operation). In contrast, `x += [1]` invokes `__iadd__`, which mutates the existing list in-place via `list.extend()` without reallocating or copying existing items (an $O(1)$ amortized operation).

#### Q8: What is Operator Precedence vs. Operator Associativity?
- **Answer**: **Precedence** determines which operator is evaluated first when operators of different ranks are present (e.g., `*` has higher precedence than `+`). **Associativity** determines the order of evaluation when operators have the **same** precedence. Most operators are left-associative (`a - b - c` evaluates as `(a - b) - c`), but exponentiation (`**`) and assignment (`=`, `:=`) are right-associative.

#### Q9: Can you overload short-circuit boolean operators `and` and `or` in Python classes?
- **Answer**: No. `and`, `or`, and `not` cannot be overloaded with dunder methods. This design decision guarantees that short-circuit evaluation semantics are universally preserved across all Python code. You can only customize how your custom class evaluates to truth or falsity via the `__bool__()` (or `__len__()`) dunder method.

#### Q10: How does Python prevent catastrophic recursion in reflected operators (`__radd__`)?
- **Answer**: When evaluating `a + b`, Python first calls `type(a).__add__(a, b)`. If that method returns `NotImplemented`, Python checks if `type(b)` is a subclass of `type(a)` or provides `__radd__`. If `b.__radd__(a)` also returns `NotImplemented`, Python halts immediately and raises `TypeError: unsupported operand type(s) for +`, preventing infinite mutual invocation."""
            },
            "code_examples": [
                {
                    "title": "Arithmetic Operators & Floor Division Mechanics",
                    "code": "a = 17\nb = 5\n\nprint(f'True Division (a / b): {a / b}')\nprint(f'Floor Division (a // b): {a // b}')\nprint(f'Modulo Remainder (a % b): {a % b}')\n\n# Negative floor division behavior\nneg_a = -17\nprint(f'Negative Floor (-17 // 5): {neg_a // 5}')\nprint(f'Negative Modulo (-17 % 5): {neg_a % 5}')",
                    "explanation": "Illustrates the exact difference between float division, integer floor division, and negative modulo calculations.",
                    "expected_output": "True Division (a / b): 3.4\nFloor Division (a // b): 3\nModulo Remainder (a % b): 2\nNegative Floor (-17 // 5): -4\nNegative Modulo (-17 % 5): 3"
                },
                {
                    "title": "Short-Circuit Logical Guards & Bitwise Masking",
                    "code": "user = {'name': 'Alice', 'role': 'admin', 'permissions': 0b0101}\n\n# Safe short-circuit guard\nis_authorized = user is not None and user.get('role') == 'admin'\nprint(f'Admin Authorized: {is_authorized}')\n\n# Bitwise mask check: 0b0100 (Read) and 0b0001 (Execute)\nCAN_EXECUTE = 0b0001\nhas_exec = bool(user['permissions'] & CAN_EXECUTE)\nprint(f'Has Execution Privilege: {has_exec}')",
                    "explanation": "Demonstrates safe guard conditions avoiding null pointers and bitwise mask conjunctions.",
                    "expected_output": "Admin Authorized: True\nHas Execution Privilege: True"
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "What is the result of the expression: -14 // 4 in Python?",
                    "options": ["-3", "-4", "-3.5", "-2"],
                    "correct_answer": 1,
                    "explanation": "Floor division rounds down towards negative infinity. -14 / 4 is -3.5, and the nearest integer towards negative infinity is -4."
                },
                {
                    "id": 2,
                    "question": "What is the evaluated output of: 2 ** 3 ** 2?",
                    "options": ["64", "512", "256", "128"],
                    "correct_answer": 1,
                    "explanation": "Exponentiation (**) is right-associative in Python, so it is evaluated as 2 ** (3 ** 2) = 2 ** 9 = 512."
                }
            ],
            "practical_challenge": {
                "prompt": "Write a function is_in_range(val, low, high) that uses chained comparisons to return True if val is between low and high inclusive.",
                "starter_code": "def is_in_range(val, low, high):\n    # Return True if low <= val <= high\n    pass",
                "test_call": "is_in_range(50, 10, 100)",
                "expected": "True"
            }
        }
    ]
}
