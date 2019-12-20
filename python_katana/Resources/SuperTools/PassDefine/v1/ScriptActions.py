from Katana import (
    NodegraphAPI
)


def change_node_layout(node, x_spacing=200, y_spacing=100):
    pos_x, pos_y = NodegraphAPI.GetNodePosition(node)

    # Start far enough to the left to leave room for all the node's inputs
    new_pos_x = pos_x - (x_spacing * (node.getNumInputPorts() - 1)) / 2
    new_pos_y = pos_y + y_spacing

    for input_port in node.getInputPorts():
        if input_port.getNumConnectedPorts():
            input_node = input_port.getConnectedPort(0).getNode()

            # Stop if we hit our own parent - this means the connection leaves
            # the GroupNode we're in
            if input_node != node.getParent():
                NodegraphAPI.SetNodePosition(input_node, (new_pos_x, new_pos_y))

                # Recursively call this function
                change_node_layout(input_node, x_spacing, y_spacing)

        new_pos_x += x_spacing


def add_node_reference_param(dest_node, dest_node_param_name, node):
    # Get or create the parameter on the given node
    dest_node_param = dest_node.getParameter(dest_node_param_name)

    if not dest_node_param:
        dest_node_param = dest_node.getParameters().createChildString(dest_node_param_name, "")

    # Set the expression to point to the node name
    dest_node_param.setExpression("getNode('{node_name}').getNodeName()".format(node_name=node.getName()))


def get_reference_node(node, key):
    parameter = node.getParameter("node_" + key)

    if not parameter:
        return None

    return NodegraphAPI.GetNode(parameter.getValue(0))
