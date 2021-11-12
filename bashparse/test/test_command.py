from unittest import TestCase
from bashparse.commands import *
import bashlex, bashparse

class TestVariables(TestCase):

	def test_find_specific_commands(self):
		self.assertRaises(ValueError, find_specific_commands, 'this', ['str'], {}, bool)
		self.assertRaises(ValueError, find_specific_commands, bashlex.parse('this'), [1], {}, bool)
		self.assertRaises(ValueError, find_specific_commands, bashlex.parse('this'), 'str', {}, bool)
		self.assertRaises(ValueError, find_specific_commands, bashlex.parse('this'), ['str'], [], bool)
		self.assertRaises(ValueError, find_specific_commands, bashlex.parse('this'), ['str'], {}, 'str')
		# Test returning as string works fine
		command_string = "wget website.com"
		nodes = bashlex.parse(command_string)
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": ['wget website.com']}
		saved_command_dictionary = find_specific_commands(nodes[0], commands_looking_for, {}, True)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		# Test returning as node works fine
		command_string = "wget website.com"
		nodes = bashlex.parse(command_string)
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": [nodes[0]]}
		saved_command_dictionary = find_specific_commands(nodes[0], commands_looking_for, {}, False)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		# Verify that command substitutions work correctly
		command_string = "$(wget website.com)"
		nodes = bashlex.parse(command_string)
		command_substitution = nodes[0].parts[0].parts[0]
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": ['wget website.com']}
		saved_command_dictionary = find_specific_commands(command_substitution, commands_looking_for, {}, True)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		# Test that compound nodes are parsed well
		command_string = "for a in $n\n do\n wget website.com\n wget othercite.com\n done"
		nodes = bashlex.parse(command_string)
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": ['wget website.com','wget othercite.com']}
		saved_command_dictionary = find_specific_commands(nodes[0], commands_looking_for, {}, True)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		# Piggy back off the old results to make sure pure for loops work as well
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": ['wget website.com','wget othercite.com']}
		saved_command_dictionary = find_specific_commands(nodes[0].list[0], commands_looking_for, {}, True)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		# Veryify that list nodes are parsed correctly
		command_string = "wget website.com; cd here; wget othercite2.com"
		nodes = bashlex.parse(command_string)
		commands_looking_for = ['wget']
		expected_results_dictionary = {"wget": ['wget website.com','wget othercite2.com']}
		saved_command_dictionary = find_specific_commands(nodes[0], commands_looking_for, {}, True)
		self.assertTrue(expected_results_dictionary == saved_command_dictionary)
		
	def test_return_commands_from_variable_delcaraction(self):
		self.assertRaises(ValueError, return_commands_from_variable_delcaraction, 'this')
		# Verify that it works for a regular assignment node
		nodes = bashlex.parse('a=$(wget this)')
		assignment_node = nodes[0].parts[0]
		commands = return_commands_from_variable_delcaraction(assignment_node)
		expected_str = "CommandNode(parts=[WordNode(parts=[] pos=(4, 8) word='wget'), WordNode(parts=[] pos=(9, 13) word='this')] pos=(4, 13))"
		self.assertTrue(str(commands[0]) == expected_str)
		# Test that it works for a complexly nested node. (This depends on return_path_to_node_type so as long as that works, so will this)
		nodes = bashlex.parse('a=$(wget this2)')
		commands = return_commands_from_variable_delcaraction(nodes[0])
		expected_str = "CommandNode(parts=[WordNode(parts=[] pos=(4, 8) word='wget'), WordNode(parts=[] pos=(9, 14) word='this2')] pos=(4, 14))"
		self.assertTrue(str(commands[0]) == expected_str)
	
	def test_return_commands_from_command_substitutions(self):
		self.assertRaises(ValueError, return_commands_from_command_substitutions, 'this')
		# Test assignment case works
		substitution_string = "testing=$(cd here)"
		expected_results = ["CommandNode(parts=[WordNode(parts=[] pos=(10, 12) word='cd'), WordNode(parts=[] pos=(13, 17) word='here')] pos=(10, 17))"]
		nodes = bashlex.parse(substitution_string)
		results = return_commands_from_command_substitutions(nodes[0])
		for i in range(0, len(results)):
			self.assertTrue(expected_results[i] == str(results[i]))
		# Test nested case works
		substitution_string = "testing=$(cd $(cd there))"
		nodes = bashlex.parse(substitution_string)
		expected_results = [
			"CommandNode(parts=[WordNode(parts=[] pos=(10, 12) word='cd'), WordNode(parts=[CommandsubstitutionNode(command=CommandNode(parts=[WordNode(parts=[] pos=(15, 17) word='cd'), WordNode(parts=[] pos=(18, 23) word='there')] pos=(15, 23)) pos=(13, 24))] pos=(13, 24) word='$(cd there)')] pos=(10, 24))", 
			"CommandNode(parts=[WordNode(parts=[] pos=(15, 17) word='cd'), WordNode(parts=[] pos=(18, 23) word='there')] pos=(15, 23))"
		]
		results = return_commands_from_command_substitutions(nodes[0])
		for i in range(0, len(results)):
			self.assertTrue(expected_results[i] == str(results[i]))
		# Test for loops
		substitution_string = "for x in $(cd here)\n do\n wget there\n done"
		expected_results = ["CommandNode(parts=[WordNode(parts=[] pos=(11, 13) word='cd'), WordNode(parts=[] pos=(14, 18) word='here')] pos=(11, 18))"]
		nodes = bashlex.parse(substitution_string)
		results = return_commands_from_command_substitutions(nodes[0])
		for i in range(0, len(results)):
			self.assertTrue(expected_results[i] == str(results[i]))


