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
