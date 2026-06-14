from typing import Dict, Any, List

class UserModel:
    def __init__(self, id: str, name: str, email: str, prime: bool = False, preferences: List[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.prime = prime
        self.preferences = preferences or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            prime=bool(data.get('prime', False)),
            preferences=data.get('preferences', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"USER#{self.id}",
            'SK': "PROFILE",
            'entityType': "USER",
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'prime': self.prime,
            'preferences': self.preferences
        }
