import base64
import hashlib
import os

from Crypto import Random
from Crypto.Cipher import AES


def pad(s):
    """
    pad with spaces at the end of the text because AES needs 16 byte blocks
    :param s:
    :return:
    """
    block_size = 16
    remainder = len(s) % block_size
    padding_needed = block_size - remainder
    return s + padding_needed * ' '


def un_pad(s):
    """
    remove the extra spaces at the end
    :param s:
    :return:
    """
    return s.rstrip()


def encrypt(plain_text, password):
    # generate a random salt
    salt = os.urandom(AES.block_size)

    # generate a random iv
    iv = Random.new().read(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

    # pad text with spaces to be valid for AES CBC mode
    padded_text = pad(plain_text)

    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_CBC, iv)

    # return a dictionary with the encrypted text
    return {
        'cipher_text': base64.b64encode(cipher_config.encrypt(padded_text)),
        'salt': base64.b64encode(salt),
        'iv': base64.b64encode(iv)
    }


def decrypt(enc_dict, password):
    # decode the dictionary entries from base64
    salt = base64.b64decode(enc_dict['salt'])
    enc = base64.b64decode(enc_dict['cipher_text'])
    iv = base64.b64decode(enc_dict['iv'])

    # generate the private key from the password and salt
    private_key = hashlib.scrypt(password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_CBC, iv)

    # decrypt the cipher text
    decrypted = cipher.decrypt(enc)

    # un pad the text to remove the added spaces
    original = un_pad(decrypted)

    return original.decode('utf-8')
