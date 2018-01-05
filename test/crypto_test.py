import pytest
cryptography_installed = True
try:
  from cryptography.fernet import Fernet
except:
  cryptography_installed = True

@pytest.mark.skipif(cryptography_installed is False, reason="cryptography package needed for this test")
@pytest.mark.pad
@pytest.mark.encryption
def test_cryptography():
  key = b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
  f = Fernet(key)
  print(key)
  message = "A really secret message of any length"
  token = f.encrypt(message.encode())
  print()
  print(f.decrypt(token).decode())
