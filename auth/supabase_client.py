from supabase import create_client, Client
import os
import hashlib

# ✅ Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(name, email, password, role):
    try:
        # 🔐 Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user_id = response.user.id
        password_hash = hash_password(password)

        # 🗂️ Insert into public.users table
        supabase.table("users").insert({
            "id": user_id,
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "verified": False
        }).execute()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
