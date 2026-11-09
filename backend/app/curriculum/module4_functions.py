# -*- coding: utf-8 -*-
"""
Module 4: Functions & Scope Architecture
5+ Pages In-Depth Systems Knowledge, Call Stack Frames, Closure Mechanics,
Decorator Architecture, Mutable Default Arguments Trap, and 10 Viva Q&As.
"""

MODULE_4 = {
    "module_number": 4,
    "module_name": "Functions",
    "description": "Master stack frame mechanics, lexical scoping (LEGB), closures, and decorator architectures.",
    "icon": "⚡",
    "topics": [
        {
            "slug": "functions",
            "name": "Functions, Closures & Scope",
            "order": 1,
            "difficulty": "intermediate",
            "icon": "🧩",
            "subtopics": [
                "The CPython Call Stack & Stack Frame Architecture (PyFrameObject)",
                "Lexical Scoping Hierarchy: The LEGB Rule & Nonlocal Variables",
                "First-Class Functions & Closure Mechanics Under the Hood",
                "Decorator Architecture & High-Performance Wrapper Design (@functools.wraps)",
                "Argument Binding: Positional-Only (/), Keyword-Only (*), and the Mutable Default Trap"
            ],
            "learning_objectives": [
                "Understand the CPython call stack and examine PyFrameObject memory structures",
                "Master lexical scope resolution via the LEGB rule (Local, Enclosing, Global, Built-in)",
                "Deconstruct closures, free variables, and the __closure__ tuple in memory",
                "Design enterprise decorators for authentication, distributed tracing, and retry logic",
                "Avoid the classic mutable default argument trap in production API signatures"
            ],
            "lesson_content": {
                "introduction": "Functions are the primary unit of computation and abstraction in software engineering. In Python, functions are **first-class citizens**—they are full heap objects (`PyFunctionObject`) that can be assigned to variables, passed as arguments, returned from other functions, and inspected at runtime.\n\nIn this comprehensive deep dive, we explore the physical mechanics of the CPython call stack (`PyFrameObject`), deconstruct closures down to the byte level, analyze the LEGB scoping rule, build production decorators with `@functools.wraps`, and compare Python closures with C++ lambdas, Java Functional Interfaces, and C function pointers.",
                "explanation": """### 1. Conceptual Architecture & CPython Call Stack Mechanics

#### 1.1 The Anatomy of `PyFrameObject`
When Python invokes a function, it pushes a **Stack Frame (`PyFrameObject`)** onto the execution thread's call stack.
In CPython (`Include/cpython/frameobject.h`), a frame contains:
```c
struct _frame {
    PyObject_VAR_HEAD
    struct _frame *f_back;       // Pointer to previous frame on call stack (for tracebacks)
    PyCodeObject *f_code;        // Compiled bytecode instructions
    PyObject *f_builtins;        // Built-in namespace dictionary
    PyObject *f_globals;         // Global module namespace dictionary
    PyObject *f_locals;          // Local namespace dictionary
    PyObject **f_valuestack;     // Fast evaluation stack pointer
    PyObject *f_localsplus[1];   // Fast local variable slots (evaluated in O(1) time)
};
```

**Key Takeaways**:
- **`fastlocals` Array**: Local variables declared inside a function are not looked up in a dictionary! CPython statically determines their indices at compile time and stores them in the contiguous C array `f_localsplus`. This allows local variable access (`LOAD_FAST`) to execute in a blistering **$O(1)$ CPU cycle**!
- **Call Overhead**: Calling a function in Python costs ~100 to 150 nanoseconds due to frame allocation and argument tuple binding. In tight mathematical loops, inlining or vectorization is preferred.

#### 1.2 Lexical Scoping & The LEGB Rule
When an identifier is referenced inside Python code, CPython searches namespaces in strict hierarchical order:

$$\text{Local (L)} \longrightarrow \text{Enclosing (E)} \longrightarrow \text{Global (G)} \longrightarrow \text{Built-in (B)}$$

1. **Local (L)**: Names bound inside the currently executing function (via assignment or parameters).
2. **Enclosing (E)**: Names bound in the local scope of any enclosing/outer functions (closures).
3. **Global (G)**: Names bound at the top module level (`globals()`).
4. **Built-in (B)**: Built-in names pre-loaded by Python (`len`, `range`, `ValueError`).

```python
x = "GLOBAL"

def outer():
    x = "ENCLOSING"
    def inner():
        # Searches Local -> Enclosing ("ENCLOSING") -> Global -> Built-in
        print(x)
    return inner
```

#### 1.3 Closures: How Python Preserves Outer Scope Memory
A **Closure** occurs when an inner function retains a reference to variables in an outer enclosing scope, even after the outer function has finished executing and returned!
- When `outer()` exits, its `PyFrameObject` is popped from the call stack.
- However, variables referenced by the inner function are moved to a special heap structure called a **Cell Object (`PyCellObject`)**.
- The inner function holds a `__closure__` attribute containing pointers to these cell objects, allowing the variables to survive indefinitely!

---

### 2. Polyglot Comparative Function & Closure Matrix

| Dimension | Python 3.12+ | ANSI C (C99/C11) | Modern C++ (C++20) | Java 21 LTS |
| :--- | :--- | :--- | :--- | :--- |
| **First-Class Functions** | Yes (`PyFunctionObject`) | Function Pointers | `std::function` / Lambdas | Method References / Lambdas |
| **Closures** | Yes (Cell objects in heap) | Not natively supported | Yes (Lambda capture `[&]` / `[=]`) | Yes (Effectively final variables) |
| **Default Arguments** | Evaluated **ONCE** at import time | Not supported | Evaluated at each call site | Method Overloading required |
| **Keyword Arguments** | Native (`f(age=25, name='A')`) | Not supported | Not supported (Designated init) | Builder pattern or Records |
| **Variadic Arguments** | `*args` (tuple), `**kwargs` (dict) | `va_list` (stdarg.h) | Variadic Templates (`Args&&...`) | Varargs (`Type... args`) |
| **Decorators** | Native `@decorator` syntax | Macro wrapping | RAII / Function wrappers | Annotations + Bytecode AspectJ |

---

### 3. The Classic Mutable Default Argument Trap

One of the most dangerous and notorious production bugs in Python is using a mutable object (like a `list` or `dict`) as a default argument:
```python
# ❌ DANGEROUS PRODUCTION BUG:
def append_event(event_id: str, event_log: list = []):
    event_log.append(event_id)
    return event_log

print(append_event("LOGIN"))   # ['LOGIN']
print(append_event("LOGOUT"))  # ❌ ['LOGIN', 'LOGOUT'] - Memory leaked across calls!
```
**Why does this happen?**
In Python, function default arguments are evaluated **EXACTLY ONCE**—at the moment the function definition is compiled when the module is imported, NOT when the function is called! The default list `[]` is a single object created on the heap and bound to the function's `__defaults__` tuple. Every subsequent call that relies on the default receives the **exact same mutable instance**!

**The Production Solution (Sentinel Pattern)**:
```python
# ✅ PRODUCTION PATTERN: Use None as immutable sentinel
def append_event_safe(event_id: str, event_log: list = None):
    if event_log is None:
        event_log = []  # Fresh list allocated on each invocation!
    event_log.append(event_id)
    return event_log
```

---

### 4. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 4.1 Production Decorator Pattern: Distributed Tracing & Execution Timing
In microservice architectures, decorators provide clean, non-intrusive instrumentation:
```python
import time
import functools
import logging

def trace_execution(logger=None):
    # Production decorator measuring execution time and logging outcomes.
    def decorator(func):
        @functools.wraps(func)  # CRITICAL: Preserves function name, docstring, and signature!
        def wrapper(*args, **kwargs):
            start_ns = time.perf_counter_ns()
            func_name = func.__qualname__
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                (logger or logging).info(f"[TRACE] {func_name} executed in {elapsed_ms:.2f}ms")
                return result
            except Exception as err:
                elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                (logger or logging).error(f"[ERROR] {func_name} failed after {elapsed_ms:.2f}ms: {err}")
                raise
        return wrapper
    return decorator

@trace_execution()
def fetch_student_records(cohort_id: int):
    # Simulated database query
    time.sleep(0.05)
    return [{"id": 1, "name": "Gayatri"}]
```

---

### 5. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What is the exact difference between `*args` and `**kwargs`?
- **Answer**: `*args` collects any excess positional arguments passed to a function into an immutable **tuple**. `**kwargs` collects any excess keyword arguments passed into a mutable **dictionary** of key-value pairs. In function definitions, `*args` must precede `**kwargs`.

#### Q2: What does `@functools.wraps` do, and what happens if you omit it in a decorator?
- **Answer**: `@functools.wraps(func)` is a helper decorator that copies essential metadata (such as `__name__`, `__doc__`, `__module__`, `__annotations__`, and `__wrapped__`) from the original function to the inner wrapper function. If omitted, the decorated function will appear with the wrapper's name (`wrapper.__name__ == 'wrapper'`) and empty docstrings, breaking introspection, automated API documentation (FastAPI/Swagger), debug tracebacks, and unit testing mocks.

#### Q3: Why does Python evaluate default parameter values at definition time rather than execution time?
- **Answer**: Performance and determinism. Evaluating default expressions once when the function is defined allows CPython to store the resulting objects directly in the function object's `__defaults__` tuple. During function execution, CPython simply binds the pre-existing pointer, avoiding repeated evaluation overhead on every single function call.

#### Q4: How does the `nonlocal` keyword differ from the `global` keyword?
- **Answer**: `global` declares that an identifier refers to a variable in the top-level module namespace. `nonlocal` (introduced in Python 3) declares that an identifier refers to a variable in the **nearest enclosing outer function scope** (excluding global and built-in scopes). It is essential in closures when an inner function needs to rebind or mutate a scalar variable belonging to the parent function.

#### Q5: What are Positional-Only (`/`) and Keyword-Only (`*`) parameters in Python?
- **Answer**: 
  - Parameters placed **before `/`** are **Positional-Only**: callers must pass them by position, not by name (e.g. `def f(a, b, /)` prevents `f(a=1, b=2)`). This allows library authors to rename parameters in the future without breaking callers.
  - Parameters placed **after `*`** are **Keyword-Only**: callers must explicitly name them (e.g. `def f(*, timeout=10)` requires `f(timeout=20)`). This prevents errors where callers pass arguments in the wrong order.

#### Q6: What is a Closure in computer science, and how is it implemented in CPython?
- **Answer**: A closure is a first-class function that retains access to variables from its lexical environment even after the enclosing scope has exited. In CPython, when an inner function references an outer variable, that variable is stored in a `PyCellObject` on the heap instead of the stack frame. The inner function stores a tuple of these cell objects in its `__closure__` attribute, preserving access to the values.

#### Q7: Can lambda functions in Python contain multi-line logic or assignments? Why?
- **Answer**: No. Python lambda functions are restricted to a single syntactic expression: `lambda args: expression`. They cannot contain statements, assignments (prior to walrus), loops, or multi-line blocks. This intentional design choice maintains Python's philosophy of code readability, encouraging developers to use standard named `def` functions for non-trivial logic.

#### Q8: How does Python's `functools.lru_cache` implement memoization?
- **Answer**: `lru_cache` wraps a function with a thread-safe in-memory cache implemented as a dictionary paired with a doubly-linked list. When called, it hashes the function's arguments to look up the result in $O(1)$ time. If found (cache hit), it returns the cached value. If not (cache miss), it executes the function, stores the result, and if the cache exceeds `maxsize`, evicts the Least Recently Used (LRU) entry in $O(1)$ time.

#### Q9: What happens if a function references a variable that is assigned later in the same function scope?
- **Answer**: It raises `UnboundLocalError: local variable referenced before assignment`. In CPython, the compiler scans the function body at compile time: if any assignment to a variable exists anywhere within the function, that variable is marked as a **local variable** for the entire scope. If you attempt to read it before the assignment statement executes, Python will NOT fall back to the global variable; it throws `UnboundLocalError`.

#### Q10: How do Python function calls compare in overhead to C function calls?
- **Answer**: A native C function call translates directly to a machine assembly instruction (`CALL`), pushing arguments to registers (`RDI`, `RSI`) and saving the return instruction pointer on the stack, taking $\sim 1$ to 2 nanoseconds. A Python function call involves allocating a `PyFrameObject` on the heap, resolving argument dictionaries, binding default arguments, and dispatching virtual machine bytecode, costing $\sim 100$ to 150 nanoseconds (roughly 100x slower than native C)."""
            },
            "code_examples": [
                {
                    "title": "Closures, Lexical Scope & The __closure__ Attribute",
                    "code": "def make_counter(start_val=0):\n    count = start_val\n    def increment(step=1):\n        nonlocal count\n        count += step\n        return count\n    return increment\n\ncounter_a = make_counter(10)\nprint('Counter A step 1:', counter_a(5))\nprint('Counter A step 2:', counter_a(2))\n\n# Inspecting the internal closure cell object:\ncell = counter_a.__closure__[0]\nprint('Closure Cell Content:', cell.cell_contents)",
                    "explanation": "Demonstrates closure memory retention using nonlocal and inspects the underlying PyCellObject.",
                    "expected_output": "Counter A step 1: 15\nCounter A step 2: 17\nClosure Cell Content: 17"
                },
                {
                    "title": "Positional-Only (/) and Keyword-Only (*) Parameter Enforcements",
                    "code": "def configure_service(host, port, /, *, api_key, timeout=30):\n    return f'Connecting to {host}:{port} with key {api_key[:4]}*** (timeout={timeout}s)'\n\n# Correct call:\nres = configure_service('api.pymentor.io', 8080, api_key='SECRET_TOKEN_982')\nprint(res)\n\ntry:\n    # Error: Passing positional-only param as keyword\n    configure_service(host='api.pymentor.io', port=8080, api_key='TEST')\nexcept TypeError as e:\n    print('Enforced Security:', e)",
                    "explanation": "Illustrates PEP 570 positional-only parameters (/) and keyword-only parameters (*).",
                    "expected_output": "Connecting to api.pymentor.io:8080 with key SECR*** (timeout=30s)\nEnforced Security: configure_service() got some positional-only arguments passed as keyword arguments: 'host, port'"
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "Which order of namespace lookup is followed by the Python interpreter?",
                    "options": ["Global -> Local -> Enclosing -> Built-in", "Local -> Enclosing -> Global -> Built-in", "Local -> Global -> Enclosing -> Built-in", "Built-in -> Global -> Enclosing -> Local"],
                    "correct_answer": 1,
                    "explanation": "Python strictly follows the LEGB rule: Local first, then Enclosing closures, then Global module scope, and finally Built-ins."
                },
                {
                    "id": 2,
                    "question": "Which keyword must be used inside an inner function to rebind a variable from the enclosing function scope?",
                    "options": ["global", "nonlocal", "outer", "super"],
                    "correct_answer": 1,
                    "explanation": "The nonlocal keyword allows an inner function to rebind an identifier belonging to the enclosing outer scope."
                }
            ],
            "practical_challenge": {
                "prompt": "Write a decorator retry(max_attempts) that executes a function up to max_attempts times if it raises an Exception, returning the result if successful or re-raising the last exception.",
                "starter_code": "import functools\ndef retry(max_attempts):\n    # Return decorator that retries func on Exception\n    pass",
                "test_call": "retry(3)(lambda: 42)()",
                "expected": "42"
            }
        }
    ]
}
