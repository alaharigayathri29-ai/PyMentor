-- ==============================================================================
-- PyMentor Polyglot Platform — Initial Platform Seed Data for Supabase
-- Populates Admin & Demo Students, Core 4-Course Topics & User Profiles
-- ==============================================================================

-- 1. Seed Core Users (Passwords hashed with bcrypt: 'admin123' / 'password123')
INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
VALUES
    ('admin', 'admin@pymentor.dev', '$2b$12$4Lp1o0qG5wXW2Oa6bYcEee8K4T1z5Q3l3C1M1s9v.L9i0s9n1u9iK', 'Platform Administrator', 'admin', true),
    ('honey_qis', 'gayatri@qiscet.edu.in', '$2b$12$4Lp1o0qG5wXW2Oa6bYcEee8K4T1z5Q3l3C1M1s9v.L9i0s9n1u9iK', 'A. Sri Lakshmi Gayatri', 'student', true),
    ('priya_beginner', 'priya@qiscet.edu.in', '$2b$12$4Lp1o0qG5wXW2Oa6bYcEee8K4T1z5Q3l3C1M1s9v.L9i0s9n1u9iK', 'Priya Sharma', 'student', true),
    ('rahul_intermediate', 'rahul@qiscet.edu.in', '$2b$12$4Lp1o0qG5wXW2Oa6bYcEee8K4T1z5Q3l3C1M1s9v.L9i0s9n1u9iK', 'Rahul Verma', 'student', true),
    ('ananya_advanced', 'ananya@qiscet.edu.in', '$2b$12$4Lp1o0qG5wXW2Oa6bYcEee8K4T1z5Q3l3C1M1s9v.L9i0s9n1u9iK', 'Ananya Iyer', 'student', true)
ON CONFLICT (username) DO NOTHING;

-- 2. Seed User Profiles
INSERT INTO user_profiles (user_id, college_name, branch, academic_year, primary_track, skill_level, xp, streak_days)
SELECT id, 'QIS College of Engineering & Technology', 'Computer Science & Engineering', '2026-2027', 'python', 'intermediate', 0, 0
FROM users
WHERE role = 'student'
ON CONFLICT (user_id) DO NOTHING;

-- 3. Seed Python Curriculum Topics (Course: 'python')
INSERT INTO topics (course, module_number, module_name, slug, name, description, order_index, difficulty, icon, subtopics, learning_objectives)
VALUES
    ('python', 1, 'Python Fundamentals', 'variables', 'Variables & Data Types', 'CPython PyObject reference model, dynamic heap binding, and scalar types.', 1, 'beginner', '📦',
     ARRAY['CPython PyObject Structs', 'Reference Counting & Object Identity', 'Memory Allocation: Stack vs Heap'],
     ARRAY['Differentiate Python heap pointers from compiled stack variables', 'Inspect object addresses via id() and sys.getsizeof()']),

    ('python', 1, 'Python Fundamentals', 'operators', 'Operators & Expressions', 'Arithmetic, bitwise operators, and logical short-circuiting.', 2, 'beginner', '🧮',
     ARRAY['Bitwise Shifts & Masks', 'Logical Operator Short-Circuit Evaluation', 'Operator Precedence & Associativity'],
     ARRAY['Apply bitwise operations for high-efficiency flag masking', 'Leverage short-circuiting in conditional evaluations']),

    ('python', 2, 'Control Structures & Flow', 'conditions', 'Conditional Statements', 'Branching logic, boolean truthiness, and ternary operators.', 3, 'beginner', '🔀',
     ARRAY['Truthiness & Falsy Values', 'Multi-Way Branching (if/elif/else)', 'Pattern Matching (match/case)'],
     ARRAY['Write clean branch logic without redundant evaluations', 'Use structural pattern matching for data decomposition']),

    ('python', 2, 'Control Structures & Flow', 'loops', 'Loops & Iteration', 'For and while loops, iterator protocol, and enumerate/zip.', 4, 'beginner', '🔄',
     ARRAY['The __iter__ and __next__ Protocol', 'Efficient Indexing with enumerate()', 'Loop Else Clauses & Break Invariants'],
     ARRAY['Implement iteration without manual index counters', 'Prevent infinite loops and understand loop performance']),

    ('python', 3, 'Functions & Modularity', 'functions', 'Functions & Scope', 'First-class functions, LEGB scope resolution, and closures.', 5, 'beginner', '🧩',
     ARRAY['LEGB Scope (Local, Enclosing, Global, Built-in)', 'First-Class Functions & Closures', '*args and **kwargs Parameter Packing'],
     ARRAY['Design modular functions with pure return values', 'Prevent mutable default argument bugs in production code']),

    ('python', 4, 'Collections & Sequences', 'lists', 'Lists & Tuples', 'Dynamic arrays, amortized O(1) growth, and tuple immutability.', 6, 'beginner', '📝',
     ARRAY['Over-Allocation Growth Factor', 'Memory Overhead: List vs Tuple', 'Slicing & Memory Shallow Copies'],
     ARRAY['Optimize memory usage with immutable tuples', 'Use list slicing efficiently without unintended memory copies']),

    ('python', 4, 'Collections & Sequences', 'dictionaries', 'Dictionaries & Hash Maps', 'CPython compact hash table, hash collisions, and O(1) lookups.', 7, 'intermediate', '🗄️',
     ARRAY['Hash Tables & Perturbation Probing', 'Key Immutability & __hash__ Requirements', 'Dictionary Comprehensions & Merging'],
     ARRAY['Implement hashable custom keys safely', 'Analyze hash collisions and worst-case algorithmic complexity'])
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    module_number = EXCLUDED.module_number,
    module_name = EXCLUDED.module_name;

