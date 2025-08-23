import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

from supabase import create_client, Client

# Replace with your actual values
url = "https://xqbqsjphvaukzmzomomc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhxYnFzanBodmF1a3ptem9tb21jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU4OTIzMTYsImV4cCI6MjA3MTQ2ODMxNn0.jaFatrvfNqb1y8nHSDWrWZyKA1eH6anERyVoqbax6qU"

supabase: Client = create_client(url, key)

# Example: Fetch all drugs
response = supabase.table("drugs").select("*").execute()
print(response.data)
