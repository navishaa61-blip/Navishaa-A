from app.schemas import ComicOutline, ComicStory, ComicPanel


def build_comic_layout(
    outline: ComicOutline,
    story: ComicStory,
    image_paths: list[str],
) -> list[ComicPanel]:
    outline_by_number = {p.panel_number: p for p in outline.panels}
    story_by_number = {p.panel_number: p for p in story.panels}

    layout: list[ComicPanel] = []
    for index, image_path in enumerate(image_paths):
        number = index + 1
        o = outline_by_number[number]
        s = story_by_number[number]
        image_url = "/static/panels/" + image_path.replace("\\", "/").split("/static/panels/")[-1]
        layout.append(
            ComicPanel(
                panel_number=number,
                title=o.title,
                scene_description=o.scene_description,
                caption=s.caption,
                narration=s.narration,
                dialogue=s.dialogue,
                image_prompt=o.image_prompt,
                image_url=image_url,
                image_path=image_path,
            )
        )
    return layout
