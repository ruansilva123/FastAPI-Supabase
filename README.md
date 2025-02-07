# FastAPI-Supabase
 This project was created to learn FastAPI with Supabase.


## To execute app 
- pip install poetry
- poetry shell
- poetry install
- cd src
- new file .env: echo > .env
- write in env file:
> SUPABASE_URL = "your-supabase-url"
> SUPABASE_KEY = "your-supabase-key"
> SUPABASE_URL_TOKEN = "your-supabase-url-token"
> SUPABASE_JWT_SECRET = "your-supabase-jwt-secret"
> ALGORITHM = "your-supabase-argorithm"
- uvicorn main:app --reload