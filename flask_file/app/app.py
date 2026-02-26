import os
from flask import Flask, send_from_directory

app = Flask(__name__)
FILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

@app.route('/files/<path:filename>', methods=['GET'])
def serve_file(filename):
    print(f"Tentative de récupération : {filename}")
    return send_from_directory(FILES_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
