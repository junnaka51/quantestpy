import sys
import unittest
from io import StringIO
from unittest.mock import patch

from quantestpy import PauliCircuit, assert_equal_qubit_value
from quantestpy.exceptions import QuantestPyAssertionError, QuantestPyError


class TestAssertEqualQubitVal(unittest.TestCase):
    """
    How to execute this test:
    $ pwd
    {Your directory where you git-cloned quantestpy}/quantestpy
    $ python -m unittest \
        test.assertion.equal_qubit_value.test_assert_equal_qubit_value
    .......
    ----------------------------------------------------------------------
    Ran 7 tests in 0.010s

    OK
    $
    """

    def test_return_none(self,):

        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})
        pc.add_gate({"name": "y", "control_qubit": [0, 2], "target_qubit": [3],
                    "control_value": [1, 1]})

        for draw_circuit in [True, False]:
            self.assertIsNone(
                assert_equal_qubit_value(
                    circuit=pc,
                    input_reg=[0, 1],
                    output_reg=[2, 3],
                    input_to_output_expect={
                        "00": "00",
                        "01": "00",
                        "10": "00",
                        "11": "11"
                    },
                    draw_circuit=draw_circuit
                )
            )

    def test_return_assert_error(self,):

        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})
        pc.add_gate({"name": "y", "control_qubit": [0, 2], "target_qubit": [3],
                    "control_value": [1, 0]})

        expected_error_msg = "In bitstring: 10\n" \
            + "Out bitstring expect: 00\n" \
            + "Out bitstring actual: 01"

        with self.assertRaises(QuantestPyAssertionError) as cm:
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1],
                output_reg=[2, 3],
                input_to_output_expect={
                    "00": "00",
                    "01": "00",
                    "10": "00",
                    "11": "11"
                }
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)


class TestAssertEqualQubitValDrawCirc(unittest.TestCase):

    def setUp(self):
        self.capture = StringIO()
        sys.stdout = self.capture

    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('builtins.input', return_value='')
    def test_assert_error(self, input):

        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})
        pc.add_gate({"name": "y", "control_qubit": [0, 2], "target_qubit": [3],
                    "control_value": [1, 0]})

        self.assertIsNone(
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1],
                output_reg=[2, 3],
                input_to_output_expect={
                    "00": "00",
                    "01": "00",
                    "10": "00",  # error
                    "11": "11"  # error
                },
                draw_circuit=True
            )
        )

        stdout = self.capture.getvalue()
        self.assertIsInstance(stdout, str)

        for i in ["In bitstring: 10", "In bitstring: 11"]:
            self.assertTrue(i in stdout)


class TestAssertEqualQubitValInput(unittest.TestCase):

    def test_raise_from_invalid_input_type(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})
        pc.add_gate({"name": "z", "control_qubit": [], "target_qubit": [2],
                    "control_value": []})
        pc.add_gate({"name": "y", "control_qubit": [0, 2], "target_qubit": [3],
                    "control_value": [1, 0]})

        expected_error_msg = "Input must be a binary bitstring."

        with self.assertRaises(QuantestPyError) as cm:
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1],
                output_reg=[2, 3],
                input_to_output_expect={11: "00"}
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)

    def test_raise_from_invalid_input_length(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})

        expected_error_msg = "Input bitstring has an invalid length."

        with self.assertRaises(QuantestPyError) as cm:
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1, 3],
                output_reg=[2],
                input_to_output_expect={"11": "0"}
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)

    def test_raise_from_invalid_output_type(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})

        expected_error_msg = \
            "Output_expect must be either a binary bitstring or a tuple of" \
            + " having both a binary bitstring and a list of qubit phases."

        with self.assertRaises(QuantestPyError) as cm:
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1, 3],
                output_reg=[2],
                input_to_output_expect={
                    "111": ["1", [0.5]]
                }
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)

    def test_raise_from_invalid_output_bitstring_length(self,):
        pc = PauliCircuit(4)
        pc.add_gate({"name": "x", "control_qubit": [0, 1], "target_qubit": [2],
                    "control_value": [1, 1]})
        pc.add_gate({"name": "x", "control_qubit": [], "target_qubit": [3],
                    "control_value": []})

        expected_error_msg = "Output bitstring has an invalid length."

        with self.assertRaises(QuantestPyError) as cm:
            assert_equal_qubit_value(
                circuit=pc,
                input_reg=[0, 1],
                output_reg=[2, 3],
                input_to_output_expect={"11": "1"}
            )

        self.assertEqual(cm.exception.args[0], expected_error_msg)
