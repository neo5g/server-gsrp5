# -*- coding: utf-8 -*-

ELEMENT_TYPES = (type(str),type(unicode),type(0),type(0.0),type(True))
NODE_TYPES = ( type(list()),type(tuple()))
PRIORITY_TOKEN = {'(':0, ')':0, '=':1, '!=':1, '>':1, '<':1,'>=':1, '<=':1,'like':1, 'ilike':1, '~':1, '!':2, '&':3, '|':4}

class Stack(list): pass

class Node(object):
	
	left = None
	
	rigth = None
	
	def __init__(self, node):
		if type(node) in NODE_TYPES:
			self.rigth = self.parse_node(node)
		elif type(node) in EXPR_TYPES:
			self.left = node

	def pasre_node(self, node):
		for e in node:
			if type(e) in NODE_TYPES:
				self.rigth = Stack()
def parse(expr):
	stack = Stack()
	for node in expr:
		stack.append(Node(node))

if __name__ == "__main__":
	e = ['&','!']
