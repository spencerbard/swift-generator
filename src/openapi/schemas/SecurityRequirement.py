from pydantic import BaseModel, ConfigDict


class SecurityRequirement(BaseModel):  # TODO: too complicated for now
    model_config = ConfigDict(extra="allow")
