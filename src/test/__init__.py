import time
from threading import Thread

import ollama


def run():
    resp = ollama.chat("llama3.2:latest", [{'role': 'user', 'content': 'Why is the sky blue?'}], stream=True, keep_alive=0)
    for i in resp:
        print(i['message']['content'], end='', flush=True)


Thread(target=run).start()
time.sleep(10)
