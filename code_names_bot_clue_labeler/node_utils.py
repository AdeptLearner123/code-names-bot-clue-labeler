def get_key(item_type, data):
    return f"{item_type}|{data}"


def parse_node(node):
    return node.split("|")