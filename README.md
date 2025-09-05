# **🚀 CP-ABE Benchmarking and Visualization Toolkit**

## **🔑 Overview**
This repository provides a complete toolkit to **benchmark Ciphertext-Policy Attribute-Based Encryption (CP-ABE) schemes** using [Charm-Crypto](https://github.com/JHUISI/charm) and to **visualize performance results** with publication-quality graphs.  

It includes:
- **Benchmarking Script** → Runs CP-ABE schemes (BSW07, AC17, Waters11) on two pairing curves ('SS512', 'MNT159').  
- **Graphing Script** → Generates comparative performance graphs from benchmark results.  

---

## **📂 Project Structure**
- `benchmark_cpabe.py` → Benchmarks CP-ABE schemes and saves results as JSON  
- `plot_results.py` → Loads JSON results and generates performance graphs  
- `README.md` → Documentation  

---

## **✨ Features**
- ⚙️ **Setup**: Initialize schemes with pairing groups  
- 🔑 **Key Generation**: Test performance for increasing attribute sizes  
- 🔒 **Encryption**: Benchmark encryption under policies  
- 🔓 **Decryption**: Measure decryption performance and correctness  
- 📊 **Graphs**: Log-scale plots for keygen, encryption, and decryption  

---
## **🛠 Requirements & Installation**

This project requires **<Python 3.10**, [Charm-Crypto](https://github.com/JHUISI/charm), and the **PBC library**.  
Follow the steps below to set up the environment:

### 1. Install system dependencies
```bash
sudo apt update
sudo apt install -y \
    build-essential python3 python3-dev python3-pip \
    libgmp-dev libssl-dev libmpfr-dev libmpc-dev \
    flex bison autoconf automake libtool \
    git
```
### 2. Install the PBC library
```
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xvf pbc-0.5.14.tar.gz
cd pbc-0.5.14
./configure
make
sudo make install
sudo ldconfig
cd ..
```
### 3. Install Charm-Crypto
```bash
git clone https://github.com/JHUISI/charm.git
cd charm
./configure.sh
make
sudo make install
cd ..
```
### 4. (Optional) Create a virtual environment
```bash
sudo apt install python3.12-venv
python3 -m venv charm-env
source charm-env/bin/activate
```
### 5. Install Python dependencies
```bash
pip install pycryptodome numpy matplotlib
```
---

## **⚡ How to Run Benchmarks**
1. Clone the repository:
   ```bash
   cd charm
   git clone https://github.com/your-username/cpabe-benchmarking.git
   cd cpabe-benchmarking
   benchmark_cpabe.py
   plot_results.py 
