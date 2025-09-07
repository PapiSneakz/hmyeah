from flask import Flask
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))  # use 8080 or another free port
    app.run(host='0.0.0.0', port=port)
