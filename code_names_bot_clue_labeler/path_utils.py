def path_to_key(graph, path):
    path_str = ""
    for i, node in enumerate(path):
        path_str += node

        if i < len(path) - 1:
            next_node = path[i + 1]
            if next_node in graph.successors(node):
                path_str += " --> "
            else:
                path_str += " <-- "
    return path_str


def key_to_path(path_key):
    return path_key.replace(" --> ", " <-- ").split(" <-- ")
