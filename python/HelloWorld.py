def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}! Welcome to Python."

def main():
    print("=" * 40)
    print("Welcome to Hello World Application")
    print("=" * 40)
    
    name = input("What is your name? ")
    message = greet(name)
    print(message)
    print("=" * 40)

if __name__ == "__main__":
    main()
