from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

#Allow requests from your Vercel frontend
CORS(app, origins=[
    "https://toolverse.vercel.app",
    "https://tool-verse-six.vercel.app",
    "https://tool-verse-git-main-darklegions-projects.vercel.app",
    "http://localhost:3000"  # for local development
])

# Your existing routes...
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "name": "ToolVerse API", "version": "1.0.0"})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Save to database or just return success
    print("Received user data:", data)
    return jsonify({"message": "User created successfully", "user": data}), 201

# Add other routes (/api/domains, etc.) as needed

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
