from comp import *

from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator, MCMT, ZGate, WeightedAdder, IntegerComparator


# DRAFT!!!!

# from qiskit_ibm_runtime import QiskitRuntimeService
# from qiskit_ibm_runtime import SamplerV2 as Sampler

# To run on hardware, select the backend with the fewest number of jobs in the queue
# service = QiskitRuntimeService(channel="ibm_quantum")
# backend = service.least_busy(operational=True, simulator=False)
# backend.name

# https://learning.quantum.ibm.com/tutorial/grovers-algorithm

# https://docs.quantum.ibm.com/api/qiskit/circuit_library
# https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.WeightedAdder
# https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.IntegerComparator

# https://egrettathula.wordpress.com/2023/04/18/efficient-quantum-comparator-circuit/

type Weights = list[int]

class GroverComputer(Computer):
    def __init__(self, threshold):
        self.threshold = threshold

    def extract_weights(formula: Sum, acc: Weights = []) -> Weights:
        while True:
            match formula:
                case Sum(Zero(), Mul(x, name)):
                    return x + acc
                case Sum(next, Mul(x, name)):
                    formula = next
                    acc = x + acc

    def build_curcuit(formula: Sum) -> QuantumCircuit:
        qnum = len(Computer.extract_vars(formula))

        oracle = QuantumCircuit(qnum)

        adder = WeightedAdder(qnum, extract_weights(formula))
        comp = IntegerComparator(qnum, self.threshold, geq=True, name='Comparator')
        
        oracle.h(qnum)
        oracle.append(adder)
        oracle.append(comp)

        oracle.compose(MCMT(ZGate(), qnum - 1, 1), inplace=True)

        qc = QuantumCircuit(qnum)
        grover_op = GroverOperator(oracle)

        qc.h(range(grover_op.num_qubits))

        qc.compose(grover_op.power(optimal_num_iterations), inplace=True)

        qc.measure_all()
        return qc

    def maximize(self, formula: Sum) -> VarState:
        qc = GroverComputer.build_curcuit(formula)
        from qiskit import transpile
        from qiskit_aer import AerSimulator
 
        simulator = AerSimulator()
 
        circ = transpile(qc, backend=simulator)
        job = simulator.run(circ)
        result = list(sorted(job.result().get_counts())[0]).map(lambda x: 1 if x == '1' else 0)
        names = computer.extract_vars(formula)
        return {names[i]: result[i] for i in range(len(names))}
        

    