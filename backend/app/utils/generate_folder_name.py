import re


def generate_folder_name(title: str) -> str:
    """
    Convert a title into a folder-friendly name by converting to lowercase
    and replacing spaces with underscores.

    Args:
        title (str): The title to convert.

    Returns:
        str: The converted folder name.
    """
    if not re.match(r"^[a-zA-Z0-9_ ]+$", title):
        raise ValueError(
            "The title can only contain letters, numbers, underscores, and spaces."
        )
    return title.lower().replace(" ", "_")
