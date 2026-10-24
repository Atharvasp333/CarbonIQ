"""
Sample compute-intensive workload for testing CarbonIQ CLI.
This script performs some CPU-intensive calculations.
"""

import time
import math

def compute_pi(iterations=10000000):
    """Compute pi using Monte Carlo method."""
    inside_circle = 0
    total_points = iterations
    
    for i in range(total_points):
        x = (i * 1234567) % 10000 / 10000.0
        y = (i * 7654321) % 10000 / 10000.0
        
        if x*x + y*y <= 1:
            inside_circle += 1
    
    return 4 * inside_circle / total_points

def fibonacci(n):
    """Calculate fibonacci numbers."""
    if n <= 1:
        return n
    
    fib = [0, 1]
    for i in range(2, n + 1):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib[n]

def prime_factorization(n):
    """Find prime factors of a number."""
    factors = []
    d = 2
    while d * d <= n:
        while (n % d) == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def main():
    print("🔢 Starting compute-intensive workload...")
    print("="*60)
    
    # Task 1: Compute Pi
    print("\n1. Computing Pi using Monte Carlo method...")
    start = time.time()
    pi_estimate = compute_pi(5000000)
    elapsed = time.time() - start
    print(f"   Pi estimate: {pi_estimate:.6f}")
    print(f"   Time taken: {elapsed:.2f}s")
    
    # Task 2: Fibonacci
    print("\n2. Computing large Fibonacci number...")
    start = time.time()
    fib_40 = fibonacci(50000)
    elapsed = time.time() - start
    print(f"   Fib(50000) has {len(str(fib_40))} digits")
    print(f"   Time taken: {elapsed:.2f}s")
    
    # Task 3: Prime factorization
    print("\n3. Prime factorization of large numbers...")
    start = time.time()
    numbers = [123456789, 987654321, 1122334455]
    for num in numbers:
        factors = prime_factorization(num)
        print(f"   {num} = {' × '.join(map(str, factors))}")
    elapsed = time.time() - start
    print(f"   Time taken: {elapsed:.2f}s")
    
    # Task 4: Matrix operations (manual)
    print("\n4. Matrix multiplication (manual)...")
    start = time.time()
    size = 200
    matrix_a = [[i + j for j in range(size)] for i in range(size)]
    matrix_b = [[i * j for j in range(size)] for i in range(size)]
    
    # Simple matrix multiplication
    result = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]
    
    elapsed = time.time() - start
    print(f"   {size}x{size} matrix multiplication completed")
    print(f"   Time taken: {elapsed:.2f}s")
    
    print("\n" + "="*60)
    print("✅ Workload completed!")

if __name__ == "__main__":
    main()
