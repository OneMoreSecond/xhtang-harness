#!/usr/bin/env python3
"""Calculate and display the first 30 Fibonacci numbers and their cumulative sum."""


def fibonacci(n: int) -> list[int]:
    """Return the first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]

    fibs = [0, 1]
    for _ in range(2, n):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def cumsum(seq: list[int]) -> list[int]:
    """Return the cumulative sum of a sequence."""
    result = []
    total = 0
    for val in seq:
        total += val
        result.append(total)
    return result


def main() -> None:
    n = 30
    fibs = fibonacci(n)
    sums = cumsum(fibs)
    fib_width = len(str(fibs[-1]))
    sum_width = len(str(sums[-1]))

    print(f"{'n':>3s}  {'Fib(n)':>{fib_width}s}  {'CumSum':>{sum_width}s}")
    print("-" * (3 + 2 + fib_width + 2 + sum_width))
    for i, (f, s) in enumerate(zip(fibs, sums), start=1):
        print(f"{i:3d}  {f:{fib_width}d}  {s:{sum_width}d}")


if __name__ == "__main__":
    main()
