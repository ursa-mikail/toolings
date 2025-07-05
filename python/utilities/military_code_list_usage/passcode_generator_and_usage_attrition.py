import random
import string
import time

PASSWORD_FILE = "passwords.txt"
NUM_PASSWORDS = 10
PASSWORD_LENGTH = 8

RED = "\033[31m"
BLUE = "\033[34m"
RESET = "\033[0m"

# Generate a list of random passwords
def generate_passwords(n, length):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return [''.join(random.choices(chars, k=length)) for _ in range(n)]

# Write passwords to file
def write_passwords_to_file(passwords, filename):
    with open(filename, "w") as f:
        f.write("\n".join(passwords) + "\n")

# Display color diff
def show_color_diff(prev_list, current_list):
    removed = set(prev_list) - set(current_list)
    print("List after removal:")
    for pwd in prev_list:
        if pwd in removed:
            print(f"{RED}- {pwd}{RESET}")
        else:
            print(f"{BLUE}+ {pwd}{RESET}")
    print("=" * 40)

# Try passwords and remove each one with progress
def try_passwords_and_remove(filename):
    with open(filename, "r") as f:
        passwords = f.read().splitlines()

    total = len(passwords)
    attempts = 0

    while passwords:
        current_pwd = passwords[0]
        attempts += 1
        print(f"\n🔐 Trying password: {current_pwd}")
        print(f"Progress: {attempts} of {total} used | Remaining: {total - attempts}")

        prev_passwords = passwords.copy()
        passwords.pop(0)

        show_color_diff(prev_passwords, passwords)

        with open(filename, "w") as f:
            f.write("\n".join(passwords) + "\n")

        time.sleep(0.3)

    print(f"\n✅ All {total} passwords tried and removed.")

# === Main Entry ===
if __name__ == "__main__":
    pwds = generate_passwords(NUM_PASSWORDS, PASSWORD_LENGTH)
    write_passwords_to_file(pwds, PASSWORD_FILE)
    #try_passwords_and_remove(PASSWORD_FILE)

