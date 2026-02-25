from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


BASE_CONFIG = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
    json_encoders={datetime: lambda v: v.isoformat().replace("+00:00", "Z")},
)


class CamelCaseModel(BaseModel):
    model_config = BASE_CONFIG
