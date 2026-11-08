"""
AI Service — clean provider abstraction.

Switch between providers via the AI_PROVIDER environment variable:
  AI_PROVIDER=mock    → MockMentorProvider (always available, no API key needed)
  AI_PROVIDER=openai  → OpenAIProvider (requires OPENAI_API_KEY)

Adding a new provider:
  1. Subclass AIProvider
  2. Implement async chat(messages, student_context) -> str
  3. Add a branch in get_ai_provider()
"""
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.config import settings


class AIProvider(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict], student_context: Dict) -> str:
        pass

    @staticmethod
    def detect_script_language(text: str) -> Optional[str]:
        if not text:
            return None
        import re
        # Telugu script (\u0C00-\u0C7F)
        if re.search(r"[\u0C00-\u0C7F]", text):
            return "te"
        # Devanagari / Hindi script (\u0900-\u097F)
        if re.search(r"[\u0900-\u097F]", text):
            return "hi"
        # Tamil script (\u0B80-\u0BFF)
        if re.search(r"[\u0B80-\u0BFF]", text):
            return "ta"
        # Kannada script (\u0C80-\u0CFF)
        if re.search(r"[\u0C80-\u0CFF]", text):
            return "kn"
        # Bengali script (\u0980-\u09FF)
        if re.search(r"[\u0980-\u09FF]", text):
            return "bn"
        # Romanized Telugu / Telugish keywords
        if re.search(r"\b(enti|cheppandi|cheppu|ela|gurinchi|kavali|ardham|chudandi|yemi|telugu)\b", text, re.IGNORECASE):
            return "te"
        # Romanized Hindi / Hinglish keywords
        if re.search(r"\b(kya hai|batao|kaise|karo|samjhao|mujhe|chahiye|hindi)\b", text, re.IGNORECASE):
            return "hi"
        # Spanish indicators
        if re.search(r"[áéíóúñ¿¡]|\b(hola|por favor|explicar|como|que es|espanol)\b", text, re.IGNORECASE):
            return "es"
        # French indicators
        if re.search(r"[àâçèéêëîïôùûü]|\b(bonjour|merci|comment|francais)\b", text, re.IGNORECASE):
            return "fr"
        # German indicators
        if re.search(r"[äöüß]|\b(hallo|bitte|deutsch)\b", text, re.IGNORECASE):
            return "de"
        return None

    def build_system_prompt(self, context: Dict, last_user_message: str = "") -> str:
        level = context.get("skill_level", "beginner")
        topic = context.get("current_topic", "Python basics")
        weak = context.get("weak_topics", [])
        weak_str = ", ".join(weak) if weak else "None identified yet"

        # Determine language — auto-detect from user's message if not specified or defaulting to en
        lang_code = context.get("language")
        detected = self.detect_script_language(last_user_message)
        if detected:
            lang_code = detected
            context["language"] = detected
        elif not lang_code:
            lang_code = "en"

        lang_names = {
            "en": "English",
            "hi": "Hindi (हिंदी)",
            "te": "Telugu (తెలుగు)",
            "ta": "Tamil (தமிழ்)",
            "kn": "Kannada (ಕನ್ನಡ)",
            "bn": "Bengali (বাংলা)",
            "es": "Spanish (Español)",
            "fr": "French (Français)",
            "de": "German (Deutsch)",
        }
        lang_name = lang_names.get(lang_code, "English")

        if lang_code and lang_code != "en":
            lang_instruction = f"""
================================================================================
CRITICAL MULTI-LANGUAGE TEACHING & VOICE POLICY (ZERO TRANSLATION MANDATE):
================================================================================
The student is interacting in: {lang_name} ({lang_code}).

1. STRICTLY NO TRANSLATION TO ENGLISH:
   - You MUST NEVER translate the student's question into English.
   - You MUST NEVER answer with an English translation of what they asked.
   - You MUST NEVER say "In English this means...", "Translation: ...", or switch to English.
   - DO NOT provide dual English/native language lines — explain 100% in {lang_name}.

2. CREATE ORIGINAL EXPLANATION DIRECTLY IN {lang_name}:
   - Answer directly and completely in {lang_name} using native script and natural, respectful phrasing (e.g. in Telugu use clear words like "నమస్కారం", "తెలుసుకుందాం", "ఉదాహరణ").
   - Create your OWN original, high-quality pedagogical explanation with real-world analogies tailored for {lang_name} learners.
   - Act as a patient, encouraging native-speaking teacher having a direct conversation with the student.

3. PYTHON CODE SAMPLES:
   - Python keywords and syntax remain valid runnable Python (e.g. `fruits = ["యాపిల్", "అరటిపండు"]`).
   - Every comment inside code (`# ...`) and every paragraph before and after the code MUST be written entirely in {lang_name}.

4. NATURAL CONVERSATIONAL SPEECH COMPATIBILITY:
   - When the student clicks "Listen" or uses the Voice Assistant, your answer should sound like a human tutor speaking naturally aloud to them.
   - Avoid excessive Markdown symbols, robotic formatting, or raw bullet lists so the voice assistant sounds fluid, natural, and engaging.
================================================================================
"""
        else:
            lang_instruction = """
Language Instruction:
- The student requested explanations in English.
- Provide clear, engaging conceptual explanations directly in English with runnable Python code examples.
- When spoken aloud by the voice assistant, ensure sentences flow smoothly and conversationally.
"""

        return f"""You are PyMentor, an expert Python programming mentor and voice-enabled learning assistant. Your goal is to TEACH, not just answer.

Student Profile:
- Skill Level: {level.capitalize()}
- Current Topic: {topic}
- Areas Needing Work: {weak_str}
- Preferred Language: {lang_name}

Teaching Philosophy:
1. Guide students toward answers rather than giving them directly
2. Use language and examples appropriate for a {level} learner
3. Provide concise, runnable Python code examples in markdown code blocks
4. Ask follow-up questions to check understanding
5. Break complex concepts into digestible steps
6. Celebrate effort and correct progress
7. For "explain differently" requests, use a completely different analogy or approach
8. For hints, give a nudge — not the full solution
9. For practice problems, create engaging real-world tasks at the right difficulty
{lang_instruction}
Always wrap Python code in ```python ... ``` blocks."""


# ── Google Gemini Provider ───────────────────────────────────────────────────

