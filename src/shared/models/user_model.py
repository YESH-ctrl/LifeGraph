from typing import Dict, Any

class UserModel:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'PK': f"USER#{self.id}",
            'SK': "METADATA",
            'id': self.id,
            'name': self.name,
            'email': self.email
        }
