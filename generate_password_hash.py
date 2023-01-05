import sys
from passlib.context import CryptContext
if len(sys.argv) < 2:
    print("syntax: python generate_password_hash.py <your-password>")
    exit()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash(sys.argv[1]))
