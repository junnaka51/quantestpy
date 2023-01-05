import copy
import sys

import numpy as np

from quantestpy.exceptions import QuantestPyError
from quantestpy.simulator.circuit_drawer import CircuitDrawer
from quantestpy.simulator.pauli_circuit import PauliCircuit


class CircuitDrawerGateColoring(CircuitDrawer):
    def __init__(self, pc: PauliCircuit, draw_phase: bool = True):
        super().__init__(pc)
        self._color_code_line_1 = self.get_color_code("green")
        # new attributes
        self._color_code_gate = self.get_color_code("red")
        self._decimals = 2
        self._draw_phase = draw_phase
        self._output_qubit_id_to_color_code \
            = {qubit_id: "" for qubit_id in range(self._num_qubit)}
        self._qubit_id_to_output_reg_name \
            = {qubit_id: "" for qubit_id in range(self._num_qubit)}

    def set_color_to_output_reg(self, color_to_reg: dict) -> None:
        for color, reg in color_to_reg.items():
            self._pc._assert_is_correct_reg(reg)
            for qubit_id in reg:
                self._output_qubit_id_to_color_code[qubit_id] = \
                    self.get_color_code(color)

    def set_name_to_output_reg(self, name_to_reg: dict) -> None:
        for name, reg in name_to_reg.items():
            self._pc._assert_is_correct_reg(reg)
            for qubit_id in reg:
                self._qubit_id_to_output_reg_name[qubit_id] = name

    def is_gate_executed(self, gate_id: int) -> bool:
        gate = self._pc._gates[gate_id]
        if len(gate["control_qubit"]) == 0 or \
                np.all(self._pc._qubit_value[gate["control_qubit"]]
                       == gate["control_value"]):
            return True
        else:
            return False

    @staticmethod
    def get_phase(qubit_phase: float,
                  decimals: int,
                  color_code: str = "") -> str:
        qubit_phase_str = str(np.round(qubit_phase / np.pi, decimals))
        return color_code + qubit_phase_str + "\033[0m"

    def draw_phase(self) -> None:
        """Draws qubit phases in unit of PI.

        ::
        0.5

        0.0
        """
        phase_max_length = 0
        for qubit_phase in self._pc.qubit_phase:
            qubit_phase_str_length = \
                len(self.get_phase(qubit_phase, self._decimals))
            if qubit_phase_str_length > phase_max_length:
                phase_max_length = qubit_phase_str_length

        for line_id in range(self._num_line):
            if line_id in self._line_id_to_qubit_id.keys():
                qubit_id = self._line_id_to_qubit_id[line_id]
                qubit_phase = self._pc.qubit_phase[qubit_id]
                qubit_phase_str = self.get_phase(qubit_phase, self._decimals)
                self._line_id_to_text[line_id] += qubit_phase_str \
                    + self.get_space(phase_max_length-len(qubit_phase_str))
            else:
                self._line_id_to_text[line_id] += self.get_space(
                    length=phase_max_length)

    def draw_final_vector(self) -> None:
        """Draws final state vectors.

        ::
        |1>

        |0>
        """
        super().draw_init_vector()

    def draw_qubit_identifier_at_end(self) -> None:
        """Draws a qubit identifer at the end

        ::
        'out 0'

        '    1'
        """
        reg_name_max_length = 0
        for reg_name in self._qubit_id_to_output_reg_name.values():
            if len(reg_name) > reg_name_max_length:
                reg_name_max_length = len(reg_name)
        if reg_name_max_length > 0:
            reg_name_max_length += 1

        id_max_length = len(str(self._num_qubit-1))
        for line_id in range(self._num_line):
            if line_id in self._line_id_to_qubit_id.keys():
                qubit_id = self._line_id_to_qubit_id[line_id]
                reg_name = self._qubit_id_to_output_reg_name[qubit_id]
                self._line_id_to_text[line_id] += \
                    self._output_qubit_id_to_color_code[qubit_id] \
                    + reg_name \
                    + self.get_space(reg_name_max_length-len(reg_name)) \
                    + str(qubit_id) \
                    + "\033[0m" \
                    + self.get_space(id_max_length+1-len(str(qubit_id)))
            else:
                self._line_id_to_text[line_id] += \
                    self.get_space(id_max_length+1+reg_name_max_length)

    def draw_tgt(self, gate_id: int) -> None:
        """Overrides self.draw_tgt"""
        if self.is_gate_executed(gate_id):
            self._color_code_tgt = self._color_code_gate
        else:
            self._color_code_tgt = ""
        super().draw_tgt(gate_id)

    def draw_ctrl(self, gate_id: int) -> None:
        """Overrides self.draw_ctrl"""
        if self.is_gate_executed(gate_id):
            self._color_code_ctrl = self._color_code_gate
        else:
            self._color_code_ctrl = ""
        super().draw_ctrl(gate_id)

    def draw_wire(self, gate_id: int) -> None:
        """Overrides self.draw_wire"""
        if self.is_gate_executed(gate_id):
            self._color_code_wire = self._color_code_gate
            self._color_code_cross = self._color_code_gate
        else:
            self._color_code_wire = ""
            self._color_code_cross = ""
        super().draw_wire(gate_id)

    def draw_circuit(self) -> None:
        """Overrides self.draw_circuit"""
        super().draw_circuit()
        self.draw_space()
        self.draw_final_vector()
        if self._draw_phase:
            self.draw_space()
            self.draw_phase()
        self.draw_space()
        self.draw_qubit_identifier_at_end()


def assert_draw_pauli_circuit(
        circuit: PauliCircuit,
        input_reg: list,
        input_binary_bitstring: list = [],
        draw_phase: bool = False):

    # check inputs
    PauliCircuit._assert_is_pauli_circuit(circuit)
    circuit._assert_is_correct_reg(input_reg)
    if not isinstance(input_binary_bitstring, list):
        raise QuantestPyError("input_binary_bitstring must be a list.")
    if not isinstance(draw_phase, bool):
        raise QuantestPyError("draw_phase must be bool type.")

    len_input_reg = len(input_reg)
    for element in input_binary_bitstring:
        if not isinstance(element, str):
            raise QuantestPyError(
                "Element in input_binary_bitstring must be a string."
            )
        if len(element) != len_input_reg:
            raise QuantestPyError(
                f"Element {element} in input_binary_bitstring has an invalid "
                "length."
            )

    def _draw_circuit(bitstring: str) -> None:
        # define the circuit
        pc = copy.deepcopy(circuit)
        pc.set_qubit_value(input_reg, [int(i) for i in bitstring])

        # create an instance of CircuitDrawer
        gc = CircuitDrawerGateColoring(pc, draw_phase)
        gc.set_name_to_reg({"in": input_reg})
        gc.draw_circuit()
        length = len(list(gc.line_id_to_text.values()))
        fig = gc.create_single_string()

        # show result
        print(bitstring)
        print(fig)
        input("press enter")
        for _ in range(1+length+1):
            sys.stdout.write("\033[1A\033[2K")
        del pc, gc
        return

    if len(input_binary_bitstring) == 0:
        for decimal_ in range(2**len_input_reg):
            bitstring = \
                ("0" * len_input_reg + bin(decimal_)[2:])[-len_input_reg:]
            _draw_circuit(bitstring)

    else:
        for bitstring in input_binary_bitstring:
            _draw_circuit(bitstring)
