def build_dict(**kwargs):
    """Build a dictionary from keyword arguments, excluding None values."""
    return {k: v for k, v in kwargs.items() if v is not None}
