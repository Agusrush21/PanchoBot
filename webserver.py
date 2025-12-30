from flask import Flask
from threading import Thread
import os


app = Flask("")

@app.route("/")
def index():
    return "Hola CARABOLA"

def run():
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    server = Thread(target=run, daemon=True)
    server.start()