class GeminiProvider(AIProvider):
    def __init__(self):
        try:
            import google.generativeai as genai
            self.genai = genai
            self.model_name = settings.GEMINI_MODEL or "gemini-3.5-flash"
            self.genai.configure(api_key=settings.GEMINI_API_KEY)
        except ImportError:
            raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")

    async def chat(self, messages: List[Dict], student_context: Dict) -> str:
        import asyncio
        last_user_prompt = (messages[-1].get("content", "") if messages else "Hello").strip() or "Hello"
        system_prompt = self.build_system_prompt(student_context, last_user_prompt)

        model = self.genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt,
        )

        # Build normalized, strictly alternating content list
        raw_turns = []
        for msg in messages[:-1]:
            role = "user" if msg.get("role") == "user" else "model"
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            if raw_turns and raw_turns[-1]["role"] == role:
                raw_turns[-1]["parts"][0] += f"\n\n{content}"
            else:
                raw_turns.append({"role": role, "parts": [content]})

        # Ensure first turn is user if history exists
        while raw_turns and raw_turns[0]["role"] != "user":
            raw_turns.pop(0)

        # Ensure history ends with model so the next message is user
        while raw_turns and raw_turns[-1]["role"] != "model":
            raw_turns.pop()

        last_user_prompt = (messages[-1].get("content", "") if messages else "Hello").strip() or "Hello"
        contents = list(raw_turns)
        contents.append({"role": "user", "parts": [last_user_prompt]})

        try:
            # Run generate_content in thread to prevent event-loop blocking on Windows
            def _call_gemini():
                res = model.generate_content(contents)
                return res.text if res and res.text else None

            result_text = await asyncio.wait_for(asyncio.to_thread(_call_gemini), timeout=14.0)
            if result_text and result_text.strip():
                return result_text.strip()
            raise ValueError("Empty response received from Gemini model")
        except Exception as err:
            print(f"[Gemini Error]: {err}. Serving instant pedagogical fallback.")
            mock = MockMentorProvider()
            return await mock.chat(messages, student_context)


# ── OpenAI Provider ──────────────────────────────────────────────────────────

class OpenAIProvider(AIProvider):
    def __init__(self):
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

    async def chat(self, messages: List[Dict], student_context: Dict) -> str:
        last_user_prompt = (messages[-1].get("content", "") if messages else "Hello").strip() or "Hello"
        system_prompt = self.build_system_prompt(student_context, last_user_prompt)
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            max_tokens=1200,
            temperature=0.7,
        )
        return response.choices[0].message.content


# ── Mock Mentor Provider ─────────────────────────────────────────────────────

