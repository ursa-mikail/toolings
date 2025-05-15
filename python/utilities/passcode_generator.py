import base64
import secrets
import string
import sys
import math
import string

# Base58 Alphabet (Bitcoin's)
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def generate_hex(length: int) -> str:
    return secrets.token_hex(length)

def generate_base64(length: int) -> str:
    raw = secrets.token_bytes(length)
    return base64.b64encode(raw).decode('utf-8')[:length]

def generate_base58(length: int) -> str:
    return ''.join(secrets.choice(BASE58_ALPHABET) for _ in range(length))

def generate_ascii(length: int) -> str:
    ascii_chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(ascii_chars) for _ in range(length))

def generate_numbers(length: int) -> str: 
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def menu():
    print("\n=== Passcode Generator ===")
    print("1. Generate Hexadecimal Passcode")
    print("2. Generate Base64 Passcode")
    print("3. Generate Base58 Passcode")
    print("4. Generate ASCII (keyboard) Passcode")
    print("5. Generate Numbers Passcode")
    print("6. Exit")

def get_length():
    while True:
        try:
            length = int(input("Enter desired length: "))
            if length > 0:
                return length
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def password_strength(password: str) -> str:
    length = len(password)
    categories = {
        'lower': any(c in string.ascii_lowercase for c in password),
        'upper': any(c in string.ascii_uppercase for c in password),
        'digit': any(c in string.digits for c in password),
        'symbol': any(c in string.punctuation for c in password),
    }
    
    # Count how many character sets are used
    variety_score = sum(categories.values())
    
    # Entropy estimation: log2(possible symbols ^ length)
    possible_chars = 0
    if categories['lower']: possible_chars += 26
    if categories['upper']: possible_chars += 26
    if categories['digit']: possible_chars += 10
    if categories['symbol']: possible_chars += len(string.punctuation)
    
    entropy = length * math.log2(possible_chars) if possible_chars > 0 else 0

    # Strength thresholds (based on entropy bits)
    if entropy < 40:
        strength = "Weak"
    elif entropy < 60:
        strength = "Moderate"
    elif entropy < 80:
        strength = "Strong"
    else:
        strength = "Very Strong"

    # Optional: Verbose output
    print(f"\nPasscode: {password}")
    print("==========================================")
    print(f"Length: {length}")
    print(f"Character Categories Used: {list(k for k, v in categories.items() if v)}")
    print(f"Entropy Estimate: {entropy:.2f} bits")
    print(f"Password Strength: {strength}\n")

    return strength

def main():
    while True:
        menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == '1':
            length = get_length()
            if length % 2 != 0:
                print("Hex requires even length (each byte = 2 hex chars). Rounding up.")
                length += 1
            print("Hex Passcode:", passcode := generate_hex(length))

        elif choice == '2':
            length = get_length()
            print("Base64 Passcode:", passcode := generate_base64(length))

        elif choice == '3':
            length = get_length()
            print("Base58 Passcode:", passcode := generate_base58(length))

        elif choice == '4':
            length = get_length()
            print("ASCII Passcode:", passcode := generate_ascii(length))

        elif choice == '5':
            length = get_length()
            print("Numbers Passcode:", passcode := generate_numbers(length))

        elif choice == '6':
            print("Exiting...")
            # sys.exit(0)
            break
        else:
            print("Invalid choice. Try again.")

        password_strength(passcode)

if __name__ == "__main__":
    main()

"""
=== Passcode Generator ===
1. Generate Hexadecimal Passcode
2. Generate Base64 Passcode
3. Generate Base58 Passcode
4. Generate ASCII (keyboard) Passcode
5. Generate Numbers Passcode
6. Exit
Choose an option (1-5): 1
Enter desired length: 8
Hex Passcode: 26bfa4139fd7cedd

Passcode: 26bfa4139fd7cedd
==========================================
Length: 16
Character Categories Used: ['lower', 'digit']
Entropy Estimate: 82.72 bits
Password Strength: Very Strong


=== Passcode Generator ===
1. Generate Hexadecimal Passcode
2. Generate Base64 Passcode
3. Generate Base58 Passcode
4. Generate ASCII (keyboard) Passcode
5. Generate Numbers Passcode
6. Exit
Choose an option (1-5): 4
Enter desired length: 10
ASCII Passcode: #%xWpz_)Ry

Passcode: #%xWpz_)Ry
==========================================
Length: 10
Character Categories Used: ['lower', 'upper', 'symbol']
Entropy Estimate: 63.92 bits
Password Strength: Strong


=== Passcode Generator ===
1. Generate Hexadecimal Passcode
2. Generate Base64 Passcode
3. Generate Base58 Passcode
4. Generate ASCII (keyboard) Passcode
5. Generate Numbers Passcode
6. Exit
Choose an option (1-5): 6
Exiting...
"""