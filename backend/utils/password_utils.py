import bcrypt


def encrypt_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password: str, correct_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), correct_password.encode('utf-8'))
