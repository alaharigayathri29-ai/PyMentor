# -*- coding: utf-8 -*-
"""
Polyglot Systems Engineering Knowledge Matrix for AI Mentor.
Contains comprehensive, textbook-grade pedagogical explanations, architectural analysis,
and runnable code demonstrations across Java, C, Modern C++, and Python.
"""

from typing import Dict, Optional, Tuple
import re

JAVA_KNOWLEDGE = {
    "loops": {
        "explain": """### ☕ Comprehensive Guide to Loops in Java

In Java, loops allow you to repeat a block of code deterministically. Java provides **4 fundamental loop constructs** and modern **Stream-based iteration**:

#### 1. Standard `for` Loop (Index-Based)
Best when you know the exact iteration count in advance:
```java
public class ForLoopDemo {
    public static void main(String[] args) {
        // Syntax: for (initialization; condition; increment/decrement)
        for (int i = 1; i <= 5; i++) {
            System.out.println("Iteration count: " + i);
        }
    }
}
```

#### 2. Enhanced `for-each` Loop (Iterable Traversal)
Introduced in Java 5, this is the idiomatic way to iterate over arrays and `Collection` objects (`List`, `Set`):
```java
public class ForEachDemo {
    public static void main(String[] args) {
        String[] frameworks = {"Spring Boot", "Quarkus", "Micronaut", "Hibernate"};
        
        for (String framework : frameworks) {
            System.out.println("Enterprise framework: " + framework);
        }
    }
}
```

#### 3. `while` Loop (Condition-Controlled)
Evaluates the condition **before** entering the loop body. Runs 0 or more times:
```java
public class WhileLoopDemo {
    public static void main(String[] args) {
        int balance = 100;
        int transactionCost = 25;
        
        while (balance >= transactionCost) {
            balance -= transactionCost;
            System.out.println("Processed payment. Remaining balance: $" + balance);
        }
    }
}
```

#### 4. `do-while` Loop (Post-Condition Controlled)
Guaranteed to execute **at least once** because the condition is evaluated at the bottom:
```java
public class DoWhileDemo {
    public static void main(String[] args) {
        int attempt = 1;
        do {
            System.out.println("Handshake attempt #" + attempt);
            attempt++;
        } while (attempt <= 3);
    }
}
```

#### 5. Functional Stream `.forEach()` (Java 8+)
Functional and parallelizable iteration using lambda expressions:
```java
import java.util.List;

public class StreamLoopDemo {
    public static void main(String[] args) {
        List<String> services = List.of("AuthService", "PaymentService", "NotificationService");
        
        services.stream()
                .filter(s -> s.startsWith("Pay"))
                .forEach(service -> System.out.println("Processing: " + service));
    }
}
```

#### Loop Control Statements:
- `break`: Immediately terminates the innermost loop.
- `continue`: Skips the remainder of the current iteration and jumps to the next condition check.
- **Labeled Break/Continue**: Used to escape deeply nested loops directly:
```java
outerLoop:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (i == 1 && j == 1) break outerLoop; // Exits both loops!
    }
}
```

Would you like to explore nested loops, loop performance optimization in the JVM, or work on a Java loop coding challenge? 🎯""",

        "hint": """💡 **Java Loop Tip:**
- Make sure loop variables are initialized properly (`int i = 0;`).
- In `while` loops, ensure the loop condition variable is updated inside the body, otherwise you will trigger an **infinite loop** that consumes 100% of a CPU core!
- Prefer the enhanced `for-each` loop (`for (Type item : collection)`) unless you specifically need the numeric index.""",

        "practice": """**Java Loop Practice Challenge: Matrix Multiplier & Prime Sieve** 🚀

**Problem:** Write a Java program that:
1. Prints all prime numbers between 2 and 50 using a nested loop.
2. Formats output neatly on a single line separated by commas.

```java
public class PrimeFinder {
    public static void main(String[] args) {
        // Implement your nested loop logic here:
    }
}
```
Try implementing it in the Practice Lab! ☕"""
    },

    "oop": {
        "explain": """### ☕ Object-Oriented Programming (OOP) in Java

Java is a class-based, object-oriented language designed around **4 core pillars**:

#### 1. Encapsulation
Hiding internal object state and requiring all interaction through public methods (getters/setters):
```java
public class BankAccount {
    // Private fields: internal state is protected
    private String accountNumber;
    private double balance;

    public BankAccount(String accountNumber, double initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = Math.max(0.0, initialBalance);
    }

    public void deposit(double amount) {
        if (amount > 0) this.balance += amount;
    }

    public double getBalance() {
        return this.balance;
    }
}
```

#### 2. Inheritance (`extends`)
Subclasses inherit attributes and methods from a superclass:
```java
public class SavingsAccount extends BankAccount {
    private double interestRate;

    public SavingsAccount(String accNo, double balance, double rate) {
        super(accNo, balance); // Invoke superclass constructor
        this.interestRate = rate;
    }

    public void applyInterest() {
        deposit(getBalance() * (interestRate / 100.0));
    }
}
```

#### 3. Polymorphism & Interfaces (`implements`)
Treating different underlying implementations through a common interface contract:
```java
public interface PaymentGateway {
    boolean processPayment(double amount);
}

public class StripeGateway implements PaymentGateway {
    @Override
    public boolean processPayment(double amount) {
        System.out.println("Processing $" + amount + " via Stripe API.");
        return true;
    }
}
```

#### 4. Modern Java 17+ Records (Immutable Data Carriers)
Eliminates boilerplate getters, constructors, `equals()`, and `hashCode()`:
```java
// Pure immutable DTO in one line!
public record OrderDto(long orderId, String customerEmail, double totalAmount) {}
```
""",
        "hint": "💡 In Java, every class extends `java.lang.Object`. Always annotate overridden methods with `@Override` so the compiler catches naming typos!",
        "practice": "Build an `Employee` hierarchy with `Manager` and `Engineer` subclasses overriding a `calculateBonus()` method."
    },

    "variables": {
        "explain": """### ☕ Java Data Types & Memory Allocation

Java is **statically typed** and enforces strict type boundaries at compile time.

#### 1. Primitive Data Types (Stored on the Stack)
Java has exactly 8 primitive scalar types:
- `byte` (8-bit signed, range: -128 to 127)
- `short` (16-bit signed, range: -32,768 to 32,767)
- `int` (32-bit signed, default integer type)
- `long` (64-bit signed, suffix with `L`: `10000000000L`)
- `float` (32-bit IEEE 754 float, suffix with `f`: `3.14f`)
- `double` (64-bit IEEE 754 float, default decimal type)
- `boolean` (`true` or `false`)
- `char` (16-bit Unicode character: `'A'`, `'\\u0041'`)

#### 2. Reference Types (Stored on the JVM Heap)
- Objects, Arrays, and Strings are reference types.
- The **reference pointer** (4 or 8 bytes depending on Compressed OOPs) lives on the thread stack, while the actual object body lives on the **JVM Heap**.
```java
public class MemoryDemo {
    public static void main(String[] args) {
        int primitiveAge = 25;                  // Direct stack value
        String name = new String("PyMentor");    // Pointer on stack -> Object in heap
    }
}
```
"""
    },

    "jvm": {
        "explain": """### ☕ JVM Architecture & Garbage Collection

When Java source code (`.java`) is compiled by `javac`, it generates platform-independent **Bytecode** (`.class`). The **Java Virtual Machine (JVM)** executes this bytecode:

1. **ClassLoader Subsystem**: Loading, Linking (Verification, Preparation, Resolution), Initialization.
2. **JVM Runtime Memory Areas**:
   - **Eden & Survivor (Young Generation)**: Where new objects are rapidly allocated.
   - **Tenured (Old Generation)**: Objects that survive multiple GC cycles are promoted here.
   - **Metaspace**: Stores class metadata in native OS RAM.
   - **JVM Stack**: Stack frames for thread method calls.
3. **Garbage Collection (G1GC & ZGC)**: Automatically reclaims unreachable heap memory without manual `free()`.
"""
    }
}

