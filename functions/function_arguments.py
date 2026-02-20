# Function arguments: positional and default

def introduce(name, age=17):
    """
    Returns information about a person (name; age (default 17))
    """
    print(f"Name: {name}, Age: {age}")

introduce("Askar", 17)
introduce("Tair")