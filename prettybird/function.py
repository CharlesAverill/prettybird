from copy import deepcopy
from lark import Tree

import numpy as np


class Function:
    def __init__(self, function_name, parameter_names, statements_tree):
        self.function_name = function_name
        self.parameter_names = parameter_names
        self.statements_tree = statements_tree
        self.instruction_buffer = ()
        self.instructions = []

    def prepare_instruction(self, draw_mode, fill_mode):
        """Prepare the function to receive an instruction declaration

        Args:
            draw_mode (str): One of ["draw", "erase"] describing the behavior of the instruction
            fill_mode (bool): True if the instruction will be filled, false if it will only be an outline

        Raises:
            ValueError: If the instruction buffer is non-empty
        """
        if self.instruction_buffer != ():
            raise ValueError(
                f'Symbol "{self.function_name}" was told to prepare an instruction, but it has not finished parsing the current function!'
            )
        self.instruction_buffer = (draw_mode, fill_mode)

    def add_instruction(self, instruction_name, inputs):
        """Finish adding an instruction to the function's instruction list

        Args:
            instruction_name (str): Name of instruction type
            inputs (list): List of input data to instruction
        """
        self.instructions.append(
            (instruction_name, *self.instruction_buffer, inputs))
        self.instruction_buffer = ()

    def _reduce_argument(self, instruction_arg, function_arguments):
        if type(instruction_arg) == Tree and len(instruction_arg.children) == 1:
            instruction_arg = instruction_arg.children[0].value

        if type(instruction_arg) == str:
            return function_arguments[self.parameter_names.index(instruction_arg)]
        elif type(instruction_arg) in (list, tuple):
            # Expression
            if (
                len(instruction_arg)
                and repr(type(instruction_arg[0])) == "<class 'function'>"
            ):
                x = instruction_arg[0](
                    np.array(
                        self._reduce_argument(
                            instruction_arg[1], function_arguments)
                    ),
                    np.array(
                        self._reduce_argument(
                            instruction_arg[2], function_arguments)
                    ),
                )
                return x
            return [
                self._reduce_argument(arg, function_arguments)
                for arg in instruction_arg
            ]

        return instruction_arg

    def compile(self, width, height, arguments):
        # Local imports because Symbol needs to import Function
        from .symbol import Symbol
        from .utils import get_empty_grid

        # Setup function subspace
        subspace = Symbol(f"{self.function_name}_subspace", 0)
        subspace.grid = get_empty_grid(int(width), int(height))

        if len(arguments) != len(self.parameter_names):
            raise TypeError(
                f"{self.function_name} missing arguments {self.parameter_names[len(arguments):]}"
            )

        for orig_instruction in self.instructions:
            # Don't modify instruction data!
            instruction = deepcopy(orig_instruction)
            instruction_args = instruction[3]
            for i, arg in enumerate(instruction_args):
                instruction_args[i] = self._reduce_argument(arg, arguments)
            subspace.prepare_instruction(instruction[1], instruction[2])
            subspace.add_instruction(instruction[0], instruction[3])

        subspace.compile()

        return subspace.grid
