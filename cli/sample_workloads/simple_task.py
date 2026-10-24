"""
Simple quick workload for testing CarbonIQ CLI.
"""

import time

def main():
    print("Starting simple task...")
    
    # Do some simple computation
    total = 0
    for i in range(1000000):
        total += i
    
    print(f"Sum of first 1,000,000 numbers: {total}")
    
    # Small sleep to ensure measurable duration
    time.sleep(2)
    
    print("Task completed!")

if __name__ == "__main__":
    main()
