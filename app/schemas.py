from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Validate incoming application data
class JobApplication(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: Literal[
        "Applied",
        "Interview",
        "Selected",
        "Rejected",
        "Withdrawn"
    ] = "Applied"
