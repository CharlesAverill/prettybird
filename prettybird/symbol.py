from lib2to3.pytree import convert
from multiprocessing.sharedctypes import Value


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
        self._instruction_buffer = ()
        self._instructions = []

        self._instructions_map = {
            "vector": self.vector
        }

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

        grid_split = new_grid.splitlines()
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
            self._width = len(self._grid.splitlines()[0])
        
    def point_within_grid(self, point):
        """Determine whether or not a point lies within the grid

        Args:
            point (tuple[int, int]): Point in question

        Returns:
            bool: True if the point is within the grid, otherwise False
        """
        return point[0] >= 0 and point[1] >= 0 and point[0] < self._width and point[1] < self._height
    
    def replace_in_grid(self, new_character, point):
        """Replace a character in the grid

        Args:
            new_character (str): Replacement character
            point (tuple[int, int]): Position of character to replace

        Raises:
            ValueError: If the replacement character has a length longer than 1, or if the point is not within the grid
        """
        if len(new_character) != 1:
            raise ValueError("Tried to replace a character in the grid, but the new character has length > 1")
        if not self.point_within_grid(point):
            raise ValueError("Tried to replace a character in the grid, but the point is out of range:", point)
        converted_index = (self._width + 1) * point[1] + point[0]
        self._grid = self._grid[:converted_index] + new_character + self._grid[converted_index + 1:]

    @property
    def parsed_base(self):
        """Determine whether or not the Symbol has set its base yet

        Returns:
            bool: True if the Symbol has set its base, otherwise False
        """
        return self._parsed_base

    def prepare_instruction(self, draw_mode, fill_mode):
        """Prepare the symbol to receive an instruction declaration

        Args:
            draw_mode (str): One of ["draw", "erase"] describing the behavior of the instruction
            fill_mode (bool): True if the instruction will be filled, false if it will only be an outline

        Raises:
            ValueError: If the instruction buffer is non-empty
        """
        if self._instruction_buffer != ():
            raise ValueError(
                f"Symbol \"{self.identifier}\" was told to prepare an instruction, but it has not finished parsing the current function!")
        self._instruction_buffer = (draw_mode, fill_mode)

    def add_instruction(self, instruction_name, inputs):
        """Finish adding an instruction to the symbol's instruction list

        Args:
            instruction_name (str): Name of instruction type
            inputs (list): List of input data to instruction
        """
        self._instructions.append(
            (instruction_name, *self._instruction_buffer, inputs))
        self._instruction_buffer = ()
    
    def get_draw_char(self, draw_mode):
        """Get the character to draw given a draw mode

        Args:
            draw_mode (str): Draw mode descriptor (one of ["draw", "erase"])

        Returns:
            str: Either the fill character if draw_mode == "draw" or the empty character otherwise
        """
        if draw_mode == "draw":
            return "0"
        return "."
    
    def compile(self):
        for instruction in self._instructions:
            instruction_name, draw_mode, fill_mode, inputs = instruction
            if instruction_name not in self._instructions_map:
                raise NameError(f"Received bad instruction \"{instruction_name}\"")
            self._instructions_map[instruction_name](draw_mode, fill_mode, inputs)
            
    def vector(self, draw_mode, fill_mode, inputs):
        """Draw a vector onto the grid using Bresenham's Line Generation algorithm

        Args:
            draw_mode (str): One of ["draw", "erase"] describing the behavior of the instruction
            fill_mode (bool): True if the instruction will be filled, false if it will only be an outline
            inputs (list): Two points, p1 and p2, denoting the start and end of the vector
        """
        draw_char = self.get_draw_char(draw_mode)

        p1, p2 = inputs[0], inputs[1]
        x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]

        dx, dy = x2 - x1, y2 - y1

        x_sign, y_sign = 1 if dx > 0 else -1, 1 if dy > 0 else -1

        dx, dy = abs(dx), abs(dy)

        if dx > dy:
            xx, xy, yx, yy = x_sign, 0, 0, y_sign
        else:
            dx, dy = dy, dx
            xx, xy, yx, yy = 0, y_sign, x_sign, 0
        
        integer_difference = 2 * dy - dx
        y = 0

        for x in range(dx + 1):
            point = (x1 + x * xx + y * yx, y1 + x * xy + y * yy)
            if(self.point_within_grid(point)):
                self.replace_in_grid(draw_char, point)
            if integer_difference >= 0:
                y += 1
                integer_difference -= 2 * dx
            integer_difference += 2 * dy


    def __repr__(self):
        """Get string representation of object

        Returns:
            _type_: _description_
        """
        out = ("~" * self._width)
        if self._grid:
            out += f"\n{self._identifier}\nGrid:\n{self._grid}\n"
        if self._instructions:
            out += "Steps:\n"
        for instruction in self._instructions:
            out += " ".join([str(instr_subset) if type(instr_subset) != bool else "filled=" + str(instr_subset) for instr_subset in instruction]) + "\n"
        out += ("~" * self._width)
        return out