# -*- coding: utf-8 -*-
"""
Module 7: Practical Python Projects & Architecture
5+ Pages In-Depth Systems Knowledge, AsyncIO Event Loop Mechanics,
High-Throughput Microservice Architecture, Connection Pooling, and 10 Viva Q&As.
"""

MODULE_7 = {
    "module_number": 7,
    "module_name": "Practical Python",
    "description": "Master asynchronous I/O (asyncio), production microservices, database connection pooling, and scalable system design.",
    "icon": "🚀",
    "topics": [
        {
            "slug": "practical-python",
            "name": "Production Microservices & Async Systems Architecture",
            "order": 1,
            "difficulty": "advanced",
            "icon": "🌐",
            "subtopics": [
                "The CPython AsyncIO Event Loop: Coroutines, Tasks & Non-Blocking Epoll/Kqueue",
                "Asynchronous Microservices with FastAPI, Pydantic & Uvicorn ASGI Server",
                "Database Connection Pooling & ACID vs BASE Consistency Trade-offs",
                "Distributed Caching with Redis & In-Memory Rate Limiting",
                "Polyglot Microservices: Python AsyncIO vs Go Goroutines vs Node.js Event Loop vs Java Virtual Threads (Project Loom)"
            ],
            "learning_objectives": [
                "Understand the internal mechanics of the asyncio event loop and how non-blocking OS selectors (epoll/kqueue) manage 10,000+ concurrent connections",
                "Design enterprise asynchronous microservices with FastAPI and validated Pydantic schemas",
                "Implement database connection pooling to prevent connection exhaustion under high traffic spikes",
                "Apply distributed caching patterns and token bucket rate limiters for API defense",
                "Compare Python's single-threaded event loop with Go Goroutines and Java 21 Virtual Threads"
            ],
            "lesson_content": {
                "introduction": "Building real-world software requires synthesizing language syntax with distributed systems engineering. Modern production backends demand asynchronous architectures capable of serving tens of thousands of concurrent clients while maintaining sub-millisecond latencies.\n\nIn this capstone module, we dissect the internal mechanics of Python's **`asyncio` Event Loop**, examine how non-blocking OS I/O multiplexers (`epoll` on Linux, `kqueue` on macOS, IOCP on Windows) operate, build production-grade microservices with connection pools, and benchmark Python's asynchronous model against Go, Node.js, and Java Virtual Threads.",
                "explanation": """### 1. Conceptual Architecture: The `asyncio` Event Loop Under the Hood

#### 1.1 The Classical Multi-Threaded vs. Asynchronous Concurrency Models
- **Multi-Threaded Concurrency (Preemptive)**: Each incoming HTTP connection spawns or borrows an OS native thread. Every thread requires its own stack (typically 2MB to 8MB). Serving 10,000 concurrent connections requires **40GB to 80GB of RAM** just for thread stacks! Furthermore, the OS scheduler incurs severe CPU overhead performing **Context Switches** (saving and restoring CPU registers `RAX`, `RBX`, `RIP`).
- **Asynchronous Concurrency (Cooperative)**: A single OS thread executes an **Event Loop** using OS I/O multiplexing (`epoll` / `kqueue` / IOCP). Coroutines suspend cooperatively via `await` when waiting for network I/O, allowing the single thread to handle **100,000+ concurrent sockets with only a few megabytes of RAM**!

```
                  THE ASYNCIO EVENT LOOP ARCHITECTURE
                  ┌───────────────────────────────────┐
                  │    AsyncIO Event Loop (Thread 1)  │
                  └─────────────────┬─────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
     Task 1 (HTTP Req)        Task 2 (DB Query)        Task 3 (Redis)
     Executes until await     Suspended at await       Executes until await
     Yields to Event Loop     Waiting for socket...    Yields to Event Loop
           │                        │                        │
           └────────────────────────┴────────────────────────┘
                                    │
                                    ▼
                     OS Kernel Multiplexer: epoll() / IOCP
                     Notifies loop when network bytes arrive!
```

#### 1.2 Coroutine Mechanics: `async def` and `await`
Under the hood, an `async def` function compiles into a generator-like `coroutine` object:
1. Calling `my_coroutine()` does **NOT** execute the function body; it returns a coroutine object.
2. When passed to the event loop via `asyncio.create_task()`, it is wrapped in an `asyncio.Task` object.
3. The event loop calls `.send(None)` on the coroutine, running it until it encounters `await awaitable`.
4. The `await` keyword yields execution back to the event loop, releasing the single CPU thread to execute other pending tasks while the kernel waits for network bytes to arrive!

---

### 2. Polyglot Comparative Concurrency & Microservice Matrix

| Dimension | Python 3.12+ AsyncIO | Go (Golang) | Node.js (V8) | Java 21 (Project Loom) |
| :--- | :--- | :--- | :--- | :--- |
| **Concurrency Paradigm** | Single-threaded Event Loop + Coroutines | Communicating Sequential Processes (CSP) | Single-threaded Event Loop (libuv) | Virtual Threads (Fibers) |
| **Execution Primitive** | Coroutines (`async` / `await`) | Goroutines (`go func()`) | Promises (`async` / `await`) | Virtual Threads (`Thread.ofVirtual()`) |
| **Scheduling** | Cooperative (Must yield via `await`) | Preemptive runtime scheduler | Cooperative (Must yield via `await`) | Preemptive on ForkJoinPool carrier |
| **Memory per Unit** | $\sim 2.5$ KB per Task | $\sim 2$ KB initial stack | $\sim 1$ KB per Promise | $\sim 1$ KB per Virtual Thread |
| **Multi-Core Scaling** | Requires multiple worker processes (Uvicorn) | Multi-core native runtime | Cluster module / Worker threads | Multi-core native runtime |

---

### 3. Enterprise Production Patterns (Fullstack & Data Engineering)

#### 3.1 Production Database Connection Pooling
In cloud environments, opening a new TCP connection to a PostgreSQL database takes 30-50ms (TCP handshake, SSL negotiation, user authentication). Under a traffic spike of 1,000 requests/sec, opening connections on demand crashes the database with connection exhaustion.
**The Solution: Connection Pooling**:
```python
# Production Connection Pool Architecture:
class DatabasePool:
    def __init__(self, min_size: int = 5, max_size: int = 20):
        self._pool = asyncio.Queue(maxsize=max_size)
        self.min_size = min_size

    async def initialize(self):
        for _ in range(self.min_size):
            conn = await create_raw_db_socket()
            await self._pool.put(conn)

    @asynccontextmanager
    async def acquire(self):
        conn = await self._pool.get()
        try:
            yield conn
        finally:
            # Reclaim connection back to pool in O(1) time:
            await self._pool.put(conn)
```

---

### 4. Senior Engineering Interview & Viva Questions (10 Detailed Q&As)

#### Q1: What is the Event Loop in Python `asyncio`, and how does it achieve high concurrency on a single thread?
- **Answer**: The event loop is an infinite loop that monitors OS file descriptors and timers using kernel multiplexers (`epoll` on Linux, `kqueue` on BSD/macOS, IOCP on Windows). It dispatches tasks when network sockets become readable or writable. Because tasks yield control cooperatively via `await` during I/O wait periods, the single thread never blocks, allowing a single CPU core to service tens of thousands of concurrent network connections with minimal memory overhead.

#### Q2: What happens if you execute a CPU-bound operation (like calculating prime numbers) inside an `async def` function?
- **Answer**: It blocks the entire event loop. Because Python's `asyncio` is single-threaded, a CPU-intensive operation occupies the CPU without yielding, preventing the event loop from servicing any other concurrent tasks or responding to new network connections. To run CPU-bound work in an async app, you must offload it to a separate process pool using `loop.run_in_executor(ProcessPoolExecutor, func)`.

#### Q3: What is the difference between `asyncio.gather()` and `asyncio.TaskGroup`?
- **Answer**: `asyncio.gather(*aws)` runs multiple awaitables concurrently. However, if one fails with an exception, other tasks continue running in the background unmanaged (orphaned tasks). `asyncio.TaskGroup` (introduced in Python 3.11 for Structured Concurrency) acts as an async context manager: if any child task fails, the `TaskGroup` immediately cancels all remaining sibling tasks and re-raises an `ExceptionGroup`, guaranteeing clean error propagation and preventing leaked background tasks.

#### Q4: Why is Uvicorn typically run behind a reverse proxy like Nginx or AWS ALB with multiple worker processes?
- **Answer**: Because a single Uvicorn ASGI instance runs on a single CPU core due to the Python Global Interpreter Lock (GIL). Running Uvicorn behind Nginx or using multiple worker processes (`uvicorn --workers 4`) allows the application to utilize all available CPU cores on the host, with Nginx handling SSL termination, static file serving, and load balancing across workers.

#### Q5: What is the C10K Problem, and how did asynchronous I/O solve it?
- **Answer**: The C10K problem (coined by Dan Kegel in 1999) refers to the inability of traditional web servers to handle 10,000 concurrent client connections due to the memory overhead ($O(N)$ thread stacks) and CPU context-switching costs of the one-thread-per-connection model. Asynchronous non-blocking I/O multiplexers (`epoll`) solved it by decoupling connection count from thread count, managing thousands of sockets on a single thread.

#### Q6: How does Pydantic v2 achieve high serialization performance in FastAPI?
- **Answer**: In Pydantic v2, the entire validation, parsing, and JSON serialization core was rewritten from pure Python into **Rust** (`pydantic-core`). When validating incoming HTTP payloads, Python passes the raw C buffer directly to compiled Rust machine code, executing validation 5 to 20 times faster than pure Python.

#### Q7: What is the difference between ACID and BASE database consistency models in distributed architectures?
- **Answer**:
  - **ACID** (Atomicity, Consistency, Isolation, Durability): Strict guarantees used in relational databases (PostgreSQL, MySQL). Transactions are immediately consistent, prioritizing data correctness over availability.
  - **BASE** (Basically Available, Soft state, Eventual consistency): Relaxed guarantees used in NoSQL distributed databases (Cassandra, DynamoDB). Prioritizes high availability and partition tolerance, with data replica consistency achieved eventually.

#### Q8: How does the Token Bucket algorithm work for API rate limiting?
- **Answer**: A token bucket holds a maximum capacity of $B$ tokens and refills with tokens at a constant rate $R$ tokens per second. When an incoming API request arrives, it attempts to draw 1 token from the bucket:
  - If a token is available, it is consumed, and the request is permitted.
  - If the bucket is empty, the request is rejected immediately with HTTP 429 Too Many Requests.
  This permits controlled traffic bursts up to capacity $B$ while enforcing an average rate limit $R$.

#### Q9: How do Go Goroutines compare with Python AsyncIO Coroutines?
- **Answer**: Python coroutines require explicit cooperative yielding via `await` on a single-threaded event loop. If a coroutine fails to await, it freezes the entire process. In contrast, Go Goroutines are managed by a **preemptive multi-threaded runtime scheduler**: if a Goroutine executes a long-running CPU loop, the Go runtime automatically preempts it at function call preambles and schedules it across a pool of OS threads, providing seamless multi-core scaling without async keywords.

#### Q10: What are Java 21 Virtual Threads (Project Loom) and how do they eliminate async/await complexity?
- **Answer**: Java 21 Virtual Threads are lightweight user-mode threads managed by the JVM rather than the OS kernel. When a virtual thread executes blocking I/O (like a database query), the JVM automatically unmounts it from the underlying carrier OS thread and mounts another virtual thread. This allows developers to write simple, synchronous, sequential code (`val res = fetch()`) without any `async`/`await` colored-function syntax, while achieving the exact same high-concurrency scaling as Python or Node.js."""
            },
            "code_examples": [
                {
                    "title": "FastAPI Async Microservice Endpoint with Pydantic Validation",
                    "code": "from pydantic import BaseModel, Field\nimport asyncio\n\nclass StudentPayload(BaseModel):\n    name: str = Field(..., min_length=2, max_length=50)\n    cohort_id: int = Field(..., gt=0)\n    gpa: float = Field(..., ge=0.0, le=4.0)\n\nasync def simulate_db_write(data: dict):\n    await asyncio.sleep(0.02)  # Non-blocking async sleep simulating I/O\n    return {'status': 'PERSISTED', 'id': 'STU-991'}\n\nasync def register_student_handler(raw_data):\n    # 1. Pydantic validation\n    validated = StudentPayload(**raw_data)\n    # 2. Async non-blocking database write\n    res = await simulate_db_write(validated.model_dump())\n    return {'success': True, 'record': res, 'student': validated.name}\n\n# Simulating request execution\nimport asyncio\noutput = asyncio.run(register_student_handler({'name': 'Gayatri', 'cohort_id': 10, 'gpa': 3.92}))\nprint('Endpoint Execution Output:', output)",
                    "explanation": "Demonstrates an asynchronous microservice handler with Pydantic validation and non-blocking I/O.",
                    "expected_output": "Endpoint Execution Output: {'success': True, 'record': {'status': 'PERSISTED', 'id': 'STU-991'}, 'student': 'Gayatri'}"
                }
            ],
            "practice_questions": [
                {
                    "id": 1,
                    "question": "What is the primary mechanism through which asyncio achieves high concurrency on a single thread?",
                    "options": [
                        "Spawning 10,000 OS threads in parallel",
                        "Cooperative multitasking on an Event Loop using non-blocking OS I/O multiplexers (epoll/kqueue)",
                        "Executing bytecode on the GPU",
                        "Disabling the Global Interpreter Lock (GIL)"
                    ],
                    "correct_answer": 1,
                    "explanation": "AsyncIO uses a single-threaded Event Loop that delegates socket monitoring to OS kernel multiplexers, switching tasks cooperatively when I/O operations are awaited."
                }
            ],
            "practical_challenge": {
                "prompt": "Write an async function fetch_all_parallel(tasks) that executes a list of coroutines concurrently using asyncio.gather and returns their results.",
                "starter_code": "import asyncio\nasync def fetch_all_parallel(tasks):\n    # Return results of tasks gathered concurrently\n    pass",
                "test_call": "True",
                "expected": "True"
            }
        }
    ]
}

