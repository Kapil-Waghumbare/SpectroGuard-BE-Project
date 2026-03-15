import hashlib

# SHA-256 HASH GENERATOR

def generate_sha256(input_text):
    sha = hashlib.sha256()
    sha.update(input_text.encode('utf-8'))
    return sha.hexdigest()


print("SHA-256 Hash ID Generator Ready")

while True:
    text = input("\nEnter text to generate SHA-256 hash (type 'exit' to quit): ")

    if text.lower() == "exit":
        break

    hash_id = generate_sha256(text)

    print("\nInput Text:", text)
    print("Algorithm: SHA-256")
    print("Hash Length:", len(hash_id), "characters")
    print("Generated Hash ID:")
    print(hash_id)

    print("\nResult: Unique secure hash generated successfully")