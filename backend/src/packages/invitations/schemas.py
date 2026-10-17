from models import CamelCaseModel


class InvitationCreateInfo(CamelCaseModel):
    role: str = "member"
    expires_in_days: int = 7
