import unittest

from quantestpy import TestCircuit


class TestAddQubitAnnotation(unittest.TestCase):
    """
    How to execute this test:
    $ pwd
    {Your directory where you git-cloned quantestpy}/quantestpy
    $ python -m unittest test.simulator.test_circuit.test_add_qubit_annotation
    ....
    ----------------------------------------------------------------------
    Ran 4 tests in 0.001s

    OK
    $
    """

    def test_initial(self,):
        tc = TestCircuit(4)
        expect = {0: {}, 1: {}, 2: {}, 3: {}}
        actual = tc.qubit_annotation
        self.assertEqual(actual, expect)

    def test_one_qubit(self,):
        tc = TestCircuit(4)
        tc.add_qubit_annotation(
            qubit_id_list=[1],
            key="register_name",
            value="register_hoge"
        )
        expect = {0: {},
                  1: {"register_name": "register_hoge"},
                  2: {},
                  3: {}}
        actual = tc.qubit_annotation
        self.assertEqual(actual, expect)

    def test_multi_qubit(self,):
        tc = TestCircuit(5)
        tc.add_qubit_annotation(
            qubit_id_list=[0, 2, 4],
            key="register_id",
            value=1
        )
        expect = {0: {"register_id": 1},
                  1: {},
                  2: {"register_id": 1},
                  3: {},
                  4: {"register_id": 1}}
        actual = tc.qubit_annotation
        self.assertEqual(actual, expect)

    def test_multi_exec(self,):
        tc = TestCircuit(5)
        tc.add_qubit_annotation(
            qubit_id_list=[1, 2],
            key="register_name",
            value="register_hoge"
        )
        tc.add_qubit_annotation(
            qubit_id_list=[0, 2, 4],
            key="register_id",
            value=1
        )
        expect = {0: {"register_id": 1},
                  1: {"register_name": "register_hoge"},
                  2: {"register_name": "register_hoge", "register_id": 1},
                  3: {},
                  4: {"register_id": 1}}
        actual = tc.qubit_annotation
        self.assertEqual(actual, expect)
