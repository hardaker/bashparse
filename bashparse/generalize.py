import re, bashparse

def run_generalize_nodes(generalize_nodes):
    # return basic_generalization(generalize_nodes)
    return parameter_tracking_generalization(generalize_nodes)
    #return variable_tracking_generalization(generalize_nodes)


def basic_generalization(generalize_nodes):
    # Basic replacement. 
    # Variables are not taken into account in this one
    # The use of local is not accounted for with this
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    for node in generalize_nodes:
        if node.kind == 'word':
            node.word = '%s'
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    node.parts[0].word = "%d=%s"
                for i in range(1, len(node.parts)):
                    node.parts[i].word = "%s"
            else:
                for part in node.parts:
                    basic_generalization(part)
                
        if hasattr(node, 'list'):
            for part in node.list:
                basic_generalization(part)
        if hasattr(node,'command'):
            basic_generalization(node.command)
        if hasattr(node, 'output'):
            basic_generalization(node.output)

            for i in range(1, len(node.parts)): node.parts[i].word = "%d"
    return generalize_nodes


def parameter_tracking_generalization(generalize_nodes):
    """ This replacement scheme tracks the parameters used to show any consistency 
    amoung the arguments. Start the parameter count at 0 and go up from there 
    referencing a dictionary to maintain internal consistency
    The number shouldn't matter but the pattern of the numbers will """
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    params_used = {}
    param_num = 0
    for node in generalize_nodes:
        if node.kind == 'word':
            if node.word not in params_used: 
                params_used[node.word] = str(param_num) 
                param_num += 1
            node.word = '%' + params_used[node.word]
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    # Should the variable assignments always be different? I think yes
                    # What about the values that are assigned?
                    value_assigned = node.parts[0].word.split('=', 1)[1]
                    if value_assigned not in params_used:
                        params_used[value_assigned] = param_num 
                        param_num += 1
                    node.parts[0].word = "%d=%" + str(params_used[value_assigned])
                for i in range(1, len(node.parts)):
                    if hasattr(node.parts[i], 'word'):
                        if node.parts[i].word not in params_used: 
                            params_used[node.parts[i].word] = str(param_num) 
                            param_num += 1
                        node.parts[i].word = '%' + str(params_used[node.parts[i].word])
            else:
                for part in node.parts:
                    parameter_tracking_generalization(part)
                
        if hasattr(node, 'list'):
            for part in node.list:
                parameter_tracking_generalization(part)
        if hasattr(node,'command'):
            parameter_tracking_generalization(node.command)
        if hasattr(node, 'output'):
            parameter_tracking_generalization(node.output)

            for i in range(1, len(node.parts)): 
                if node.parts[i].word not in params_used: 
                    params_used[node.parts[i].word] = str(param_num) 
                    param_num += 1
                node.parts[i].word = '%' + params_used[node.parts[i].word]
    return generalize_nodes


def variable_tracking_generalization(generalize_nodes, params_used = {}, param_num = 0):
    """ This funciton tracks the variable usage through the 
    """
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    for node in generalize_nodes:
        if node.kind == 'word':
            if node.word not in params_used: 
                params_used[node.word] = str(param_num) 
                param_num += 1
            node.word = '%' + params_used[node.word]
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    # Theres no reason we can't use the param number here
                    # Should the variable assignments always be different? I think yes
                    # What about the values that are assigned?
                    variable_name, value_assigned = node.parts[0].word.split('=', 1)
                    # We should also assume its unrolled
                    if value_assigned not in params_used:
                        params_used[value_assigned] = str(param_num) 
                        param_num += 1
                    
                    params_used['$'+variable_name] = str(param_num) 
                    param_num += 1
                    
                    node.parts[0].word = "%" + params_used['$'+variable_name] +"=%" + params_used[value_assigned]
                for i in range(1, len(node.parts)):
                    node.parts = variable_tracking_generalization(node.parts[1:], params_used, param_num)

            else:
                for part in node.parts:
                    if part.kind != 'parameter':
                        parameter_tracking_generalization(part)
                    elif '$'+part.value in params_used:
                        node.word = node.word.replace(part.value, '%'+params_used['$'+part.value])
                        node.parts.remove(part)

        if hasattr(node, 'list'):
            for part in node.list:
                parameter_tracking_generalization(part)
        if hasattr(node,'command'):
            parameter_tracking_generalization(node.command)
        if hasattr(node, 'output'):
            parameter_tracking_generalization(node.output)

            for i in range(1, len(node.parts)): 
                if node.parts[i].word not in params_used: 
                    params_used[node.parts[i].word] = str(param_num) 
                    param_num += 1
                node.parts[i].word = '%' + params_used[node.parts[i].word]
    return generalize_nodes


def is_url(string):
    return  len(re.findall(
            r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", \
            string))

def is_path(string):
    return len(re.findall(r"^(/[^/ ]*)+/?$", string))

def interpret_string(word):
    str_type = 'd'  # data / undefined

    if word[0] == '-': str_type = 'f'  # flag
    elif word[0:2] == '$(': str_type = 's'  # command substitution 
    elif word[0] == '$': str_type = 'v'  # variable
    elif is_url(word): str_type = 'u'  # url
    elif is_path(word): str_type = 'p'  # path

    return '%s-' + str_type

def context_based_generalization(generalize_ndoes):
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    for node in generalize_nodes:
        if node.kind == 'word':
            node.word = interpret_string(node.word)
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    value_assigned = node.parts[0].word.split('=', 1)[1]
                    node.parts[0].word = "%d=%" + interpret_string(value_assigned)
                for i in range(1, len(node.parts)):
                    node.parts[i].word = '%' + interpret_string(node.parts[i].word)
            else:
                for part in node.parts:
                    parameter_tracking_generalization(part)
                
        if hasattr(node, 'list'):
            for part in node.list:
                parameter_tracking_generalization(part)
        if hasattr(node,'command'):
            parameter_tracking_generalization(node.command)
        if hasattr(node, 'output'):
            parameter_tracking_generalization(node.output)

    return generalize_nodes
