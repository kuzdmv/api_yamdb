import jwt

from api_yamdb.settings import SECRET_KEY


def decode(code):
    return jwt.decode(
        jwt=code,
        key=SECRET_KEY,
        algorithms=['HS256']
    )

def get_user_role(token):
    """Извлекает роль из токена, без обращения к базе."""
    data = jwt.decode(
        jwt=str(token),
        key=SECRET_KEY,
        algorithms=['HS256']
    )
    role = data.get('role')
    return role