-- 4. Seed ANSI C Systems Topics (Course: 'c')
INSERT INTO topics (course, module_number, module_name, slug, name, description, order_index, difficulty, icon, subtopics, learning_objectives)
VALUES
    ('c', 1, 'C Fundamentals & Memory Architecture', 'c-fundamentals', 'Data Types, CPU Alignment & Byte Storage', 'Primitive scalar types, CPU word boundaries, and endianness.', 1, 'beginner', '⚙️',
     ARRAY['Scalar Types (char, int, long, double)', 'CPU Word Boundaries & Struct Padding', 'Endianness: Big vs Little Endian'],
     ARRAY['Examine raw memory bytes using pointer casts', 'Determine CPU endianness programmatically via unions']),

    ('c', 2, 'Pointers & Memory Addressing', 'c-pointers', 'Pointers, Arithmetic & Dereferencing', 'Direct memory addressing, indirection, pointer arithmetic, and double pointers.', 2, 'intermediate', '🎯',
     ARRAY['Pointer Indirection & Memory Addresses', 'Pointer Arithmetic & Scaling Factors', 'Double Pointers (char**) & Array of Pointers'],
     ARRAY['Manipulate memory safely without segmentation faults', 'Pass pointers to modify caller state and build linked structures']),

    ('c', 3, 'Dynamic Memory Management', 'c-dynamic-memory', 'Dynamic Memory Allocation (malloc, free)', 'Heap allocation, memory leaks, and buffer safety.', 3, 'intermediate', '📦',
     ARRAY['malloc, calloc, realloc & free APIs', 'Heap Fragmentation & Valgrind Detection', 'Dangling Pointers & Double-Free Mitigation'],
     ARRAY['Manage dynamic heap memory with zero memory leaks', 'Audit buffer safety against heap overflow vulnerabilities'])
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- 5. Seed Modern C++ Topics (Course: 'cpp')
INSERT INTO topics (course, module_number, module_name, slug, name, description, order_index, difficulty, icon, subtopics, learning_objectives)
VALUES
    ('cpp', 1, 'Modern C++ Systems & Resource Management', 'cpp-raii', 'RAII Architecture & Smart Pointers', 'Resource Acquisition Is Initialization, unique_ptr, and shared_ptr.', 1, 'intermediate', '⚡',
     ARRAY['The RAII Idiom', 'Exclusive Ownership: std::unique_ptr', 'Shared Ownership: std::shared_ptr & weak_ptr'],
     ARRAY['Guarantee exception-safe resource release', 'Prevent cyclic memory leaks using std::weak_ptr']),

    ('cpp', 2, 'Move Semantics & Performance', 'cpp-move-semantics', 'Rvalue References & Move Semantics', 'Zero-copy transfers, std::move, and the Rule of 5.', 2, 'advanced', '🚀',
     ARRAY['Lvalues vs Rvalues & std::move', 'Move Constructors & Move Assignment', 'Rule of 0 / 3 / 5'],
     ARRAY['Eliminate redundant heap allocations via move semantics', 'Design modern zero-overhead movable classes'])
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- 6. Seed Enterprise Java Topics (Course: 'java')
INSERT INTO topics (course, module_number, module_name, slug, name, description, order_index, difficulty, icon, subtopics, learning_objectives)
VALUES
    ('java', 1, 'JVM Architecture & Memory Management', 'java-jvm-memory', 'JVM Memory Model & Bytecode', 'ClassLoaders, Heap, Metaspace, and Garbage Collection tuning.', 1, 'intermediate', '☕',
     ARRAY['JVM Memory Zones (Heap, Metaspace, Stack)', 'Garbage Collectors (G1GC, ZGC)', 'Java Bytecode & JIT Compilation (C1/C2)'],
     ARRAY['Tune JVM heap parameters (-Xms, -Xmx) for low latency', 'Analyze memory leaks via heap dumps and JConsole']),

    ('java', 2, 'OOP Domain Modeling', 'java-oop-domain', 'Enterprise OOP & Interfaces', 'Clean architecture, abstract classes, interfaces, and records.', 2, 'intermediate', '🏛️',
     ARRAY['Polymorphism & Dynamic Dispatch', 'Default & Static Methods in Interfaces', 'Immutable Domain Models with Java Records'],
     ARRAY['Design decoupled domain models using modern Java interfaces', 'Apply SOLID principles to enterprise services'])
ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;