C_KNOWLEDGE = {
    "pointers": {
        "explain": """### ⚙️ Deep Dive: C Pointers & Memory Architecture

In the C programming language, a **pointer** is a variable that stores the memory address of another variable. Pointers give C its unmatched speed and direct hardware control.

#### 1. The Address-of (`&`) and Dereference (`*`) Operators
```c
#include <stdio.h>

int main(void) {
    int target = 42;
    int *ptr = &target; // ptr holds the memory address of target

    printf("Value of target:   %d\\n", target);
    printf("Address of target: %p\\n", (void *)&target);
    printf("Value of ptr:      %p\\n", (void *)ptr);
    printf("Dereferenced *ptr: %d\\n", *ptr); // Reads value at the address

    // Mutating memory through pointer:
    *ptr = 99;
    printf("New target value:  %d\\n", target); // Output: 99
    return 0;
}
```

#### 2. Pointer Arithmetic Rule
When adding an integer $k$ to a pointer `T *ptr`, the address advances by $k \\times \\text{sizeof}(T)$ bytes:
$$\\text{Address}(\\text{ptr} + k) = \\text{Address}(\\text{ptr}) + (k \\times \\text{sizeof}(T))$$

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr; // Decay to pointer to first element

printf("First:  %d\\n", *p);       // 10
printf("Second: %d\\n", *(p + 1)); // 20 (advances by 4 bytes)
```

#### 3. Dynamic Heap Allocation (`malloc` & `free`)
```c
#include <stdlib.h>

int *allocate_buffer(size_t size) {
    int *buf = (int *)malloc(size * sizeof(int));
    if (buf == NULL) return NULL; // Always check for allocation failure!
    
    // Fill buffer
    for (size_t i = 0; i < size; i++) buf[i] = (int)i * 10;
    return buf;
}

void cleanup(int **buf_ptr) {
    if (buf_ptr && *buf_ptr) {
        free(*buf_ptr);
        *buf_ptr = NULL; // Prevent dangling pointer!
    }
}
```
"""
    },

    "loops": {
        "explain": """### ⚙️ Loops and Iteration in C

C provides 3 fundamental loop constructs with direct translation to CPU branch and jump instructions (`jmp`, `jne`):

#### 1. Standard `for` Loop
```c
#include <stdio.h>

int main(void) {
    // for (init; condition; step)
    for (int i = 0; i < 5; i++) {
        printf("Index: %d\\n", i);
    }
    return 0;
}
```

#### 2. Fast Pointer-Based Array Traversal
In systems programming, traversing an array via a pointer increment is faster than index lookups:
```c
#include <stdio.h>

void print_array(const int *arr, size_t length) {
    const int *end = arr + length;
    for (const int *ptr = arr; ptr < end; ++ptr) {
        printf("%d ", *ptr);
    }
    printf("\\n");
}
```

#### 3. `while` and `do-while` Loops
```c
int count = 10;
while (count > 0) {
    count--;
}

int retry = 0;
do {
    retry++;
} while (retry < 3);
```
"""
    },

    "structs": {
        "explain": """### ⚙️ C Structs, Memory Alignment & Padding

In C, a `struct` is a composite type that groups variables under a single memory block.

#### 1. Memory Alignment and Compiler Padding
```c
#include <stdio.h>

struct Misaligned {
    char a;    // 1 byte
    // 3 bytes padding inserted by compiler!
    int b;     // 4 bytes (aligned to 4-byte boundary)
    short c;   // 2 bytes
    // 2 bytes padding to round total size to multiple of 4
}; // Total size = 12 bytes!

struct Optimized {
    int b;     // 4 bytes
    short c;   // 2 bytes
    char a;    // 1 byte
    // 1 byte padding
}; // Total size = 8 bytes! (33% RAM savings)
```
"""
    }
}

