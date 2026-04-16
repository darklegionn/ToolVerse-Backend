from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ToolVerse API",
    description="Backend API for ToolVerse platform",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://toolverse.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (simple, no MongoDB needed)
users_db = []

# Create router
api_router = APIRouter(prefix="/api")

# ============= MODELS =============

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    education: str
    domain: str
    level: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    education: str
    domain: str
    level: Optional[str]
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str

# ============= API ENDPOINTS =============

@api_router.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to ToolVerse API",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        database="in-memory (no MongoDB)"
    )

@api_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: UserCreate):
    """
    Create a new user
    """
    try:
        # Check if user already exists
        existing_user = next((u for u in users_db if u["email"] == user.email), None)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "name": user.name,
            "email": user.email,
            "education": user.education,
            "domain": user.domain,
            "level": user.level,
            "created_at": datetime.now(timezone.utc)
        }
        
        users_db.append(new_user)
        logger.info(f"User created: {user.email}")
        
        return UserResponse(**new_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@api_router.get("/users", response_model=List[UserResponse], tags=["Users"])
async def get_users():
    """
    Get all users
    """
    return users_db

@api_router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: str):
    """
    Get a specific user by ID
    """
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ============= DOMAIN ROADMAPS =============

@api_router.get("/domains", tags=["Domains"])
async def get_domains():
    """
    Get all available domains with roadmaps
    """
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
    return domains

# Include router
app.include_router(api_router)

# ============= ROOT ENDPOINT =============

@app.get("/")
async def home():
    return {
        "name": "ToolVerse API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "users": "/api/users",
            "domains": "/api/domains"
        }
    }

# ============= RUN SERVER =============

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
