from supabase import create_client, Client
import os

# ✅ Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(email, password, role, name):
    try:
        # 🔐 Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # 🗂️ Add user to public.users table with name and role
        user_id = response.user.id
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "role": role,
            "name": name,
            "verified": False
        }).execute()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
