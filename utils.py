import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

def generate_identity(id):
    identity = generate_password_hash(id)
    return ''.join(identity)

def check_identity(identity, id):
    return check_password_hash(identity, id)

