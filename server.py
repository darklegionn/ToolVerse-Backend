from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://toolverse.vercel.app").split(",")
CORS(app, origins=cors_origins)

# In-memory storage
users_db = []

# Helper functions
def find_user_by_email(email):
    return next((u for u in users_db if u["email"] == email), None)

def find_user_by_id(user_id):
    return next((u for u in users_db if u["id"] == user_id), None)

# ============= ROUTES =============

@app.route('/')
def home():
    return jsonify({
        "name": "ToolVerse API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "users": "/api/users",
            "domains": "/api/domains"
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "in-memory"
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'email', 'education', 'domain']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Check if user exists
    if find_user_by_email(data['email']):
        return jsonify({"error": "User with this email already exists"}), 400
    
    # Create new user
    new_user = {
        "id": str(uuid.uuid4()),
        "name": data['name'],
        "email": data['email'],
        "education": data['education'],
        "domain": data['domain'],
        "level": data.get('level'),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    users_db.append(new_user)
    return jsonify(new_user), 201

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users_db)

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route('/api/domains', methods=['GET'])
def get_domains():
    domains = {
        "cyber-security": {
            "name": "Cyber Security 🔒",
            "roadmap": [
                "Learn Networking Basics (TCP/IP, OSI Model)",
                "Master Linux Command Line",
                "Learn Python for Security",
                "Study Cryptography Basics",
                "Practice with Wireshark & Nmap",
                "Get Certified: Security+, CEH",
                "Learn Cloud Security (AWS/Azure)"
            ],
            "resources": [
                "TryHackMe - Hands-on cybersecurity training",
                "HackTheBox - Advanced penetration testing",
                "Cybrary - Free security courses",
                "OWASP - Web security guidelines"
            ]
        },
        "web-development": {
            "name": "Web Development 🌐",
            "roadmap": [
                "HTML5 & CSS3 Fundamentals",
                "JavaScript (ES6+)",
                "Version Control (Git/GitHub)",
                "Choose Framework: React or Vue",
                "Backend Basics: Node.js or Python",
                "Database: MongoDB or PostgreSQL",
                "Deployment: Vercel/Netlify"
            ],
            "resources": [
                "The Odin Project - Full-stack curriculum",
                "FreeCodeCamp - Interactive learning",
                "MDN Web Docs - Documentation",
                "Frontend Mentor - Practice projects"
            ]
        },
        "software-engineering": {
            "name": "Software Engineering 💻",
            "roadmap": [
                "Master a Language (Python/Java)",
                "Data Structures & Algorithms",
                "Object-Oriented Programming",
                "Design Patterns",
                "System Design Basics",
                "Testing & Debugging",
                "CI/CD Pipelines"
            ],
            "resources": [
                "LeetCode - Practice coding problems",
                "Clean Code by Robert Martin",
                "Design Patterns by Gang of Four",
                "System Design Interview by Alex Xu"
            ]
        },
        "data-science": {
            "name": "Data Science 📊",
            "roadmap": [
                "Python Programming",
                "Statistics & Mathematics",
                "Data Analysis (Pandas, NumPy)",
                "Data Visualization (Matplotlib, Seaborn)",
                "Machine Learning (Scikit-learn)",
                "Deep Learning (TensorFlow/PyTorch)",
                "Big Data Tools (Spark)"
            ],
            "resources": [
                "Kaggle - Real-world datasets & competitions",
                "DataCamp - Interactive courses",
                "Andrew Ng's ML Course - Coursera",
                "Towards Data Science - Articles"
            ]
        },
        "ai-ml": {
            "name": "AI & Machine Learning 🤖",
            "roadmap": [
                "Python & Mathematics",
                "Linear Algebra & Calculus",
                "Statistics & Probability",
                "Machine Learning Algorithms",
                "Neural Networks & Deep Learning",
                "NLP & Computer Vision",
                "MLOps & Deployment"
            ],
            "resources": [
                "Fast.ai - Practical deep learning",
                "DeepLearning.AI - Specialization",
                "Kaggle Competitions",
                "Papers with Code - Latest research"
            ]
        },
        "ui-ux-design": {
            "name": "UI/UX Design 🎨",
            "roadmap": [
                "Design Fundamentals",
                "Color Theory & Typography",
                "Figma/Sketch/Adobe XD",
                "User Research Methods",
                "Wireframing & Prototyping",
                "Usability Testing",
                "Portfolio Development"
            ],
            "resources": [
                "Google UX Design Certificate",
                "Nielsen Norman Group - Articles",
                "Dribbble - Design inspiration",
                "UX Collective - Blog"
            ]
        },
        "devops": {
            "name": "DevOps Engineering ⚙️",
            "roadmap": [
                "Linux System Administration",
                "Scripting (Bash/Python)",
                "Version Control (Git)",
                "CI/CD (Jenkins/GitHub Actions)",
                "Containerization (Docker)",
                "Orchestration (Kubernetes)",
                "Cloud Platforms (AWS/Azure/GCP)"
            ],
            "resources": [
                "DevOps Roadmap - roadmap.sh/devops",
                "KodeKloud - Hands-on DevOps",
                "AWS Free Tier - Practice",
                "Docker Curriculum"
            ]
        },
        "mobile-development": {
            "name": "Mobile Development 📱",
            "roadmap": [
                "Choose Platform: iOS or Android",
                "Learn Swift (iOS) or Kotlin (Android)",
                "Cross-platform: Flutter/React Native",
                "UI/UX for Mobile",
                "API Integration",
                "App Store Deployment",
                "App Maintenance"
            ],
            "resources": [
                "Apple Developer Documentation",
                "Android Developers Documentation",
                "Flutter Official Docs",
                "Ray Wenderlich - Tutorials"
            ]
        },
        "networking": {
            "name": "Networking 🌐",
            "roadmap": [
                "OSI & TCP/IP Models",
                "IP Addressing & Subnetting",
                "Routing & Switching",
                "Network Security Basics",
                "Cisco Packet Tracer",
                "CCNA Certification",
                "Cloud Networking"
            ],
            "resources": [
                "Cisco Networking Academy",
                "Professor Messer - Videos",
                "GNS3 - Network simulation",
                "Wireshark - Packet analysis"
            ]
        }
    }
    return jsonify(domains)

# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
