from typing import Literal

from models import CamelCaseModel


class SettingsUpdateInfo(CamelCaseModel):
    registration_policy: Literal["invite", "open"]


class McpSettingsUpdateInfo(CamelCaseModel):
    enabled: bool
