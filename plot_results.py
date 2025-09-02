# Script to Plot CP-ABE Benchmark Results
# Reads JSON data from the benchmark script and generates separate,
# publication-quality graphs for each cryptographic operation.

import json
import matplotlib.pyplot as plt
import numpy as np
import os

def load_results(filename):
    """Loads benchmark results from a JSON file."""
    if not os.path.exists(filename):
        print(f"Warning: The file {filename} was not found. Skipping.")
        return None
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {filename}. Skipping.")
        return None

def plot_comparison_graphs(results, schemes, curves):
    """
    Generates and saves a separate plot for each operation.
    """
    if not results:
        print("Cannot generate plots due to missing data.")
        return

    # Define operations to plot
    operations = {
        'keygen': 'Key Generation Performance Comparison',
        'encrypt': 'Encryption Performance Comparison',
        'decrypt': 'Decryption Performance Comparison'
    }

    # Define plotting styles to differentiate schemes and curves
    markers = ['o', 's', '^', 'D', 'v', 'p']
    linestyles = ['-', '--', ':', '-.']
    
    plt.style.use('seaborn-v0_8-deep')

    for op_key, title in operations.items():
        # Create a new figure for each operation
        plt.figure(figsize=(12, 8))
        ax = plt.gca()
        
        scheme_markers = {s_name: markers[i] for i, s_name in enumerate(schemes)}
        curve_styles = {c_name: linestyles[i] for i, c_name in enumerate(curves)}

        for s_name in schemes:
            for curve in curves:
                result_key = f"{s_name}_{curve}"
                if result_key in results and results[result_key]:
                    data = results[result_key]
                    attributes = data['attributes']
                    times = data[op_key]
                    label = f"{s_name} ({curve})"
                    
                    marker = scheme_markers.get(s_name, 'x')
                    linestyle = curve_styles.get(curve, '-')
                    
                    ax.plot(attributes, times, marker=marker, linestyle=linestyle, label=label, markersize=5)
        
        ax.set_xlabel('Number of Attributes', fontsize=14)
        ax.set_ylabel('Time (milliseconds, log scale)', fontsize=14)
        ax.set_title(title, fontsize=18, pad=15)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(fontsize=12)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_yscale('log')

        plt.tight_layout()
        
        # Save figure to separate PDF and PNG files
        pdf_filename = f'cp-abe-{op_key}-performance.pdf'
        png_filename = f'cp-abe-{op_key}-performance.png'
        plt.savefig(pdf_filename, bbox_inches='tight')
        plt.savefig(png_filename, dpi=300, bbox_inches='tight')
        print(f"[*] Saved graph to {pdf_filename} and {png_filename}")
        plt.close() # Close the figure to free up memory before creating the next one

if __name__ == '__main__':
    schemes_to_test = ['BSW07', 'ac17', 'waters11']
    curves_to_test = ['SS512', 'MNT159']
    all_results = {}

    for s_name in schemes_to_test:
        for curve in curves_to_test:
            filename = f'benchmark_results_{s_name}_{curve}.json'
            data = load_results(filename)
            if data:
                all_results[f"{s_name}_{curve}"] = data
    
    if all_results:
        plot_comparison_graphs(all_results, schemes_to_test, curves_to_test)
    else:
        print("No benchmark data found. Please run the benchmark.py script first.")

