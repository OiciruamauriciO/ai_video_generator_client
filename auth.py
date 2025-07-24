import base64
from config import WP_USERNAME, WP_APP_PASSWORD

def get_auth_header():
    token = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    b64_token = base64.b64encode(token.encode()).decode()
    return {
        "Authorization": f"Basic {b64_token}",
        "Content-Type": "application/json"
    }