# Sample computationally heavy script with energy anti-patterns
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def matrix_multiply():
    matrix_a = [[1 for _ in range(500)] for _ in range(500)]
    matrix_b = [[2 for _ in range(500)] for _ in range(500)]
    result = []
    for i in range(len(matrix_a)):
        row = []
        for j in range(len(matrix_b[0])):
            val = 0
            for k in range(len(matrix_b)):
                val += matrix_a[i][k] * matrix_b[k][j]
            row.append(val)
        result.append(row)
    return result

if __name__ == '__main__':
    print("Fibonacci:", fibonacci(15))
    print("Done")
