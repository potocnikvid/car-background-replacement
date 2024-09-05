# app/services/supabase_service.py

from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY


# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def upload_image_to_supabase(bucket_name: str, file_path: str, file_name: str):
    """Uploads a file to the specified Supabase bucket."""
    try:
        with open(file_path, "rb") as file:
            # Perform the upload using the Supabase storage client
            response = supabase.storage.from_(bucket_name).upload(file_name, file)

        # Check the response status and handle errors
        if response.status_code != 200:
            # Log the response content if the upload fails
            error_message = response.json().get('error', 'Unknown error')
            raise Exception(f"Error uploading to Supabase: {error_message}")

        # Successfully uploaded, return relevant data or success message
        return response.json()  # Or response.content, depending on what you need

    except Exception as e:
        print(f"Failed to upload image: {e}")
        raise