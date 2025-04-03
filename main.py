from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import shutil
import os
from fastapi.testclient import TestClient

# FastAPI App
app = FastAPI()

# Secret key for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake database
fake_users_db = {}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username not in fake_users_db:
            raise HTTPException(status_code=401, detail="Invalid token")
        return fake_users_db[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/users/")
def create_user(username: str, password: str, role: str = "user"):
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {"username": username, "password": hashed_password, "role": role}
    return {"message": "User created successfully"}

@app.post("/upload/")
def upload_video(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    save_path = f"videos/{file.filename}"
    os.makedirs("videos", exist_ok=True)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "status": "Uploaded"}

@app.get("/analyze/{video_name}")
def analyze_video(video_name: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"video": video_name, "analysis": "Video analysis data here"}

# Test Cases
client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"username": "testuser", "password": "testpass", "role": "user"})
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_login_success():
    client.post("/users/", json={"username": "admin", "password": "admin123", "role": "admin"})
    response = client.post("/token", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/token", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401

def test_upload_video_unauthorized():
    response = client.post("/upload/", files={"file": ("test.mp4", b"fake video data")})
    assert response.status_code == 403

def test_analyze_video_unauthorized():
    response = client.get("/analyze/test.mp4")
    assert response.status_code == 403
