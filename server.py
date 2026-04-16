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

# Try to import OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed. Using fallback responses.")

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

# Try to connect to MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "toolverse")

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    MONGODB_AVAILABLE = True
    logger.info(f"MongoDB connected: {DB_NAME}")
except Exception as e:
    MONGODB_AVAILABLE = False
    logger.warning(f"MongoDB not available: {e}. Using in-memory storage.")

# Initialize OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY and OPENAI_AVAILABLE:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    OPENAI_ENABLED = True
    logger.info("OpenAI enabled")
else:
    openai_client = None
    OPENAI_ENABLED = False
    logger.warning("OpenAI not available. Using fallback responses.")

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
    openai: str

class ChatMessage(BaseModel):
    message: str
    domain: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# In-memory storage (fallback if MongoDB not available)
in_memory_users = []

# ============= DATABASE HELPERS =============

async def create_user_in_db(user_data: dict):
    if MONGODB_AVAILABLE:
        result = await db.users.insert_one(user_data)
        return result.inserted_id
    else:
        in_memory_users.append(user_data)
        return user_data["id"]

async def get_all_users_from_db():
    if MONGODB_AVAILABLE:
        users = await db.users.find({}, {"_id": 0}).to_list(1000)
        return users
    else:
        return in_memory_users

async def get_user_from_db(user_id: str):
    if MONGODB_AVAILABLE:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        return user
    else:
        user = next((u for u in in_memory_users if u["id"] == user_id), None)
        return user

# ============= API ENDPOINTS =============

@api_router.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to ToolVerse API",
        "version": "1.0.0",
        "status": "running",
        "mongodb": MONGODB_AVAILABLE,
        "openai": OPENAI_ENABLED
    }

@api_router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    db_status = "connected" if MONGODB_AVAILABLE else "disconnected (using in-memory)"
    openai_status = "enabled" if OPENAI_ENABLED else "disabled (using fallback)"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        openai=openai_status
    )

@api_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
async def create_user(user: UserCreate):
    """
    Create a new user
    """
    try:
        # Check if user already exists
        existing_users = await get_all_users_from_db()
        existing_user = next((u for u in existing_users if u.get("email") == user.email), None)
        
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
        
        await create_user_in_db(new_user.copy())
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
    users = await get_all_users_from_db()
    return users

@api_router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: str):
    """
    Get a specific user by ID
    """
    user = await get_user_from_db(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ============= DOMAIN ROADMAPS =============

DOMAINS_DATA = {
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

@api_router.get("/domains", tags=["Domains"])
async def get_domains():
    """
    Get all available domains with roadmaps
    """
    return DOMAINS_DATA

@api_router.get("/domains/{domain_key}", tags=["Domains"])
async def get_domain(domain_key: str):
    """
    Get specific domain roadmap
    """
    domain = DOMAINS_DATA.get(domain_key.lower())
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    return domain

# ============= CHATBOT WITH OPENAI =============

FALLBACK_RESPONSES = {
    "cyber-security": "Cybersecurity is about protecting systems and data. Start with CompTIA Security+ certification. Practice on TryHackMe daily. Learn Python for automation. Remember: 'Defense in depth' is key!",
    "web-development": "Web development is a great choice! Start with HTML/CSS/JS. Build 3 projects: portfolio, todo app, and a small e-commerce site. Learn React after mastering vanilla JS.",
    "software-engineering": "Software engineering requires strong fundamentals. Master data structures and algorithms first. Practice LeetCode daily. Learn system design patterns.",
    "data-science": "Data science combines stats and coding. Learn Python pandas first. Practice on Kaggle. Build a portfolio of 5 projects. Understand business problems.",
    "ai-ml": "AI/ML is cutting-edge! Start with Andrew Ng's ML course. Master Python libraries: numpy, pandas, sklearn. Practice on Kaggle competitions.",
    "ui-ux-design": "UI/UX is about user empathy. Start with Google's UX certificate. Learn Figma. Create case studies. Build a portfolio with 3 projects.",
    "devops": "DevOps bridges dev and ops. Learn Linux fundamentals. Master Docker. Understand CI/CD. Get AWS cloud practitioner certified.",
    "mobile-development": "Mobile dev is rewarding. Choose one platform first. Build and publish 2 apps to store. Learn about app architecture patterns.",
    "networking": "Networking is infrastructure backbone. Master CCNA concepts. Use Packet Tracer daily. Understand TCP/IP deeply."
}

@api_router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(chat: ChatMessage):
    """
    Chat with AI assistant for domain guidance
    """
    try:
        # Try OpenAI first
        if OPENAI_ENABLED and openai_client:
            system_message = f"""You are a helpful career guidance assistant for TOOL VERSE platform.
The user is interested in: {chat.domain}
Keep responses under 200 words. Be encouraging, practical, and give actionable advice.
Focus on learning paths, resources, and daily practice routines."""

            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": chat.message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
        else:
            # Use fallback responses
            for key, response in FALLBACK_RESPONSES.items():
                if key in chat.domain.lower():
                    ai_response = response
                    break
            else:
                ai_response = f"For {chat.domain}, start with fundamentals. Practice daily for 2 hours. Build projects. Join communities. Stay consistent!"
        
        # Add personalized tips based on question type
        if "roadmap" in chat.message.lower() or "path" in chat.message.lower():
            ai_response += "\n\n📚 Check the roadmap section for detailed learning path!"
        elif "resource" in chat.message.lower() or "learn" in chat.message.lower():
            ai_response += "\n\n📖 Online platforms: Coursera, Udemy, YouTube, and official documentation are great resources!"
        elif "time" in chat.message.lower() or "how long" in chat.message.lower():
            ai_response += "\n\n⏰ Consistency is key! Even 1-2 hours daily adds up to mastery over time."
        
        return ChatResponse(
            response=ai_response,
            session_id=chat.session_id or str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return ChatResponse(
            response="I'm here to help! Please ask your question again or check the roadmap section for guidance.",
            session_id=chat.session_id or str(uuid.uuid4())
        )

# Include router
app.include_router(api_router)

# ============= ROOT ENDPOINT =============

@app.get("/")
async def home():
    return {
        "name": "ToolVerse API",
        "version": "1.0.0",
        "status": "running",
        "mongodb": MONGODB_AVAILABLE,
        "openai": OPENAI_ENABLED,
        "endpoints": {
            "health": "/api/health",
            "users": "/api/users",
            "domains": "/api/domains",
            "chat": "/api/chat"
        }
    }

# ============= SHUTDOWN =============

@app.on_event("shutdown")
async def shutdown_event():
    if MONGODB_AVAILABLE:
        mongo_client.close()
        logger.info("MongoDB connection closed")

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

# Add this at the very bottom of server.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)