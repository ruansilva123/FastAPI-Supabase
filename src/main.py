from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from supabase import create_client, Client
from decouple import config
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
import requests

from schemas import TodoSchema, LoginSchema, RefreshSchema


url = config("SUPABASE_URL")
key = config("SUPABASE_KEY")
url_token = config("SUPABASE_URL_TOKEN")


app = FastAPI()


supabase : Client = create_client(url, key)


# origins = [
#     "http://localhost:8000"
# ]


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,   
#     allow_credentials=True,
#     allow_methods=["*"],     
#     allow_headers=["*"],     
# )


# In future versions, functions must be async

# ===== POSTGRES MANIPULATION =====

@app.get('/todos/')
def get_todos():
    try:
        todos = supabase.table('todos').select('*').execute()

        if not todos.data:
            return JSONResponse(content={'error' : 'No todo found!'}, status_code=status.HTTP_404_NOT_FOUND)

        return todos
    
    except:
        return JSONResponse(content={'error' : 'Error to return all todos!'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get('/todos/{id}')
def get_todo(id : int):
    try:
        todo = supabase.table('todos').select('*').eq('id', id).execute()

        if not todo.data:
            return JSONResponse(content={'error' : 'Not found todo with this id!'}, status_code=status.HTTP_404_NOT_FOUND)
        
        return todo
    
    except:
        return JSONResponse(content={'error' : 'Error to return todo!'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post('/todos/', status_code=status.HTTP_201_CREATED)
def post_todo(todo: TodoSchema):
    try:
        new_todo = supabase.table('todos').insert({
            'title' : todo.title,
            'description' : todo.description
        }).execute()

        return new_todo
    
    except:
        return JSONResponse(content={'error' : 'Error to create new todo!'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@app.delete('/todos/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id : str):
    try:
        todo = supabase.table('todos').select('*').eq('id', id).execute()

        if not todo.data:
            return JSONResponse(content={'error' : 'Not found todo with this id!'}, status_code=status.HTTP_404_NOT_FOUND)
        
        supabase.table('todos').delete().eq('id', id).execute()

        return JSONResponse(content={'message' : 'Todo deleted successfully!'})

    except:
        return JSONResponse(content={'error' : 'Error to delete todo!'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# ===== SSO MANIPULATION =====

def generate_access_token(data : dict, expires_delta : timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({'exp' : expire})
    encode_jwt = jwt.encode(to_encode, config('SUPABASE_JWT_SECRET'), config('ALGORITHM'))
    return encode_jwt


@app.post('/login/')
def login(data : LoginSchema):
    try: 
        response = supabase.auth.sign_in_with_password(credentials = {"email" : data.email, "password" : data.password})

        # access_token = generate_access_token(
        #     data = {'sub' : data.email},
        #     expires_delta = timedelta(minutes = int(config('ACCESS_TOKEN_EXPIRE_MINUTES')))
        # )

        return {"access_token" : response.session.access_token, "refresh_token" : response.session.refresh_token, "expires_in" : response.session.expires_in}
    
    except Exception as e:
        print(e)
        return JSONResponse(content={'error' : 'Invalid credentials!'}, status_code=status.HTTP_401_UNAUTHORIZED)
    

@app.post('/token/refresh')
def refresh_token(refresh_token : str):
    try:
        response = supabase.auth.refresh_session(refresh_token = refresh_token)

        return {"access_token" : response.session.access_token, "refresh_token" : response.session.refresh_token, "expires_in" : response.session.expires_in}
    
    except Exception as e:
        print(e)
        return JSONResponse(content={'error' : 'Invalid token!'}, status_code=status.HTTP_401_UNAUTHORIZED)
    

# ===== POSTGRES MANIPULATION WITH AUTHENTICATION

@app.post('/auth-todos/')
def post_auth_todo(todo : TodoSchema, authorization : str = Header(...)):

    if not authorization.startswith("Bearer"):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Invalid authorization header format.'
        )

    headers = {"Authorization": f"{authorization}", "apikey" : key}
    print(headers)
    
    response = requests.get(url = url_token, headers = headers)

    print(response)
    print(response.json())

    try: 
        new_todo = supabase.table('auth_todo').insert(dict(todo)).execute()

        return new_todo

    except Exception as e:
        return JSONResponse(content={"error" : f"Error: {e}"}, status_code=status.HTTP_401_UNAUTHORIZED)