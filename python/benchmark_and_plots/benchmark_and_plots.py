#!pip install pycryptodome

import time
import psutil
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Protocol.KDF import scrypt

"""
# Helper function to profile a given function
def profile_func(func, *args, **kwargs):
    process = psutil.Process()
    start_time = time.time()
    start_cpu = process.cpu_percent(interval=None)
    start_mem = process.memory_info().rss     # RSS (Resident Set Size)

    result = func(*args, **kwargs)

    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)
    end_mem = process.memory_info().rss

    elapsed_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    mem_usage = end_mem - start_mem

    return elapsed_time, cpu_usage, mem_usage
"""

import tracemalloc

def profile_func(func, *args, **kwargs):
    process = psutil.Process()
    start_time = time.time()
    start_cpu = process.cpu_percent(interval=None)
    
    tracemalloc.start()  # Start tracking memory
    func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()  # Get memory usage
    tracemalloc.stop()  # Stop tracking memory

    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)

    elapsed_time = end_time - start_time
    cpu_usage = end_cpu - start_cpu
    mem_usage = peak - current  # Use peak memory usage

    return elapsed_time, cpu_usage, mem_usage

"""
 ____                  _                          _           _                   
| __ )  ___ _ __   ___| |__  _ __ ___   __ _ _ __| | __      / \   _ __ ___  __ _ 
|  _ \ / _ \ '_ \ / __| '_ \| '_ ` _ \ / _` | '__| |/ /     / _ \ | '__/ _ \/ _` |
| |_) |  __/ | | | (__| | | | | | | | | (_| | |  |   <     / ___ \| | |  __/ (_| |
|____/ \___|_| |_|\___|_| |_|_| |_| |_|\__,_|_|  |_|\_\   /_/   \_\_|  \___|\__,_|
                                                                               
"""
# Benchmarking functions for each algorithm
def benchmark_ed25519():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking Ed25519"
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

def benchmark_ed448():
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking Ed448"
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA384()))
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA384()))

def benchmark_secp256r1():
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking secp256r1"
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

def benchmark_secp256k1():
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking secp256k1"
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))

def benchmark_secp384r1():
    private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking secp384r1"
    signature = private_key.sign(data, ec.ECDSA(hashes.SHA384()))
    public_key.verify(signature, data, ec.ECDSA(hashes.SHA384()))

