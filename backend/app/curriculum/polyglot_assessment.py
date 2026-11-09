# -*- coding: utf-8 -*-
"""
Polyglot Diagnostic Assessment Questions (Python, C, Modern C++, Enterprise Java).
Authoritative, systems-level diagnostic questions for authentic skill calibration.
"""

from typing import Dict, List

POLYGLOT_QUESTIONS: Dict[str, List[dict]] = {
    "c": [
        {
            "id": 101,
            "text": "What is printed by the following C program?\n```c\n#include <stdio.h>\nint main() {\n    int arr[] = {10, 20, 30, 40};\n    int *p = arr;\n    printf(\"%d\", *(p + 2));\n    return 0;\n}\n```",
            "type": "mcq",
            "options": ["10", "20", "30", "Address of arr[2]"],
            "correct_answer": "2",
            "difficulty": "medium",
            "topic": "Pointers & Memory",
            "topic_slug": "c-pointers",
            "explanation": "Pointer arithmetic in C scales by sizeof(type). Since p points to arr[0], p + 2 offsets by 2 * sizeof(int), dereferencing *(p + 2) yields arr[2] which is 30."
        },
        {
            "id": 102,
            "text": "In which memory segment are local non-static variables stored during C function execution?",
            "type": "mcq",
            "options": ["Data Segment", "BSS Segment", "Call Stack", "Heap Memory"],
            "correct_answer": "2",
            "difficulty": "easy",
            "topic": "Memory Architecture",
            "topic_slug": "c-memory",
            "explanation": "Automatic local variables are pushed onto the Call Stack when entering a function frame and popped automatically upon return."
        },
        {
            "id": 103,
            "text": "What is the primary difference between `malloc()` and `calloc()` in standard C (<stdlib.h>)?",
            "type": "mcq",
            "options": [
                "malloc() allocates on stack; calloc() allocates on heap",
                "calloc() zero-initializes memory; malloc() leaves memory uninitialized (indeterminate garbage)",
                "calloc() cannot be freed with free()",
                "malloc() can allocate contiguous arrays while calloc() only allocates single structs"
            ],
            "correct_answer": "1",
            "difficulty": "easy",
            "topic": "Dynamic Memory Allocation",
            "topic_slug": "c-memory",
            "explanation": "calloc(n, size) clears the allocated memory block by setting all bytes to zero. malloc(size) does not clear memory, leaving indeterminate values."
        },
        {
            "id": 104,
            "text": "Why is `sizeof(struct { char a; int b; })` typically 8 bytes instead of 5 on 32-bit and 64-bit architectures?",
            "type": "mcq",
            "options": [
                "Compiler adds a null terminator byte",
                "CPU bus memory alignment padding: 4-byte integers must align on 4-byte boundaries",
                "char is automatically promoted to double in structs",
                "The struct keyword adds 3 bytes of header metadata"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Struct Alignment & Padding",
            "topic_slug": "c-structs",
            "explanation": "Processors fetch data most efficiently when word-aligned. To align the 4-byte int 'b' on a multiple of 4, the compiler inserts 3 bytes of padding after 'a'."
        },
        {
            "id": 105,
            "text": "What occurs if a character array in C is printed with `printf(\"%s\", str)` but lacks a terminating `\'\\0\'` character?",
            "type": "mcq",
            "options": [
                "Compiler syntax error",
                "Prints only the first character",
                "Undefined behavior: printf continues reading adjacent memory until a zero byte is found, risking buffer over-read",
                "Automatically appends a space and stops"
            ],
            "correct_answer": "2",
            "difficulty": "medium",
            "topic": "String Manipulation",
            "topic_slug": "c-strings",
            "explanation": "printf with %s expects a null-terminated C string. Without '\0', it continues scanning past array bounds, reading indeterminate memory or triggering a segmentation fault."
        },
        {
            "id": 106,
            "text": "Which bitwise expression correctly checks if the 3rd bit (0-indexed) of integer `x` is set (1)?",
            "type": "mcq",
            "options": [
                "(x & (1 << 3)) != 0",
                "(x | (1 << 3)) == 0",
                "x ^ 3 == 1",
                "(x >> 3) == 0"
            ],
            "correct_answer": "0",
            "difficulty": "medium",
            "topic": "Bitwise Operations",
            "topic_slug": "c-bitwise",
            "explanation": "(1 << 3) generates the bitmask 00001000 (decimal 8). Performing bitwise AND (&) masks all other bits; if the result is non-zero, bit 3 is set."
        },
        {
            "id": 107,
            "text": "What is the correct declaration for a function pointer `fp` that points to a function returning `double` and accepting two `int` parameters?",
            "type": "mcq",
            "options": [
                "double *fp(int, int);",
                "double (*fp)(int, int);",
                "(*double fp)(int, int);",
                "fp(double)(int, int);"
            ],
            "correct_answer": "1",
            "difficulty": "hard",
            "topic": "Function Pointers",
            "topic_slug": "c-pointers",
            "explanation": "double (*fp)(int, int) declares fp as a pointer to a function taking two ints and returning double. Without parentheses, double *fp(int, int) declares a function returning a pointer to double."
        },
        {
            "id": 108,
            "text": "What is the output of the following macro call?\n```c\n#define SQUARE(x) x * x\nprintf(\"%d\", SQUARE(2 + 3));\n```",
            "type": "mcq",
            "options": ["25", "11", "10", "13"],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Preprocessor Directives",
            "topic_slug": "c-preprocessor",
            "explanation": "Macros perform raw textual substitution before compilation: SQUARE(2 + 3) expands to 2 + 3 * 2 + 3. By operator precedence, 3 * 2 = 6, so 2 + 6 + 3 = 11. Proper macro safety requires #define SQUARE(x) ((x) * (x))."
        },
        {
            "id": 109,
            "text": "What is a 'Dangling Pointer' in C programming?",
            "type": "mcq",
            "options": [
                "A pointer initialized to NULL",
                "A pointer that points to deallocated (freed) memory",
                "A void pointer that cannot be dereferenced",
                "A pointer declared without an asterisk"
            ],
            "correct_answer": "1",
            "difficulty": "easy",
            "topic": "Memory Safety",
            "topic_slug": "c-memory",
            "explanation": "A dangling pointer arises when memory pointed to is released (via free() or stack frame pop) while the pointer still holds that stale address."
        },
        {
            "id": 110,
            "text": "What does the declaration `const int *ptr` signify in C?",
            "type": "mcq",
            "options": [
                "The pointer address is constant and cannot point elsewhere",
                "The integer pointed to is read-only through ptr; ptr itself can point to another address",
                "Both pointer and value are strictly immutable",
                "Allocates integer on read-only flash memory"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Const Correctness",
            "topic_slug": "c-pointers",
            "explanation": "'const int *ptr' means pointer to constant int (value cannot be changed via *ptr). In contrast, 'int * const ptr' means constant pointer to mutable int."
        }
    ],
    "cpp": [
        {
            "id": 201,
            "text": "What is the foundational principle of Resource Acquisition Is Initialization (RAII) in Modern C++?",
            "type": "mcq",
            "options": [
                "All variables must be allocated on the heap inside constructors",
                "Resource lifetime is bound to object lifetime; acquire in constructor, release deterministically in destructor",
                "All classes must inherit from std::raii_base",
                "Global resources are loaded when main() starts"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "RAII & Smart Pointers",
            "topic_slug": "cpp-raii",
            "explanation": "RAII guarantees exception-safe resource cleanup (memory, mutex locks, sockets) because stack objects invoke destructors automatically during stack unwinding."
        },
        {
            "id": 202,
            "text": "Which smart pointer in C++11/20 provides zero-overhead exclusive ownership and cannot be copied?",
            "type": "mcq",
            "options": ["std::shared_ptr", "std::weak_ptr", "std::unique_ptr", "std::auto_ptr"],
            "correct_answer": "2",
            "difficulty": "easy",
            "topic": "Smart Pointers",
            "topic_slug": "cpp-smart-pointers",
            "explanation": "std::unique_ptr enforces single ownership with deleted copy constructor. Ownership can only be transferred using move semantics (std::move)."
        },
        {
            "id": 203,
            "text": "Why must a polymorphic base class declare a `virtual` destructor in C++?",
            "type": "mcq",
            "options": [
                "Otherwise instances cannot be instantiated with new",
                "To ensure the derived class destructor executes when deleting an object through a base class pointer",
                "To allow private inheritance",
                "It is mandatory by the C++ compiler syntax for all structs"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Polymorphism & OOP",
            "topic_slug": "cpp-oop",
            "explanation": "Deleting a derived object via Base* with a non-virtual destructor results in undefined behavior; only Base::~Base() runs, causing derived resource leaks."
        },
        {
            "id": 204,
            "text": "What does `std::move(x)` perform under the hood in C++?",
            "type": "mcq",
            "options": [
                "Physically copies the bytes of x to new memory",
                "Performs an unconditional static_cast to an rvalue reference (Type&&), enabling move constructors",
                "Deletes x immediately from memory",
                "Creates a background thread to transfer memory asynchronously"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Move Semantics",
            "topic_slug": "cpp-move",
            "explanation": "std::move does not move anything at runtime. It is purely a compile-time cast that converts an lvalue to an rvalue reference (static_cast<T&&>(x)) so move constructors can steal its resources."
        },
        {
            "id": 205,
            "text": "What happens to existing iterators and references to elements of a `std::vector` when `push_back()` triggers capacity reallocation?",
            "type": "mcq",
            "options": [
                "They remain fully valid and auto-update",
                "They are all invalidated because elements were copied/moved to a new larger heap block",
                "Only the end() iterator is invalidated",
                "A std::realloc_exception is thrown"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "STL Containers",
            "topic_slug": "cpp-stl",
            "explanation": "When vector size exceeds capacity, it allocates a new contiguous block, moves elements, and deallocates old memory. Any pointer or iterator to the old block is invalidated."
        },
        {
            "id": 206,
            "text": "According to the C++ 'Rule of Five', if you define a custom destructor, what 4 other special members should you consider?",
            "type": "mcq",
            "options": [
                "Copy constructor, copy assignment, move constructor, move assignment",
                "Default constructor, print method, equals method, clone method",
                "Virtual constructor, static constructor, friend operator, cast operator",
                "Heap allocator, stack deallocator, serialiser, deserialiser"
            ],
            "correct_answer": "0",
            "difficulty": "hard",
            "topic": "Class Design & Lifetimes",
            "topic_slug": "cpp-classes",
            "explanation": "The Rule of Five states that managing a resource requires explicitly managing or deleting: Destructor, Copy Constructor, Copy Assignment, Move Constructor, and Move Assignment Operator."
        },
        {
            "id": 207,
            "text": "What is the primary benefit of `std::string_view` (introduced in C++17) over `const std::string&`?",
            "type": "mcq",
            "options": [
                "std::string_view is thread-safe while std::string is not",
                "Zero-allocation non-owning view of contiguous character buffers (string literals, substrings, arrays)",
                "Allows modifying the underlying characters in-place without reallocation",
                "Automatically compresses string data using UTF-8"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Modern C++ Strings",
            "topic_slug": "cpp-strings",
            "explanation": "std::string_view contains only a pointer and length (16 bytes). Passing string literals or substrings to functions does not allocate dynamic memory on the heap."
        },
        {
            "id": 208,
            "text": "Can a `const` member function in C++ modify a class member variable marked with the `mutable` specifier?",
            "type": "mcq",
            "options": [
                "No, const strictly forbids all modifications",
                "Yes, mutable allows modification even on const objects (useful for mutexes, caching, counters)",
                "Only if compiled in debug mode",
                "Only inside the class constructor"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Const Correctness",
            "topic_slug": "cpp-const",
            "explanation": "The mutable keyword exempts a member from const-correctness rules. Common production use cases include mutable std::mutex or memoization cache inside const getter methods."
        },
        {
            "id": 209,
            "text": "How is dynamic polymorphic dispatch typically implemented by modern C++ compilers?",
            "type": "mcq",
            "options": [
                "String name lookup in a hash table at each call site",
                "Virtual method tables (vtables) and hidden pointer (vptr) in each object instance",
                "Direct CPU register jumping via labels",
                "Bytecode interpretation through an embedded JIT"
            ],
            "correct_answer": "1",
            "difficulty": "hard",
            "topic": "Vtables & Internals",
            "topic_slug": "cpp-internals",
            "explanation": "Classes with virtual functions contain an invisible vptr pointer pointing to a static array of function pointers (vtable). Calls through base pointers index this table in O(1) time."
        },
        {
            "id": 210,
            "text": "What does SFINAE stand for in template metaprogramming?",
            "type": "mcq",
            "options": [
                "Static Functions In Namespaces Always Execute",
                "Substitution Failure Is Not An Error",
                "Standard Framework for Inline Assembly Execution",
                "System File Initialization And Navigation Engine"
            ],
            "correct_answer": "1",
            "difficulty": "hard",
            "topic": "Templates & Metaprogramming",
            "topic_slug": "cpp-templates",
            "explanation": "SFINAE (Substitution Failure Is Not An Error) is the rule that when substituting deduced template types fails, the compiler discards the candidate rather than emitting a compile error."
        }
    ],
    "java": [
        {
            "id": 301,
            "text": "In the Java Virtual Machine (JVM) memory architecture, where are all object instances (`new Object()`) stored?",
            "type": "mcq",
            "options": ["Thread Call Stack", "Metaspace / PermGen", "JVM Heap Memory", "Native Program Counter (PC) Register"],
            "correct_answer": "2",
            "difficulty": "easy",
            "topic": "JVM Memory Model",
            "topic_slug": "java-jvm",
            "explanation": "In Java, all objects and array instances are allocated on the Heap. The Call Stack holds local variable primitives and object reference pointers."
        },
        {
            "id": 302,
            "text": "What does `str1 == str2` test when comparing two Java `String` variables?",
            "type": "mcq",
            "options": [
                "Lexicographical character sequence equality",
                "Reference equality (whether both reference variables point to the exact same memory address)",
                "Length comparison",
                "Case-insensitive match"
            ],
            "correct_answer": "1",
            "difficulty": "easy",
            "topic": "Strings & Equality",
            "topic_slug": "java-strings",
            "explanation": "In Java, == compares memory references for objects. To test value equality of string characters, str1.equals(str2) must always be used."
        },
        {
            "id": 303,
            "text": "What is the difference between Minor Garbage Collection and Full Garbage Collection in the JVM?",
            "type": "mcq",
            "options": [
                "Minor GC only deletes strings; Full GC deletes arrays",
                "Minor GC collects dead objects in Young Generation (Eden/Survivor); Full GC cleans the entire heap including Old/Tenured generation",
                "Minor GC stops all threads; Full GC runs entirely without pause",
                "Minor GC is manual; Full GC is automatic"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Garbage Collection",
            "topic_slug": "java-gc",
            "explanation": "Generational GC collects the Young Generation frequently with minimal latency (Minor GC). When Old Generation fills up, a comprehensive Full GC runs."
        },
        {
            "id": 304,
            "text": "In Java 8+, what occurs when a single hash bucket in `java.util.HashMap` exceeds 8 colliding elements (`TREEIFY_THRESHOLD`)?",
            "type": "mcq",
            "options": [
                "Throws a ConcurrentModificationException",
                "Converts the linked list of collisions into a balanced Red-Black Tree, improving lookup from O(n) to O(log n)",
                "Discards old entries silently",
                "Resizes the entire map to twice the size immediately without treeifying"
            ],
            "correct_answer": "1",
            "difficulty": "hard",
            "topic": "Collections Internals",
            "topic_slug": "java-collections",
            "explanation": "To prevent worst-case O(n) degradation and DoS collision attacks, Java 8 replaces linked lists with Red-Black tree nodes (TreeNode) when collisions in a bin reach 8."
        },
        {
            "id": 305,
            "text": "What does the `volatile` keyword guarantee when applied to a variable in Java?",
            "type": "mcq",
            "options": [
                "Atomic execution of compound operations like count++",
                "Memory visibility across threads: reads and writes bypass CPU registers/caches and go directly to main memory",
                "Object serialization is bypassed",
                "The variable is stored in read-only ROM"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Multithreading & Concurrency",
            "topic_slug": "java-concurrency",
            "explanation": "volatile guarantees visibility (all threads see the latest write) and establishes a happens-before memory ordering. It does NOT make compound operations like i++ atomic."
        },
        {
            "id": 306,
            "text": "What distinguishes Checked Exceptions from Unchecked Exceptions in the Java type hierarchy?",
            "type": "mcq",
            "options": [
                "Checked exceptions cause JVM crash; unchecked exceptions do not",
                "Checked exceptions inherit from Exception and must be handled via try-catch or declared in throws; unchecked inherit from RuntimeException",
                "Unchecked exceptions cannot be caught in try-catch",
                "Checked exceptions only occur in web applications"
            ],
            "correct_answer": "1",
            "difficulty": "easy",
            "topic": "Exception Handling",
            "topic_slug": "java-exceptions",
            "explanation": "Checked exceptions (IOException, SQLException) are verified at compile-time. Unchecked exceptions (NullPointerException, IllegalArgumentException) inherit from RuntimeException."
        },
        {
            "id": 307,
            "text": "What is Type Erasure in Java Generics (`List<T>`)?",
            "type": "mcq",
            "options": [
                "Deleting classes from the classpath after compilation",
                "The compiler removes all generic type parameters at compile-time and inserts type casts, maintaining backwards compatibility with raw types",
                "Automatic conversion of primitives to wrapper types",
                "Deleting unused variables during Garbage Collection"
            ],
            "correct_answer": "1",
            "difficulty": "hard",
            "topic": "Generics & Metaprogramming",
            "topic_slug": "java-generics",
            "explanation": "Java generics are implemented via Type Erasure. At bytecode level, List<String> and List<Integer> both become raw List with casts inserted by the compiler."
        },
        {
            "id": 308,
            "text": "Which interface must a class implement to be automatically closed in a Java `try-with-resources` statement?",
            "type": "mcq",
            "options": ["java.lang.AutoCloseable", "java.io.Serializable", "java.lang.Cloneable", "java.util.Disposable"],
            "correct_answer": "0",
            "difficulty": "easy",
            "topic": "Resource Management",
            "topic_slug": "java-resources",
            "explanation": "The try-with-resources statement requires resources to implement java.lang.AutoCloseable (or java.io.Closeable), invoking close() deterministically."
        },
        {
            "id": 309,
            "text": "What is the difference between an Abstract Class and an Interface in Java 8+?",
            "type": "mcq",
            "options": [
                "Interfaces cannot have method implementations at all",
                "An abstract class can hold instance state (fields) and constructors, whereas interfaces cannot maintain mutable instance state",
                "A class can extend multiple abstract classes but only implement one interface",
                "Abstract classes cannot be inherited by public classes"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "OOP Architecture",
            "topic_slug": "java-oop",
            "explanation": "Java 8 added default/static methods to interfaces, but interfaces cannot hold instance variables or constructors. Classes also only support single class inheritance."
        },
        {
            "id": 310,
            "text": "Are intermediate operations in the Java Stream API (such as `.filter()` or `.map()`) evaluated eagerly or lazily?",
            "type": "mcq",
            "options": [
                "Eagerly: they execute immediately when declared and produce new lists",
                "Lazily: they are recorded as pipeline stages and only execute when a terminal operation (like .collect() or .count()) is invoked",
                "Eagerly in parallel streams, lazily in sequential streams",
                "Asynchronously in background daemon threads"
            ],
            "correct_answer": "1",
            "difficulty": "medium",
            "topic": "Java Streams & Lambdas",
            "topic_slug": "java-streams",
            "explanation": "Intermediate operations are lazy; they transform a stream into another stream without consuming elements until a terminal operation triggers the pipeline execution."
        }
    ]
}

