# CP-ABE Performance Benchmark using Charm-Crypto
# This script benchmarks multiple CP-ABE schemes on different elliptic curves.

import time
import json
import numpy as np
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.schemes.abenc.ac17 import AC17CPABE
from charm.schemes.abenc.waters11 import Waters11

def run_benchmark(scheme_class, scheme_name, group_name, max_attributes, num_iterations):
    """
    Runs the benchmark for a specific scheme, pairing group, and number of attributes.

    :param scheme_class: The class of the CP-ABE scheme to benchmark.
    :param scheme_name: The name of the scheme (e.g., 'BSW07').
    :param group_name: The name of the pairing group (e.g., 'SS512').
    :param max_attributes: The maximum number of attributes to test.
    :param num_iterations: The number of times to run each operation for averaging.
    """
    print(f"[*] Starting benchmark for scheme: {scheme_name} on curve: {group_name} ({num_iterations} iterations)")
    group = PairingGroup(group_name)
    
    # Instantiate the correct scheme class
    print(scheme_name)
    if(scheme_name=='ac17'):
        cpabe = scheme_class(group, 2)
    elif(scheme_name=='BSW07'):
        cpabe = scheme_class(group)
    elif(scheme_name=='waters11'):
        cpabe = scheme_class(group, max_attributes)
    
    results = {
        'setup': [],
        'keygen': [],
        'encrypt': [],
        'decrypt': [],
        'attributes': list(range(1, max_attributes + 1)),
        'water11_attributes' :list(range(1, max_attributes + 1))
    }

    # 1. Setup Phase (Averaged over iterations)
    setup_times = []
    for _ in range(num_iterations):
        start_time = time.perf_counter()
        (pk, msk) = cpabe.setup()
        end_time = time.perf_counter()
        setup_times.append((end_time - start_time) * 1000)
    
    avg_setup_time = np.mean(setup_times)
    results['setup'] = [avg_setup_time] * max_attributes # Setup time is constant
    print(f"  - Average Setup time: {avg_setup_time:.2f} ms")

    if(scheme_name=='waters11'):
        temp = results['water11_attributes']
    else:
        temp = results['attributes']
        
    for i in temp:
        attributes = [f'ATTR{j}' for j in range(1, i + 1)]
        water11_attributes = [f'{j}' for j in range(1, i + 1)]
        policy_str = ' and '.join(attributes)
        water11_policy_str = str(' and '.join(water11_attributes))

        # --- Helper function to run and time an operation over N iterations ---
        def time_operation(op_func, num_iter):
            times = []
            for _ in range(num_iter):
                start = time.perf_counter()
                op_func()
                end = time.perf_counter()
                times.append((end - start) * 1000)
            return np.mean(times)

        # 2. Key Generation Phase
        keygen_times = []
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            if(scheme_name=='waters11'):
                sk_water11 = cpabe.keygen(pk, msk, water11_attributes)
            else:
                sk = cpabe.keygen(pk, msk, attributes)
            end_time = time.perf_counter()
            keygen_times.append((end_time - start_time) * 1000)
        avg_keygen_time = np.mean(keygen_times)
        results['keygen'].append(avg_keygen_time)
        print(f"  - KeyGen with {i} attributes: {avg_keygen_time:.2f} ms")

        # Pre-generate the secret key for encryption/decryption tests to avoid re-running keygen
        if(scheme_name=='waters11'):
            sk_water11 = cpabe.keygen(pk, msk, water11_attributes)
        else:
            sk = cpabe.keygen(pk, msk, attributes)

        # 3. Encryption Phase
        encrypt_times = []
        for _ in range(num_iterations):
            msg = group.random(GT)
            start_time = time.perf_counter()
            if(scheme_name=='waters11'):
                ciphertext = cpabe.encrypt(pk, msg, water11_policy_str)
            else:
                ciphertext = cpabe.encrypt(pk, msg, policy_str)
            end_time = time.perf_counter()
            encrypt_times.append((end_time - start_time) * 1000)
        avg_encrypt_time = np.mean(encrypt_times)
        results['encrypt'].append(avg_encrypt_time)
        print(f"  - Encrypt with {i} attributes: {avg_encrypt_time:.2f} ms")

        # 4. Decryption Phase
        # Pre-encrypt a message to test decryption speed consistently
        final_msg = group.random(GT)
        if(scheme_name=='waters11'):
            final_ciphertext = cpabe.encrypt(pk, final_msg, water11_policy_str)
        else:
            final_ciphertext = cpabe.encrypt(pk, final_msg, policy_str)
            
        decrypt_times = []
        for _ in range(num_iterations):
            start_time = time.perf_counter()
            if(scheme_name=='ac17'):
                decrypted_msg = cpabe.decrypt(pk, final_ciphertext, sk)
            elif(scheme_name=='waters11'):
                decrypted_msg = cpabe.decrypt(pk, final_ciphertext, sk_water11)
            elif(scheme_name=='BSW07'):
                decrypted_msg = cpabe.decrypt(pk, sk, final_ciphertext)
            end_time = time.perf_counter()
            decrypt_times.append((end_time - start_time) * 1000)
        
        avg_decrypt_time = np.mean(decrypt_times)
        results['decrypt'].append(avg_decrypt_time)
        print(f"  - Decrypt with {i} attributes: {avg_decrypt_time:.2f} ms")

        # Verify correctness once
        if decrypted_msg != final_msg:
            print(f"Decryption failed for {scheme_name} on {group_name} with {i} attributes!")

    # Save results to a file named after the scheme and curve
    output_filename = f'benchmark_results_{scheme_name}_{group_name}.json'
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"[*] Benchmark results for {scheme_name} on {group_name} saved to {output_filename}\n")


if __name__ == '__main__':
    # --- User Input ---
    while True:
        try:
            MAX_ATTR = int(input("Enter the maximum number of attributes to test (e.g., 30): "))
            if MAX_ATTR > 0:
                break
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
            
    while True:
        try:
            NUM_ITERATIONS = int(input("Enter the number of iterations for each operation (e.g., 10): "))
            if NUM_ITERATIONS > 0:
                break
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
    
    # Define the schemes and curves to benchmark
    schemes = {
        'BSW07': CPabe_BSW07,
        'ac17': AC17CPABE,
        'waters11': Waters11
    }
    curves = ['SS512', 'MNT159']

    # Run the benchmark for each combination
    for s_name, s_class in schemes.items():
        for curve in curves:
            run_benchmark(s_class, s_name, curve, MAX_ATTR, NUM_ITERATIONS)

    print("[*] All benchmarks complete.")

