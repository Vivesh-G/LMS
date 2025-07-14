from fastapi import Request

async def get_current_user(request: Request):
    session = request.session
    if not session.get('loggedin'):
        return None
    return {
        'id': session.get('id'),
        'username': session.get('username'),
        'role': session.get('role')
    }
