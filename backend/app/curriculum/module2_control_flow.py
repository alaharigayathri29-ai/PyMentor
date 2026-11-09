# -*- coding: utf-8 -*-
"""
Module 2: Control Flow (Conditions & Loops)
5+ Pages In-Depth Systems Knowledge, Branch Prediction, Iterator Protocol,
Memory Streaming, Polyglot Comparisons, Production Patterns, and 10 Viva Q&As.
"""

MODULE_2 = {
    "module_number": 2,
    "module_name": "Control Flow",
    "description": "Master branching conditionals, pattern matching, iteration protocols, and loop optimizations.",
    "icon": "🔀",
    "topics": [
        {
            "slug": "conditions",
            "name": "Conditional Statements",
            "order": 1,
            "difficulty": "beginner",
            "icon": "⚖️",
            "subtopics": [
                "Branch Prediction & CPU Instruction Pipelining Mechanics",
                "Conditional Dispatch: if / elif / else vs Structural Pattern Matching (PEP 634)",
                "Ternary Expressions, Truthiness Tables & False Equivalence",
                "Polyglot Comparison: Python match/case vs C/C++ switch jump tables vs Java switch expressions",
                "Production Data Engineering: Vectorized Masking vs Scalar Branching"
            ],
            "learning_objectives": [
                "Understand CPU branch prediction and speculative execution overhead in branching control flow",
                "Implement structural pattern matching (match/case) with guards, sequence destructuring, and class patterns",
                "Utilize idiomatic ternary expressions (a if cond else b) for concise inline assignments",
                "Master Python truthiness evaluation rules across empty containers, custom classes (__bool__), and None",
                "Avoid branch mispredictions in high-throughput data processing via vectorized boolean masks"
            ],
            "lesson_content": {
                "introduction": "Conditional execution represents the fundamental decision-making capability of computing systems. In high-performance software engineering, branching is not merely an `if/else` syntactical construct—it directly influences CPU instruction pipelines, branch target buffers (BTB), and cache locality.\n\nPython 3.10 introduced **Structural Pattern Matching (`match/case`)**, providing algebraic data type destructuring comparable to Scala, Rust, and Haskell. In this deep dive, we examine the hardware costs of branching, structural pattern matching, polyglot conditional architectures, and vectorized data filtering.",
                "explanation": """### 1. Conceptual Architecture & Hardware Branch Prediction

#### 1.1 CPU Instruction Pipelining & Branch Misprediction
Modern CPUs achieve gigahertz clock rates through deep instruction pipelines (typically 14 to 20 stages). The CPU fetches and decodes instructions dozens of cycles before they are executed.
- When the CPU encounters a conditional jump (`if x > 0`), it cannot know with certainty which branch will be taken until previous instructions complete.
- **Branch Predictor**: Modern CPUs use sophisticated hardware predictors (such as Two-Level Adaptive Predictors or TAGE predictors) that track execution history in a Branch Target Buffer (BTB).
- **Branch Misprediction Penalty**: If the CPU speculatively executes instructions down the wrong path, it must **flush the entire instruction pipeline** and re-fetch from the correct address. A single branch misprediction costs **15 to 25 CPU cycles**!

In Python, the overhead is amplified:
- Python bytecode represents conditionals using `POP_JUMP_IF_FALSE` or `POP_JUMP_IF_TRUE`.
- Each bytecode instruction is dispatched by CPython's evaluation loop (`ceval.c`), adding interpreter interpretation latency on top of native CPU branch costs.

#### 1.2 Truthiness Hierarchy in CPython
In Python, any object can be tested for truth value. Under the hood, CPython checks truthiness in the following strict order:
1. Calls `type(obj).__bool__(obj)`. Must return `True` or `False`.
2. If `__bool__` is not implemented, calls `type(obj).__len__(obj)`. If the length is `0`, the object evaluates to `False`; otherwise `True`.
3. If neither is defined, **all objects default to `True`**!

**CPython Falsy Singletons & Sentinels**:
- Constants: `None`, `False`
- Numeric zeros: `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0, 1)`
- Empty sequences: `""`, `()`, `[]`, `range(0)`
- Empty mappings: `{}`
- Empty sets: `set()`, `frozenset()`

---

### 2. Polyglot Comparative Syntax & Performance Matrix

| Feature | Python 3.12+ | ANSI C (C99/C11) | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- | :--- |
| **If-Else Syntax** | `if cond:\n elif:\n else:` | `if (cond) {} else if {}` | `if (cond) {} else if {}` | `if (cond) {} else if {}` |
| **Ternary Operator** | `x = a if cond else b` | `x = cond ? a : b;` | `x = cond ? a : b;` | `x = cond ? a : b;` |
| **Multi-way Branching** | `match / case` (Pattern Matching) | `switch / case` (Integral only) | `switch / case` (Jump table) | `switch` expressions + Pattern Matching |
| **Jump Table Optimization** | No (Sequential bytecode search) | Yes (Compiler jump table $O(1)$) | Yes (Compiler jump table $O(1)$) | Yes (`tableswitch` / `lookupswitch`) |
| **Destructuring Pattern** | Sequence, Mapping, Class patterns | None | Structured Binding (`auto [x, y]`) | Record Patterns (`record Point(x, y)`) |
| **Guard Clauses** | `case Point() if p.x > 0:` | None | `if constexpr` or manual check | `case Point(var x, var y) when x > 0` |
| **Fallthrough Behavior** | No fallthrough (`break` unnecessary) | Mandatory `break` to prevent bug | Mandatory `break` unless `[[fallthrough]]` | Arrow syntax `->` prevents fallthrough |

---

### 3. Structural Pattern Matching Specification (PEP 634)

Introduced in Python 3.10, `match/case` is not a simple C-style switch statement; it is a **pattern decomposition engine**:

```python
def process_event(event: dict):
    match event:
        # 1. Literal Pattern
        case {"type": "ping"}:
            return "pong"

        # 2. Sequence & Capture Pattern with Guard Clause
        case {"type": "transfer", "amount": float(amt), "recipient": str(user)} if amt > 10_000:
            trigger_compliance_alert(user, amt)
            return "flagged"

        # 3. Class Pattern with Positional Arguments
        case Point(x=0, y=0):
            return "Origin"

        # 4. Wildcard Catch-All
        case _:
            return "Unknown event"
```

**Key Advantages over chained `if/elif`**:
- Clean separation between structural shape validation and business constraints.
- Prevents verbose nested dictionary indexing (`event.get('type') == 'transfer' and ...`).

---

### 4. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 4.1 Data Engineering: Branchless Vectorization
In large-scale ETL (e.g. processing 50M transaction records), using an `if/else` inside a Python loop causes massive CPU branch mispredictions and takes minutes to finish.
**Senior Data Engineering Solution**: Use **Branchless Vectorization** (via NumPy / Polars):
```python
import numpy as np

# Processing 10,000,000 transaction amounts:
amounts = np.random.uniform(5, 500, size=10_000_000)

# ❌ BAD: Scalar branching (Takes ~4.8 seconds, millions of branch stalls)
# categories = ['HIGH' if a > 100 else 'LOW' for a in amounts]

# ✅ PRODUCTION: Branchless Vectorized Mask (Takes ~0.03 seconds — 160x faster!)
# Modern CPUs use AVX-512 SIMD vector registers with zero branch misprediction:
categories = np.where(amounts > 100, 'HIGH', 'LOW')
```

#### 4.2 Fullstack Pattern: Guard Clauses & Return Early
In API controllers and services, avoid deep nesting (the "Arrow Anti-Pattern"). Use early return guards:
```python
# ✅ Clean Guard Clause Pattern:
def register_student(payload: dict) -> dict:
    if not payload.get("email"):
        raise ValidationError("Email is required")
    if not payload.get("password") or len(payload["password"]) < 8:
        raise ValidationError("Password must contain at least 8 characters")
    if user_exists(payload["email"]):
        raise ConflictError("User already registered")

    # Happy path code remains cleanly at zero indentation level!
    return create_user_record(payload)
```

---

### 5. Common Production Pitfalls & Anti-Patterns

#### Anti-Pattern 1: The Subtle `if x:` Bug with Numeric Zeros
```python
# ❌ BUG: 0 is a valid quantity or index, but evaluates to False!
def apply_discount(item_price: float, discount_percent: float):
    # If discount_percent is 0.0, 'if not discount_percent' evaluates to True!
    if not discount_percent:
        return item_price

    # Bug occurs if user explicitly passes 0 or empty string:
    # Always check explicit sentinels:
    if discount_percent is None:
        raise ValueError("Discount cannot be None")
```

#### Anti-Pattern 2: Dangling Else & Unintended Equality Checks
```python
# ❌ INCORRECT ASSUMPTION:
if is_authenticated == True:  # Anti-pattern: Non-idiomatic
    pass

# ✅ IDIOMATIC PYTHON:
if is_authenticated:
    pass
```

---

### 6. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What is Branch Prediction and how does it affect CPU pipeline performance?
- **Answer**: Branch prediction is a hardware optimization where the CPU guesses the outcome of a conditional jump before it is evaluated, keeping the instruction pipeline full. If the prediction is correct, execution continues without delay. If mispredicted, the pipeline must be flushed, wasting 15-25 cycles. In performance-critical data engineering loops, branchless code (e.g. bitwise masks, conditional moves `CMOV`, or SIMD vectorization) eliminates this penalty.

#### Q2: How does Python's `match/case` differ fundamentally from a C/C++ `switch` statement?
- **Answer**: A C/C++ `switch` statement is a scalar branching mechanism that operates exclusively on integral or enumeration values; compilers typically translate it into an $O(1)$ memory jump table. Python's `match/case` is a structural pattern matching engine capable of destructuring complex data structures (tuples, sequences, mappings, class objects), binding variables, and executing guard conditions. It evaluates patterns sequentially at runtime.

#### Q3: What is the exact evaluation order of `a if cond else b`? Is `b` evaluated if `cond` is True?
- **Answer**: Python evaluates `cond` first. If `cond` is truthy, `a` is evaluated and returned, and `b` is **never evaluated**. If `cond` is falsy, `b` is evaluated and returned, and `a` is never evaluated. This lazy evaluation allows ternary guards like `result = user.name if user is not None else "Guest"`.

#### Q4: How does CPython decide whether an arbitrary custom class instance is True or False?
- **Answer**: CPython first checks for the `__bool__()` magic method, which must return a boolean. If `__bool__()` is not defined, CPython falls back to `__len__()`: if the length is greater than 0, it evaluates to `True`; if 0, `False`. If neither method is implemented, the object instance unconditionally evaluates to `True`.

#### Q5: Why is `if x is None` preferred over `if x == None`?
- **Answer**: `None` is a singleton in CPython; there is only ever one instance of `NoneType` in memory. `x is None` compares raw pointer addresses (`id(x) == id(None)`) in a single CPU instruction without invoking any methods. In contrast, `x == None` calls `x.__eq__(None)`. If a custom class overrides `__eq__` to return `True` or raise an exception, `x == None` can produce incorrect behavior or crash.

#### Q6: Explain the difference between Python's `match` Wildcard (`_`) and Variable Capture (`x`).
- **Answer**: In `match/case`, an identifier like `case value:` binds the matching object to the variable `value` in the local namespace. The wildcard `case _:` acts as a catch-all pattern that matches anything but does **not** bind the object to any variable name, preventing namespace pollution.

#### Q7: What are Guard Clauses in Structural Pattern Matching?
- **Answer**: A guard clause is an `if` expression appended directly to a `case` pattern (e.g., `case [x, y] if x > y:`). The pattern match succeeds only if the structural shape matches **and** the guard expression evaluates to a truthy value. If the guard fails, matching falls through to the next `case` block.

#### Q8: What is the "Arrow Anti-Pattern" in full-stack code and how do you refactor it?
- **Answer**: The Arrow Anti-Pattern (or Pyramid of Doom) refers to deeply nested conditional blocks (`if { if { if { ... } } }`) that form a horizontal arrow shape, severely degrading code readability and testability. It is refactored using **Guard Clauses** (early returns): validating error preconditions upfront and returning or raising immediately, keeping the primary logic unnested at the root scope.

#### Q9: Can boolean operations return non-boolean objects in Python? Give an example.
- **Answer**: Yes. Python's `and` and `or` operators do not coerce operands to booleans; they return the operand that terminated evaluation. For example, `'apple' and 'banana'` returns `'banana'`. `0 or 'default'` returns `'default'`. Only explicit comparisons (`==`, `<`, `>`) and the `bool()` constructor return literal `True` or `False`.

#### Q10: How do SIMD instructions in modern hardware eliminate conditional branches in Data Engineering?
- **Answer**: SIMD (Single Instruction, Multiple Data) architectures (like Intel AVX-512 or ARM Neon) process vectors of 8 to 16 numbers simultaneously in 512-bit registers. Rather than evaluating scalar `if/else` jumps for each element, SIMD generates a bitmask across all lanes in parallel and executes a vectorized blend instruction (`VPBLENDMD`), computing results for 16 elements in a single CPU clock cycle without any branching."""
            },
            "code_examples": [
                {
                    "title": "Structural Pattern Matching with Guard Clauses (Python 3.10+)",
                    "code": "def parse_api_response(status, payload):\n    match (status, payload):\n        case (200, {'items': list(data)}):\n            return f'Success: Retrieved {len(data)} items'\n        case (404, {'detail': str(msg)}):\n            return f'Resource Not Found: {msg}'\n        case (500 | 502 | 503, _):\n            return 'Server Error: Upstream service unavailable'\n        case _:\n            return 'Unhandled response signature'\n\nprint(parse_api_response(200, {'items': ['prod_1', 'prod_2', 'prod_3']}))\nprint(parse_api_response(404, {'detail': 'User STU-001 does not exist'}))\nprint(parse_api_response(503, {}))",
                    "explanation": "Shows algebraic structural pattern matching with tuple destructuring, dictionary key typing, and OR (|) patterns.",
                    "expected_output": "Success: Retrieved 3 items\nResource Not Found: User STU-001 does not exist\nServer Error: Upstream service unavailable"
                },
                {
                    "title": "Guard Clause Architecture vs Nested Pyramid",
                    "code": "def process_order(order):\n    # Guard 1: Existence check\n    if not order:\n        return 'Order is empty'\n    # Guard 2: Status check\n    if order.get('status') != 'PENDING':\n        return f'Cannot process order in status {order.get(\"status\")}'\n    # Guard 3: Inventory validation\n    if order.get('quantity', 0) <= 0:\n        return 'Quantity must be positive'\n\n    # Main logic cleanly executed\n    return f'Order {order[\"id\"]} successfully queued for fulfillment'\n\nprint(process_order({'id': 'ORD-982', 'status': 'PENDING', 'quantity': 4}))\nprint(process_order({'id': 'ORD-101', 'status': 'CANCELLED', 'quantity': 1}))",
                    "explanation": "Illustrates enterprise guard clause patterns that keep code flat, readable, and resilient.",
                    "expected_output": "Order ORD-982 successfully queued for fulfillment\nCannot process order in status CANCELLED"
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "What is the output of the expression: [] or 0 or 'fallback' or 'final'?",
                    "options": ["True", "[]", "'fallback'", "'final'"],
                    "correct_answer": 2,
                    "explanation": "The 'or' operator evaluates from left to right and returns the first truthy operand. Both [] and 0 are falsy, so it returns 'fallback' immediately."
                },
                {
                    "id": 2,
                    "question": "In structural pattern matching (match/case), which symbol represents the universal wildcard catch-all?",
                    "options": ["*", "_", "default", "..."],
                    "correct_answer": 1,
                    "explanation": "The underscore (_) is the universal wildcard pattern in Python 3.10+ match/case statements."
                }
            ],
            "practical_challenge": {
                "prompt": "Write a function evaluate_tier(score) that uses pattern matching or if/elif to return 'PLATINUM' if score >= 90, 'GOLD' if score >= 75, 'SILVER' if score >= 50, otherwise 'BRONZE'.",
                "starter_code": "def evaluate_tier(score):\n    # Return tier based on score\n    pass",
                "test_call": "evaluate_tier(82)",
                "expected": "GOLD"
            }
        },
        {
            "slug": "loops",
            "name": "Loops & Iteration Protocols",
            "order": 2,
            "difficulty": "beginner",
            "icon": "🔄",
            "subtopics": [
                "The CPython Iterator Protocol: __iter__ and __next__ Under the Hood",
                "for and while Loops: Bytecode Mechanics (GET_ITER & FOR_ITER)",
                "Loop Control: break, continue, and the Loop-else Construct",
                "Polyglot Comparison: Python Generators vs C Pointer Increments vs C++ Ranges vs Java Streams",
                "Production Data Engineering: Streaming Terabytes via Chunked Iterators"
            ],
            "learning_objectives": [
                "Master the internal CPython Iterator Protocol and understand how StopIteration terminates loops",
                "Analyze loop execution at the bytecode level and measure interpreter dispatch overhead",
                "Effectively utilize the loop-else clause for clean search algorithms without boolean flags",
                "Compare Python's iterator abstractions with C/C++ memory pointer increments and Java Iterators",
                "Build memory-constant streaming pipelines for processing massive datasets without OOM crashes"
            ],
            "lesson_content": {
                "introduction": "Iteration is the engine of data transformation. In Python, iteration is not merely an index counter incrementing an address slot like in C; it is governed by an elegant, protocol-driven architecture known as the **Iterator Protocol**.\n\nMastering iteration unlocks generator pipelines, memory-constant streaming of multi-gigabyte files, and high-performance algorithms. In this module, we dissect how the CPython virtual machine dispatches loops, compare Python iteration with native C pointers and Java streams, explore the loop `else` clause, and implement enterprise streaming patterns.",
                "explanation": """### 1. Conceptual Architecture: The CPython Iterator Protocol

#### 1.1 How `for` Loops Actually Work in CPython
When you write:
```python
for item in collection:
    process(item)
```
Python does NOT use index access (`collection[0], collection[1]`). Instead, it executes the strict **Iterator Protocol**:
1. Python passes `collection` to `iter(collection)`. This invokes `collection.__iter__()`, which returns an **iterator object**.
2. An iterator object must implement `__next__()`.
3. In each iteration, Python calls `next(iterator)`. This invokes `iterator.__next__()` to retrieve the next element.
4. When elements are exhausted, `__next__()` raises the built-in **`StopIteration`** exception.
5. Python catches `StopIteration` internally and terminates the loop gracefully.

```
┌────────────────────────────────────────────────────────┐
│               CPYTHON ITERATION PROTOCOL               │
└────────────────────────────────────────────────────────┘
  Iterable (e.g. list, dict, file)
     │
     ▼ Calls __iter__()
  Iterator Object (maintains internal cursor)
     │
     ├─► Calls __next__() ──► Returns next item
     ├─► Calls __next__() ──► Returns next item
     └─► Calls __next__() ──► RAISES StopIteration! (Loop terminates cleanly)
```

#### 1.2 Bytecode Disassembly: `FOR_ITER`
Let's inspect the compiled bytecode using `dis`:
```python
import dis

def loop_demo(items):
    for x in items:
        print(x)

dis.dis(loop_demo)
```
Output:
```
  2           0 GET_ITER
        >>    2 FOR_ITER                10 (to 24)
              4 STORE_FAST               1 (x)
  3           6 LOAD_GLOBAL              0 (print)
              8 LOAD_FAST                1 (x)
             10 PRECALL                  1
             12 CALL                     1
             20 POP_TOP
             22 JUMP_BACKWARD           11 (to 2)
        >>   24 RETURN_CONST             0 (None)
```
Notice instruction `2 FOR_ITER`: This single virtual machine instruction calls the C function `tp_iternext` directly on the iterator object. If an item is returned, it pushes it to the evaluation stack and proceeds. If `StopIteration` is raised, it automatically jumps forward to instruction `24`, exiting the loop in a single instruction!

---

### 2. Polyglot Comparative Syntax & Performance Matrix

| Dimension | Python 3.12+ | ANSI C (C99/C11) | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- | :--- |
| **For Loop** | `for x in iterable:` | `for (int i = 0; i < n; i++)` | `for (const auto& x : vec)` | `for (var x : list)` |
| **Iterator Mechanism** | Protocol (`__iter__`, `__next__`) | Pointer increment (`ptr++`) | Iterators (`begin()`, `end()`) | `Iterator<T>` (`hasNext()`, `next()`) |
| **Memory Overhead** | Heap Iterator Object | Zero (Direct Register `RCX`) | Zero (Inlined pointers) | Small Heap Iterator / JIT inlined |
| **Lazy Evaluation** | Generators (`yield`) | Manual state struct | Coroutines (`co_yield`) / Views | `Stream<T>` API |
| **Loop-Else Clause** | Native `else:` syntax | Not supported (requires flag) | Not supported | Not supported |
| **Index Access** | `enumerate(seq, start=0)` | Native index variable `i` | `for (auto [i, v] : std::views::enumerate(v))` | IntStream or manual index |
| **Parallel Iteration** | `zip(seq1, seq2)` | Manual synchronized indices | `std::views::zip(v1, v2)` | Custom or Streams |

---

### 3. The Power of the Loop-`else` Clause

A unique feature of Python is that both `for` and `while` loops support an optional `else` block:
- **Rule**: The `else` block executes **ONLY if the loop completed naturally** (without encountering a `break` statement).
- **Use Case**: Eliminates clumsy boolean search flags (`found = False`):

```python
# Search algorithm without boolean flags:
def find_user_by_id(user_list, target_id):
    for user in user_list:
        if user['id'] == target_id:
            print(f"Found user: {user['name']}")
            break  # Exits loop; skips else block!
    else:
        # Executes ONLY if loop finished without breaking:
        print(f"User with ID {target_id} does not exist.")
```

---

### 4. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 4.1 Data Engineering: Chunked Generator Pipelines for Gigabyte Datasets
When reading a 50GB log file or database dump on an 8GB RAM worker:
- Reading the entire file via `file.readlines()` loads all 50GB into RAM at once, causing the OS Out-Of-Memory (OOM) killer to terminate your process immediately.
- **Senior Solution: Streaming Generator Pipeline**:
```python
from typing import Generator

def stream_log_chunks(filepath: str, chunk_size: int = 100_000) -> Generator[list[str], None, None]:
    # Streams massive files in memory-constant batches
    with open(filepath, 'r', encoding='utf-8') as f:
        chunk = []
        for line in f:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []  # Releases memory for previous batch immediately!
        if chunk:
            yield chunk

# Memory consumption remains FLAT at ~50MB regardless of whether the file is 10GB or 1TB!
for batch in stream_log_chunks("massive_server_logs.txt"):
    process_batch_records(batch)
```

#### 4.2 Fullstack Pattern: Safe Retries with Exponential Backoff
In microservices, network requests to third-party APIs can intermittently fail:
```python
import time

def call_payment_gateway_with_retry(payload: dict, max_retries: int = 3):
    backoff_seconds = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            return execute_payment_api(payload)
        except TransientNetworkError as err:
            if attempt == max_retries:
                raise ServiceUnavailableError("Payment gateway down after retries") from err
            time.sleep(backoff_seconds)
            backoff_seconds *= 2.0  # Exponential backoff: 1s, 2s, 4s...
```

---

### 5. Common Production Pitfalls & Anti-Patterns

#### Anti-Pattern 1: Mutating a Collection While Iterating Over It
```python
# ❌ CATASTROPHIC BUG: Modifying list during iteration skips elements!
numbers = [1, 2, 3, 4, 5, 6]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)
# Result: [1, 3, 5] is expected, but [1, 3, 5, 6] occurs because indices shift left!

# ✅ PRODUCTION FIX: Iterate over a copy or use list comprehension
numbers = [num for num in numbers if num % 2 != 0]
```

#### Anti-Pattern 2: Quadratic Loop Lookups ($O(N^2)$ Disaster)
```python
# ❌ PRODUCTION HAZARD: Linear search inside a loop creates O(N * M) bottleneck!
def reconcile_transactions(transactions: list, blacklist_user_ids: list):
    valid = []
    for tx in transactions:
        # 'tx.user_id in blacklist_user_ids' scans the list sequentially every single time!
        # For 100K transactions and 100K blacklist users, this takes 10,000,000,000 operations (~15 minutes)!
        if tx.user_id not in blacklist_user_ids:
            valid.append(tx)
    return valid

# ✅ PRODUCTION FIX: Convert blacklist to O(1) Hash Set upfront!
def reconcile_transactions_fast(transactions: list, blacklist_user_ids: list):
    # O(M) Set conversion once:
    blacklist_set = set(blacklist_user_ids)
    # Total complexity drops from O(N * M) to O(N + M) — completes in 0.08 seconds!
    return [tx for tx in transactions if tx.user_id not in blacklist_set]
```

---

### 6. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What methods must an object implement to adhere to the Python Iterator Protocol?
- **Answer**: An object must implement two dunder methods: `__iter__()` and `__next__()`. The `__iter__()` method must return the iterator object itself (typically `return self`). The `__next__()` method must return the next sequential item, or raise `StopIteration` when no further elements remain.

#### Q2: What is the difference between an Iterable and an Iterator in Python?
- **Answer**: An **Iterable** is any object that can return an iterator when passed to `iter()` (it implements `__iter__()` or `__getitem__()`, such as `list`, `dict`, `str`, `set`). An **Iterator** is the stateful stream object that actually produces values one at a time via `__next__()` and maintains an internal position cursor. All iterators are iterables (their `__iter__` returns `self`), but not all iterables are iterators.

#### Q3: When does a loop's `else` clause execute, and when is it bypassed?
- **Answer**: A loop's `else` clause executes if and only if the loop terminates normally by exhausting all items (in a `for` loop) or when the loop condition becomes false (in a `while` loop). It is bypassed if the loop is terminated prematurely via a `break` statement, an uncaught exception, or a `return` statement.

#### Q4: How does a Python Generator function differ from a standard function?
- **Answer**: A standard function executes from entry to `return` and destroys its stack frame upon completion. A generator function contains at least one `yield` statement; calling it does not execute the function body but returns a `generator` object. When `next()` is called on the generator, it executes until it hits `yield`, suspends execution, preserves its entire local stack frame (variables, instruction pointer), and yields the value. Subsequent calls resume execution immediately after the `yield`.

#### Q5: What is the time and space complexity of `range(1_000_000_000)` in Python 3?
- **Answer**: In Python 3, `range()` is an immutable sequence type that operates in $O(1)$ time and $O(1)$ space. It does not generate a billion numbers in memory; it merely stores three integers internally: `start`, `stop`, and `step`. Values are computed dynamically on-demand during iteration.

#### Q6: Why is `enumerate(items)` preferred over `for i in range(len(items))`?
- **Answer**: `enumerate(items)` is more pythonic, readable, and faster. It operates directly via the iterator protocol without performing repeated dictionary or array index lookups (`items[i]`) on every iteration. In CPython, `enumerate` is implemented in C as a fast struct tracking both counter and item pointer in a single pass.

#### Q7: How does `zip(*[iter(s)] * n)` work to group elements into fixed-size chunks?
- **Answer**: `[iter(s)] * n` creates a list containing $n$ references to the **exact same iterator object**. When unpacked into `zip(*...)`, `zip` calls `next()` on each argument sequentially. Because all arguments share the same underlying iterator, `zip` pulls $n$ consecutive elements from the stream per iteration, yielding clean $n$-element chunks in $O(1)$ auxiliary space.

#### Q8: What causes an infinite loop in a `while` loop when using floating-point incrementation?
- **Answer**: Floating-point rounding inaccuracies. For example, in `while x != 1.0: x += 0.1`, `x` will never be exactly equal to `1.0` due to IEEE 754 precision issues (e.g. `0.9999999999999999` followed by `1.0999999999999999`), bypassing `1.0` entirely and looping indefinitely. Always use inequalities (`while x < 1.0:`) or integer step counters.

#### Q9: How can you write a custom class that supports iteration?
- **Answer**: Implement `__iter__(self)` to return an iterator object. If the class manages its own state, it can implement both `__iter__(self): return self` and `__next__(self)` containing the increment logic and raising `StopIteration`. Alternatively, `__iter__(self)` can be written as a generator using `yield`, which automatically handles iterator protocol mechanics.

#### Q10: How do CPython's `itertools` module functions achieve higher performance than pure Python loops?
- **Answer**: Functions in the `itertools` module (such as `islice`, `chain`, `cycle`, `groupby`) are implemented entirely in compiled C (`Modules/itertoolsmodule.c`). Their loop iteration, state tracking, and element dispatch occur within native CPU registers and C structs, completely bypassing the Python virtual machine's bytecode evaluation loop (`ceval.c`), executing 5 to 20 times faster with zero intermediate Python object allocation."""
            },
            "code_examples": [
                {
                    "title": "Custom Class Implementing the CPython Iterator Protocol",
                    "code": "class FibonacciStream:\n    def __init__(self, limit=10):\n        self.limit = limit\n        self.count = 0\n        self.a, self.b = 0, 1\n\n    def __iter__(self):\n        return self\n\n    def __next__(self):\n        if self.count >= self.limit:\n            raise StopIteration\n        val = self.a\n        self.a, self.b = self.b, self.a + self.b\n        self.count += 1\n        return val\n\nfib = FibonacciStream(7)\nprint('Fibonacci sequence via Iterator Protocol:')\nfor num in fib:\n    print(num, end=' ')\nprint()",
                    "explanation": "Demonstrates a complete iterator implementing __iter__ and __next__ with StopIteration termination.",
                    "expected_output": "Fibonacci sequence via Iterator Protocol:\n0 1 1 2 3 5 8"
                },
                {
                    "title": "Loop-else Clause for Search Optimization",
                    "code": "def check_user_access(users, target_id):\n    for u in users:\n        if u['id'] == target_id:\n            print(f'Access Granted: {u[\"name\"]}')\n            break\n    else:\n        print(f'Access Denied: User {target_id} not found in authorization table.')\n\nactive_users = [{'id': 101, 'name': 'Gayatri'}, {'id': 102, 'name': 'Rahul'}]\ncheck_user_access(active_users, 102)\ncheck_user_access(active_users, 999)",
                    "explanation": "Illustrates how the loop-else clause eliminates boolean flags in search routines.",
                    "expected_output": "Access Granted: Rahul\nAccess Denied: User 999 not found in authorization table."
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "Which exception must be raised by __next__() to signal that an iterator has exhausted its elements?",
                    "options": ["IndexError", "StopIteration", "EOFError", "GeneratorExit"],
                    "correct_answer": 1,
                    "explanation": "CPython's iterator protocol specifies that StopIteration must be raised when no more items remain."
                },
                {
                    "id": 2,
                    "question": "When does the else block attached to a for loop execute?",
                    "options": [
                        "Whenever the loop body encounters an error",
                        "Only if the loop terminates normally without encountering a break",
                        "On every iteration of the loop",
                        "Only when the loop is bypassed on the first check"
                    ],
                    "correct_answer": 1,
                    "explanation": "The loop-else construct executes only if the loop runs to completion without being terminated by a break statement."
                }
            ],
            "practical_challenge": {
                "prompt": "Write a generator function chunk_stream(data_list, size) that yields successive chunks of length size from data_list.",
                "starter_code": "def chunk_stream(data_list, size):\n    # Yield slices of data_list of length size\n    pass",
                "test_call": "list(chunk_stream([1, 2, 3, 4, 5], 2))",
                "expected": "[[1, 2], [3, 4], [5]]"
            }
        }
    ]
}
