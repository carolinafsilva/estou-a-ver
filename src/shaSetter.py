import hashlib
import os

f_out = open("datab.txt", "w")


path = input("Enter the input file name: ")

sha256_hash = hashlib.sha256()
for fname in os.listdir(path):
    os.chdir(path)
    with open(fname, "rb") as f:
        # Read and update hash string value in blocks of 4096
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        # Saves output file the project's directory
        f_out.write('%s -> %s\n' % (fname, sha256_hash.hexdigest()))


f_out.close()
