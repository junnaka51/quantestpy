import sys
import unittest
from io import StringIO
from unittest.mock import patch

from quantestpy import PauliCircuit, assert_draw_pauli_circuit
from quantestpy.exceptions import QuantestPyError


class TestAssertDrawCircuit(unittest.TestCase):
    """
    How to execute this test:
    $ pwd
    {Your directory where you git-cloned quantestpy}/quantestpy
    $ python -m unittest \
        test.assertion.draw_pauli_circuit.test_assert_draw_circuit
    ......
    ----------------------------------------------------------------------
    Ran 6 tests in 0.014s

    OK
    $
    """

    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('builtins.input', return_value='')
    def test_regular(self, input):
        pc = PauliCircuit(3)
        pc.add_gate({"name": "x", "control_qubit": [0], "target_qubit": [1],
                     "control_value": [1]})

        self.assertIsNone(
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[0, 1]
            )
        )

        stdout = self.capture.getvalue()
        self.assertIsInstance(stdout, str)

        for i in ["00", "01", "10", "11"]:
            self.assertTrue(i in stdout)

    @patch('builtins.input', return_value='')
    def test_limited_inputs(self, input):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0], "target_qubit": [1],
                     "control_value": [1]})
        pc.add_gate({"name": "swap", "control_qubit": [],
                     "target_qubit": [1, 3], "control_value": []})

        self.assertIsNone(
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[0, 1],
                input_binary_bitstring=["11", "10"]
            )
        )

        stdout = self.capture.getvalue()
        self.assertIsInstance(stdout, str)

        for i in ["10", "11"]:
            self.assertTrue(i in stdout)

        for i in ["00", "01"]:
            self.assertFalse(i in stdout)

    @patch('builtins.input', return_value='')
    def test_qiskit_convention(self, input):
        pc = PauliCircuit(3)
        pc.add_gate({"name": "x", "control_qubit": [0], "target_qubit": [1],
                     "control_value": [1]})

        self.assertIsNone(
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[1, 0]
            )
        )

        stdout = self.capture.getvalue()
        self.assertIsInstance(stdout, str)

        for i in ["00", "01", "10", "11"]:
            self.assertTrue(i in stdout)

    @patch('builtins.input', return_value='')
    def test_draw_phase(self, input):
        pc = PauliCircuit(3)
        pc.add_gate({"name": "x", "control_qubit": [], "target_qubit": [0],
                     "control_value": []})
        pc.add_gate({"name": "y", "control_qubit": [], "target_qubit": [1],
                     "control_value": []})
        pc.add_gate({"name": "z", "control_qubit": [], "target_qubit": [2],
                     "control_value": []})

        self.assertIsNone(
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[0, 1, 2],
                draw_phase=True
            )
        )

        stdout = self.capture.getvalue()
        self.assertIsInstance(stdout, str)

        for i in ["0.0", "0.5", "1.0", "-0.5"]:
            self.assertTrue(i in stdout)


class TestAssertDrawCircuitInput(unittest.TestCase):

    def test_raise_from_invalid_val_type(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0], "target_qubit": [1],
                     "control_value": [1]})
        expected_error_msg = \
            "Element in input_binary_bitstring must be a string."

        with self.assertRaises(QuantestPyError) as cm:
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[0, 1, 2],
                input_binary_bitstring=[111, 101, "001"]
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)

    def test_raise_from_invalid_val_length(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 2], "target_qubit": [1],
                     "control_value": [1, 0]})
        expected_error_msg = \
            "Element 01 in input_binary_bitstring has an invalid length."

        with self.assertRaises(QuantestPyError) as cm:
            assert_draw_pauli_circuit(
                circuit=pc,
                input_reg=[0, 1, 2],
                input_binary_bitstring=["111", "01", "11"]
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)
