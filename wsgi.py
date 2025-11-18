import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()
DEBUG= os.getenv('FLASK_DEBUG', True)
HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = os.getenv('SERVER_PORT', 5000)

app = create_app()

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
