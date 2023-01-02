import copy
import re
import sys

import numpy as np

from quantestpy.assertion.draw_pauli_circuit import CircuitDrawerGateColoring
from quantestpy.exceptions import QuantestPyAssertionError, QuantestPyError
from quantestpy.simulator.pauli_circuit import PauliCircuit


class CircuitDrawerLabelErrorQubit(CircuitDrawerGateColoring):
    def __init__(self,
                 pc: PauliCircuit,
                 output_reg: list,
                 val_err_reg: list,
                 color_phase: bool,
                 phase_err_reg: list):
        super().__init__(pc, draw_phase=True)
        # new attributes
        self._output_reg = output_reg
        self._val_err_reg = val_err_reg
        self._color_phase = color_phase
        self._phase_err_reg = phase_err_reg
        self._color_code_succeed = self.get_color_code("blue")
        self._color_code_err = self.get_color_code("red")

    def draw_phase(self) -> None:
        """Overrides self.draw_phase"""
        phase_max_length = 0
        for qubit_phase in self._pc.qubit_phase:
            qubit_phase_str_length = \
                len(str(np.round(qubit_phase / np.pi, self._decimals)))
            if qubit_phase_str_length > phase_max_length:
                phase_max_length = qubit_phase_str_length

        for line_id in range(self._num_line):
            if line_id in self._line_id_to_qubit_id.keys():
                qubit_id = self._line_id_to_qubit_id[line_id]
                qubit_phase = self._pc.qubit_phase[qubit_id]
                if qubit_id in self._phase_err_reg and self._color_phase:
                    cc = self._color_code_err
                elif qubit_id in self._output_reg and self._color_phase:
                    cc = self._color_code_succeed
                else:
                    cc = ""
                qubit_phase_str = self.get_phase(
                    qubit_phase, self._decimals, cc)
                self._line_id_to_text[line_id] += qubit_phase_str \
                    + self.get_space(phase_max_length-len(qubit_phase_str))
            else:
                self._line_id_to_text[line_id] += self.get_space(
                    length=phase_max_length)

    def draw_final_vector(self) -> None:
        """Overrides self.draw_final_vector"""
        for line_id in range(self._num_line):
            if line_id in self._line_id_to_qubit_id.keys():
                qubit_id = self._line_id_to_qubit_id[line_id]
                qubit_val = self._pc.qubit_value[qubit_id]
                if qubit_id in self._val_err_reg:
                    cc = self._color_code_err
                elif qubit_id in self._output_reg:
                    cc = self._color_code_succeed
                else:
                    cc = self.get_color_code_line(qubit_val)
                self._line_id_to_text[line_id] += \
                    self.get_init_state(qubit_val=qubit_val, color_code=cc)
            else:
                self._line_id_to_text[line_id] += self.get_space(length=3)


