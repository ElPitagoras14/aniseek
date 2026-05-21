from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


def camelize(data):
    if isinstance(data, list):
        return [camelize(item) for item in data]

    if isinstance(data, Mapping):
        return {to_camel(str(k)): camelize(v) for k, v in data.items()}

    return data


class AppResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    status: str
    message: str
    payload: Any | None = None
    status_code: int

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)

        if data.get("payload") is not None:
            data["payload"] = camelize(data["payload"])

        return data


class SuccessResponse(AppResponse):
    status: str = "success"
    message: str = "Operación exitosa"
    status_code: int = 200
