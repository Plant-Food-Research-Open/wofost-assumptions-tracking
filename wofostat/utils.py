def snake_case_string(text: str) -> str:
	"""Apply some processing to convert a string to snakecase.

	Args:
	    text (str): The input text.

	Returns:
	    str: The snakecase string.
	"""
	snake_string = (
		text.strip().replace(" ", "_").replace(".", "_").replace("-", "_").lower()
	)
	return snake_string
