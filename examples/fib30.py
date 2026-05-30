"""Calculate and print the first 30 Fibonacci numbers."""

def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    
    fib = [0, 1]
    for _ in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib


if __name__ == "__main__":
    first_30 = fibonacci(30)
    for i, num in enumerate(first_30):
        print(f"F({i}) = {num}")
