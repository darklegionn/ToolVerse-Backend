from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow requests from your Vercel frontend and localhost
CORS(app, origins=[
    "https://toolverse.vercel.app",
    "https://tool-verse-six.vercel.app",
    "https://tool-verse-git-main-darklegions-projects.vercel.app",
    "http://localhost:3000"
])

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "name": "ToolVerse API",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        print("Received user data:", data)  # Logs to Render console
        
        # Validate required fields
        required = ['name', 'email', 'education', 'domain']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        # Here you can save to a database later
        # For now, just return success
        return jsonify({
            "message": "User saved successfully",
            "user": data
        }), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/domains', methods=['GET'])
def get_domains():
    domains = [
        "cyber-security", "web-development", "software-engineering",
        "ui-ux-design", "data-science", "mobile-development",
        "devops", "ai-ml", "networking"
    ]
    return jsonify(domains)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
