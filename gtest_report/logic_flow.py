#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for analysis logic control flow of cpp source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-06-07
#
# --------------------------------------------------------------------------------- #
import logging


class Block:
  block_type = None
  no = None
  start_no = None
  end_no = None
  body_start_no = None
  body_end_no = None
  code_lines = None
  parent_block = None

  branchs = []


print("111111111111111111111111")
print(__name__)
log = logging.getLogger(__name__)


class LogicFlow:

  def analysis(self, code):
    lines = code.splitlines()

    block_codes = self.analysis_lines(lines)

    return block_codes

  def analysis_lines(self, lines):

    block_codes = []
    self.analysis_code(block_codes, lines)

    return block_codes

  def analysis_code(self, blocks, code_lines, parent_block=None):
    log.info("=== analysis_code ===")

    block_start = False
    nested_level = 0

    code_lines_new = []
    block_id = None
    pre_block = None

    for idx, line in enumerate(code_lines):
      log.debug("%d: %s" % (idx, line))
      line = line.strip()
      pre_line = line

      if idx > 0:
        if block_start is False and line.startswith(("if", "for", "else")):

          block_type = None
          if line.startswith("if"):
            block_type = "if"
          elif line.startswith("for"):
            block_type = "for"
          elif line.startswith("else"):
            block_type = "else"

          log.debug("block start: %s", block_type)

          # print("===block begin...", line)
          code_lines_new = []
          block = Block()
          block.block_type = block_type
          block.parent_block = parent_block
          if parent_block:
            block.start_no = parent_block.start_no + idx
          else:
            block.start_no = idx + 1
          # print(code_lines_new)

          block_id = idx
          block_start = True

        if block_start is True:
          log.debug("inside and append to lines.")
          code_lines_new.append(line)
          # print(code_lines_new)

          if idx == block_id + 1:
            log.debug("next line after block begin.")
            if line.endswith("{") is False:
              log.debug("only one line code without brace.")
              block.code_lines = code_lines_new
              block.end_no = idx
              blocks.append(block)
              code_lines_new = []

          if line.endswith("{"):
            nested_level = nested_level + 1
            log.debug("nested_level {: %d", nested_level)

          if line.startswith("}"):
            nested_level = nested_level - 1
            log.debug("nested_level }: %d", nested_level)

            if nested_level == 0:
              # print("===block end.", line)
              if len(code_lines_new) > 0:
                block.code_lines = code_lines_new
                block.no = "C" + str(len(blocks) + 1)
                if parent_block:
                  block.end_no = parent_block.start_no + idx + 2
                else:
                  block.end_no = idx + 1

                if block.block_type == "else":
                  log.debug("append else branch to block:%s." % pre_block.no)
                  pre_block.branchs.append(block)
                else:
                  pre_block = block
                  log.debug("append to blocks.")
                  blocks.append(block)
                self.analysis_code(blocks, code_lines_new, block)

              code_lines_new = []
              block_start = False

  def analysis_block(self, block_code):
    lines = block_code.splitlines()

    block = None
    for idx, line in enumerate(lines):
      print("%d: %s" % (idx, line))
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
