import time
import random
import csv

def system_under_test(k, N, scale_factor):
    """
    Simulate the system behavior.
    Replace this with the actual benchmarking logic.
    """
    time.sleep(0.01 * scale_factor)  # Placeholder for system logic under test
    return random.random() < (k / N)  # Simulated success condition

def benchmark(k_values, N, scale_factors, output_file="results.csv"):
    results = []
    for k in k_values:
        for scale in scale_factors:
            start_time = time.time()
            
            # Run the test for the current (k, N, scale)
            success = system_under_test(k, N, scale)
            
            elapsed_time = time.time() - start_time
            results.append((k, N, scale, elapsed_time, success))
            print(f"Test (k={k}, N={N}, scale={scale}): Time={elapsed_time:.4f}s, Success={success}")
    
    # Save results to CSV for later analysis
    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["k", "N", "Scale", "Time", "Success"])
        writer.writerows(results)

if __name__ == "__main__":
    # System Parameters
    N = 10  # Total systems
    k_values = [int(p * N) for p in [0.1, 0.2, 0.3, 0.4]]  # k/N ratios
    scale_factors = list(range(1, 51))  # 1x to 50x load

    benchmark(k_values, N, scale_factors)

"""
Test (k=1, N=10, scale=1): Time=0.0101s, Success=False
Test (k=1, N=10, scale=2): Time=0.0201s, Success=False
Test (k=1, N=10, scale=3): Time=0.0301s, Success=False
Test (k=1, N=10, scale=4): Time=0.0401s, Success=False
Test (k=1, N=10, scale=5): Time=0.0501s, Success=True
Test (k=1, N=10, scale=6): Time=0.0608s, Success=False
Test (k=1, N=10, scale=7): Time=0.0701s, Success=False
Test (k=1, N=10, scale=8): Time=0.0801s, Success=True
Test (k=1, N=10, scale=9): Time=0.0901s, Success=False
:
Test (k=4, N=10, scale=44): Time=0.4402s, Success=False
Test (k=4, N=10, scale=45): Time=0.4502s, Success=True
Test (k=4, N=10, scale=46): Time=0.4602s, Success=False
Test (k=4, N=10, scale=47): Time=0.4702s, Success=False
Test (k=4, N=10, scale=48): Time=0.4802s, Success=True
Test (k=4, N=10, scale=49): Time=0.4902s, Success=False
Test (k=4, N=10, scale=50): Time=0.5002s, Success=True
"""