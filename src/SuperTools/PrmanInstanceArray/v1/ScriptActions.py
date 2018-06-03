from Katana import NodegraphAPI

# Some helpers functions coming from Foundry's code examples
def FnAddNodeReferenceParam(destNode, paramName, node):
    param = destNode.getParameter(paramName)
    if not param:
        param = destNode.getParameters().createChildString(paramName, "")
    
    param.setExpression("getNode(%r).getNodeName()" % node.getName())

def FnLayoutInputNodes(node):
    spacing = (200, 100)
    pos = NodegraphAPI.GetNodePosition(node)
    x = pos[0] - (spacing[0] * (node.getNumInputPorts()-1))/2
    y = pos[1] + spacing[1]

    for port in node.getInputPorts():
        if port.getNumConnectedPorts():
            inputNode = port.getConnectedPort(0).getNode()
            
            if inputNode != node.getParent():
                NodegraphAPI.SetNodePosition(inputNode, (x, y))
                FnLayoutInputNodes(inputNode)
        
        x += spacing[0]