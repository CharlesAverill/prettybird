import math

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

        self._instructions_map = {"vector": self.vector, "circle": self.circle, "from_char": self._init_grid_from_symbol}

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
                f'Symbol "{self._identifier}" does not have an initialized base yet'
            )

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

    def _init_grid_from_symbol(self, draw_mode, fill_mode, inputs):
        self.set_grid(inputs[0].get_grid())

    def append_to_grid(self, new_char):
        """Append a character to the grid

        Args:
            new_char (str): Character to append

        Raises:
            RuntimeError: If the base has already been completed
        """
        if self._parsed_base:
            raise RuntimeError("Tried to update base, but base has already been defined")
        self._grid += new_char
        if new_char == "\n":
            self._height += 1
            self._width = len(self._grid.splitlines()[0])
    
    def finish_grid(self):
        self._height += 1
        self._parsed_base = True

    def _point_within_grid(self, point):
        """Determine whether or not a point lies within the grid

        Args:
            point (tuple[int, int]): Point in question

        Returns:
            bool: True if the point is within the grid, otherwise False
        """
        return (
            point[0] >= 0
            and point[1] >= 0
            and point[0] < self._width
            and point[1] < self._height
        )

    def _replace_in_grid(self, new_character, point):
        """Replace a character in the grid

        Args:
            new_character (str): Replacement character
            point (tuple[int, int]): Position of character to replace

        Raises:
            ValueError: If the replacement character has a length longer than 1, or if the point is not within the grid
        """
        if len(new_character) != 1:
            raise ValueError(
                "Tried to replace a character in the grid, but the new character has length > 1"
            )
        if not self._point_within_grid(point):
            raise ValueError(
                "Tried to replace a character in the grid, but the point is out of range:",
                point,
            )
        converted_index = (self._width + 1) * point[1] + point[0]
        self._grid = (
            self._grid[:converted_index]
            + new_character
            + self._grid[converted_index + 1 :]
        )

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
                f'Symbol "{self.identifier}" was told to prepare an instruction, but it has not finished parsing the current function!'
            )
        self._instruction_buffer = (draw_mode, fill_mode)

    def add_instruction(self, instruction_name, inputs):
        """Finish adding an instruction to the symbol's instruction list

        Args:
            instruction_name (str): Name of instruction type
            inputs (list): List of input data to instruction
        """
        self._instructions.append((instruction_name, *self._instruction_buffer, inputs))
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
        """Apply all instructions to grid

        Raises:
            NameError: If an instruction was not recognized
        """
        for instruction in self._instructions:
            instruction_name, draw_mode, fill_mode, inputs = instruction
            if instruction_name not in self._instructions_map:
                raise NameError(f'Received bad instruction "{instruction_name}"')
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

        decision_parameter = 2 * dy - dx
        y = 0

        for x in range(dx + 1):
            point = (x1 + x * xx + y * yx, y1 + x * xy + y * yy)
            if self._point_within_grid(point):
                self._replace_in_grid(draw_char, point)
            if decision_parameter >= 0:
                y += 1
                decision_parameter -= 2 * dx
            decision_parameter += 2 * dy

    def _plot_circle_points(self, center, deltas, draw_char):
        """A part of Bresenham's Circle Generation algorithm

        Args:
            center (tuple[int, int]): Center of circle
            deltas (tuple[int, int]): Offsets to determine where to draw circle edge points
            draw_char (str): Character to replace on grid
        """
        cx, cy = center
        dx, dy = deltas

        for point in [
            (cx + dx, cy + dy),
            (cx - dx, cx + dy),
            (cx + dx, cy - dy),
            (cx - dx, cy - dy),
            (cx + dy, cy + dx),
            (cx - dy, cy + dx),
            (cx + dy, cy - dx),
            (cx - dy, cy - dx)
        ]:
            if self._point_within_grid(point):
                self._replace_in_grid(draw_char, point)

    def circle(self, draw_mode, fill_mode, inputs):
        """Draw a vector onto the grid using Bresenham's Circle Generation algorithm

        Args:
            draw_mode (str): One of ["draw", "erase"] describing the behavior of the instruction
            fill_mode (bool): True if the instruction will be filled, false if it will only be an outline
            inputs (list): The circle's center point and radius
        """
        draw_char = self.get_draw_char(draw_mode)
        center, radius = inputs[0], inputs[1]

        dx, dy = 0, radius
        decision_parameter = 3 - 2 * radius

        self._plot_circle_points(center, (dx, dy), draw_char)

        while dy >= dx:
            dx += 1

            if decision_parameter > 0:
                dy -= 1
                decision_parameter = decision_parameter + 4 * (dx - dy) + 10
            else:
                decision_parameter = decision_parameter + 4 * dx + 6
            

            self._plot_circle_points(center, (dx, dy), draw_char)
        
        if fill_mode:
            # https://stackoverflow.com/a/24453110/11085206
            radius_squared = radius * radius
            dy = -radius
            while dy <= radius:
                dx = (int)(math.sqrt(radius_squared - dy * dy) + 0.5)
                self.vector(draw_mode, True, [(center[0] - dx, dy + center[1]), (center[0] + dx, dy + center[1])])
                dy += 1

    def square(draw_mode, fill_mode, inputs)
        pass

    def __repr__(self):
        """Get string representation of object

        Returns:
            _type_: _description_
        """
        out = "~" * self._width
        if self._grid:
            out += f"\n{self._identifier}\nGrid:\n{self._grid}\n"
        if self._instructions and self._instructions[0][0] not in ("from_char"):
            out += "Steps:\n"
            for instruction in self._instructions:
                out += (
                    " ".join(
                        [
                            str(instr_subset)
                            if type(instr_subset) != bool
                            else "filled=" + str(instr_subset)
                            for instr_subset in instruction
                        ]
                    )
                    + "\n"
                )
        
        out += "~" * self._width
        return out
