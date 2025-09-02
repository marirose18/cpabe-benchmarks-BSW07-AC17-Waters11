# CP-ABE Performance Benchmark using Charm-Crypto
# This script benchmarks multiple CP-ABE schemes on different elliptic curves.

import time
import json
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.schemes.abenc.ac17 import AC17CPABE
from charm.schemes.abenc.waters11 import Waters11

def run_benchmark(scheme_class, scheme_name, group_name, max_attributes):
    """
    Runs the benchmark for a specific scheme, pairing group, and number of attributes.

    :param scheme_class: The class of the CP-ABE scheme to benchmark.
    :param scheme_name: The name of the scheme (e.g., 'BSW07').
    :param group_name: The name of the pairing group (e.g., 'SS512').
    :param max_attributes: The maximum number of attributes to test.
    """
    print(f"[*] Starting benchmark for scheme: {scheme_name} on curve: {group_name}")
    group = PairingGroup(group_name)
    
    # Instantiate the correct scheme class
    print(scheme_name)
    if(scheme_name=='ac17'):
    	cpabe = scheme_class(group,2)
    if(scheme_name=='BSW07'):
    	cpabe = scheme_class(group)
    if(scheme_name=='waters11'):
    	cpabe = scheme_class(group,max_attributes)
    results = {
        'setup': [],
        'keygen': [],
        'encrypt': [],
        'decrypt': [],
        'attributes': list(range(1, max_attributes + 1)),
        'water11_attributes' :list(range(1, max_attributes + 1))
    }

    # 1. Setup Phase
    start_time = time.perf_counter()
    # Note: AW11 setup returns (pk, msk), other schemes might differ if they were multi-authority
    (pk, msk) = cpabe.setup()
    end_time = time.perf_counter()
    setup_time = (end_time - start_time) * 1000  # Convert to milliseconds
    results['setup'] = [setup_time] * max_attributes # Setup time is constant
    print(f"  - Setup time: {setup_time:.2f} ms")
    if(scheme_name=='waters11'):
    	temp=results['water11_attributes']
    else:
    	temp=results['attributes']
    for i in temp:
        attributes = [f'ATTR{j}' for j in range(1, i + 1)]
        water11_attributes=[f'{j}' for j in range(1, i + 1)]
        print(water11_attributes)
        policy_str = ' and '.join(attributes)
        water11_policy_str=str(' and '.join(water11_attributes))
        print(type(water11_policy_str))
        # 2. Key Generation Phase
        start_time = time.perf_counter()
        if(scheme_name=='waters11'):
             sk_water11 = cpabe.keygen(pk, msk, water11_attributes)
        else:
             sk = cpabe.keygen(pk, msk, attributes)
        end_time = time.perf_counter()
        keygen_time = (end_time - start_time) * 1000
        results['keygen'].append(keygen_time)
        print(f"  - KeyGen with {i} attributes: {keygen_time:.2f} ms")

        # 3. Encryption Phase
        msg = group.random(GT)
        start_time = time.perf_counter()
        if(scheme_name=='waters11'):
             ciphertext = cpabe.encrypt(pk, msg, water11_policy_str)
        else:
             ciphertext = cpabe.encrypt(pk, msg, policy_str)
        end_time = time.perf_counter()
        encrypt_time = (end_time - start_time) * 1000
        results['encrypt'].append(encrypt_time)
        print(f"  - Encrypt with {i} attributes: {encrypt_time:.2f} ms")

        # 4. Decryption Phase
        start_time = time.perf_counter()
        if(scheme_name=='ac17'):
            decrypted_msg = cpabe.decrypt(pk, ciphertext, sk)
        if(scheme_name=='waters11'):
            decrypted_msg = cpabe.decrypt(pk, ciphertext, sk_water11)
        if(scheme_name=='BSW07'):
    	    decrypted_msg = cpabe.decrypt(pk, sk, ciphertext)
        end_time = time.perf_counter()
        decrypt_time = (end_time - start_time) * 1000
        results['decrypt'].append(decrypt_time)
        print(f"  - Decrypt with {i} attributes: {decrypt_time:.2f} ms")

        # Verify correctness
        if decrypted_msg != msg:
            print(f"Decryption failed for {scheme_name} on {group_name} with {i} attributes!")

    # Save results to a file named after the scheme and curve
    output_filename = f'benchmark_results_{scheme_name}_{group_name}.json'
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"[*] Benchmark results for {scheme_name} on {group_name} saved to {output_filename}\n")


if __name__ == '__main__':
    MAX_ATTR = 30  # Maximum number of attributes to test
    
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
            run_benchmark(s_class, s_name, curve, MAX_ATTR)

    print("[*] All benchmarks complete.")

