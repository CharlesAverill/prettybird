def get_empty_grid(width, height):
    """Get a string containing a grid filled with the "." character given dimensions

    Args:
        width (int): Width of grid
        height (int): Height of grid

    Raises:
        ValueError: If either width or height is less than 1
    """
    if height < 1 or width < 1:
        raise ValueError("Empty grid dimensions must be at least 1x1")

    return (("." * width + "\n") * height).strip()
