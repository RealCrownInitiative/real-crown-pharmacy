from supabase import create_client, Client
import os

# ✅ Connect to Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(email, password, role):
    try:
        # 🔐 Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # 🗂️ Add role to public.users table (optional)
        user_id = response.user.id
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "role": role
        }).execute()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
