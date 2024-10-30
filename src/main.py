from fastapi import FastAPI
from supabase import create_client, Client
from decouple import config


url = config("SUPABASE_URL")
key = config("SUPABASE_KEY")


app = FastAPI()


supabase : Client = create_client(url, key)


@app.get('/todos/')
def get_todos():
    todos = supabase.table('todos').select('*').execute()
    return todos