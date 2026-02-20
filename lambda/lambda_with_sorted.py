# sorted() + lambda

students = [
    ("Askar", 90),
    ("Tair", 85),
    ("Adilkhan", 95)
]

# Sort by score
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)