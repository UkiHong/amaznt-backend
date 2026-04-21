from passlib.context import CryptContext

# tool for hashing and verifying passwords using bcrypt algorithm
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Password verification
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