def assert_equal_qubit_value(
        circuit: PauliCircuit,
        input_reg: list,
        output_reg: list,
        input_to_output_expect: dict,
        draw_circuit: bool = False):
    """
    e.g.
    input_to_output_expect = {
        "1000": ("100000", [0,0,0,0,0,0]),
        "1001": "100001"
    }
    """
    # check inputs
    PauliCircuit._assert_is_pauli_circuit(circuit)
    circuit._assert_is_correct_reg(input_reg)
    circuit._assert_is_correct_reg(output_reg)
    if not isinstance(input_to_output_expect, dict):
        raise QuantestPyError("input_to_output_expect must be a dict.")
    if not isinstance(draw_circuit, bool):
        raise QuantestPyError("draw_circuit must be bool type.")

    def _assert_equal(in_bitstring: str,
                      out_bitstring: str,
                      out_phase: list):
        # define the circuit object
        pc = copy.deepcopy(circuit)
        pc.set_qubit_value(input_reg, [int(i) for i in in_bitstring])

        # execute all gates
        pc._execute_all_gates()

        # get output
        out_bitstring_actual = \
            "".join([str(i) for i in pc.qubit_value[output_reg]])
        out_phase_actual = (pc.qubit_phase[output_reg] / np.pi).tolist()

        del pc

        if out_bitstring_actual != out_bitstring:
            return out_bitstring_actual, out_phase_actual
        elif len(out_phase) > 0 and out_phase_actual != out_phase:
            return out_bitstring_actual, out_phase_actual
        else:
            return None

    def _draw_circuit(in_bitstring: str,
                      err_msg: str,
                      val_err_reg: list,
                      color_phase: bool,
                      phase_err_reg: list) -> None:
        # define the circuit
        pc = copy.deepcopy(circuit)
        pc.set_qubit_value(input_reg, [int(i) for i in in_bitstring])

        # create an instance of CircuitDrawer
        gc = CircuitDrawerLabelErrorQubit(
            pc, output_reg, val_err_reg, color_phase, phase_err_reg)
        gc.set_name_to_reg({"in": input_reg})
        gc.set_name_to_output_reg({"out": output_reg})
        gc.draw_circuit()
        length = len(list(gc.line_id_to_text.values()))
        fig = gc.create_single_string()

        # show result
        err_msg_len = len(re.findall(r"\n{1}", err_msg)) + 1
        print(err_msg)
        print(fig)
        input("press enter")
        for _ in range(err_msg_len+length+1):
            sys.stdout.write("\033[1A\033[2K")
        del pc, gc
        return

    len_input_reg = len(input_reg)
    len_output_reg = len(output_reg)

    for in_bitstring, out_expect in input_to_output_expect.items():
        # check input type
        if not isinstance(in_bitstring, str):
            raise QuantestPyError("Input must be a binary bitstring.")
        if len(in_bitstring) != len_input_reg:
            raise QuantestPyError("Input bitstring has an invalid length.")

        # check output type
        if not isinstance(out_expect, str) and \
                not isinstance(out_expect, tuple):
            raise QuantestPyError(
                "Output_expect must be either a binary bitstring or a tuple of"
                " having both a binary bitstring and a list of qubit phases."
            )

        if isinstance(out_expect, str):
            out_bitstring = out_expect
            out_phase = []
        else:
            out_bitstring, out_phase = out_expect
            if not isinstance(out_phase, list):
                raise QuantestPyError(
                    "qubit phases must be given by a list in a tuple."
                )
            if len(out_phase) != len_output_reg:
                raise QuantestPyError(
                    "List of qubit phases has an invalid length."
                )

        if len(out_bitstring) != len_output_reg:
            raise QuantestPyError("Output bitstring has an invalid length.")

        result_from_assert_equal = _assert_equal(in_bitstring,
                                                 out_bitstring,
                                                 out_phase)

        if result_from_assert_equal is not None:
            out_bitstring_actual, out_phase_actual = result_from_assert_equal

            err_msg = f"In bitstring: {in_bitstring}\n" \
                + f"Out bitstring expect: {out_bitstring}\n" \
                + f"Out bitstring actual: {out_bitstring_actual}"

            if len(out_phase) > 0:
                err_msg += f"\nOut phase expect: {out_phase}\n" \
                    + f"Out phase actual: {out_phase_actual}"

            if draw_circuit:
                # correct err qubit ids
                val_err_reg, phase_err_reg = [], []
                color_phase = False
                for i, (j, k) in enumerate(
                        zip(out_bitstring, out_bitstring_actual)):
                    if j != k:
                        val_err_reg.append(output_reg[i])

                if len(out_phase) > 0:
                    color_phase = True
                    for i, (j, k) in enumerate(
                            zip(out_phase, out_phase_actual)):
                        if j != k:
                            phase_err_reg.append(output_reg[i])

                _draw_circuit(
                    in_bitstring,
                    err_msg,
                    val_err_reg,
                    color_phase,
                    phase_err_reg)

            else:
                raise QuantestPyAssertionError(err_msg)
