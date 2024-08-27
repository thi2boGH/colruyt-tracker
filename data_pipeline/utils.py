import hashlib

def hash_row(row):
    row_str = ''.join(row.astype(str))
    return hashlib.md5(row_str.encode()).hexdigest()