class MockMentorProvider(AIProvider):
    """
    Fully functional mock mentor for MVP demo / development.
    Provides educationally meaningful, contextualized responses without an API key.
    """

    # ── Rich topic-based knowledge base ─────────────────────────────────────

    TOPIC_CONTENT: Dict[str, Dict[str, str]] = {
        "variables": {
            "explain": """Great question! Let me explain **variables** in Python. 📦

Think of a variable as a **labeled container** — a named box where you store information:

```python
# Creating variables
name = "Alice"        # stores text (string)
age = 25              # stores a whole number (integer)
height = 5.7          # stores a decimal number (float)
is_student = True     # stores True or False (boolean)

# Using variables
print(f"Hello, {name}! You are {age} years old.")
# Output: Hello, Alice! You are 25 years old.
```

**Key rules for variable names:**
- Must start with a letter or underscore (`_`)
- Can contain letters, numbers, underscores
- **Case-sensitive**: `name` and `Name` are different
- Use `snake_case` convention: `student_age` not `studentAge`

**Quick exercise:** Create variables to describe yourself (name, age, favourite language) and print them!

What would you like to store in a variable? 🤔""",

            "hint": """💡 **Hint on Variables:**

In Python, `=` means **assignment** (not equality).

```python
x = 10   # "put 10 into the box labelled x"
```

- Variable names can't start with a number or contain spaces
- Use descriptive names: `student_score` is better than `s`
- To see what's in a variable: `print(variable_name)` or `type(variable_name)`

Try writing the first line of code — even just `x = 5` — and build from there! 🎯""",

            "practice": """Here's a practice problem on Variables! 🚀

**Problem: Student Profile**

Create variables to store information about a student, then print a formatted summary:
- First name (string)
- Last name (string)
- Age (integer)
- GPA (float, e.g. 3.85)
- Is enrolled? (boolean)

**Expected output format:**
```
Name: Alice Smith
Age: 20
GPA: 3.85
Enrolled: True
```

**Starter code:**
```python
first_name = "Alice"
last_name = ???
# ... complete the rest

print(f"Name: {first_name} {last_name}")
# ... print the rest
```

Try it and share your solution! 💪""",

            "differently": """Let me try a different analogy — **variables as a movie production board** 🎬

On a film set, the director keeps a board with sticky notes:
```
📌 "HERO_NAME"   → "Spider-Man"
📌 "BUDGET"      → 200000000
📌 "IS_FILMING"  → True
```

In Python, each sticky note IS a variable:
```python
hero_name = "Spider-Man"
budget = 200_000_000       # underscores for readability!
is_filming = True
```

You can update a sticky note any time — the old value disappears:
```python
hero_name = "Batman"   # Spider-Man is gone; Batman is now in the box
print(hero_name)       # Batman
```

The **label** = variable name. The **note content** = variable value. The `=` = the act of sticking the note.

Does this analogy help? 🎬"""
        },

        "data types": {
            "explain": """Python's **data types** are the building blocks of all programs! 🏗️

```python
# 1. str  — text (always in quotes)
course = "Python Programming"
char   = 'A'

# 2. int  — whole numbers
students = 42
year     = 2024
negative = -7

# 3. float — decimal numbers
pi    = 3.14159
grade = 98.5

# 4. bool — True or False (capital T/F!)
is_complete = True
has_error   = False

# 5. NoneType — represents "no value"
result = None
```

**Check the type of anything with `type()`:**
```python
print(type("hello"))   # <class 'str'>
print(type(42))        # <class 'int'>
print(type(3.14))      # <class 'float'>
print(type(True))      # <class 'bool'>
```

**Convert between types:**
```python
age_text   = "25"
age_num    = int(age_text)     # "25"  → 25
price      = float("9.99")    # "9.99"→ 9.99
as_text    = str(42)          # 42    → "42"
as_bool    = bool(0)          # 0     → False
```

**Question to check your understanding:** What type would you use to store a phone number like `+91-9876543210`? (Think carefully — is it really a number?) 🤔""",

            "hint": "💡 Python has 4 core types: `str` (text), `int` (whole numbers), `float` (decimals), `bool` (True/False). Use `type()` to inspect any value. Use `int()`, `float()`, `str()` to convert between them.",

            "practice": """**Practice: Data Type Detective** 🔍

```python
# Predict the type before running:
v1 = 42
v2 = 3.14
v3 = "hello"
v4 = True
v5 = "123"
v6 = None

# Task 1: Print each variable and its type
for val in [v1, v2, v3, v4, v5, v6]:
    print(f"Value: {val!r:15} | Type: {type(val).__name__}")

# Task 2: Convert v5 to an integer, then multiply by 2. Print the result.

# Task 3 (Bonus): What happens when you run int("hello")? Why?
```

Run it and explore! 🚀""",

            "differently": """**Data types as file cabinet drawers** 🗂️

Imagine a filing cabinet where each drawer only accepts a specific kind of document:

| Drawer Label | What goes in | Python type |
|---|---|---|
| 📝 Text | "Hello", "Python" | `str` |
| 🔢 Whole Numbers | 1, 42, -7, 0 | `int` |
| 🔣 Decimals | 3.14, 0.5, -2.7 | `float` |
| ✅ Yes/No | True, False | `bool` |
| ∅ Empty | Nothing | `None` |

Python automatically puts values in the right drawer based on how you write them:
- Quotes → `str` drawer
- Plain numbers → `int` drawer
- Decimal point → `float` drawer
- `True`/`False` → `bool` drawer

Does this cabinet analogy make it clearer? 🗂️"""
        },

        "conditions": {
            "explain": """**Conditional statements** let your program make decisions! 🛤️

```python
temperature = 35

if temperature > 30:
    print("🌞 It's hot!")
elif temperature > 20:
    print("😊 It's warm!")
elif temperature > 10:
    print("🌤️ It's cool!")
else:
    print("🥶 It's cold!")
```

**Comparison operators:**
```python
x = 10
x > 5    # True   (greater than)
x < 5    # False  (less than)
x >= 10  # True   (greater than or equal)
x <= 10  # True   (less than or equal)
x == 10  # True   (equal — double equals!)
x != 5   # True   (not equal)
```

**Logical operators:**
```python
age = 20
has_id = True

if age >= 18 and has_id:       # BOTH must be True
    print("Access granted ✅")

if age < 13 or age > 65:       # EITHER can be True
    print("Discount applies 🏷️")

if not has_id:                  # Flips True/False
    print("Please show ID ❌")
```

**Reminder:** Python evaluates conditions **top to bottom** and stops at the first `True`. That's why order matters!

What would print if `temperature = 25`? Try reasoning through it! 🤔""",

            "hint": "💡 Remember the structure: `if condition:` → `elif condition:` → `else:`. Each condition is checked in order; only the first `True` block runs. Use `==` (double equals) to compare, not `=` (assignment).",

            "practice": """**Practice: Grade Calculator** 📝

Write a function `get_grade(score)` that returns the letter grade:
- 90–100 → `'A'`
- 80–89  → `'B'`
- 70–79  → `'C'`
- 60–69  → `'D'`
- Below 60 → `'F'`

Also print whether the student passed (A, B, or C = pass).

```python
def get_grade(score):
    # Your if/elif/else chain here
    pass

# Test with these values:
for score in [95, 82, 71, 65, 45, 100]:
    grade = get_grade(score)
    passed = grade in ['A', 'B', 'C']
    print(f"{score} → {grade} ({'Pass' if passed else 'Fail'})")
```""",

            "differently": """**Conditionals as a decision flowchart** 📊

```
START
  │
  ▼
Is temperature > 30?
  ├─ YES → print "🌞 Hot"  → END
  └─ NO  ↓
         Is temperature > 20?
           ├─ YES → print "😊 Warm" → END
           └─ NO  ↓
                  Is temperature > 10?
                    ├─ YES → print "🌤️ Cool" → END
                    └─ NO  → print "🥶 Cold" → END
```

Each diamond is an `if`/`elif`. Each left branch is the `True` path. The final right branch is `else`.

Python walks DOWN the flowchart, takes the first `True` branch, and then STOPS — it never checks the rest.

Does the flowchart view help you see the flow? 📊"""
        },

        "loops": {
            "explain": """**Loops** let you repeat code without copy-pasting — essential for any real program! 🔄

### `for` loops — iterate over a sequence:
```python
# Over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}")

# Over a range of numbers
for i in range(5):            # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):         # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):     # 0, 2, 4, 6, 8 (step 2)
    print(i)
```

### `while` loops — repeat while condition is True:
```python
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1   # ⚠️ Always update the condition or you'll infinite loop!
```

### Loop control:
```python
for i in range(10):
    if i == 3:
        continue   # Skip this iteration, go to next
    if i == 7:
        break      # Exit the loop entirely
    print(i)
# Prints: 0 1 2 4 5 6
```

### Looping over strings:
```python
for char in "Python":
    print(char)   # P y t h o n (one per line)
```

**Use case:** When would you use a `while` loop instead of a `for` loop? (Think: when you don't know in advance how many times to repeat.) 🤔""",

            "hint": "💡 `for` loops are great when you know how many iterations (use `range()` or loop over a list). `while` loops work when you repeat until something changes. **Don't forget** to update the `while` condition variable, or you'll get an infinite loop!",

            "practice": """**Practice: Loop Challenges** 🏃

**Challenge 1:** Print the multiplication table for 7 (7×1 through 7×10)

**Challenge 2:** Find and print the sum of all even numbers from 1 to 100

**Challenge 3:** Print this triangle pattern using nested loops:
```
*
**
***
****
*****
```

**Challenge 4 (Bonus):** Use a `while` loop to find the first number greater than 1000 that is divisible by both 7 and 11.

Start with Challenge 1 — what approach will you use? 💪""",

            "differently": """**Loops as assembly line robots** 🏭

Imagine a factory assembly line. A robot performs the SAME action on each item as it passes by:

```
📦 📦 📦 📦 📦  ← items (list or range)
 ↑  ↑  ↑  ↑  ↑
🤖 🤖 🤖 🤖 🤖  ← robot does the loop body each time
```

**`for` loop:** The conveyor belt has a fixed number of items.
```python
for item in [📦, 📦, 📦]:
    robot.process(item)
```

**`while` loop:** The belt keeps running until a sensor says "stop":
```python
while sensor.items_remaining > 0:
    robot.process(belt.next())
```

**`break`:** Emergency stop button — halts the whole belt immediately.
**`continue`:** "Skip this item, move to next" — defective part bypass.

Does the factory analogy make loops clearer? 🏭"""
        },

        "functions": {
            "explain": """**Functions** are reusable blocks of code — the backbone of clean programming! 🧩

```python
# Define a function
def greet(name):
    \"\"\"Say hello to someone.\"\"\"
    message = f"Hello, {name}! 👋"
    return message

# Call the function
result = greet("Alice")
print(result)   # Hello, Alice! 👋
print(greet("Bob"))   # Hello, Bob! 👋
```

**Parameters and return values:**
```python
def calculate_bmi(weight_kg, height_m):
    \"\"\"Calculate Body Mass Index.\"\"\"
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

bmi = calculate_bmi(70, 1.75)
print(f"BMI: {bmi}")   # BMI: 22.86
```

**Default parameters:**
```python
def power(base, exponent=2):
    return base ** exponent

print(power(5))      # 25  (exponent defaults to 2)
print(power(3, 3))   # 27  (exponent is 3)
```

**Multiple return values:**
```python
def stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = stats([5, 2, 8, 1, 9])
print(f"Min={low}, Max={high}, Avg={avg:.1f}")
```

**DRY Principle:** Don't Repeat Yourself. If you write the same code 3+ times, make it a function!

What repetitive task in your life would you automate with a function? 🤔""",

            "hint": "💡 Functions need: `def` keyword, name, parentheses (with optional params), colon, then an indented body. Use `return` to send back a value. Without `return`, functions return `None`. Call a function by writing `function_name(arguments)`.",

            "practice": """**Practice: Function Workshop** 🔧

Write these three functions:

**1.** `is_even(n)` → returns `True` if n is even, `False` otherwise

**2.** `reverse_string(s)` → returns the string reversed

**3.** `count_vowels(text)` → counts vowels (a, e, i, o, u), case-insensitive

```python
# Test your functions:
print(is_even(4))               # True
print(is_even(7))               # False
print(reverse_string("hello"))  # "olleh"
print(reverse_string("Python")) # "nohtyP"
print(count_vowels("Python"))   # 2
print(count_vowels("aeiou"))    # 5
```

Start with `is_even` — it's the simplest. What's your approach? 🎯""",

            "differently": """**Functions as a recipe card** 🍳

A recipe card has:
- **Name:** "Chocolate Cake"
- **Ingredients (parameters):** flour, sugar, eggs, chocolate
- **Steps (function body):** mix, bake, cool
- **Output (return value):** 🎂 a delicious cake

```python
# Recipe card = function definition
def make_cake(flour, sugar, eggs, chocolate):
    batter = mix(flour, sugar, eggs, chocolate)
    cake = bake(batter, temp=180, minutes=30)
    return cake

# Following the recipe = calling the function
my_cake = make_cake(200, 150, 3, 100)
friend_cake = make_cake(400, 300, 6, 200)  # Double recipe!
```

The beauty: write the recipe **once**, use it **unlimited times** with different ingredients!

That's exactly what functions do — write once, call many times. Does this help? 🎂"""
        },

        "lists": {
            "explain": """**Lists** store multiple ordered items — one of Python's most powerful tools! 📝

```python
# Creating lists
fruits   = ["apple", "banana", "cherry"]
numbers  = [1, 2, 3, 4, 5]
mixed    = [1, "hello", 3.14, True]   # Can mix types
empty    = []

# Accessing items (0-indexed!)
print(fruits[0])    # "apple"  (first)
print(fruits[-1])   # "cherry" (last)
print(fruits[1:3])  # ["banana", "cherry"] (slicing)
print(fruits[:2])   # ["apple", "banana"]
print(fruits[::2])  # ["apple", "cherry"] (every 2nd)
```

**Common operations:**
```python
fruits = ["apple", "banana"]

# Add
fruits.append("cherry")         # end
fruits.insert(1, "blueberry")   # at index
fruits.extend(["mango", "kiwi"]) # merge list

# Remove
fruits.remove("banana")   # by value (first match)
last = fruits.pop()       # remove & return last
del fruits[0]             # by index

# Info
len(fruits)               # count
"mango" in fruits         # True/False membership check
fruits.index("cherry")    # find index
fruits.count("apple")     # count occurrences

# Organize
fruits.sort()             # sort in-place
fruits.reverse()          # reverse in-place
sorted_copy = sorted(fruits)  # returns new sorted list
```

**List comprehensions (Pythonic magic!):**
```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
```

What collection of real-world data would you model as a Python list? 🤔""",

            "hint": "💡 Lists are ordered and mutable (changeable). Indexing starts at **0**. Negative indices count from the end (`-1` = last). Use `.append()` to add to end, `.remove(val)` to delete by value, `len()` to count items.",

            "practice": """**Practice: Playlist Manager** 🎵

Build a simple playlist using list operations:

```python
playlist = ["Bohemian Rhapsody", "Hotel California", "Stairway to Heaven"]

# Task 1: Add "Imagine" to the end
# Task 2: Insert "Yesterday" at position 1
# Task 3: Remove "Hotel California"
# Task 4: Sort the playlist alphabetically
# Task 5: Print the first 3 songs
# Task 6: Create a new list with only songs that contain the letter 'e'

# After all operations, print the final playlist and its length
```

What's the final sorted playlist? Work through it step by step! 🎼""",

            "differently": """**Lists as a numbered train** 🚂

Imagine a train where each car has a number starting from 0:

```
🚂 [Car 0] [Car 1] [Car 2] [Car 3] [Car 4]
     "apple" "banana" "cherry" "date"  "elderberry"
```

- `fruits[0]` → 🍎 first car
- `fruits[-1]` → 🫐 last car (counting from the back)
- `fruits[1:3]` → 🍌🍒 cars 1 and 2 (up to but NOT including 3)

Operations:
- `.append()` → 🚃 add a new car to the END
- `.insert(2, "new")` → squeeze a new car between 1 and 2
- `.pop()` → 🚫 detach the last car
- `.remove("banana")` → find and remove the 🍌 car

Does the train analogy click? 🚂"""
        },

        "oop": {
            "explain": """**Object-Oriented Programming** models real-world things as code objects! 🏗️

**Class** = Blueprint. **Object** = Instance built from the blueprint.

```python
class Dog:
    \"\"\"Blueprint for a Dog.\"\"\"

    def __init__(self, name, breed, age):
        \"\"\"Constructor: called when creating a new Dog.\"\"\"
        self.name  = name     # instance attribute
        self.breed = breed
        self.age   = age

    def bark(self):
        return f"{self.name} says: Woof! 🐕"

    def info(self):
        return f"{self.name} is a {self.age}-year-old {self.breed}"

# Create objects (instances)
buddy = Dog("Buddy", "Labrador", 3)
max   = Dog("Max",   "Poodle",   5)

print(buddy.bark())   # Buddy says: Woof!
print(max.info())     # Max is a 5-year-old Poodle
print(buddy.name)     # Buddy
```

**The 4 pillars of OOP:**
1. **Encapsulation** — bundle data + behaviour together
2. **Inheritance** — child classes inherit from parent
3. **Polymorphism** — same method name, different behaviour
4. **Abstraction** — hide complexity behind a simple interface

**Inheritance example:**
```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Cat(Animal):          # Cat inherits Animal
    def speak(self):        # Override speak()
        return f"{self.name} says: Meow! 🐱"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says: Woof! 🐕"

animals = [Cat("Whiskers"), Dog("Rex")]
for a in animals:
    print(a.speak())   # Polymorphism: each uses its own speak()
```

Think of a real-world object. What attributes and methods would it have? 🤔""",

            "hint": "💡 Class = template/blueprint. `__init__` = constructor (runs automatically on object creation). `self` = the specific instance. Attributes store data (`self.name`), methods are functions belonging to the class. Call a method with `object.method()`.",

            "practice": """**Practice: Build a Bank Account** 🏦

Create a `BankAccount` class:
- **Constructor:** `__init__(self, owner, balance=0)`
- **`deposit(amount)`** — add money, return new balance
- **`withdraw(amount)`** — subtract if funds available, otherwise return `"Insufficient funds"`
- **`get_balance()`** — return current balance
- **`__str__()`** — return `"BankAccount(owner=Alice, balance=1300)"`

```python
# Test your class:
acc = BankAccount("Alice", 1000)
print(acc.deposit(500))     # 1500
print(acc.withdraw(200))    # 1300
print(acc.withdraw(5000))   # Insufficient funds
print(acc.get_balance())    # 1300
print(acc)                  # BankAccount(owner=Alice, balance=1300)
```

What happens when Alice tries to withdraw more than she has? 🔒""",

            "differently": """**OOP as a cookie cutter** 🍪

- **Class** = the cookie cutter (shape/template)
- **Object** = an actual cookie made with that cutter
- **Attributes** = the cookie's properties (size, flavour, sprinkles)
- **Methods** = things the cookie can do (be_eaten, be_decorated)

```python
# The cutter (class)
class Cookie:
    def __init__(self, flavour, has_sprinkles=False):
        self.flavour = flavour
        self.has_sprinkles = has_sprinkles

    def describe(self):
        sprinkles = "with sprinkles" if self.has_sprinkles else "plain"
        return f"A {self.flavour} cookie, {sprinkles}"

# Making cookies (creating objects)
c1 = Cookie("chocolate", True)
c2 = Cookie("vanilla")
c3 = Cookie("oatmeal", True)

# Each cookie is independent
print(c1.describe())  # A chocolate cookie, with sprinkles
print(c2.describe())  # A vanilla cookie, plain
```

One cutter → unlimited distinct cookies. One class → unlimited distinct objects. Does this help? 🍪"""
        },

        "error handling": {
            "explain": """**Error handling** prevents your program from crashing unexpectedly! 🛡️

```python
# Without error handling — program CRASHES on bad input
number = int(input("Enter a number: "))  # crashes if user types "abc"

# With try/except — graceful handling
try:
    number = int(input("Enter a number: "))
    result = 100 / number
    print(f"Result: {result}")
except ValueError:
    print("❌ Please enter a valid number, not text!")
except ZeroDivisionError:
    print("❌ Can't divide by zero!")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
else:
    print("✅ No errors occurred!")    # runs if no exception
finally:
    print("🏁 This always runs")      # runs no matter what
```

**Common exception types:**
| Exception | When it occurs |
|---|---|
| `ValueError` | Wrong value type (e.g., `int("abc")`) |
| `ZeroDivisionError` | Dividing by zero |
| `IndexError` | List index out of range |
| `KeyError` | Dictionary key doesn't exist |
| `TypeError` | Wrong type for operation |
| `FileNotFoundError` | File doesn't exist |
| `AttributeError` | Object doesn't have that attribute |

**Raising your own exceptions:**
```python
def set_age(age):
    if age < 0:
        raise ValueError(f"Age cannot be negative: {age}")
    return age
```

When have YOU encountered a program crash that better error handling would have prevented? 🤔""",

            "hint": "💡 Wrap risky code in `try:`. Catch specific exceptions in `except ExceptionType:`. The `finally:` block always runs (use it for cleanup like closing files). Catch the most specific exception first — don't just use bare `except:` which catches everything including keyboard interrupts!",

            "practice": """**Practice: Robust Input Handler** 🛡️

Write a function `safe_int_input(prompt, min_val=None, max_val=None)` that:
1. Repeatedly asks for input until valid
2. Handles `ValueError` if the user enters non-numeric text
3. Validates that the number is within `[min_val, max_val]` if provided
4. Returns the validated integer

```python
# Usage:
age = safe_int_input("Enter your age: ", min_val=0, max_val=150)
print(f"Valid age: {age}")
```

Then test it with: age prompt (0–150), score prompt (0–100).

Hint: use a `while True:` loop with `break` on success! 🔄""",
        },

        "dictionaries": {
            "explain": """**Dictionaries** store data as key-value pairs — like a real dictionary! 📖

```python
# Creating a dictionary
student = {
    "name": "Alice",
    "age": 20,
    "gpa": 3.85,
    "courses": ["Python", "Math", "English"]
}

# Accessing values
print(student["name"])         # Alice
print(student.get("age"))      # 20
print(student.get("phone", "N/A"))  # N/A (default if missing)

# Modifying
student["age"] = 21            # update
student["year"] = "Sophomore"  # add new key
del student["gpa"]             # delete key

# Iterating
for key in student:
    print(key, ":", student[key])

for key, value in student.items():
    print(f"{key}: {value}")

# Useful methods
print(student.keys())    # all keys
print(student.values())  # all values
print("name" in student) # True (check key existence)
```

**Nested dictionaries:**
```python
school = {
    "Alice": {"grade": "A", "score": 95},
    "Bob":   {"grade": "B", "score": 82}
}
print(school["Alice"]["score"])  # 95
```

What real-world data would you model with a dictionary? 🤔""",
            "hint": "💡 Dictionary keys must be immutable (strings, numbers, tuples). Use `d.get(key, default)` instead of `d[key]` to avoid `KeyError`. Check if a key exists with `key in d`. Use `.items()` to loop over both keys and values.",
            "practice": """**Practice: Student Grade Book** 📚

Build a simple grade book:

```python
grades = {
    "Alice": [90, 85, 92, 88],
    "Bob":   [75, 80, 70, 85],
    "Carol": [95, 98, 92, 96]
}

# Task 1: Write a function get_average(scores) that returns the average
# Task 2: Write a function class_report(grades) that prints:
#   - Each student's name and average score
#   - The top student (highest average)
#   - The class average

class_report(grades)
```""",
        },

        "comprehensions": {
            "explain": """**List comprehensions** let you create lists in one elegant, Pythonic line! ⚡

**Basic syntax:** `[expression for item in iterable]`

```python
# Traditional way
squares = []
for x in range(10):
    squares.append(x ** 2)

# Pythonic way — list comprehension!
squares = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

**With a condition filter:**
```python
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

long_words = [w for w in words if len(w) > 5]
```

**Transform strings:**
```python
names  = ["alice", "bob", "charlie"]
upper  = [name.upper() for name in names]
# ["ALICE", "BOB", "CHARLIE"]

lengths = [len(name) for name in names]
# [5, 3, 7]
```

**Dictionary comprehensions:**
```python
word_lengths = {word: len(word) for word in ["Python", "is", "great"]}
# {"Python": 6, "is": 2, "great": 5}
```

**Set comprehensions:**
```python
unique_lengths = {len(word) for word in ["hello", "world", "hi"]}
# {5, 2}
```

**Rule of thumb:** If a comprehension needs 3+ lines or complex logic, use a regular loop instead — readability wins!

What's a list you'd want to transform or filter in a program? 🤔""",
            "hint": "💡 Comprehension structure: `[what_to_add  for each_item in collection  if condition]`. The `if condition` part is optional. Think of it as: 'Add `x²` for each `x` in range, but only if `x` is even'.",
            "practice": """**Practice: Comprehension Challenges** ⚡

```python
# Challenge 1: Create a list of cubes of numbers 1–10
# Expected: [1, 8, 27, 64, 125, 216, 343, 512, 729, 1000]

# Challenge 2: Filter only the words longer than 4 chars from:
words = ["Python", "is", "a", "great", "programming", "language"]
# Expected: ["Python", "great", "programming", "language"]

# Challenge 3: Create a dict mapping numbers 1–5 to their squares
# Expected: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Challenge 4 (Bonus): Flatten a 2D list into 1D using a comprehension
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = ???
# Expected: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Start with Challenge 1! 🚀"""
        },
    }

    DEFAULT_RESPONSES = [
        """That's a great Python question! 🐍

Let me help you think through it. The best way to understand programming concepts is to:

1. **Break it down** — what's the smallest piece you can understand?
2. **Experiment** — try running code and see what happens
3. **Read errors** — Python error messages tell you exactly what went wrong

Could you share more about what you're working on or what's confusing you? I can give you a much more targeted explanation with more context.

What topic are you currently exploring? 📚""",

        """Good question! Let me think through this with you. 🤔

When you're stuck in Python, try this debugging approach:

```python
# Add print statements to see what's happening
print("Before the problematic line:", my_variable)
print("Type:", type(my_variable))
```

Can you describe what you expected to happen vs what actually happened? That usually points directly to the issue.

Also, which topic does this relate to? I can tailor my explanation to your current level. 💡""",
    ]

    async def chat(self, messages: List[Dict], student_context: Dict) -> str:
        if not messages:
            return self._welcome(student_context)

        last_msg = messages[-1].get("content", "")
        action = student_context.get("action")
        level = student_context.get("skill_level", "beginner")
        current_topic = student_context.get("current_topic", "")
        lang = student_context.get("language")
        detected = self.detect_script_language(last_msg)
        if detected:
            lang = detected
            student_context["language"] = detected
        elif not lang:
            lang = "en"

        if lang == "te":
            return self._get_telugu_explanation(last_msg, current_topic, action)
        elif lang == "hi":
            return self._get_hindi_explanation(last_msg, current_topic, action)

        # Detect topic from message + current topic context
        topic_key = self._detect_topic(last_msg.lower() + " " + current_topic.lower())

        if action == "explain_differently":
            return self._explain_differently(topic_key, level)
        elif action == "hint":
            return self._get_hint(topic_key)
        elif action == "practice_problem":
            return self._get_practice(topic_key, level)
        else:
            return self._get_explanation(topic_key, last_msg, level)

    def _get_telugu_explanation(self, msg: str, current_topic: str, action: str = None) -> str:
        lower = msg.lower() + " " + current_topic.lower()
        if "list" in lower or "లిస్ట్" in msg:
            return """నమస్కారం! పైథాన్ లో **List (లిస్ట్)** అంటే ఏమిటో చాలా సులభంగా తెలుసుకుందాం. 🧺

మనం మార్కెట్‌కు వెళ్ళినప్పుడు ఒక కాగితం మీద కావాల్సిన వస్తువుల పేర్లు రాసుకుంటాం కదా? పైథాన్‌లో కూడా **అనేక విలువలను ఒకే వేరియబుల్ లో వరుసగా భద్రపరచడానికి 'List' ఉపయోగిస్తాం.**

```python
# పండ్ల పేర్లతో ఒక పైథాన్ లిస్ట్
fruits = ["యాపిల్", "అరటిపండు", "మామిడి"]

# మొదటి అంశం పొందడం (ఇండెక్స్ 0 నుండి ప్రారంభమవుతుంది)
print(fruits[0])  # అవుట్‌పుట్: యాపిల్

# కొత్త పండును జోడించడం
fruits.append("ద్రాక్ష")
print(fruits)
```

**గుర్తుంచుకోవలసిన ముఖ్య విషయాలు:**
1. లిస్ట్‌ను స్క్వేర్ బ్రాకెట్లు `[]` తో తయారు చేస్తాం.
2. ఇండెక్స్ ఎప్పుడూ `0` తోనే ప్రారంభమవుతుంది.
3. లిస్ట్‌లోని అంశాలను మనం ఎప్పుడైనా మార్చవచ్చు లేదా కొత్తవి చేర్చవచ్చు.

మీకు నచ్చిన 3 అంశాలతో ఒక లిస్ట్ రాసి ప్రయత్నించండి! 🚀"""

        elif "loop" in lower or "లూప్" in msg or "for" in lower:
            return """నమస్తే! పైథాన్ లో **`for loop`** అనేది ఒకే పనిని వరుసగా పదే పదే చేయడానికి ఉపయోగిస్తారు. 🔄

ఉదాహరణకు ఒక బుట్టలో పండ్లు ఉన్నాయనుకోండి, ఒక్కొక్క పండును బయటకు తీసి చూసే పద్ధతినే `loop` అంటాం.

```python
fruits = ["యాపిల్", "అరటిపండు", "మామిడి"]

# ప్రతి పండును వరుసగా ప్రింట్ చేయడం
for fruit in fruits:
    print(f"నాకు {fruit} అంటే ఇష్టం!")
```

**లక్షణాలు:**
1. `for` లూప్ లిస్ట్ లోని ప్రతి అంశం వద్దకు వెళ్తుంది.
2. పని పూర్తయ్యే వరకు వాటంతట అవే తిరుగుతాయి.

దీనిపై మీకు ఏదైనా సందేహం ఉందా? అడగండి! 💡"""

        elif "variable" in lower or "వేరియబుల్" in msg:
            return """హలో! పైథాన్ లో **Variables (వేరియబుల్స్)** అంటే సమాచారాన్ని భద్రపరిచే ఒక లేబుల్ ఉన్న డబ్బా లాంటివి. 📦

```python
# వేరియబుల్స్ తయారు చేయడం
name = "సాయి"        # పేరు (Text/String)
age = 22             # వయస్సు (Number/Integer)
score = 95.5         # మార్కులు (Decimal/Float)

print(f"హలో {name}, మీ వయస్సు {age} సంవత్సరాలు!")
```

ఇక్కడ `name`, `age` అనేవి డబ్బా పేర్లు, అందులో విలువలను దాచుకున్నాం.

మీరు ఏ కాన్సెప్ట్ గురించి మరింత తెలుసుకోవాలనుకుంటున్నారు? 🚀"""

        elif "function" in lower or "ఫంక్షన్" in msg or "def" in lower:
            return """నమస్కారం! పైథాన్ లో **Function (ఫంక్షన్)** అనేది ఒక నిర్దిష్టమైన పనిని పదే పదే చేయడానికి రూపొందించిన కోడ్ బ్లాక్. ⚙️

ఒక బటన్ నొక్కితే ఫ్యాన్ తిరిగినట్లే, ఒక ఫంక్షన్‌ని పిలిచినప్పుడు అది అందులోని కోడ్‌ను అమలు చేస్తుంది.

```python
# ఒక సాధారణ గ్రీటింగ్ ఫంక్షన్
def greet(name):
    return f"నమస్కారం {name}, స్వాగతం!"

# ఫంక్షన్‌ని పిలవడం
message = greet("సురేష్")
print(message)
```

ఫంక్షన్‌ను తయారు చేయడానికి `def` కీవర్డ్‌ను ఉపయోగిస్తాం. 🎯"""

        return """నమస్కారం! నేను మీ **PyMentor** ని — మీ వ్యక్తిగత పైథాన్ గురువుని! 🎓

మీరు ఏ పైథాన్ ప్రశ్న అయినా అడగవచ్చు, లేదా మైక్రోఫోన్ ద్వారా మాట్లాడవచ్చు. నేను మీకు వివరంగా తెలుగులో సొంత వివరణతో నేర్పిస్తాను!

**మీరు వీటిని అడగవచ్చు:**
- "పైథాన్ లో లిస్ట్ అంటే ఏమిటి?"
- "ఫర్ లూప్ ఎలా పనిచేస్తుంది?"
- "ఫంక్షన్స్ అంటే ఏమిటి?"
- "నా కోడ్ లో వచ్చిన లోపాన్ని (Error) ఎలా సరిచేయాలి?"

ఈ రోజు మీరు ఏమి నేర్చుకోవాలనుకుంటున్నారు? 🐍"""

    def _get_hindi_explanation(self, msg: str, current_topic: str, action: str = None) -> str:
        lower = msg.lower() + " " + current_topic.lower()
        if "list" in lower or "लिस्ट" in msg:
            return """नमस्ते! पायथन में **List (लिस्ट)** को बहुत आसानी से समझते हैं। 🧺

जैसे हम बाज़ार जाते समय एक पर्ची पर चीज़ों के नाम लिखते हैं, वैसे ही पायथन में **कई वैल्यूज को एक साथ एक ही वेरिएबल में क्रमबद्ध रखने के लिए List का उपयोग किया जाता है।**

```python
# फलों की एक लिस्ट
fruits = ["सेब", "केला", "आम"]

# पहला आइटम प्राप्त करना (इंडेक्स 0 से शुरू होता है)
print(fruits[0])  # आउटपुट: सेब

# नया फल जोड़ना
fruits.append("अंगूर")
print(fruits)
```

**मुख्य बातें:**
1. लिस्ट को स्क्वायर ब्रैकेट्स `[]` से बनाया जाता है।
2. इंडेक्स हमेशा `0` से शुरू होता है।
3. लिस्ट के आइटम्स को कभी भी बदला जा सकता है।

आप भी अपनी पसंद के 3 आइटम्स की लिस्ट बनाकर मुझे दिखाइए! 🚀"""
        return """नमस्ते! मैं हूँ आपका **PyMentor** — आपका निजी पायथन मेंटर! 🎓

आप मुझसे पायथन का कोई भी सवाल पूछ सकते हैं या बोलकर सवाल कर सकते हैं। मैं आपको पूरी तरह से हिंदी में समझाऊँगा!

आप क्या सीखना चाहते हैं? 🐍"""

    def _detect_topic(self, text: str) -> str:
        topic_keywords = {
            "variables": ["variable", "variables", "assign", "assignment", "naming convention", "snake_case"],
            "data types": ["data type", "datatype", "type(", "isinstance(", "integer vs float", "str to int"],
            "conditions": ["if condition", "if statement", "if/else", "if-else", "elif", "else:", "boolean logic", "comparison operator"],
            "loops": ["for loop", "while loop", "nested loop", "looping", "range(", "break", "continue", "infinite loop"],
            "functions": ["def ", "function", "return value", "parameter", "argument", "scope", "lambda"],
            "lists": ["python list", "lists", "list indexing", "list slicing", ".append(", ".pop(", ".sort("],
            "oop": ["class ", "oop", "inheritance", "object-oriented", "dunder", "__init__", "self.", "polymorphism"],
            "error handling": ["try:", "except", "try/except", "exception", "valueerror", "keyerror", "typeerror", "try-except"],
            "dictionaries": ["dictionary", "dict()", "key-value", ".items()", ".get(", "hash map", "mapping"],
            "comprehensions": ["comprehension", "list comp", "dict comp", "generator"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                return topic
        return "general"

    def _get_explanation(self, topic: str, message: str, level: str) -> str:
        if topic in self.TOPIC_CONTENT:
            return self.TOPIC_CONTENT[topic]["explain"]
        return random.choice(self.DEFAULT_RESPONSES)

    def _explain_differently(self, topic: str, level: str) -> str:
        content = self.TOPIC_CONTENT.get(topic, {})
        if "differently" in content:
            return content["differently"]
        # Generic alternative explanation
        return f"""Let me try a completely different approach! 🔄

Instead of a formal definition, here's a **real-world analogy** for the concept you asked about:

Imagine you're building a food delivery app. Every Python concept maps to something in that app:
- **Variables** = storing customer name, order total, delivery address
- **Conditions** = "if order > $50, apply free delivery"
- **Loops** = process each item in the cart
- **Functions** = the "calculate_total()" step you reuse everywhere
- **Classes** = the Order, Customer, Restaurant templates

Which part of the concept would you like me to re-explain through this lens? 🍕

Or try asking me: **"Explain [specific thing] like I'm 10"** and I'll simplify even further!"""

    def _get_hint(self, topic: str) -> str:
        content = self.TOPIC_CONTENT.get(topic, {})
        if "hint" in content:
            return content["hint"]
        return """💡 **General Hint:**

Break the problem into the smallest possible step.

Ask yourself:
1. What do I **already know** how to do?
2. What **information** do I have available?
3. What is the **very next** small step?

Try writing just **one line** of code — it doesn't have to be the full solution. Progress beats perfection!

If you're getting an error, copy it here and I'll help you decode it. 🔍"""

    def _get_practice(self, topic: str, level: str) -> str:
        content = self.TOPIC_CONTENT.get(topic, {})
        if "practice" in content:
            return content["practice"]

        level_problems = {
            "beginner": """**Practice Problem: FizzBuzz** 🎮

Print numbers 1 to 30:
- Divisible by 3 → print `"Fizz"`
- Divisible by 5 → print `"Buzz"`
- Divisible by 3 AND 5 → print `"FizzBuzz"`
- Otherwise → print the number

```python
for i in range(1, 31):
    # Your logic here
    pass
```

Hint: check divisibility by 15 (= 3×5) **first**! Use `%` (modulo) operator. 🔢""",

            "intermediate": """**Practice Problem: Word Frequency Counter** 📊

```python
def word_count(text):
    \"\"\"Count how often each word appears (case-insensitive).\"\"\"
    pass

text = "Python is great. Python is fun. Programming is fun too."
print(word_count(text))
# {"python": 2, "is": 3, "great": 1, ...}
```

Hints:
- `.lower()` → case-insensitive
- `.replace('.', '')` → remove punctuation
- `.split()` → split into words
- Loop and build a dictionary 📖""",

            "advanced": """**Practice Problem: Custom Decorator** 🎯

Write a `@timer` decorator that measures and prints how long a function takes to run, then still returns the original result:

```python
@timer
def slow_sum(n):
    import time; time.sleep(0.5)
    return sum(range(n))

result = slow_sum(1000000)
# Prints: slow_sum took 0.502s
# result = 499999500000
```

Hints: `time.time()`, `functools.wraps`, closure pattern ⏱️""",
        }

        return level_problems.get(level, level_problems["beginner"])

    def _welcome(self, context: Dict) -> str:
        level = context.get("skill_level", "beginner")
        topic = context.get("current_topic", "Python")
        return f"""👋 Hello! I'm **PyMentor** — your personal Python learning assistant!

I'm here to help you learn Python interactively as a **{level.capitalize()}** learner.
Your current focus: **{topic}**

**How I can help you:**
- 💬 Ask me any Python question
- 🔄 Click **"Explain Differently"** if my explanation doesn't click
- 💡 Click **"Give me a Hint"** when you're stuck on a problem
- 🎯 Click **"Practice Problem"** for hands-on coding challenges

**Try asking me:**
- "What are variables and how do I use them?"
- "Explain loops with a real example"
- "How do functions work?"
- "What is object-oriented programming?"
- "Why do I get an IndexError?"

What would you like to learn today? 🚀"""


# ── Factory ──────────────────────────────────────────────────────────────────

_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    provider_name = (settings.AI_PROVIDER or "").lower()

    if (provider_name == "gemini" or (not provider_name and settings.GEMINI_API_KEY)) and settings.GEMINI_API_KEY:
        try:
            p = GeminiProvider()
            print(f"[AI] Using GeminiProvider ({settings.GEMINI_MODEL})")
            return p
        except Exception as exc:
            print(f"[AI] Gemini init failed ({exc}). Falling back to MockMentorProvider.")

    if provider_name == "openai" and settings.OPENAI_API_KEY:
        try:
            p = OpenAIProvider()
            print(f"[AI] Using OpenAIProvider ({settings.OPENAI_MODEL})")
            return p
        except Exception as exc:
            print(f"[AI] OpenAI init failed ({exc}). Falling back to MockMentorProvider.")

    print("[AI] Using MockMentorProvider  (set AI_PROVIDER=gemini + GEMINI_API_KEY for real AI)")
    return MockMentorProvider()


def get_provider() -> AIProvider:
    """Singleton accessor."""
    global _provider
    if _provider is None:
        _provider = get_ai_provider()
    return _provider
