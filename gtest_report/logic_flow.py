#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for analysis logic control flow of cpp source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-06-07
#
# --------------------------------------------------------------------------------- #
from pprint import pprint

class Block:
  block_type = None
  no = None
  start_no = None
  end_no = None
  body_start_no = None
  body_end_no = None
  code_lines = None


def analysis(code):
  lines = code.splitlines()

  block_codes = analysis_lines(lines)

  return block_codes

def analysis_lines(lines):

  block_codes = []
  analysis_code(block_codes, lines)

  return block_codes

def analysis_code(blocks, code_lines, parent_block=None):
  # print("*** analysis_code ===")
  # pprint(code_lines)

  block_start = False
  nested_level = 0

  code_lines_new  = []
  block_id = None

  for idx, line in enumerate(code_lines):
    # print("%d: %s" % ( idx, line))
    line = line.strip()
    pre_line = line

    if idx > 0:
      if block_start is False and line.startswith(("if","for","else")):
        # print("===block begin...", line)
        code_lines_new  = []
        block = Block()
        if parent_block:
          block.start_no = parent_block.start_no + idx
        else:
          block.start_no = idx + 1
        # print(code_lines_new)
        
        block_id = idx
        block_start = True
    
      if block_start is True:
        # print("===block inside...", line)
        code_lines_new.append(line)
        # print(code_lines_new)

        # next line after block begin
        if idx == block_id + 1:
          # only one line code without brace 
          if line.endswith("{") is False:
            block.code_lines = code_lines_new
            block.end_no = idx
            blocks.append(block)
            code_lines_new = []

        if line.endswith("{"):
          nested_level = nested_level + 1

        if line.startswith("}"):
          nested_level = nested_level - 1  

          if nested_level == 0:
            # print("===block end.", line)
            if len(code_lines_new) > 0:
              block.code_lines = code_lines_new
              block.no  = "C"+ str(len(blocks) + 1)
              if parent_block:
                block.end_no = parent_block.start_no + idx + 1
              else:
                block.end_no = idx + 1
              blocks.append(block)
              analysis_code(blocks, code_lines_new, block)

            code_lines_new = []
            block_start = False

def analysis_block(block_code):
  lines = code.splitlines()

  block = None
  for idx, line in enumerate(lines):
    print("%d: %s" % ( idx, line))
    line = line.strip()

    block_start = False

    if line.startswith("if"):
      block = Block()
      block.block_type = "if"
      block.start_no = idx + 1
      block_start = True
    
    if line.startswith("for"):
      block = Block()
      block.block_type = "for"
      block.start_no = idx + 1

    if line.startswith("{"):
      block.body_start_no = idx + 2

    if line.startswith("}"):
      block.body_end_no = idx
      block.end_no = idx + 1
      block_start = False
  
  return block  