CPP_KNOWLEDGE = {
    "raii": {
        "explain": """### ⚡ Modern C++: RAII & Smart Pointers

**RAII (Resource Acquisition Is Initialization)** is the foundation of Modern C++ systems engineering. Resources (memory, sockets, mutexes) are tied to object lifetimes on the stack. When the object goes out of scope, its destructor deterministically cleans up the resource with **zero leaks**.

#### 1. `std::unique_ptr` (Exclusive Ownership, 0 Overhead)
```cpp
#include <iostream>
#include <memory>

class DatabaseConnection {
public:
    DatabaseConnection() { std::cout << "Connected to DB\\n"; }
    ~DatabaseConnection() { std::cout << "Closed DB connection\\n"; }
    void query() { std::cout << "Executing query...\\n"; }
};

void run_task() {
    // Automatically freed when scope exits, even on exceptions!
    auto conn = std::make_unique<DatabaseConnection>();
    conn->query();
} // Destructor runs HERE automatically!
```

#### 2. `std::shared_ptr` & `std::weak_ptr` (Shared Ownership)
- Uses an atomic reference count control block.
- `std::weak_ptr` breaks circular reference cycles.
"""
    },

    "loops": {
        "explain": """### ⚡ Modern C++ Loops & Ranges

Modern C++ (C++11 through C++20) provides elegant, type-safe iteration:

#### 1. Range-Based `for` Loop
```cpp
#include <iostream>
#include <vector>

int main() {
    std::vector<std::string> engines = {"V8", "HotSpot", "SpiderMonkey", "JSC"};

    // Use const auto& to avoid expensive deep copies!
    for (const auto& engine : engines) {
        std::cout << "JavaScript Engine: " << engine << std::endl;
    }
    return 0;
}
```

#### 2. C++20 Ranges & Views
```cpp
#include <iostream>
#include <vector>
#include <ranges>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Lazy, non-allocating transformation pipeline:
    auto evens_doubled = numbers 
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * 2; });

    for (int n : evens_doubled) {
        std::cout << n << " "; // 4 8 12 16 20
    }
    std::cout << std::endl;
}
```
"""
    },

    "oop": {
        "explain": """### ⚡ Modern C++ Object-Oriented Architecture & VTables

#### 1. Pure Virtual Interfaces & Virtual Destructors
```cpp
#include <iostream>
#include <memory>

class RenderEngine {
public:
    // ALWAYS declare base class destructor virtual to prevent memory leaks!
    virtual ~RenderEngine() = default;
    virtual void renderFrame() = 0; // Pure virtual method
};

class VulkanEngine : public RenderEngine {
public:
    void renderFrame() override {
        std::cout << "Rendering frame via Vulkan pipeline.\\n";
    }
};
```
"""
    }
}


