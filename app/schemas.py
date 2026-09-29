from pydantic import BaseModel, Field, field_validator
from typing import List


class ComicRequest(BaseModel):
    story_prompt: str = Field(min_length=5, max_length=1200)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(default="funny", max_length=40)
    art_style: str = Field(default="comic book", max_length=60)

    @field_validator("story_prompt", "character_name", "setting", "tone", "art_style")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[PanelOutline] = Field(min_length=1, max_length=10)


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str


class ComicStory(BaseModel):
    panels: List[PanelStory] = Field(min_length=1, max_length=10)


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
    image_url: str
    image_path: str


class ComicResponse(BaseModel):
    panels: List[ComicPanel]
    pdf_url: str
    filename: str
