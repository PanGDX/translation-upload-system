import frontmatter
from app.models import Raw_Chapter, Translated_Chapter, Chapter


def markdown_string_to_chapter_class(markdown_str: str) -> Raw_Chapter | Translated_Chapter:
    """
    Parses a markdown string with frontmatter and converts it 
    into a Raw_Chapter or Translated_Chapter Pydantic model.
    """
    metadata, content = frontmatter.parse(markdown_str)

    chapter_data = metadata.copy()
    chapter_data['content'] = content

    if chapter_data.get("type") == "raw":
        return Raw_Chapter(**chapter_data)
    
    elif chapter_data.get("type") == "translated":
        return Translated_Chapter(**chapter_data)
    
    else:
        raise ValueError(f"Unknown or missing 'type' in frontmatter: {chapter_data.get('type')}")

def chapter_class_to_markdown_string(chapter: Raw_Chapter | Translated_Chapter) -> str:
    data = chapter.model_dump()
    
    content = data.pop("content", "")
    
    post = frontmatter.Post(content, **data)
    return frontmatter.dumps(post)
