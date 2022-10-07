class Symbol:
    def __init__(self, identifier):
        """Initiailze new Symbol

        Args:
            identifier (str): Name of Symbol
        """
        self._identifier = identifier
        self._parsed_base = False
        self._width = 0
        self._height = 0
        self._grid = ""

    @property
    def identifier(self):
        """Get the name of the Symbol

        Returns:
            str: Name of Symbol
        """
        return self._identifier

    @property
    def dimensions(self):
        """Get dimensions of Symbol

        Raises:
            RuntimeWarning: If the base has not been initialized yet

        Returns:
            tuple[int, int]: Tuple containing width and height of Symbol
        """
        if not self._parsed_base:
            raise RuntimeWarning(
                f"Symbol \"{self._identifier}\" does not have an initialized base yet")

        return (self._width, self._height)

    def set_grid(self, new_grid):
        """Set the grid of the Symbol

        Args:
            new_grid (str): New grid string
        """
        self._grid = new_grid

        grid_split = new_grid.split("\n")
        self._width = len(grid_split[0])
        self._height = len(grid_split)

        self._parsed_base = True

    def get_grid(self):
        """Get the grid of the Symbol

        Returns:
            str: Grid of the Symbol
        """
        return self._grid

    grid = property(get_grid, set_grid)

    def append_to_grid(self, new_char):
        self._grid += new_char
        if new_char == "\n":
            self._height += 1
            self._width = len(self._grid.split("\n")[0])

    @property
    def parsed_base(self):
        """Determine whether or not the Symbol has set its base yet

        Returns:
            bool: True if the Symbol has set its base, otherwise False
        """
        return self._parsed_base

    def __repr__(self):
        """Get string representation of object

        Returns:
            _type_: _description_
        """
        return ("~" * self._width) + f"\n{self._identifier}:\n{self._grid}\n" + ("~" * self._width)
