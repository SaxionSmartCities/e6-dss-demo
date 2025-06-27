import pysmile
from pysmile import SMILEException

"""
Prints information about the nodes in a network.
"""

debug = False

NODE_TYPES = {
    pysmile.NodeType.CPT: 'CPT',
    pysmile.NodeType.EQUATION: 'EQUATION',
    pysmile.NodeType.MAU: 'MAU',
    pysmile.NodeType.DECISION: 'DECISION',
    pysmile.NodeType.DEMORGAN: 'DEMORGAN',
    pysmile.NodeType.NOISY_MAX: 'NOISY_MAX',
    pysmile.NodeType.TRUTH_TABLE: 'TRUTH_TABLE',
    pysmile.NodeType.UTILITY: 'UTILITY',
}

class SmileInfo:
    def __init__(self, net):
        self.net = net
        # print(*dir(net), sep='\n')

    def print_network_info(self):
        print(f"Network name: {self.net.get_name()}")
        print(f"Number of nodes: {self.net.get_node_count()}")
        print("Dump Network")
        for h in self.net.get_all_nodes():
            self.print_node_info(h)


    def get_node_type_name(self, node_handle):
        try:
            node_type = self.net.get_node_type(node_handle)
            return NODE_TYPES[node_type]
        except SMILEException as e:
            print(f"Error {e}")
            return "UNKNOWN"

    def _get_node_basic_info(self, node_handle):
        """Helper method to retrieve basic node information"""
        try:
            return {
                'type': self.net.get_node_type(node_handle),
                'typename': self.get_node_type_name(node_handle),
                'id': self.net.get_node_id(node_handle),
                'name': self.net.get_node_id(node_handle),
            }
        except SMILEException as e:
            print(f"Error retrieving node info: {e}")
            return None

    def print_node_info_by_id(self, node_id):
        """Prints information about a node in the network by its node id"""
        node_handle = self.net.get_node(node_id)
        if debug:
            print(f'Node {node_id} --> {node_handle}')
        self.print_node_info(node_handle)

    def print_node_info(self, node_handle):
        # try:
        node_type = self.net.get_node_type(node_handle)
        node_name = self.net.get_node_id(node_handle)
        match node_type:
            case pysmile.NodeType.EQUATION:
                self.print_equation_stats(node_handle)
            case pysmile.NodeType.CPT:
                self.print_node_definition(node_handle)
            case pysmile.NodeType.TRUTH_TABLE:
                self.print_node_definition(node_handle)
            case _:
                print(f"Node {node_handle} {node_name} is of an unsupported type {node_type} {self.get_node_type_name(node_handle)}.")
        # except SMILEException as e:
        #     print(f"Error {e}")

    # def print_truth_table_info(self, net, node_handle):
    #     print(f"{self.get_node_type_name(node_handle)} Node id/name: {self.net.get_node_id(node_handle)}/{self.net.get_node_name(node_handle)}")
    #     node_id = self.net.get_node_id(node_handle)
    #     print(self.net.get_result_string(node_handle))

    def print_equation_stats(self, node_handle):
        print(f"{self.get_node_type_name(node_handle)} Node id/name: {self.net.get_node_id(node_handle)}/{self.net.get_node_name(node_handle)}")
        node_id = self.net.get_node_id(node_handle)
        if self.net.is_evidence(node_handle):
            v = self.net.get_cont_evidence(node_handle)
            print(f"\tEvidence set: {v}")
        elif self.net.is_value_discretized(node_handle):
            iv = self.net.get_node_equation_discretization(node_handle)
            bounds = self.net.get_node_equation_bounds(node_handle)
            disc_beliefs = self.net.get_node_value(node_handle)
            lo = bounds[0]
            for i in range(0, len(disc_beliefs)):
                hi = iv[i].boundary
                id = iv[i].id
                if disc_beliefs[i] > 0:
                    print(f"\tP({node_id} {(id + ' ') if len(id) > 0 else ''}in {lo}..{hi}) = {disc_beliefs[i]}")
                lo = hi
        # elif self.net.is_value_valid(node_handle):
        else:
            stats = self.net.get_node_sample_stats(node_handle)
            print(f"\tmean={stats[0]:.3f} stddev={stats[1]:.3f} min={stats[2]:.3f} max={stats[3]:.3f}")
        # else:
        #     print(f"{node_id} has no statistics.")

    def print_node_definition(self, node_handle):
        print(f"{self.get_node_type_name(node_handle)} Node id/name: {self.net.get_node_id(node_handle)}/{self.net.get_node_name(node_handle)}")
        print(f"  Outcomes: {' '.join(self.net.get_outcome_ids(node_handle))}")
        parent_ids = self.net.get_parent_ids(node_handle)
        if len(parent_ids) > 0:
            print(f"  Parents: {' '.join(parent_ids)}")
        child_ids = self.net.get_child_ids(node_handle)
        if len(child_ids) > 0:
            print(f"  Children: {' '.join(child_ids)}")
        self.print_cpt_matrix(node_handle)

    def print_cpt_matrix(self, node_handle):
        cpt = self.net.get_node_definition(node_handle)
        parents = self.net.get_parents(node_handle)
        dim_count = 1 + len(parents)
        dim_sizes = [0] * dim_count
        for i in range(0, dim_count - 1):
            dim_sizes[i] = self.net.get_outcome_count(parents[i])
        dim_sizes[len(dim_sizes) - 1] = self.net.get_outcome_count(node_handle)
        coords = [0] * dim_count
        # print(f"len(parents) = {len(parents)}, len(coords = {len(coords)}) ")
        for elem_idx in range(0, len(cpt)):
            self.index_to_coords(elem_idx, dim_sizes, coords)
            outcome = self.net.get_outcome_id(node_handle, coords[dim_count - 1])
            prob = cpt[elem_idx]
            if prob > 0:
                print(f"\tP({outcome}", end="")
                if dim_count > 1:
                    print(" | ", end="")
                    for parent_idx in range(0, len(parents)):
                        if parent_idx > 0:
                            print(", ", end="")
                        parent_handle = parents[parent_idx]
                        parent_outcome_count = self.net.get_outcome_count(parent_handle)
                        if parent_outcome_count > 0:
                            outcome = self.net.get_outcome_id(parent_handle, coords[parent_idx])
                        else:
                            outcome = ''
                            iv = self.net.get_node_equation_discretization(parent_handle)
                            bounds = self.net.get_node_equation_bounds(parent_handle)
                            disc_beliefs = self.net.get_node_value(parent_handle)
                            lo = bounds[0]
                            for i in range(0, len(disc_beliefs)):
                                hi = iv[i].boundary
                                id = iv[i].id
                                # if disc_beliefs[i] > 0:
                                outcome = outcome + f"{(id + ' ') if len(id) > 0 else ''}in {lo}..{hi}) = {disc_beliefs[i]}"
                                lo = hi

                        print(f"{self.net.get_node_id(parent_handle)} = {outcome}", end="")
                print(f") = {prob}")

    def index_to_coords(self, index, dim_sizes, coords):
        prod = 1
        for i in range(len(dim_sizes) - 1, -1, -1):
            coords[i] = int(index / prod) % dim_sizes[i]
            prod *= dim_sizes[i]

    def get_posteriors_by_id(self, node_id, state = None):
        results = dict()
        node_handle = self.net.get_node(node_id)
        if not self.net.is_evidence(node_handle) and self.net.is_value_valid(node_handle):
            posteriors = self.net.get_node_value(node_handle)
            for i in range(0, len(posteriors)):
                outcome_id = self.net.get_outcome_id(node_handle, i)
                if state is None or state == outcome_id:
                    results[outcome_id] = posteriors[i]
        return results

    def print_posteriors(self, node_handle, state = None):
        node_id = self.net.get_node_id(node_handle)
        if self.net.is_evidence(node_handle):
            print(f"{node_id} has evidence set ({self.net.get_evidence_id(node_handle)})")
        else:
            posteriors = self.net.get_node_value(node_handle)
            for i in range(0, len(posteriors)):
                outcome_id = self.net.get_outcome_id(node_handle, i)
                if state is None or state == outcome_id:
                    print(f"P({node_id} = {outcome_id}) = {posteriors[i]}")

    def print_posteriors_by_id(self, node_id, state = None):
        node_handle = self.net.get_node(node_id)
        self.print_posteriors(node_handle, state)

    def list_outcome_ids(self, node_id):
        node_handle = self.net.get_node(node_id)
        return self.net.get_outcome_ids(node_handle)

    def get_posterior(self, node_id, outcome_id):
        node_handle = self.net.get_node(node_id)
        posterior = None
        if self.net.is_evidence(node_handle):
            posterior = 1.0 if self.net.get_evidence_id(node_handle) == outcome_id else 0.0
        elif self.net.is_value_valid(node_handle):
            posteriors = self.net.get_node_value(node_handle)
            # Filter the list and lookup the first (and only) index for a matching outcome_id
            ix = next(filter(lambda i: self.net.get_outcome_id(node_handle, i) == outcome_id, range(0, len(posteriors))))
            posterior = posteriors[ix]
        return posterior

    def set_evidence(self, node_id, outcome_id):
        node_handle = self.net.get_node(node_id)
        # if self.net.is_propagated_evidence(node_handle):
        #     print("Cannot modify evidence, evidence propagation is active.")
        if outcome_id:
            self.net.set_evidence(node_handle, outcome_id)
        else:
            self.net.clear_evidence(node_handle)

    def set_cont_evidence(self, node_id, value):
        node_handle = self.net.get_node(node_id)
        if value is not None:
            self.net.set_cont_evidence(node_handle, value)
        else:
            self.net.clear_evidence(node_handle)

    def update_beliefs(self):
        print("Updating beliefs...")
        self.net.update_beliefs()

    def has_propagated_evidence(self, node_id):
        node_handle = self.net.get_node(node_id)
        return self.net.is_propagated_evidence(node_handle)

    def get_evidence(self, node_id):
        node_handle = self.net.get_node(node_id)
        return self.net.get_evidence_id(node_handle)

    def has_evidence(self, node_id):
        node_handle = self.net.get_node(node_id)
        return self.net.is_evidence(node_handle)

