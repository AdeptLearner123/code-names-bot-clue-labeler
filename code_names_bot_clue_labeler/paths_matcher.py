from collections import namedtuple

Rule = namedtuple("Rule", "node_types min_times max_times include_out include_in")

def match_paths(graph, source, rules, target=None, cutoff=None):
    rules = [ rule_to_tuple(rule) for rule in rules ]
    rules = [ rule for rule in rules if rule.max_times > 0 ]
    return match_paths_helper(graph, [source], rules, target, cutoff)


def rule_to_tuple(rule):
    if "node_types" in rule:
        node_types = rule["node_types"]
    else:
        node_types = rule["node_type"]
    
    min_times = 1
    max_times = 1
    if "times" in rule:
        min_times = rule["times"]
        max_times = rule["times"]
    else:
        if "max_times" in rule:
            max_times = rule["max_times"]
        if "min_times" in rule:
            min_times = rule["min_times"]
    
    include_out = not rule["in_only"] if "in_only" in rule else True
    include_in = not rule["out_only"] if "out_only" in rule else True

    return Rule(node_types, min_times, max_times, include_out, include_in)


def match_paths_helper(graph, current_path, rules, target = None, cutoff = None):
    curr_node = current_path[-1]
    #print("Calling helper", current_path, rules, cutoff, curr_node, target, curr_node == target)

    if len(rules) == 0:
        if target is None or curr_node == target:
            return [current_path]
        return []

    if cutoff is not None and len(current_path) == cutoff:
        return []

    curr_rule = rules[0]
    node_types, min_times, max_times, include_out, include_in = curr_rule
    paths = []

    if min_times <= 0:
        # If the min requirement has been satisfied, can skip this rule
        paths += match_paths_helper(graph, current_path, rules[1:], target, cutoff)

    if max_times > 0:
        # If max requirement is still satisfied, apply rule again  
        updated_rule = Rule(node_types, min_times - 1, max_times - 1, include_out, include_in)
        updated_rules = rules[1:] if updated_rule.max_times <= 0 else [updated_rule] + rules[1:]
 
        edge_nodes = []
        if include_out:
            edge_nodes += [ out_node for _, out_node in graph.out_edges(curr_node )]
        if include_in:
            edge_nodes += [ in_node for in_node, _ in graph.in_edges(curr_node) ]

        for edge_node in edge_nodes:
            if edge_node in current_path:
                continue

            node_key = edge_node.split("|")[0]
            
            if node_key not in node_types:
                continue

            paths += match_paths_helper(graph, current_path + [edge_node], updated_rules, target, cutoff)
    
    return paths