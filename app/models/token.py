from datetime import datetime
import uuid

class RefreshToken:
    def __init__(
        self,
        id: str = None,
        user_id: str = None,
        token: str = None,
        expires_at: datetime = None,
        created_at: datetime = None
    ):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.token = token
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            token=data.get('token'),
            expires_at=data.get('expires_at'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if isinstance(self.expires_at, datetime) else self.expires_at,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }