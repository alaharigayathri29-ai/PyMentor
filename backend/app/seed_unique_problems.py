"""
Seed 50 Completely Unique, Non-Duplicate, Easy & Practical Practice Problems per Topic.
Preserves existing problem IDs (1, 2, 9) and existing user submissions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.models import Topic, PracticeProblem, PracticeSubmission

def get_unique_problems_catalog():
    return {
        "variables": [
            ("Calculate Area of Rectangle", "Write `rectangle_area(length, width)` that returns the area.", "easy",
             "def rectangle_area(length, width):\n    return length * width",
             [{"call": "rectangle_area(5, 10)", "expected_output": "50"}, {"call": "rectangle_area(7, 3)", "expected_output": "21"}]),
            ("Calculate Perimeter of Rectangle", "Write `rectangle_perimeter(l, w)` that returns `2 * (l + w)`.", "easy",
             "def rectangle_perimeter(l, w):\n    return 2 * (l + w)",
             [{"call": "rectangle_perimeter(5, 10)", "expected_output": "30"}, {"call": "rectangle_perimeter(3, 4)", "expected_output": "14"}]),
            ("Calculate Simple Interest", "Write `simple_interest(principal, rate, time)` returning `(P * R * T) / 100`.", "easy",
             "def simple_interest(principal, rate, time):\n    return (principal * rate * time) / 100",
             [{"call": "simple_interest(1000, 5, 2)", "expected_output": "100.0"}, {"call": "simple_interest(5000, 10, 1)", "expected_output": "500.0"}]),
            ("Convert Hours to Minutes", "Write `hours_to_minutes(hours)` that converts hours to minutes.", "easy",
             "def hours_to_minutes(hours):\n    return hours * 60",
             [{"call": "hours_to_minutes(2)", "expected_output": "120"}, {"call": "hours_to_minutes(0.5)", "expected_output": "30.0"}]),
            ("Convert Minutes to Seconds", "Write `minutes_to_seconds(m)` that returns `m * 60`.", "easy",
             "def minutes_to_seconds(m):\n    return m * 60",
             [{"call": "minutes_to_seconds(5)", "expected_output": "300"}, {"call": "minutes_to_seconds(1)", "expected_output": "60"}]),
            ("Calculate Square and Cube", "Write `square_and_cube(n)` returning tuple `(n**2, n**3)`.", "easy",
             "def square_and_cube(n):\n    return (n**2, n**3)",
             [{"call": "square_and_cube(3)", "expected_output": "(9, 27)"}, {"call": "square_and_cube(2)", "expected_output": "(4, 8)"}]),
            ("Average of Three Numbers", "Write `average_three(a, b, c)` returning their average as float.", "easy",
             "def average_three(a, b, c):\n    return (a + b + c) / 3.0",
             [{"call": "average_three(10, 20, 30)", "expected_output": "20.0"}, {"call": "average_three(4, 5, 6)", "expected_output": "5.0"}]),
            ("Swap Variables Tuple", "Write `swap_values(a, b)` returning `(b, a)`.", "easy",
             "def swap_values(a, b):\n    return (b, a)",
             [{"call": "swap_values(10, 20)", "expected_output": "(20, 10)"}, {"call": "swap_values('x', 'y')", "expected_output": "('y', 'x')"}]),
            ("Format Full Name", "Write `format_name(first, last)` that returns `'Last, First'`.", "easy",
             "def format_name(first, last):\n    return f'{last}, {first}'",
             [{"call": "format_name('Gayatri', 'Alahari')", "expected_output": "'Alahari, Gayatri'"}, {"call": "format_name('Guido', 'Rossum')", "expected_output": "'Rossum, Guido'"}]),
            ("Convert Kilometers to Miles", "Write `km_to_miles(km)` using factor `0.621371` rounded to 2 decimals.", "easy",
             "def km_to_miles(km):\n    return round(km * 0.621371, 2)",
             [{"call": "km_to_miles(10)", "expected_output": "6.21"}, {"call": "km_to_miles(5)", "expected_output": "3.11"}]),
            ("Convert Pounds to Kilograms", "Write `lbs_to_kg(lbs)` using factor `0.453592` rounded to 2 decimals.", "easy",
             "def lbs_to_kg(lbs):\n    return round(lbs * 0.453592, 2)",
             [{"call": "lbs_to_kg(10)", "expected_output": "4.54"}, {"call": "lbs_to_kg(150)", "expected_output": "68.04"}]),
            ("Area of Triangle", "Write `triangle_area(base, height)` returning `0.5 * base * height`.", "easy",
             "def triangle_area(base, height):\n    return 0.5 * base * height",
             [{"call": "triangle_area(10, 5)", "expected_output": "25.0"}, {"call": "triangle_area(8, 4)", "expected_output": "16.0"}]),
            ("Calculate Net Salary", "Write `net_salary(gross, tax_rate)` returning `gross * (1 - tax_rate/100)`.", "easy",
             "def net_salary(gross, tax_rate):\n    return gross * (1 - tax_rate / 100)",
             [{"call": "net_salary(50000, 10)", "expected_output": "45000.0"}, {"call": "net_salary(100000, 20)", "expected_output": "80000.0"}]),
            ("Calculate Speed", "Write `calc_speed(dist_km, time_hrs)` returning speed in km/h.", "easy",
             "def calc_speed(dist_km, time_hrs):\n    return dist_km / time_hrs",
             [{"call": "calc_speed(120, 2)", "expected_output": "60.0"}, {"call": "calc_speed(90, 1.5)", "expected_output": "60.0"}]),
            ("Body Mass Index", "Write `calc_bmi(weight_kg, height_m)` returning BMI `weight / (height**2)` rounded to 1 decimal.", "easy",
             "def calc_bmi(weight_kg, height_m):\n    return round(weight_kg / (height_m ** 2), 1)",
             [{"call": "calc_bmi(70, 1.75)", "expected_output": "22.9"}, {"call": "calc_bmi(80, 1.8)", "expected_output": "24.7"}]),
            ("Calculate Discounted Price", "Write `discounted_price(price, discount_pct)` returning price after discount.", "easy",
             "def discounted_price(price, discount_pct):\n    return price * (1 - discount_pct / 100)",
             [{"call": "discounted_price(100, 15)", "expected_output": "85.0"}, {"call": "discounted_price(50, 10)", "expected_output": "45.0"}]),
            ("Find Third Angle of Triangle", "Write `third_angle(a, b)` returning `180 - a - b`.", "easy",
             "def third_angle(a, b):\n    return 180 - a - b",
             [{"call": "third_angle(60, 60)", "expected_output": "60"}, {"call": "third_angle(90, 45)", "expected_output": "45"}]),
            ("Power Calculation", "Write `calc_power(base, exp)` returning `base ** exp`.", "easy",
             "def calc_power(base, exp):\n    return base ** exp",
             [{"call": "calc_power(2, 5)", "expected_output": "32"}, {"call": "calc_power(3, 3)", "expected_output": "27"}]),
            ("Quotient and Remainder", "Write `div_mod(a, b)` returning tuple `(a // b, a % b)`.", "easy",
             "def div_mod(a, b):\n    return (a // b, a % b)",
             [{"call": "div_mod(17, 5)", "expected_output": "(3, 2)"}, {"call": "div_mod(20, 4)", "expected_output": "(5, 0)"}]),
            ("Days to Years and Weeks", "Write `days_to_duration(days)` returning tuple `(years, weeks)` with 365 days/year.", "easy",
             "def days_to_duration(days):\n    return (days // 365, (days % 365) // 7)",
             [{"call": "days_to_duration(400)", "expected_output": "(1, 5)"}, {"call": "days_to_duration(800)", "expected_output": "(2, 10)"}]),
            ("Surface Area of Cube", "Write `cube_surface_area(side)` returning `6 * side**2`.", "easy",
             "def cube_surface_area(side):\n    return 6 * side**2",
             [{"call": "cube_surface_area(3)", "expected_output": "54"}, {"call": "cube_surface_area(5)", "expected_output": "150"}]),
            ("Volume of Cylinder", "Write `cylinder_volume(radius, height)` returning `3.14159 * radius**2 * height` rounded to 2 decimals.", "easy",
             "def cylinder_volume(radius, height):\n    return round(3.14159 * (radius ** 2) * height, 2)",
             [{"call": "cylinder_volume(3, 5)", "expected_output": "141.37"}, {"call": "cylinder_volume(2, 4)", "expected_output": "50.27"}]),
            ("Tip Calculator", "Write `calc_tip(bill, pct)` returning tip amount rounded to 2 decimals.", "easy",
             "def calc_tip(bill, pct):\n    return round(bill * (pct / 100), 2)",
             [{"call": "calc_tip(50, 15)", "expected_output": "7.5"}, {"call": "calc_tip(120, 20)", "expected_output": "24.0"}]),
            ("Convert Inches to CM", "Write `inches_to_cm(inches)` using `2.54`.", "easy",
             "def inches_to_cm(inches):\n    return inches * 2.54",
             [{"call": "inches_to_cm(10)", "expected_output": "25.4"}, {"call": "inches_to_cm(5)", "expected_output": "12.7"}]),
            ("Circle Circumference", "Write `circle_circumference(r)` using `2 * 3.14159 * r` rounded to 2 decimals.", "easy",
             "def circle_circumference(r):\n    return round(2 * 3.14159 * r, 2)",
             [{"call": "circle_circumference(5)", "expected_output": "31.42"}, {"call": "circle_circumference(10)", "expected_output": "62.83"}]),
            ("Total Seconds from Time", "Write `total_seconds(h, m, s)` returning total seconds.", "easy",
             "def total_seconds(h, m, s):\n    return h * 3600 + m * 60 + s",
             [{"call": "total_seconds(1, 1, 1)", "expected_output": "3661"}, {"call": "total_seconds(2, 30, 0)", "expected_output": "9000"}]),
            ("ASCII Value of Char", "Write `char_ascii(c)` returning `ord(c)`.", "easy",
             "def char_ascii(c):\n    return ord(c)",
             [{"call": "char_ascii('A')", "expected_output": "65"}, {"call": "char_ascii('a')", "expected_output": "97"}]),
            ("Character from ASCII", "Write `ascii_to_char(code)` returning `chr(code)`.", "easy",
             "def ascii_to_char(code):\n    return chr(code)",
             [{"call": "ascii_to_char(65)", "expected_output": "'A'"}, {"call": "ascii_to_char(98)", "expected_output": "'b'"}]),
            ("Split Bill Among Friends", "Write `split_bill(total, num_people)` returning amount per person rounded to 2 decimals.", "easy",
             "def split_bill(total, num_people):\n    return round(total / num_people, 2)",
             [{"call": "split_bill(100, 4)", "expected_output": "25.0"}, {"call": "split_bill(75, 3)", "expected_output": "25.0"}]),
            ("Convert Gallons to Liters", "Write `gallons_to_liters(g)` using `3.78541` rounded to 2 decimals.", "easy",
             "def gallons_to_liters(g):\n    return round(g * 3.78541, 2)",
             [{"call": "gallons_to_liters(1)", "expected_output": "3.79"}, {"call": "gallons_to_liters(5)", "expected_output": "18.93"}]),
            ("Area of Trapezoid", "Write `trapezoid_area(a, b, h)` returning `((a + b) / 2) * h`.", "easy",
             "def trapezoid_area(a, b, h):\n    return ((a + b) / 2) * h",
             [{"call": "trapezoid_area(5, 7, 4)", "expected_output": "24.0"}, {"call": "trapezoid_area(3, 5, 2)", "expected_output": "8.0"}]),
            ("Kinetic Energy Calculator", "Write `kinetic_energy(m, v)` returning `0.5 * m * (v**2)`.", "easy",
             "def kinetic_energy(m, v):\n    return 0.5 * m * (v ** 2)",
             [{"call": "kinetic_energy(10, 2)", "expected_output": "20.0"}, {"call": "kinetic_energy(2, 5)", "expected_output": "25.0"}]),
            ("Potential Energy Calculator", "Write `potential_energy(m, h, g=9.8)` returning `m * g * h` rounded to 1 decimal.", "easy",
             "def potential_energy(m, h, g=9.8):\n    return round(m * g * h, 1)",
             [{"call": "potential_energy(5, 10)", "expected_output": "490.0"}, {"call": "potential_energy(2, 5)", "expected_output": "98.0"}]),
            ("Convert Bytes to Kilobytes", "Write `bytes_to_kb(b)` returning `b / 1024` rounded to 2 decimals.", "easy",
             "def bytes_to_kb(b):\n    return round(b / 1024, 2)",
             [{"call": "bytes_to_kb(2048)", "expected_output": "2.0"}, {"call": "bytes_to_kb(5000)", "expected_output": "4.88"}]),
            ("Convert Megabytes to Gigabytes", "Write `mb_to_gb(mb)` returning `mb / 1024` rounded to 2 decimals.", "easy",
             "def mb_to_gb(mb):\n    return round(mb / 1024, 2)",
             [{"call": "mb_to_gb(4096)", "expected_output": "4.0"}, {"call": "mb_to_gb(2500)", "expected_output": "2.44"}]),
            ("String Concatenator with Space", "Write `join_with_space(s1, s2)` returning `f'{s1} {s2}'`.", "easy",
             "def join_with_space(s1, s2):\n    return f'{s1} {s2}'",
             [{"call": "join_with_space('Hello', 'World')", "expected_output": "'Hello World'"}, {"call": "join_with_space('Py', 'Mentor')", "expected_output": "'Py Mentor'"}]),
            ("Negative Value Inverter", "Write `invert_sign(n)` returning `-n`.", "easy",
             "def invert_sign(n):\n    return -n",
             [{"call": "invert_sign(5)", "expected_output": "-5"}, {"call": "invert_sign(-12)", "expected_output": "12"}]),
            ("Half of a Number", "Write `half_value(n)` returning `n / 2`.", "easy",
             "def half_value(n):\n    return n / 2",
             [{"call": "half_value(10)", "expected_output": "5.0"}, {"call": "half_value(7)", "expected_output": "3.5"}]),
            ("Double Value", "Write `double_value(n)` returning `n * 2`.", "easy",
             "def double_value(n):\n    return n * 2",
             [{"call": "double_value(7)", "expected_output": "14"}, {"call": "double_value(25)", "expected_output": "50"}]),
            ("Is String Empty", "Write `is_empty_str(s)` returning `len(s) == 0`.", "easy",
             "def is_empty_str(s):\n    return len(s) == 0",
             [{"call": "is_empty_str('')", "expected_output": "True"}, {"call": "is_empty_str('abc')", "expected_output": "False"}]),
            ("First Character of String", "Write `first_char(s)` returning the first character or empty string if empty.", "easy",
             "def first_char(s):\n    return s[0] if s else ''",
             [{"call": "first_char('Python')", "expected_output": "'P'"}, {"call": "first_char('')", "expected_output": "''"}]),
            ("Last Character of String", "Write `last_char(s)` returning the last character or empty string if empty.", "easy",
             "def last_char(s):\n    return s[-1] if s else ''",
             [{"call": "last_char('Code')", "expected_output": "'e'"}, {"call": "last_char('A')", "expected_output": "'A'"}]),
            ("Multiply String", "Write `repeat_str(s, n)` returning `s * n`.", "easy",
             "def repeat_str(s, n):\n    return s * n",
             [{"call": "repeat_str('Hi', 3)", "expected_output": "'HiHiHi'"}, {"call": "repeat_str('=', 5)", "expected_output": "'====='"}]),
            ("Calculate Hypotenuse", "Write `calc_hypotenuse(a, b)` returning `(a**2 + b**2)**0.5`.", "easy",
             "def calc_hypotenuse(a, b):\n    return (a ** 2 + b ** 2) ** 0.5",
             [{"call": "calc_hypotenuse(3, 4)", "expected_output": "5.0"}, {"call": "calc_hypotenuse(5, 12)", "expected_output": "13.0"}]),
            ("Distance Between 1D Points", "Write `dist_1d(x1, x2)` returning `abs(x1 - x2)`.", "easy",
             "def dist_1d(x1, x2):\n    return abs(x1 - x2)",
             [{"call": "dist_1d(5, 12)", "expected_output": "7"}, {"call": "dist_1d(20, 8)", "expected_output": "12"}]),
            ("Percentage of Total", "Write `calc_percent(val, total)` returning `(val / total) * 100` rounded to 1 decimal.", "easy",
             "def calc_percent(val, total):\n    return round((val / total) * 100, 1)",
             [{"call": "calc_percent(25, 100)", "expected_output": "25.0"}, {"call": "calc_percent(3, 8)", "expected_output": "37.5"}]),
            ("Square Area", "Write `square_area(side)` returning `side ** 2`.", "easy",
             "def square_area(side):\n    return side ** 2",
             [{"call": "square_area(4)", "expected_output": "16"}, {"call": "square_area(9)", "expected_output": "81"}]),
            ("Convert Feet to Inches", "Write `feet_to_inches(feet)` returning `feet * 12`.", "easy",
             "def feet_to_inches(feet):\n    return feet * 12",
             [{"call": "feet_to_inches(5)", "expected_output": "60"}, {"call": "feet_to_inches(2.5)", "expected_output": "30.0"}]),
            ("Remaining Days in Week", "Write `days_left_in_week(day_num)` (1=Mon, 7=Sun) returning `7 - day_num`.", "easy",
             "def days_left_in_week(day_num):\n    return 7 - day_num",
             [{"call": "days_left_in_week(3)", "expected_output": "4"}, {"call": "days_left_in_week(6)", "expected_output": "1"}]),
            ("Float to Int Truncator", "Write `truncate_float(val)` returning `int(val)`.", "easy",
             "def truncate_float(val):\n    return int(val)",
             [{"call": "truncate_float(9.87)", "expected_output": "9"}, {"call": "truncate_float(15.2)", "expected_output": "15"}]),
        ]
    }

def generate_topic_pack(slug, name):
    """Generate 50 distinct, unique problems for a given topic."""
    catalog = get_unique_problems_catalog()
    problems = []
    if slug in catalog:
        for item in catalog[slug]:
            if isinstance(item, tuple):
                problems.append({
                    "title": item[0],
                    "description": item[1],
                    "difficulty": item[2],
                    "starter_code": item[3],
                    "test_cases": item[4],
                    "hints": ["Review basic Python syntax.", "Check test inputs carefully."],
                })
            else:
                problems.append(item)

    # Generate distinct functional challenges to make exactly 50
    actions = [
        ("Compute Sum of Array", "sum(arr)", [("[1, 2, 3]", "6"), ("[10, 20]", "30")]),
        ("Find Minimum Value", "min(arr)", [("[4, 1, 9]", "1"), ("[5, 5]", "5")]),
        ("Find Maximum Value", "max(arr)", [("[4, 1, 9]", "9"), ("[10, -2]", "10")]),
        ("Count Occurrences of Item", "arr.count(target)", [("[1, 2, 1, 1], 1", "3"), ("[4, 5], 9", "0")]),
        ("Check Element In List", "target in arr", [("[1, 2, 3], 2", "True"), ("[4, 5], 1", "False")]),
        ("Reverse Order", "arr[::-1]", [("[1, 2, 3]", "[3, 2, 1]"), ("['a', 'b']", "['b', 'a']")]),
        ("Filter Positive Numbers", "[x for x in arr if x > 0]", [("[-1, 2, -3, 4]", "[2, 4]"), ("[-5]", "[]")]),
        ("Filter Even Numbers", "[x for x in arr if x % 2 == 0]", [("[1, 2, 3, 4]", "[2, 4]"), ("[1, 3]", "[]")]),
        ("Filter Odd Numbers", "[x for x in arr if x % 2 != 0]", [("[1, 2, 3, 4]", "[1, 3]"), ("[2, 4]", "[]")]),
        ("Multiply All by Factor", "[x * k for x in arr]", [("[1, 2, 3], 2", "[2, 4, 6]"), ("[5], 3", "[15]")]),
        ("Calculate List Mean", "round(sum(arr) / len(arr), 2)", [("[2, 4, 6]", "4.0"), ("[1, 2]", "1.5")]),
        ("Find Length of Collection", "len(data)", [("[1, 2, 3]", "3"), ("'hello'", "5")]),
        ("Remove First Element", "arr[1:]", [("[1, 2, 3]", "[2, 3]"), ("[5]", "[]")]),
        ("Remove Last Element", "arr[:-1]", [("[1, 2, 3]", "[1, 2]"), ("[5]", "[]")]),
        ("Check All Greater Than Zero", "all(x > 0 for x in arr)", [("[1, 2, 3]", "True"), ("[-1, 2]", "False")]),
        ("Check Any Greater Than Ten", "any(x > 10 for x in arr)", [("[5, 12, 3]", "True"), ("[1, 2]", "False")]),
        ("Sort Ascending", "sorted(arr)", [("[3, 1, 2]", "[1, 2, 3]"), ("[9, 5]", "[5, 9]")]),
        ("Sort Descending", "sorted(arr, reverse=True)", [("[1, 3, 2]", "[3, 2, 1]"), ("[4, 8]", "[8, 4]")]),
        ("Remove Duplicates", "list(dict.fromkeys(arr))", [("[1, 2, 2, 3]", "[1, 2, 3]"), ("['a', 'a']", "['a']")]),
        ("Get Unique Count", "len(set(arr))", [("[1, 2, 2, 3]", "3"), ("[5, 5, 5]", "1")]),
        ("First Element of Sequence", "arr[0] if arr else None", [("[10, 20]", "10"), ("[]", "None")]),
        ("Last Element of Sequence", "arr[-1] if arr else None", [("[10, 20]", "20"), ("[]", "None")]),
        ("Middle Element of Odd Sequence", "arr[len(arr)//2]", [("[1, 2, 3]", "2"), ("[7, 8, 9, 10, 11]", "9")]),
        ("Cumulative Sum Pair", "[arr[0], arr[0] + arr[1]]", [("[3, 4]", "[3, 7]"), ("[10, 5]", "[10, 15]")]),
        ("Combine Two Lists", "arr1 + arr2", [("[1, 2], [3, 4]", "[1, 2, 3, 4]"), ("[], [5]", "[5]")]),
        ("Zip Two Lists to Dict", "dict(zip(keys, vals))", [("['a', 'b'], [1, 2]", "{'a': 1, 'b': 2}"), ("['x'], [9]", "{'x': 9}")]),
        ("Convert List to Set", "set(arr)", [("[1, 2, 2]", "{1, 2}"), ("[5]", "{5}")]),
        ("Set Union Operation", "set1 | set2", [("{1, 2}, {2, 3}", "{1, 2, 3}"), ("{4}, {5}", "{4, 5}")]),
        ("Set Intersection Operation", "set1 & set2", [("{1, 2}, {2, 3}", "{2}"), ("{1}, {3}", "set()")]),
        ("Set Difference Operation", "set1 - set2", [("{1, 2}, {2, 3}", "{1}"), ("{4, 5}, {4}", "{5}")]),
        ("String Uppercase Converter", "s.upper()", [("'python'", "'PYTHON'"), ("'abc'", "'ABC'")]),
        ("String Lowercase Converter", "s.lower()", [("'HELLO'", "'hello'"), ("'Py'", "'py'")]),
        ("String Strip Whitespace", "s.strip()", [("'  trim  '", "'trim'"), ("' hi '", "'hi'")]),
        ("Check String Starts With", "s.startswith(prefix)", [("'hello', 'he'", "True"), ("'world', 'a'", "False")]),
        ("Check String Ends With", "s.endswith(suffix)", [("'hello', 'lo'", "True"), ("'world', 'x'", "False")]),
        ("String Split by Delimiter", "s.split(delim)", [("'a,b,c', ','", "['a', 'b', 'c']"), ("'x-y', '-'", "['x', 'y']")]),
        ("Join Strings with Hyphen", "'-'.join(arr)", [("['a', 'b', 'c']", "'a-b-c'"), ("['2026', '11']", "'2026-11'")]),
        ("Replace Substring", "s.replace(old, new)", [("'apple', 'p', 'b'", "'abble'"), ("'cat', 'c', 'b'", "'bat'")]),
        ("Find Substring Index", "s.find(sub)", [("'banana', 'na'", "2"), ("'hello', 'z'", "-1")]),
        ("Count Vowels in String", "sum(1 for c in s.lower() if c in 'aeiou')", [("'hello'", "2"), ("'rhythm'", "0")]),
        ("Check Palindrome String", "s.lower() == s.lower()[::-1]", [("'radar'", "True"), ("'code'", "False")]),
        ("Title Case Words", "s.title()", [("'hello world'", "'Hello World'"), ("'python lab'", "'Python Lab'")]),
        ("Is Numeric String", "s.isnumeric()", [("'1234'", "True"), ("'12a3'", "False")]),
        ("Is Alphabetic String", "s.isalpha()", [("'Python'", "True"), ("'Py3'", "False")]),
        ("Format Currency String", "f'${amount:.2f}'", [("15.5", "'$15.50'"), ("100", "'$100.00'")]),
        ("Clamp Value in Range", "max(min_val, min(val, max_val))", [("15, 0, 10", "10"), ("-5, 0, 10", "0")]),
        ("Calculate Distance 2D", "round(((x2-x1)**2 + (y2-y1)**2)**0.5, 2)", [("0, 0, 3, 4", "5.0"), ("1, 1, 4, 5", "5.0")]),
        ("Modulo Arithmetic", "a % b", [("10, 3", "1"), ("25, 5", "0")]),
        ("Check Divisibility", "a % b == 0", [("10, 2", "True"), ("7, 3", "False")]),
        ("Identity Return", "val", [("42", "42"), ("'OK'", "'OK'")]),
    ]

    needed = 50 - len(problems)
    for i in range(needed):
        action_name, expr, tests = actions[i % len(actions)]
        title = f"{name}: {action_name}"
        func_name = f"solve_{slug}_{len(problems) + 1}"

        desc = (
            f"### Challenge: {title}\n\n"
            f"In this lab challenge on **{name}**, write a function `{func_name}` that returns the result of `{action_name}`.\n\n"
            f"### Example\n"
            f"Call: `{func_name}({tests[0][0]})` -> Expected: `{tests[0][1]}`\n\n"
            f"### Constraints\n"
            f"- Execution timeout: 5.0 seconds\n"
            f"- Clean, idiomatic Python 3.10+"
        )

        # Build valid signature and function body
        test_cases = []
        for t in tests:
            test_cases.append({
                "call": f"{func_name}({t[0]})",
                "expected_output": t[1],
                "description": f"Evaluate {action_name}"
            })

        # Match parameters
        param_str = "data"
        if ", " in tests[0][0]:
            args = tests[0][0].split(", ")
            param_names = [f"arg_{j+1}" for j in range(len(args))]
            param_str = ", ".join(param_names)

        starter = f"def {func_name}({param_str}):\n    # Implement {action_name} for {name}\n    return {expr.replace('arr1', 'arg_1').replace('arr2', 'arg_2').replace('arr', 'arg_1' if ', ' in tests[0][0] else 'data')}"

        problems.append({
            "title": title,
            "description": desc,
            "difficulty": "easy" if len(problems) < 25 else "medium" if len(problems) < 40 else "hard",
            "starter_code": starter,
            "test_cases": test_cases,
            "hints": [f"Apply standard Python operations for {name}.", "Ensure edge cases are handled."],
        })

    return problems

def seed_unique():
    db = SessionLocal()
    try:
        topics = db.query(Topic).order_by(Topic.order).all()
        print(f"[*] Seeding unique non-duplicate problems for {len(topics)} topics...")

        for t in topics:
            existing = db.query(PracticeProblem).filter(PracticeProblem.topic_id == t.id).all()
            preserved = [p for p in existing if p.id in (1, 2, 9)]
            
            # Delete repetitive ones
            to_delete = [p for p in existing if p.id not in (1, 2, 9)]
            for p in to_delete:
                db.delete(p)
            db.commit()

            print(f" -> Topic '{t.name}': preserved {len(preserved)} submitted problems. Generating remaining to reach 50...")
            pack = generate_topic_pack(t.slug, t.name)

            needed = 50 - len(preserved)
            for item in pack[:needed]:
                db_prob = PracticeProblem(
                    topic_id=t.id,
                    title=item["title"],
                    description=item["description"],
                    difficulty=item["difficulty"],
                    starter_code=item["starter_code"],
                    test_cases=item["test_cases"],
                    hints=item["hints"],
                    constraints="Time Limit: 5.0 seconds · Memory Limit: 128 MB · Standard Python 3.10+ environment",
                )
                db.add(db_prob)
            db.commit()

            final_count = db.query(PracticeProblem).filter(PracticeProblem.topic_id == t.id).count()
            print(f"    [OK] Topic '{t.name}' now has {final_count} unique problems.")

        total = db.query(PracticeProblem).count()
        print(f"\n[SUCCESS] Seeding complete! Total Practice Problems in DB: {total}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_unique()
