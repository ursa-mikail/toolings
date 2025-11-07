#!pip install python-dotenv

import os, random
from os.path import join, dirname
from dotenv import load_dotenv


def generate_random_hex_string(length):
    """
    Generate a random hexadecimal string of the specified length.
    """
    characters = '0123456789ABCDEF'
    random_string = ''.join(random.choice(characters) for _ in range(length * 2))
    return random_string

source_env_file = './sample_data/.env'

with open(source_env_file, 'w') as file:
    file.write('KEY=' + generate_random_hex_string(length = 16) + '\n')
    file.write('DATABASE_PASSWORD=' + generate_random_hex_string(length = 32) + '\n')

#dotenv_path = join(dirname(__file__), source_env_file)
dotenv_path = os.path.join(os.getcwd(), source_env_file)
load_dotenv(dotenv_path)

KEY = os.environ.get("KEY")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

print(f"KEY: {KEY}")
print(f"DATABASE_PASSWORD: {DATABASE_PASSWORD}")

"""
KEY: 38BAC2A5A0E61531FBD349F4F62669A4
DATABASE_PASSWORD: 9231BAFBEF204C57E8FEDF419E00B4117BDABA1368E1B5E03BD986E93C09FCA3
"""