def detect_polyglot_response(text: str, current_topic: str = "", level: str = "beginner") -> Optional[str]:
    """
    Detects if the query targets Java, C, Modern C++, or Python,
    and returns a textbook-grade, rich systems response.
    """
    clean_text = (text + " " + current_topic).lower()

    # 1. Check for Java Queries
    is_java = any(k in clean_text for k in [
        "java", "jvm", "jdk", "spring", "bytebuffer", "system.out",
        "public static void main", "garbage collect", "g1gc", "zgc",
        "hashmap in java", "records in java"
    ])
    if is_java:
        if any(k in clean_text for k in ["loop", "for loop", "while", "iteration", "for-each", "foreach"]):
            return JAVA_KNOWLEDGE["loops"]["explain"]
        if any(k in clean_text for k in ["oop", "class", "object", "interface", "inheritance", "record", "polymorphism"]):
            return JAVA_KNOWLEDGE["oop"]["explain"]
        if any(k in clean_text for k in ["variable", "data type", "primitive", "memory", "int vs integer"]):
            return JAVA_KNOWLEDGE["variables"]["explain"]
        if any(k in clean_text for k in ["jvm", "garbage", "gc", "heap", "stack", "metaspace"]):
            return JAVA_KNOWLEDGE["jvm"]["explain"]
        return """### ☕ Enterprise Java Systems Mentorship

Welcome to the Enterprise Java Engineering track! I am your AI Systems Mentor.

Java 21 LTS powers mission-critical enterprise architectures, microservices (Spring Boot / Quarkus), high-throughput distributed systems, and real-time streaming backends.

**Core Java Topics you can ask me about:**
- 🔄 **Loops & Control Flow**: Standard `for`, enhanced `for-each`, `while`, and Java 8 Streams.
- 🏛️ **OOP Architecture**: Encapsulation, inheritance, interfaces, abstract classes, and modern Java 17+ Records.
- ⚡ **JVM Internals**: Heap architecture, Garbage Collection (G1GC / ZGC), JIT compilation, and ClassLoading.
- 🧵 **Concurrency & Virtual Threads**: `ExecutorService`, `CompletableFuture`, and Project Loom Virtual Threads.

What specific Java topic or code problem would you like to explore? 🚀"""

    # 2. Check for C Queries
    is_c = any(k in clean_text for k in [
        "c language", "in c ", "in c?", "pointers in c", "pointer in c", "malloc", "free(",
        "pthreads", "sizeof", "printf", "stdio.h", "bitfield", "struct in c", "segmentation fault"
    ])
    if is_c:
        if any(k in clean_text for k in ["pointer", "memory", "address", "dereference", "malloc", "free"]):
            return C_KNOWLEDGE["pointers"]["explain"]
        if any(k in clean_text for k in ["loop", "for loop", "while", "iteration"]):
            return C_KNOWLEDGE["loops"]["explain"]
        if any(k in clean_text for k in ["struct", "union", "padding", "alignment", "bitfield"]):
            return C_KNOWLEDGE["structs"]["explain"]
        return """### ⚙️ ANSI C Systems Engineering Mentorship

Welcome to the ANSI C Systems Programming track!

C provides unmatched direct hardware access, deterministic memory layout, and zero runtime overhead. It powers operating system kernels (Linux, Windows NT), device drivers, embedded firmware, and database engines.

**Core C Systems Topics you can ask me about:**
- 🎯 **Pointers & Memory**: Addressing (`&`), dereferencing (`*`), pointer arithmetic, double pointers, and function pointers.
- 📦 **Dynamic Allocation**: Heap management with `malloc()`, `calloc()`, `realloc()`, `free()`, and memory leak prevention.
- 🏗️ **Structs & Memory Layout**: Struct alignment, compiler padding, unions, and bitfields.
- 🧵 **POSIX Multithreading**: Thread creation, mutex locks, condition variables, and race conditions.

What C concept or code challenge would you like to examine? ⚙️"""

    # 3. Check for C++ Queries
    is_cpp = any(k in clean_text for k in [
        "c++", "cpp", "modern c++", "raii", "unique_ptr", "shared_ptr", "std::",
        "cout", "vector<", "template<", "virtual destructor", "vtable", "rule of 5", "rule of five"
    ])
    if is_cpp:
        if any(k in clean_text for k in ["raii", "smart pointer", "unique_ptr", "shared_ptr", "memory"]):
            return CPP_KNOWLEDGE["raii"]["explain"]
        if any(k in clean_text for k in ["loop", "range", "iteration", "views"]):
            return CPP_KNOWLEDGE["loops"]["explain"]
        if any(k in clean_text for k in ["oop", "class", "virtual", "vtable", "destructor"]):
            return CPP_KNOWLEDGE["oop"]["explain"]
        return """### ⚡ Modern C++ Systems Architecture Mentorship

Welcome to Modern C++ (C++11 through C++20)!

Modern C++ provides type-safe, zero-cost abstractions, deterministic resource management via RAII, and ultra-high-performance compute capability for game engines, high-frequency trading (HFT), and machine learning runtimes.

**Core Modern C++ Topics you can ask me about:**
- ⚡ **RAII & Smart Pointers**: `std::unique_ptr`, `std::shared_ptr`, custom deleters, and leak-free resource lifecycles.
- 🔄 **Modern Loops & Ranges**: Range-based for loops, `std::views`, and non-allocating transformation pipelines.
- 🏛️ **Polymorphic Architecture**: Virtual method tables (VTable), abstract classes, and virtual destructors.
- 🧩 **Templates & Concepts**: Generic metaprogramming and C++20 `concepts`.

What C++ architecture or problem are you working on? ⚡"""

    return None
