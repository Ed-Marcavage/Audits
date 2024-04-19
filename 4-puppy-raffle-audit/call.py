import sys
import pprint

from solidity_parser import parser

sourceUnit = parser.parse_file(sys.argv[1], loc=False) # loc=True -> add location information to ast nodes
pprint.pprint(sourceUnit)  
# see output below
