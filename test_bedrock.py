import os
import sys
sys.path.append(os.path.abspath('src'))
from infrastructure.bedrock.client import BedrockClient

def test():
    client = BedrockClient()
    nova_ok = client.check_nova_available()
    print("Nova available:", nova_ok)
    if nova_ok:
        res = client.generate_text("Say 'Hello World'!")
        print("Nova output:", res.text)
    else:
        print("Falling back to mock.")

if __name__ == "__main__":
    test()