def benchmark_rsa_pss():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking RSA-PSS"
    signature = private_key.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    public_key.verify(signature, data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

def benchmark_rsa_PKCS1v15():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    data = b"Benchmarking RSA-PKCS1v15"
    signature = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend

def benchmark_rsa_oaep():
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Obtain the public key
    public_key = private_key.public_key()

    # Data to be signed and encrypted
    data = b"Benchmarking RSA-OAEP"

    # Sign the data
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Verify the signature
    public_key.verify(
        signature,
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Encrypt the data using RSA-OAEP
    ciphertext = public_key.encrypt(
        data,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the data using RSA-OAEP
    plaintext = private_key.decrypt(
        ciphertext,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Output the results
    print(f"Original Data: {data}")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Decrypted Data: {plaintext}")

def benchmark_aes_gcm_128():
    key = b'\x00' * 16
    iv = b'\x00' * 12
    data = b"Benchmarking AES-GCM-128"
    additional_data = b""

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(additional_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag

    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    decryptor.authenticate_additional_data(additional_data)
    decryptor.update(ciphertext) + decryptor.finalize()

def benchmark_aes_gcm_256():
    key = b'\x00' * 32
    iv = b'\x00' * 12
    data = b"Benchmarking AES-GCM-256"
    additional_data = b""

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(additional_data)
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag

    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    decryptor.authenticate_additional_data(additional_data)
    decryptor.update(ciphertext) + decryptor.finalize()


def benchmark_chacha20_poly1305():
    key = b'\x00' * 32
    nonce = b'\x00' * 12
    data = b"Benchmarking Chacha20_Poly1305"
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)

def benchmark_hmac_sha256():
    key = b'\x00' * 32
    data = b"Benchmarking HMAC-SHA256"
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    h.finalize()

def benchmark_hmac_sha384():
    key = b'\x00' * 32
    data = b"Benchmarking HMAC-SHA384"
    h = hmac.HMAC(key, hashes.SHA384(), backend=default_backend())
    h.update(data)
    h.finalize()

def benchmark_hmac_sha512():
    key = b'\x00' * 32
    data = b"Benchmarking HMAC-SHA512"
    h = hmac.HMAC(key, hashes.SHA512(), backend=default_backend())
    h.update(data)
    h.finalize()

def benchmark_hmac_poly1305():
    key = b'\x00' * 32
    data = b"Benchmarking HMAC-Poly1305"
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    h.finalize()


"""
 _   _                      
| | | |___  __ _  __ _  ___ 
| | | / __|/ _` |/ _` |/ _ \
| |_| \__ \ (_| | (_| |  __/
 \___/|___/\__,_|\__, |\___|
                 |___/      
"""
# List of benchmarks to run
benchmarks = [
    ("Ed25519", benchmark_ed25519),
    ("Ed448", benchmark_ed448),
    ("secp256r1", benchmark_secp256r1),
    ("secp256k1", benchmark_secp256k1),
    ("secp384r1", benchmark_secp384r1),
    ("RSA-PSS", benchmark_rsa_pss),
    ("RSA-PKCS1v15", benchmark_rsa_PKCS1v15),
    ("RSA-OAEP", benchmark_rsa_oaep),
    ("AES-GCM-128", benchmark_aes_gcm_128),
    ("AES-GCM-256", benchmark_aes_gcm_256),
    ("Chacha20_Poly1305", benchmark_chacha20_poly1305),
    ("HMAC-SHA256", benchmark_hmac_sha256),
    ("HMAC-SHA384", benchmark_hmac_sha384),
    ("HMAC-SHA512", benchmark_hmac_sha512),
    ("HMAC-Poly1305", benchmark_hmac_poly1305),
]

# Run benchmarks and collect results
results = []
for name, func in benchmarks:
    elapsed_time, cpu_usage, mem_usage = profile_func(func)
    print(f"name, elapsed_time, cpu_usage, mem_usage: [{name}]: {elapsed_time}, {cpu_usage}, {mem_usage}") # {elapsed_time:.3f}
    results.append((name, elapsed_time, cpu_usage, mem_usage))

# Plotting the results
def plot_results(results):
    names = [r[0] for r in results]
    times = [r[1] for r in results]
    cpus = [r[2] for r in results]
    mems = [r[3] for r in results]

    # Create a wider and taller figure
    fig, ax1 = plt.subplots(figsize=(14, 8))  # Width 14, Height 8
    #fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Algorithm')
    ax1.set_ylabel('Time (s)', color=color)
    ax1.bar(names, times, color=color, alpha=0.6, label='Time (s)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis='x', labelrotation=45)

    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('CPU Usage (%)', color=color)
    ax2.plot(names, cpus, color=color, marker='o', label='CPU Usage (%)')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.tick_params(axis='x', labelrotation=45)

    ax3 = ax1.twinx()
    color = 'tab:red'
    ax3.spines['right'].set_position(('outward', 60))
    ax3.set_ylabel('Memory Usage (bytes)', color=color)
    ax3.plot(names, mems, color=color, marker='x', linestyle='dashed', label='Memory Usage (bytes)')
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.tick_params(axis='x', labelrotation=45)

    fig.tight_layout()
    plt.title('Cryptographic Algorithm Benchmarking')
    fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.xticks(rotation=45)
    plt.show()

plot_results(results)

"""
[Sample output]
name, elapsed_time, cpu_usage, mem_usage: [Ed25519]: 0.0007300376892089844, 0.0, 684
name, elapsed_time, cpu_usage, mem_usage: [Ed448]: 0.001539468765258789, 0.0, 721
name, elapsed_time, cpu_usage, mem_usage: [secp256r1]: 0.0005204677581787109, 0.0, 685
name, elapsed_time, cpu_usage, mem_usage: [secp256k1]: 0.002115488052368164, 0.0, 683
name, elapsed_time, cpu_usage, mem_usage: [secp384r1]: 0.0014262199401855469, 0.0, 720
name, elapsed_time, cpu_usage, mem_usage: [RSA-PSS]: 0.09598159790039062, 104.1, 1042
name, elapsed_time, cpu_usage, mem_usage: [RSA-PKCS1v15]: 0.033583641052246094, 89.2, 866
Original Data: b'Benchmarking RSA-OAEP'
Ciphertext: 42230bf8221b7912d4adafd6724c95b97c35b39d7244e715d82c386950fd4b670d556e2c378906c23493c9770afd098aa1c207bab32de9ce184dbebeeec83062ea012139b45a511b600e8146160da36607a27e48ecad767f36104875d6b65e659dacc73aca34c61ec09a1c18c48797ec54cf50407aad63c5d75fc71e45783ee25f40d835403ba240ecc9f24a7cb4bf8be3e21233d32ffe72a8deec13a2347e1886d4d46eeb65f59f0edbebeee58fd52b8716efa1a1c60ee1f4121bf37138b83e992edebfd4a1c9bdc16ac53d26a4d33a26d2713bb4f818004e97d971db6f71dde7c312a1b203a865d26e292fa6a64363a87ccb3a902162a4f26b4a5118115557
Decrypted Data: b'Benchmarking RSA-OAEP'
name, elapsed_time, cpu_usage, mem_usage: [RSA-OAEP]: 0.23441195487976074, 102.4, 928
name, elapsed_time, cpu_usage, mem_usage: [AES-GCM-128]: 0.0008504390716552734, 0.0, 1162
name, elapsed_time, cpu_usage, mem_usage: [AES-GCM-256]: 0.000701904296875, 0.0, 1162
name, elapsed_time, cpu_usage, mem_usage: [Chacha20_Poly1305]: 0.0005667209625244141, 0.0, 1447
name, elapsed_time, cpu_usage, mem_usage: [HMAC-SHA256]: 0.0001499652862548828, 0.0, 384
name, elapsed_time, cpu_usage, mem_usage: [HMAC-SHA384]: 0.0001773834228515625, 0.0, 384
name, elapsed_time, cpu_usage, mem_usage: [HMAC-SHA512]: 0.0001308917999267578, 0.0, 384
name, elapsed_time, cpu_usage, mem_usage: [HMAC-Poly1305]: 0.00012493133544921875, 0.0, 384



"""