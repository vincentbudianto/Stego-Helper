from vigenere import Vigenere

#Notes : run `python test_vigenere.py in directory /src/backend/src`

if __name__ == "__main__":
    key = '+'
    vigenere = Vigenere(key)

    # #Encrypt File
    content = vigenere.encryptFile('secret.txt')
    print(type(content))

    # #Decrypt File
    # vigenere.decryptFile('example_encrypted.txt', 'contoh_decrypted.txt')