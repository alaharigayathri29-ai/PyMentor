# -*- coding: utf-8 -*-
"""
Polyglot Engineering Curriculum Matrix for C, Modern C++, and Enterprise Java.
Each track contains 7 structured modules with textbook-grade systems explanations,
architecture diagrams, memory layout analysis, code demonstrations, and interview Q&As.
"""

from typing import Dict, List

POLYGLOT_CURRICULUM: Dict[str, List[dict]] = {
    "c": [
        {
            "module_number": 1,
            "module_name": "C Fundamentals & Memory Architecture",
            "topics": [
                {
                    "id": 1001,
                    "slug": "c-fundamentals",
                    "name": "Data Types, CPU Alignment & Byte Storage",
                    "order": 1,
                    "difficulty": "beginner",
                    "icon": "⚙️",
                    "subtopics": [
                        "Primitive Scalar Types (char, short, int, long, float, double)",
                        "CPU Word Boundaries & 32-bit vs 64-bit Architecture",
                        "Endianness: Big-Endian vs Little-Endian Memory Inspection",
                        "Integer Sign Representation & Two's Complement Bit Arithmetic"
                    ],
                    "learning_objectives": [
                        "Examine raw bytes in memory using unsigned char* pointers",
                        "Determine CPU endianness programmatically via unions and pointer casts",
                        "Avoid undefined behavior in integer signed overflow and implicit conversions"
                    ],
                    "lesson_content": {
                        "introduction": "The C programming language was designed by Dennis Ritchie at Bell Labs to implement the UNIX operating system. C provides unmatched direct hardware access and deterministic memory efficiency. Unlike managed languages (Python, Java), C has no runtime overhead, no garbage collector, and no virtual machine. Every variable is mapped directly to physical memory addresses on the CPU bus.",
                        "explanation": """### 1. Architectural Memory Layout & CPU Alignment

#### 1.1 The Virtual Address Space in C
When a C binary executes, the operating system kernel maps its address space into standard memory segments:
1. **Text Segment (.text)**: Contains read-only machine instructions directly executed by the CPU.
2. **Data Segment (.data)**: Stores global and static variables explicitly initialized by the programmer.
3. **BSS Segment (.bss)**: Stores uninitialized global and static variables, automatically zeroed by the OS loader.
4. **Heap Segment**: Expands upwards from lower addresses toward higher memory via `brk()` / `sbrk()` or `mmap()`, managed manually through `malloc()` and `free()`.
5. **Call Stack**: Expands downwards from higher addresses toward lower memory, allocating activation records (stack frames) for function calls, local variables, and return instruction pointers.

#### 1.2 Two's Complement & Byte Representation
In modern architectures (x86_64, ARM64), signed integers are stored in **Two's Complement** format:
$$\\text{Value} = -b_{n-1} 2^{n-1} + \\sum_{i=0}^{n-2} b_i 2^i$$
This ensures arithmetic addition and subtraction work identically at the transistor ALU level without needing separate sign logic.

#### 1.3 Endianness Detection Under the Hood
Memory is addressed as individual 8-bit bytes. When storing a multi-byte integer (e.g. `0x12345678`), architectures differ:
- **Little-Endian (x86, ARM default)**: Least significant byte (`0x78`) is stored at the lowest address.
- **Big-Endian (Network Byte Order)**: Most significant byte (`0x12`) is stored at the lowest address.

```c
#include <stdio.h>
#include <stdint.h>

void inspect_endianness(void) {
    uint32_t val = 0x12345678;
    uint8_t *byte_ptr = (uint8_t *)&val;
    
    printf("Base Address: %p\\n", (void *)byte_ptr);
    for (int i = 0; i < 4; i++) {
        printf("Byte %d at %p = 0x%02X\\n", i, (void *)(byte_ptr + i), byte_ptr[i]);
    }
    
    if (byte_ptr[0] == 0x78) {
        printf("Architecture is: LITTLE-ENDIAN\\n");
    } else if (byte_ptr[0] == 0x12) {
        printf("Architecture is: BIG-ENDIAN\\n");
    }
}

int main(void) {
    inspect_endianness();
    return 0;
}
```

#### 1.4 Structure Alignment and Padding
CPUs fetch data in 32-bit (4-byte) or 64-bit (8-byte) words. Accessing misaligned memory incurs CPU penalty or hardware bus faults. Therefore, the C compiler inserts invisible **padding bytes**:

```c
struct MisalignedData {
    char a;     // 1 byte
    // 3 bytes padding inserted by compiler
    int b;      // 4 bytes (aligned to 4-byte boundary)
    short c;    // 2 bytes
    // 2 bytes padding to align total struct to multiple of 4
}; // Total sizeof = 12 bytes!
```
By sorting fields by size descending (`int b`, `short c`, `char a`), size shrinks to 8 bytes.
"""
                    }
                },
                {
                    "id": 1002,
                    "slug": "c-pointers-memory",
                    "name": "Pointer Mechanics, Pointer Arithmetic & Arrays",
                    "order": 2,
                    "difficulty": "intermediate",
                    "icon": "🎯",
                    "subtopics": [
                        "Pointer Dereferencing & The Address-of Operator (&)",
                        "Pointer Arithmetic: Scaling by sizeof(T)",
                        "Void Pointers (void*) & Type Casting",
                        "Function Pointers & Dynamic Dispatch Callbacks"
                    ],
                    "learning_objectives": [
                        "Master pointer arithmetic rules when traversing continuous buffers",
                        "Implement higher-order functional callbacks using function pointers",
                        "Safely cast generic void* pointers in systems data structures"
                    ],
                    "lesson_content": {
                        "introduction": "A pointer is a variable that stores the memory address of another variable. Pointers are the heart of C, powering dynamic data structures (linked lists, trees, graphs), hardware register manipulation, and zero-copy performance.",
                        "explanation": """### 1. Pointer Fundamentals & Memory Mapping

#### 1.1 Pointer Scaling Rule
When adding an integer $k$ to a pointer `T *ptr`, the resulting address increments not by $k$ bytes, but by $k \\times \\text{sizeof}(T)$ bytes!
$$\\text{Address}(\\text{ptr} + k) = \\text{Address}(\\text{ptr}) + (k \\times \\text{sizeof}(T))$$

#### 1.2 Function Pointers for Dynamic Dispatch
In C, functions reside in the `.text` segment and have fixed addresses. A function pointer enables passing algorithms as arguments:
```c
#include <stdio.h>

typedef int (*BinaryOp)(int, int);

int add(int a, int b) { return a + b; }
int multiply(int a, int b) { return a * b; }

void execute_operation(int x, int y, BinaryOp op) {
    int res = op(x, y);
    printf("Operation Result: %d\\n", res);
}

int main(void) {
    execute_operation(10, 20, add);       // Output: 30
    execute_operation(10, 20, multiply);  // Output: 200
    return 0;
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 2,
            "module_name": "Dynamic Memory Allocation & Heap Management",
            "topics": [
                {
                    "id": 1003,
                    "slug": "c-dynamic-memory",
                    "name": "Heap Allocation: malloc, calloc, realloc & free",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "📦",
                    "subtopics": [
                        "Heap Architecture & The OS Kernel sbrk / mmap System Calls",
                        "malloc() vs calloc() Zero-Initialization Performance Differences",
                        "realloc() In-Place Expansion vs Relocation Mechanics",
                        "Memory Leaks, Dangling Pointers & Double Free Vulnerabilities"
                    ],
                    "learning_objectives": [
                        "Diagnose memory leaks and heap buffer overflows",
                        "Implement defensive free wrappers that set freed pointers to NULL",
                        "Understand memory fragmentation and allocator binning strategies"
                    ],
                    "lesson_content": {
                        "introduction": "Dynamic memory allocation allows C programs to allocate variables of arbitrary size at runtime. Heap memory persists until explicitly freed by the programmer, demanding disciplined memory hygiene.",
                        "explanation": """### 1. Heap Allocation Lifecycle

#### 1.1 Defensive Allocation Pattern
Always check for NULL return values and neutralize pointers immediately after freeing:
```c
#include <stdio.h>
#include <stdlib.h>

#define SAFE_FREE(ptr) do { free(ptr); (ptr) = NULL; } while(0)

int main(void) {
    size_t count = 1000;
    int *buffer = (int *)calloc(count, sizeof(int));
    if (buffer == NULL) {
        fprintf(stderr, "Out of memory!\\n");
        return 1;
    }

    buffer[0] = 42;
    SAFE_FREE(buffer);
    // Any accidental access to buffer now triggers deterministic segmentation fault instead of subtle data corruption!
    return 0;
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 3,
            "module_name": "Data Structures & Custom Types in C",
            "topics": [
                {
                    "id": 1004,
                    "slug": "c-structures-unions",
                    "name": "Structs, Unions, Bitfields & Memory Packing",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "🏗️",
                    "subtopics": [
                        "Composite Data Layout & Struct Padding Optimization",
                        "Unions for Hardware Register Aliasing & Tagged Variants",
                        "Bitfields for Network Protocol Header Encoding",
                        "Self-Referential Structs & Singly/Doubly Linked Lists"
                    ],
                    "learning_objectives": [
                        "Pack protocol packet headers using `#pragma pack(push, 1)`",
                        "Construct type-safe tagged unions in C",
                        "Build generic linked lists using `void*` or intrusive offset nodes"
                    ],
                    "lesson_content": {
                        "introduction": "Custom types enable modeling real-world abstractions and mapping exact hardware registers in embedded firmware and operating system drivers.",
                        "explanation": """### 1. Protocol Packing & Hardware Registers
```c
#include <stdio.h>
#include <stdint.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  version_ihl;   // Version (4 bits) + IHL (4 bits)
    uint8_t  type_of_service;
    uint16_t total_length;
    uint16_t identification;
    uint16_t flags_fragment_offset;
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t checksum;
    uint32_t src_ip;
    uint32_t dest_ip;
} IPv4Header;
#pragma pack(pop)
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 4,
            "module_name": "C File I/O & Low-Level POSIX System Calls",
            "topics": [
                {
                    "id": 1005,
                    "slug": "c-file-io-posix",
                    "name": "Stream I/O vs POSIX Kernel Descriptors (read, write, mmap)",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "💾",
                    "subtopics": [
                        "Buffered Streams (FILE*, fopen, fread, fwrite, fflush)",
                        "Unbuffered OS System Calls (open, read, write, close, lseek)",
                        "Memory-Mapped File I/O using mmap() for Zero-Copy Operations",
                        "File Locking with fcntl() for Inter-Process Synchronization"
                    ],
                    "learning_objectives": [
                        "Benchmark buffered stdio versus unbuffered POSIX syscall throughput",
                        "Map 10GB+ files into virtual memory using mmap without exhausting RAM"
                    ],
                    "lesson_content": {
                        "introduction": "File I/O in C bridges user-space buffers with operating system kernel page caches and block storage devices.",
                        "explanation": """### 1. High-Performance Zero-Copy mmap File I/O
```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

void read_file_mmap(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return;
    struct stat sb;
    fstat(fd, &sb);
    char *data = mmap(NULL, sb.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (data != MAP_FAILED) {
        printf("First 16 bytes: %.*s\\n", 16, data);
        munmap(data, sb.st_size);
    }
    close(fd);
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 5,
            "module_name": "POSIX Multithreading & Concurrency",
            "topics": [
                {
                    "id": 1006,
                    "slug": "c-multithreading-pthreads",
                    "name": "POSIX Threads (pthreads), Mutexes & Condition Variables",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🧵",
                    "subtopics": [
                        "Thread Creation and Joining with pthread_create / pthread_join",
                        "Race Conditions & Mutual Exclusion with pthread_mutex_t",
                        "Producer-Consumer Queues with pthread_cond_t",
                        "Atomic Operations & Lock-Free Primitives via stdatomic.h"
                    ],
                    "learning_objectives": [
                        "Eliminate thread race conditions using POSIX mutex locks",
                        "Build high-throughput producer-consumer work queues"
                    ],
                    "lesson_content": {
                        "introduction": "Multithreading enables C applications to exploit multiple CPU cores concurrently while sharing a unified address space.",
                        "explanation": """### 1. Producer-Consumer Synchronization
```c
#include <stdio.h>
#include <pthread.h>

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int work_ready = 0;

void* worker(void* arg) {
    pthread_mutex_lock(&lock);
    while (!work_ready) {
        pthread_cond_wait(&cond, &lock);
    }
    printf("[Worker] Processing batch payload!\\n");
    pthread_mutex_unlock(&lock);
    return NULL;
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 6,
            "module_name": "Systems Networking & Socket Programming",
            "topics": [
                {
                    "id": 1007,
                    "slug": "c-socket-programming",
                    "name": "TCP/IP Sockets, Non-blocking I/O & Epoll Event Loops",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🌐",
                    "subtopics": [
                        "Berkeley Sockets: socket, bind, listen, accept, connect",
                        "Network Byte Order vs Host Byte Order (htons, htonl)",
                        "Non-blocking Sockets & Edge-Triggered epoll on Linux",
                        "Building an Asynchronous HTTP Server Engine"
                    ],
                    "learning_objectives": [
                        "Construct a robust multithreaded TCP server from scratch in C",
                        "Handle 100,000+ concurrent network connections using epoll"
                    ],
                    "lesson_content": {
                        "introduction": "Network sockets expose OS kernel networking stacks, enabling distributed network communication over TCP/IP.",
                        "explanation": """### 1. TCP Server Socket Lifecycle
```c
#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>

int start_server(int port) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(port)
    };
    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, 128);
    printf("Server listening on port %d...\\n", port);
    return server_fd;
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 7,
            "module_name": "High Performance C Systems & Memory Allocators",
            "topics": [
                {
                    "id": 1008,
                    "slug": "c-arena-allocator",
                    "name": "Arena & Linear Allocators, Cache Locality & SIMD",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "⚡",
                    "subtopics": [
                        "The Cost of General Purpose malloc Fragmentation",
                        "Designing an Arena (Region-Based) Allocator with Reset",
                        "CPU Cache Lines (L1/L2/L3), False Sharing & Data Prefetching",
                        "SIMD Vectorization with AVX-512 and SSE Intrinsics"
                    ],
                    "learning_objectives": [
                        "Implement an instantaneous zero-overhead Arena memory allocator",
                        "Optimize data structures for 64-byte CPU cache lines"
                    ],
                    "lesson_content": {
                        "introduction": "In high-frequency trading (HFT), game engines, and OS kernels, custom memory allocators outperform standard malloc by orders of magnitude.",
                        "explanation": """### 1. High-Speed Arena Allocator
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    uint8_t *buffer;
    size_t capacity;
    size_t offset;
} Arena;

void* arena_alloc(Arena *a, size_t size) {
    // Align to 8 bytes
    size_t aligned_size = (size + 7) & ~7;
    if (a->offset + aligned_size > a->capacity) return NULL;
    void *ptr = &a->buffer[a->offset];
    a->offset += aligned_size;
    return ptr;
}

void arena_reset(Arena *a) {
    a->offset = 0; // Instant bulk deallocation in O(1)!
}
```
"""
                    }
                }
            ]
        }
    ],

    "cpp": [
        {
            "module_number": 1,
            "module_name": "Modern C++ Systems & Resource Management",
            "topics": [
                {
                    "id": 2001,
                    "slug": "cpp-raii-smart-pointers",
                    "name": "RAII Architecture & Smart Pointers (unique_ptr, shared_ptr)",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "⚡",
                    "subtopics": [
                        "The RAII Idiom (Resource Acquisition Is Initialization)",
                        "Exclusive Ownership: std::unique_ptr & std::make_unique",
                        "Shared Ownership & Reference Counting: std::shared_ptr",
                        "Breaking Cyclic References via std::weak_ptr"
                    ],
                    "learning_objectives": [
                        "Eliminate memory leaks and dangling pointers using modern smart pointers",
                        "Implement custom deleters for POSIX file handles and socket descriptors",
                        "Understand atomic reference count overhead in multithreaded shared_ptr"
                    ],
                    "lesson_content": {
                        "introduction": "Modern C++ (C++11 through C++20) has transformed C++ from 'C with Classes' into a high-level, type-safe, expressive systems language. The cornerstone of Modern C++ is **RAII (Resource Acquisition Is Initialization)**: resources (heap memory, mutex locks, database handles, sockets) are bound to the lifetime of stack objects, guaranteeing zero leaks even in the presence of runtime exceptions.",
                        "explanation": """### 1. RAII Pattern & Smart Pointer Internals

#### 1.1 The Mechanics of RAII
When an exception is thrown in C++, the runtime executes **Stack Unwinding**. As each stack frame is popped, destructors of all local objects in that frame are invoked in reverse order of construction. RAII leverages this deterministic behavior:
```cpp
#include <iostream>
#include <memory>
#include <string>

class NetworkConnection {
private:
    std::string endpoint_;
public:
    NetworkConnection(std::string endpoint) : endpoint_(std::move(endpoint)) {
        std::cout << "[ACQUIRE] Socket opened to " << endpoint_ << std::endl;
    }
    ~NetworkConnection() {
        std::cout << "[RELEASE] Socket closed deterministically for " << endpoint_ << std::endl;
    }
    void transmit(const std::string& packet) {
        std::cout << "Streaming packet: " << packet << std::endl;
    }
};

void process_request() {
    auto conn = std::make_unique<NetworkConnection>("10.0.0.1:443");
    conn->transmit("AUTH_PAYLOAD");
    // Destructor runs automatically when conn goes out of scope!
}
```

#### 1.2 `std::unique_ptr` vs `std::shared_ptr`
- **`std::unique_ptr`**: Exactly **0 bytes of overhead** over a raw pointer. Ownership cannot be copied (`copy constructor = delete`), only transferred via `std::move`.
- **`std::shared_ptr`**: Uses a separate heap-allocated **Control Block** holding:
  1. Strong Reference Count (atomic increment/decrement).
  2. Weak Reference Count.
  3. Custom Deleter.
"""
                    }
                }
            ]
        },
        {
            "module_number": 2,
            "module_name": "Move Semantics & The Rule of 5",
            "topics": [
                {
                    "id": 2002,
                    "slug": "cpp-move-semantics",
                    "name": "Move Semantics, Rvalue References & Rule of Five",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "🚀",
                    "subtopics": [
                        "Lvalues vs Rvalues (Identity vs Expiry)",
                        "Rvalue References (T&&) & Move Constructor / Move Assignment",
                        "The Rule of Five (Destructor, Copy Ctor, Copy Assign, Move Ctor, Move Assign)",
                        "std::move, std::forward & Perfect Forwarding in Templates"
                    ],
                    "learning_objectives": [
                        "Eliminate expensive deep memory copies using move semantics",
                        "Implement the Rule of Five correctly for memory-managing classes",
                        "Master universal references and `std::forward`"
                    ],
                    "lesson_content": {
                        "introduction": "Move semantics introduced in C++11 eliminated unnecessary deep copying of resources by transferring ownership of dynamically allocated data from temporary objects.",
                        "explanation": """### 1. Move Constructors and Rvalue Stealing
```cpp
#include <iostream>
#include <utility>

class HeavyBuffer {
    int* data_;
    size_t size_;
public:
    HeavyBuffer(size_t size) : size_(size), data_(new int[size]) {}
    ~HeavyBuffer() { delete[] data_; }

    // Move Constructor: Steal pointer directly in O(1)!
    HeavyBuffer(HeavyBuffer&& other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }
};
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 3,
            "module_name": "Object-Oriented Architecture & Virtual Tables",
            "topics": [
                {
                    "id": 2003,
                    "slug": "cpp-vtable-polymorphism",
                    "name": "VTable Mechanics, Virtual Destructors & Interface Contracts",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "🏛️",
                    "subtopics": [
                        "Runtime Polymorphism: The `virtual` Keyword & Pure Virtual Functions",
                        "Virtual Method Tables (VTable) and `vptr` Pointer Offset Layout",
                        "Why Base Class Destructors MUST Always Be `virtual`",
                        "Static Polymorphism via CRTP (Curiously Recurring Template Pattern)"
                    ],
                    "learning_objectives": [
                        "Deconstruct the byte layout of classes containing vptr pointers",
                        "Avoid undefined behavior and memory leaks during polymorphic object destruction"
                    ],
                    "lesson_content": {
                        "introduction": "C++ supports runtime polymorphism through dynamic dispatch tables called VTables, as well as zero-cost compile-time static polymorphism.",
                        "explanation": """### 1. VTable Memory Anatomy
Every polymorphic object stores a hidden `vptr` (8 bytes) pointing to the class's shared VTable array of function pointers.
```cpp
class Strategy {
public:
    virtual ~Strategy() = default; // Essential!
    virtual void execute() = 0;
};
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 4,
            "module_name": "Standard Template Library (STL) Internals",
            "topics": [
                {
                    "id": 2004,
                    "slug": "cpp-stl-internals",
                    "name": "Vector Growth, Node Containers & Hash Table Internals",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "📊",
                    "subtopics": [
                        "std::vector Dynamic Doubling & Amortized O(1) Allocation",
                        "Node-based Containers: std::list, std::set (Red-Black Trees)",
                        "std::unordered_map Bucket Array & Collision Resolution",
                        "Custom Hash Functions & Hash Flooding DoS Defense"
                    ],
                    "learning_objectives": [
                        "Pre-allocate memory using `reserve()` to prevent vector reallocation spikes",
                        "Select the mathematically optimal STL container for throughput vs memory overhead"
                    ],
                    "lesson_content": {
                        "introduction": "The C++ Standard Template Library provides high-performance data structures and algorithms engineered with strict algorithmic time complexity guarantees.",
                        "explanation": """### 1. Vector Geometric Growth
`std::vector` expands using geometric growth ($1.5\\times$ in MSVC, $2.0\\times$ in GCC/Clang) ensuring append operations are amortized $O(1)$.
"""
                    }
                }
            ]
        },
        {
            "module_number": 5,
            "module_name": "Modern C++ Concurrency & Lock-Free Programming",
            "topics": [
                {
                    "id": 2005,
                    "slug": "cpp-concurrency-atomics",
                    "name": "Threads, Futures, Mutexes & std::atomic Memory Fences",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🧬",
                    "subtopics": [
                        "std::jthread & std::async with std::future/promise",
                        "std::unique_lock, std::scoped_lock & Deadlock Avoidance",
                        "Lock-Free Atomics: std::atomic<T> & Compare-And-Swap (CAS)",
                        "C++ Memory Models: Sequentially Consistent vs Acquire-Release"
                    ],
                    "learning_objectives": [
                        "Write deadlock-free concurrent code with modern scoped locks",
                        "Build lock-free atomic counters and ring buffers"
                    ],
                    "lesson_content": {
                        "introduction": "Modern C++ provides thread primitives, async task management, and lock-free atomic operations defined against a formal hardware memory model.",
                        "explanation": """### 1. Lock-Free Atomic Operations
```cpp
#include <atomic>
#include <iostream>

std::atomic<int> counter{0};

void increment() {
    counter.fetch_add(1, std::memory_order_relaxed);
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 6,
            "module_name": "Templates, Metaprogramming & C++20 Concepts",
            "topics": [
                {
                    "id": 2006,
                    "slug": "cpp-templates-concepts",
                    "name": "Template Specialization, SFINAE & C++20 Concepts",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🧩",
                    "subtopics": [
                        "Function and Class Template Specialization",
                        "Compile-time Computation with `constexpr` and `consteval`",
                        "SFINAE (Substitution Failure Is Not An Error) with std::enable_if",
                        "C++20 Concepts & Constrained Template Constraints"
                    ],
                    "learning_objectives": [
                        "Constrain generic functions cleanly using C++20 `requires` clauses",
                        "Compute values at compile-time with zero runtime overhead"
                    ],
                    "lesson_content": {
                        "introduction": "Templates enable generic programming, compile-time metaprogramming, and zero-cost abstractions verified entirely during compilation.",
                        "explanation": """### 1. C++20 Concepts
```cpp
#include <concepts>
#include <iostream>

template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T multiply(T a, T b) {
    return a * b;
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 7,
            "module_name": "High Performance Systems & Zero-Cost Abstractions",
            "topics": [
                {
                    "id": 2007,
                    "slug": "cpp-high-performance",
                    "name": "Custom Memory Allocators, PMR & Zero-Copy Optimization",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🏎️",
                    "subtopics": [
                        "Polymorphic Memory Resources (std::pmr::monotonic_buffer_resource)",
                        "Custom Fixed-Size Block Allocators for Ultra-Low Latency",
                        "Branch Prediction Hints: `[[likely]]` and `[[unlikely]]`",
                        "String Views (std::string_view) & Span (std::span) Zero-Copy Slicing"
                    ],
                    "learning_objectives": [
                        "Use `std::pmr` to eliminate heap allocations inside real-time loops",
                        "Slice string buffers without memory allocation via `std::string_view`"
                    ],
                    "lesson_content": {
                        "introduction": "High-performance C++ applications optimize every clock cycle through memory pre-allocation, zero-copy views, and compiler branch hints.",
                        "explanation": """### 1. Zero-Copy String Views
```cpp
#include <iostream>
#include <string_view>

void parse_header(std::string_view sv) {
    // Zero allocations: views original buffer directly!
    auto token = sv.substr(0, 4);
    std::cout << "Token: " << token << std::endl;
}
```
"""
                    }
                }
            ]
        }
    ],

    "java": [
        {
            "module_number": 1,
            "module_name": "JVM Architecture & Memory Management",
            "topics": [
                {
                    "id": 3001,
                    "slug": "java-jvm-memory",
                    "name": "JVM Internals, Heap Generations & Garbage Collection",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "☕",
                    "subtopics": [
                        "JVM Architecture: ClassLoader, Execution Engine & JIT",
                        "Heap Generations: Young Gen (Eden, S0, S1) vs Old Gen",
                        "Garbage Collection Algorithms (G1GC, ZGC, Shenandoah)",
                        "Stack Frames, Metaspace & Escape Analysis Allocations"
                    ],
                    "learning_objectives": [
                        "Analyze JVM memory heap dumps using VisualVM and JConsole",
                        "Tune garbage collection parameters (-Xms, -Xmx, -XX:+UseG1GC)",
                        "Understand Escape Analysis and Scalar Replacement on the stack"
                    ],
                    "lesson_content": {
                        "introduction": "Enterprise Java applications power the world's financial backbones, cloud infrastructures, and high-throughput transaction engines. Java executes on the **Java Virtual Machine (JVM)**, a mature execution environment that translates bytecode into optimized native machine instructions via Tiered Compilation (C1/C2 JIT compilers).",
                        "explanation": """### 1. JVM Memory Model & Generational Garbage Collection

#### 1.1 The Anatomy of the JVM Heap
The JVM divides memory into specialized pools:
1. **Young Generation**:
   - **Eden Space**: Where new objects are initially allocated.
   - **Survivor Spaces (From / S0 and To / S1)**: Objects that survive Minor GC cycles are copied between survivor spaces, incrementing their age counter.
2. **Old (Tenured) Generation**:
   - Objects that survive past the tenure threshold (typically 15 GC cycles) are promoted to the Old Generation.
3. **Metaspace (Native Memory)**:
   - Replaced PermGen in Java 8. Stores class metadata, bytecode definitions, and the runtime constant pool in OS native memory.

#### 1.2 Tiered Compilation & JIT Optimization
1. **Interpreter**: Starts executing bytecode immediately without compile latency.
2. **C1 Compiler (Client)**: Rapidly produces baseline native machine code with basic profiling.
3. **C2 Compiler (Server)**: Analyzes runtime execution paths to perform aggressive optimizations:
   - **Method Inlining**: Removes call overhead for small methods.
   - **Loop Unrolling**: Eliminates branch prediction misses.
   - **Escape Analysis**: If an object does not escape a method, the JVM skips heap allocation entirely and allocates its fields directly onto CPU registers (**Scalar Replacement**)!

```java
public class JvmMemoryDemo {
    public static void main(String[] args) {
        Runtime runtime = Runtime.getRuntime();
        long maxMemory = runtime.maxMemory();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        
        System.out.printf("Max JVM Heap:   %d MB%n", maxMemory / (1024 * 1024));
        System.out.printf("Total Allocated:%d MB%n", totalMemory / (1024 * 1024));
        System.out.printf("Free Memory:    %d MB%n", freeMemory / (1024 * 1024));
    }
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 2,
            "module_name": "Core Java OOP & SOLID Architecture",
            "topics": [
                {
                    "id": 3002,
                    "slug": "java-oop-solid",
                    "name": "Polymorphism, Interfaces, Records & Sealed Classes",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "🏛️",
                    "subtopics": [
                        "SOLID Principles in Modern Enterprise Architecture",
                        "Interfaces with Default & Private Methods",
                        "Immutable Data Carriers: Java Records",
                        "Exhaustive Pattern Matching with Sealed Classes and Interfaces"
                    ],
                    "learning_objectives": [
                        "Write clean, decoupled code adhering to the Open/Closed Principle",
                        "Model domain entities cleanly with Records and Sealed hierarchies"
                    ],
                    "lesson_content": {
                        "introduction": "Object-oriented design in modern Java embraces immutability, records, and sealed types to create type-safe enterprise architectures.",
                        "explanation": """### 1. Modern Sealed Classes & Pattern Matching
```java
public sealed interface PaymentMethod permits CreditCard, PayPal, CryptoPayment {}

public record CreditCard(String cardNumber, String cvv) implements PaymentMethod {}
public record PayPal(String email) implements PaymentMethod {}
public record CryptoPayment(String walletAddress) implements PaymentMethod {}

public class PaymentProcessor {
    public static void process(PaymentMethod method) {
        switch (method) {
            case CreditCard cc -> System.out.println("Processing card: " + cc.cardNumber());
            case PayPal pp     -> System.out.println("Processing PayPal: " + pp.email());
            case CryptoPayment cp -> System.out.println("Processing crypto: " + cp.walletAddress());
        }
    }
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 3,
            "module_name": "Collections Framework & Stream API",
            "topics": [
                {
                    "id": 3003,
                    "slug": "java-collections-streams",
                    "name": "HashMap Internals, Concurrent Collections & Streams API",
                    "order": 1,
                    "difficulty": "intermediate",
                    "icon": "⚡",
                    "subtopics": [
                        "HashMap Bucket Array, Treeification to Red-Black Trees (Threshold 8)",
                        "ConcurrentHashMap Striped Segment Locking & CAS Operations",
                        "Functional Programming with Java Stream Pipelines",
                        "Parallel Streams & The Common ForkJoinPool"
                    ],
                    "learning_objectives": [
                        "Explain HashMap resize mechanics and collision treeification",
                        "Process million-element datasets declaratively with Stream API"
                    ],
                    "lesson_content": {
                        "introduction": "The Java Collections Framework and Streams API provide enterprise developers with battle-tested algorithmic data structures.",
                        "explanation": """### 1. HashMap Internals
When a bucket accumulates more than 8 entries, Java transforms the linked list into a Red-Black Tree (`TreeNode`), improving worst-case search complexity from $O(n)$ to $O(\\log n)$.
"""
                    }
                }
            ]
        },
        {
            "module_number": 4,
            "module_name": "Multithreading & Virtual Threads (Project Loom)",
            "topics": [
                {
                    "id": 3004,
                    "slug": "java-threads-virtual",
                    "name": "Platform Threads, ThreadPools & Virtual Threads (Java 21)",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🧬",
                    "subtopics": [
                        "Operating System OS Platform Threads vs JVM Virtual Threads",
                        "ExecutorService, Future, CompletableFuture & Reactive Chains",
                        "Thread Synchronization: synchronized vs ReentrantLock",
                        "Virtual Threads (Project Loom) for 1,000,000+ Concurrent Requests"
                    ],
                    "learning_objectives": [
                        "Spawn lightweight Virtual Threads with minimal memory overhead",
                        "Compose asynchronous non-blocking workflows using `CompletableFuture`"
                    ],
                    "lesson_content": {
                        "introduction": "Java 21 Virtual Threads revolutionized concurrent programming by decoupling high-level threads from heavy 1MB OS threads.",
                        "explanation": """### 1. Virtual Threads in Java 21
```java
import java.util.concurrent.Executors;

public class VirtualThreadDemo {
    public static void main(String[] args) {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < 100_000; i++) {
                final int taskId = i;
                executor.submit(() -> {
                    Thread.sleep(100);
                    return taskId;
                });
            }
        } // Auto-waits for all 100,000 tasks with negligible RAM!
    }
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 5,
            "module_name": "Java I/O, NIO.2 & Network Systems",
            "topics": [
                {
                    "id": 3005,
                    "slug": "java-nio-networking",
                    "name": "Non-blocking NIO Channels, ByteBuffers & Sockets",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🌐",
                    "subtopics": [
                        "Traditional Blocking I/O vs Java NIO Non-blocking Architecture",
                        "ByteBuffers: Capacity, Position, Limit & Flip Operations",
                        "Selector Multiplexing for Single-Threaded Network Event Loops",
                        "Memory-Mapped File Channels with FileChannel.map()"
                    ],
                    "learning_objectives": [
                        "Build asynchronous high-throughput network servers with Selectors",
                        "Manipulate off-heap ByteBuffers safely"
                    ],
                    "lesson_content": {
                        "introduction": "Java NIO (New I/O) provides channel-based, buffer-oriented, non-blocking I/O operations for enterprise network services.",
                        "explanation": """### 1. ByteBuffer Flip Pattern
```java
ByteBuffer buffer = ByteBuffer.allocateDirect(1024);
buffer.put("Hello Enterprise Java".getBytes());
buffer.flip(); // Prepare buffer for reading!
while (buffer.hasRemaining()) {
    System.out.print((char) buffer.get());
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 6,
            "module_name": "Spring Boot & Enterprise Microservices",
            "topics": [
                {
                    "id": 3006,
                    "slug": "java-spring-boot",
                    "name": "Dependency Injection, Spring MVC, REST & JPA Repositories",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "🍃",
                    "subtopics": [
                        "Inversion of Control (IoC) & Spring ApplicationContext Lifecycle",
                        "Building Resilient REST APIs with `@RestController` and DTOs",
                        "Spring Data JPA, Hibernate ORM & N+1 Query Problem Optimization",
                        "Declarative Transactions with `@Transactional` Propagation"
                    ],
                    "learning_objectives": [
                        "Architect enterprise microservice REST APIs with Spring Boot",
                        "Eliminate Hibernate N+1 query performance bottlenecks using JOIN FETCH"
                    ],
                    "lesson_content": {
                        "introduction": "Spring Boot is the industry standard framework for developing scalable cloud microservices, providing dependency injection, data persistence, and web APIs.",
                        "explanation": """### 1. Clean Spring REST Service
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService orderService;
    
    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody OrderRequest req) {
        return ResponseEntity.ok(orderService.placeOrder(req));
    }
}
```
"""
                    }
                }
            ]
        },
        {
            "module_number": 7,
            "module_name": "Enterprise Performance Tuning & Observability",
            "topics": [
                {
                    "id": 3007,
                    "slug": "java-performance-tuning",
                    "name": "JMH Benchmarking, Profiling, Thread Dumps & GC Tuning",
                    "order": 1,
                    "difficulty": "advanced",
                    "icon": "📈",
                    "subtopics": [
                        "Java Microbenchmark Harness (JMH) for Nanosecond Profiling",
                        "Diagnosing Deadlocks and High CPU via Thread Dumps (`jstack`)",
                        "Analyzing OutOfMemoryError and Memory Leaks via Heap Dumps (`jcmd`)",
                        "Production Tuning for Ultra-Low Latency Garbage Collectors (ZGC)"
                    ],
                    "learning_objectives": [
                        "Identify JVM memory leaks and deadlocks using production diagnostics",
                        "Configure ZGC for sub-millisecond GC pause times in cloud deployments"
                    ],
                    "lesson_content": {
                        "introduction": "Enterprise systems engineers use low-level JVM profiling tools to guarantee high availability and sub-millisecond SLAs.",
                        "explanation": """### 1. JVM Diagnostics Commands
```bash
# Capture thread dump
jstack <PID> > thread_dump.txt

# Capture heap dump on live JVM
jcmd <PID> GC.heap_dump /tmp/heap.hprof

# Enable modern ZGC with low pauses
java -XX:+UseZGC -XX:+ZGenerational -jar application.jar
```
"""
                    }
                }
            ]
        }
    ]
}
