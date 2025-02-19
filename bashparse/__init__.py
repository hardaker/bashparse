from bashparse import variables, commands, ast, functions, template, main, chunk, unroll
import bashlex

parse = bashlex.parse

node = bashlex.ast.node
NodeVisitor = ast.NodeVisitor

DONT_DESCEND = ast.DONT_DESCEND
CONT = ast.CONT
HALT = ast.HALT



at_path = NodeVisitor(None).at_path

children = NodeVisitor(None).children

child = NodeVisitor(None).child

set_children = NodeVisitor(None).set_children

swap_node = ast.NodeVisitor(None).swap_node

remove = ast.NodeVisitor(None).remove

align = ast.NodeVisitor(None).align

justify = ast.NodeVisitor(None).justify



build_alias_table = commands.build_alias_table

resolve_aliasing = commands.resolve_aliasing

build_and_resolve_aliasing = commands.build_and_resolve_aliasing



update_variable_list = variables.update_variable_list

substitute_variables = variables.substitute_variables  
	
add_variable_to_list = variables.add_variable_to_list
	
replace_variables = variables.replace_variables  



build_and_resolve_fns = functions.build_and_resolve_fns

build_fn_table = functions.build_fn_table

resolve_functions = functions.resolve_functions


strip_cmd = unroll.strip_cmd

advanced_unroll = unroll.advanced_unroll



Chunk = chunk.Chunk

find_variable_chunks = chunk.find_variable_chunks

find_cd_chunks = chunk.find_cd_chunks


# Bashtemplate 


Template = template.Template
# The object class

generate_templates = main.generate_templates
    # Takes an array of nodes

generate_useful_templates = main.find_useful_templates

templatize = \
    main.templatize

filter_templates = \
    main.filter_templates








# path_variable = path_variable.path_variable

# find_and_replace_variables = variables.find_and_replace_variables     # replaced with substitute variables

# node_level_regex = regex.node_level_regex

#find_specific_commands = commands.find_specific_commands

#find_specific_command = commands.find_specific_command
	
# return_commands_from_variable_delcaraction = commands.return_commands_from_variable_delcaraction

# return_commands_from_command_substitutions = commands.return_commands_from_command_substitutions

# return_commands_from_for_loops = commands.return_commands_from_for_loops

# shift_tree_pos = ast.shift_ast_pos
	
# shift_tree_pos_to_start = ast.shift_ast_pos_to_start

# return_variable_paths = ast.return_variable_paths

# return_paths_to_node_type = ast.return_paths_to_node_type

# return_nodes_of_type = ast.return_nodes_of_type

# convert_tree_to_string = ast.convert_tree_to_string

# return_node_at_path = ast.return_node_at_path

# build_function_dictionary = functions.build_function_dictionary