# !/usr/bin/env python3
# coding=utf-8
# --------------------------------------------------------------------------------- #
# Tool for analysis logic control flow of cpp source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-06-07
#
# --------------------------------------------------------------------------------- #
import logging

log = logging.getLogger(__name__)


class Block:
  block_type = None
  no = None
  start_no = None
  end_no = None
  body_start_no = None
  body_end_no = None
  code_lines = None
  parent_idx = None
  child_blocks = None


class LogicFlow:

  def analysis(self, code):
    lines = code.splitlines()

    block_codes = self.analysis_lines(lines)

    return block_codes

  def analysis_lines(self, lines):

    block_codes = []
    self.analysis_code(block_codes, None, lines, 0)

    return block_codes

  def analysis_code(self, blocks, parent_block, code_lines, start_idx):
    log.info("= analysis_code =")
    log.debug("code_lines: ")
    log.debug(code_lines)
    log.debug("start_idx: %d" % start_idx)

    # 2. 提取重复的逻辑
    # handle block_type
    block_type = None
    block_start = False
    nested_level = 0
    for idx, line in enumerate(code_lines):
      if line.endswith("{"):
        nested_level = nested_level + 1
      if line.startswith("}"):
        nested_level = nested_level - 1
      if line.startswith("for"):
        block_type = "for"
        break
      if line.startswith("if"):
        block_type = "if"
      if nested_level == 0 and line.startswith("else"):
        block_type = "ifelse"

    # create new block
    block = Block()
    block.child_blocks = []
    block.block_type = block_type
    block.code_lines = code_lines
    block.parent_block = parent_block
    if parent_block:
      block.start_no = parent_block.start_no + start_idx + 1
      block.end_no = block.start_no + len(code_lines) - 1
      parent_block.child_blocks.append(block)
    else:
      block.start_no = 0
      block.end_no = block.start_no + len(code_lines) - 1
      block.no = "C"
      blocks.append(block)

    # 3. 缩小问题规模
    log.debug("go to next.")
    block_start = False
    nested_level = 0
    current_start_no = 0
    pre_line = ""
    next_line = ""
    go_next = False

    for idx, line in enumerate(code_lines[1:]):
      log.debug("%d: %s" % (idx, line))
      line = line.strip()

      if idx < len(code_lines) - 2:
        next_line = code_lines[idx + 2].strip()
        log.debug("next line: %s" % next_line)

      if block_start is False and line.startswith(("if", "for")):
        log.debug("find if or for")
        code_lines_new = []
        current_start_no = idx
        block_start = True

      if block_start is True:
        log.debug("block_start is true.")
        code_lines_new.append(line)

        if line.endswith("{"):
          nested_level = nested_level + 1
          log.debug("nested_level {: %d", nested_level)

        if line.startswith("}"):
          nested_level = nested_level - 1
          log.debug("nested_level }: %d", nested_level)

          if nested_level == 0:
            if next_line.startswith("else") is False:
              log.debug("next_line is not else so go to next")
              go_next = True

        # no brace
        if pre_line == "else" and line.endswith("{") is False:
          log.debug("pre line == else")
          go_next = True

        if pre_line and pre_line.startswith(("if", "for")) and \
            pre_line.endswith("{") is False and \
            line.endswith("{") is False:
          log.debug("pre line == if without brace")
          if next_line.startswith("else") is False:
            log.debug("next_line is not else so go to next")
            go_next = True

        pre_line = line

        if go_next:
          log.debug("go to next analysis_code")
          self.analysis_code(blocks, block, code_lines_new, current_start_no)
          code_lines_new = []
          block_start = False
          go_next = False
