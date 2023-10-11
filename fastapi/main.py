from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import cachetools
from cachetools import TTLCache
import jwt

app = FastAPI()

# Fake user database for demonstration
users_db = {
    "user1": {
        "username": "user1",
        "password": "password1",
    },
}

# Fake post database
posts_db = {}
post_id_counter = 1

# Secret key for JWT token
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token handling
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token related dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Cache for getPosts endpoint
cache = TTLCache(maxsize=100, ttl=300)

# Pydantic models for request and response validation
class User(BaseModel):
    username: str
    password: str

class Post(BaseModel):
    content: str

# User registration
@app.post("/signup")
def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.username] = user
    return {"message": "User registered successfully"}

# User login
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if user is None or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Add a new post
@app.post("/addPost", response_model=int)
def add_post(post: Post, token: str = Depends(oauth2_scheme)):
    if len(post.content) > 1_000_000:
        raise HTTPException(status_code=400, detail="Post content is too large")

    user = get_user_from_token(token)
    post_id = generate_post_id()
    posts_db[post_id] = {"user": user, "content": post.content}
    return post_id

# Get all posts for the user
@app.get("/getPosts", response_model=list)
def get_posts(token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(token)
    if user not in cache:
        cache[user] = []

    if not cache[user]:
        cache[user] = [post_id for post_id, post in posts_db.items() if post["user"] == user]
    
    return cache[user]

# Delete a post
@app.delete("/deletePost")
def delete_post(post_id: int, token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(token)
    
    if post_id not in posts_db or posts_db[post_id]["user"] != user:
        raise HTTPException(status_code=400, detail="Invalid post ID")
    
    del posts_db[post_id]
    return {"message": "Post deleted successfully"}

def get_user_from_token(token: str):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    if username not in users_db:
        raise credentials_exception
    return username

def generate_post_id():
    global post_id_counter
    post_id = post_id_counter
    post_id_counter += 1
    return post_id
