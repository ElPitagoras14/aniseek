from models import CamelCaseModel


class OwnerTransferInfo(CamelCaseModel):
    target_user_id: str
    current_password: str
