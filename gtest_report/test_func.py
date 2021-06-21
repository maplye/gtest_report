#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for generating unit test case from test source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-05-20
#
# --------------------------------------------------------------------------------- #
import os
from datetime import datetime
from pathlib import Path
import itertools
import logging

from jinja2 import Environment, FileSystemLoader
import pygraphviz as pyg

from .logic_flow import LogicFlow

log = logging.getLogger(__name__)
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class TestFunc:

  def __init__(self, name, descript):
    self.name = name
    self.descript = descript
    self.testcases = []
    self.test_file = None
    self.html_filename = f"{self.name}.html"
    self.created_date = NOW
    self.block_text = None
    self.blocks = None

  def __str__(self):
    return f'test suite: ({self.name})'

  @property
  def link(self):
    return f"{self.test_file.onlyname}/{self.name}.html"

  @property
  def tc_count(self):
    count = len(self.testcases)
    return count

  @property
  def tc_pass_count(self):
    testcase_list = self.testcases
    testcases_pass = [x for x in testcase_list if x.result == "OK"]
    count = len(testcases_pass)
    return count

  @property
  def tc_percent(self):
    percent = 0
    if self.tc_count > 0:
      percent = round(self.tc_pass_count * 100 / self.tc_count, 1)
    return percent

  def get_code_pos(self):
    # print("get_code_pos ...")
    start_pos = 0
    end_pos = 0
    if self.test_file.src_file:
      lookup = f'::{self.name}'
      filename = self.test_file.src_file
      nested_level = 0
      with open(filename) as f:
        for num, line in enumerate(f, 1):
          line = line.strip()
          # print(line)
          if lookup in line:
            start_pos = num - 1

          if start_pos > 0:
            if line.endswith("{"):
              nested_level = nested_level + 1

            if line.startswith("}"):
              nested_level = nested_level - 1
              if nested_level == 0:
                end_pos = num
                break
    # print(start_pos, end_pos)
    return (start_pos, end_pos)

  def generate_html(self):
    print(f"======test func: {self.name} generate_html======")
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('testfunc.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)

    func_report_path = f"{self.test_file.report_dir}{self.test_file.rela_dir}/{self.test_file.onlyname}/"
    Path(func_report_path).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(func_report_path + self.html_filename, "w") as fh:
      fh.write(output_from_parsed_template)

    for tc in self.testcases:
      tc.generate_html()

  def get_blocks(self):
    blocks = []
    (start_pos, end_pos) = self.get_code_pos()
    filename = self.test_file.src_file
    with open(filename) as f:
      blockcode_str_list = itertools.islice(f, start_pos, end_pos)
      lf = LogicFlow()
      blocks = lf.analysis_lines(list(blockcode_str_list))

    return blocks

  def add_node(self, g, n, **attr):
    log.debug("add_node: %s" % n)
    g.add_node(n, **attr)

  def add_edge(self, g, start, end):
    log.debug("add_edge: %s -> %s" % (start, end))
    g.add_edge(start, end, dir="forward")

  def generate_cfg(self):
    root_block = self.get_blocks()[0]

    g = pyg.AGraph()

    self.generate_cfg_block(g, root_block)

  def generate_cfg_block(self, root_block):

    g = pyg.AGraph()

    self.generate_cfg_block_loop(g, root_block)

    g.layout(prog='dot')  # 绘图类型
    g.draw('pyg1.png')  # 绘制

  def generate_cfg_block_loop(self, g, block):
    log.info("= generate_cfg_block ...")
    log.debug("block start no: %s" % block.start_no)
    log.debug("codelines:")
    log.debug(block.code_lines)
    log.debug("block_type: %s" % block.block_type)
    log.debug("child_blocks: %d" % len(block.child_blocks))

    if block.block_type == "ifelse":
      self.add_node(g, f'{block.start_no}')
      self.add_node(g, f'{block.start_no}_E')
      self.add_node(g, f'{block.child_blocks[0].start_no}')
      self.add_node(g, f'{block.child_blocks[1].start_no}')

      self.add_edge(g, f'{block.start_no}', f'{block.child_blocks[0].start_no}')
      self.add_edge(g, f'{block.start_no}', f'{block.child_blocks[1].start_no}')

      # 若没有子节点则连接到父结束点
      if len(block.child_blocks[0].child_blocks) == 0:
        self.add_edge(g, f'{block.child_blocks[0].start_no}', f'{block.start_no}_E')
      if len(block.child_blocks[1].child_blocks) == 0:
        self.add_edge(g, f'{block.child_blocks[1].start_no}', f'{block.start_no}_E')

      for child_block in block.child_blocks:
        self.generate_cfg_block_loop(g, child_block)

      if block.parent_block and len(block.child_blocks) > 0:
        log.debug("ifelse: add block end to parent end.")
        # self.add_edge(g, f'{block.start_no}_E', f'{block.parent_block.start_no}_E')

    if block.block_type == "if":
      self.add_node(g, f'{block.start_no}')
      self.add_node(g, f'{block.child_blocks[0].start_no}')
      self.add_node(g, f'{block.start_no}_E')
      self.add_edge(g, f'{block.start_no}', f'{block.child_blocks[0].start_no}')
      self.add_edge(g, f'{block.start_no}', f'{block.start_no}_E')
      self.add_edge(
          g,
          f'{block.child_blocks[0].start_no}',
          f'{block.start_no}_E',
      )

      # if block.parent_block:
      #   self.add_edge(g, f'{block.parent_block.start_no}', f'{block.start_no}')

      for child_block in block.child_blocks:
        self.generate_cfg_block_loop(g, child_block)

      if block.parent_block and len(block.child_blocks) > 0:
        log.debug("if: add block end to parent end.")
        self.add_edge(g, f'{block.start_no}_E', f'{block.parent_block.start_no}_E')

    if block.block_type == "code":

      self.add_node(g, f'{block.start_no}')

      pre_child_block = None
      last_child_block = None
      for child_block in block.child_blocks:
        log.debug("child_block start no: %s" % child_block.start_no)
        self.add_node(g, f'{child_block.start_no}')

        self.generate_cfg_block_loop(g, child_block)

        if pre_child_block:
          log.debug("link previous node: %s" % pre_child_block.start_no)
          self.add_edge(g, f'{pre_child_block.start_no}_E', f'{child_block.start_no}')

        pre_child_block = child_block
        last_child_block = child_block

      # 父节点链接第一个子节点
      if block.parent_block and len(block.child_blocks) > 0:
        log.debug("link parent to first child node")
        self.add_edge(g, f'{block.start_no}', f'{block.child_blocks[0].start_no}')

      # 最后一个子节点链接父尾节点
      if block.parent_block and len(block.child_blocks) > 0:
        log.debug("last child node end to block end.")
        # self.add_edge(g, f'{block.child_blocks[-1].start_no}_E', f'{block.start_no}_E')

      pre_child_block = None

      if block.parent_block and len(block.child_blocks) > 0:
        log.debug("code: add block end to parent end.")
        self.add_edge(g, f'{block.start_no}_E', f'{block.parent_block.start_no}_E')

  def generate_cfg1(self):

    blocks = self.get_blocks()
    # print(blocks)

    g = pyg.AGraph()
    pre_block = None
    for block in blocks:
      print("= current block:", block.no)

      child_blocks = [x for x in blocks if x.parent_block == block]

      g.add_node(f'{block.no}_S', label=block.no + "_S: " + block.code_lines[0])
      g.add_node(f'{block.no}')
      g.add_node(f'{block.no}_E')

      self.add_edge(g, f'{block.no}_S', block.no)

      # 如果没有子节点，则当前节点指向节点结束
      if len(child_blocks) == 0:
        self.add_edge(g, block.no, f'{block.no}_E')

      # 如果该节点有分支
      if len(block.branchs) > 0:
        print("block: %s have branches" % block.no)
        self.add_edge(g, f'{block.no}_S', block.branchs[0].no)
        self.add_edge(g, block.branchs[0].no, f'{block.no}_E')

      if block.parent_block:
        print("parent_block:", block.parent_block.no)

        # 如果有父节点，则当前节点结束指向父节点的结束
        self.add_edge(g, f'{block.no}_E', f'{block.parent_block.no}_E')
        # 如果该节点没有分支
        # if len(block.branchs) == 0:
        #   self.add_edge(g, f'{pre_block.no}_E', f'{block.parent_block.no}_S')
      else:
        print("no parent block.")
        if len(child_blocks) > 0:
          print("child_blocks[0]:", child_blocks[0].no)
          self.add_edge(g, block.no, f'{child_blocks[0].no}_S')
        else:
          print("no child.")
          self.add_edge(g, block.no, f'{block.no}_E')

        if pre_block:
          print("pre_block: ", pre_block.no)

          if pre_block.parent_block:
            # 如果前一节点有父节点，则将父节点的结束指向当前节点的开始
            self.add_edge(g, f'{pre_block.parent_block.no}_E', f'{block.no}_S')
          else:
            self.add_edge(g, f'{pre_block.no}_E', f'{block.no}_S')

      # 如果该节点没有分支
      if len(block.branchs) == 0:
        self.add_edge(g, f'{block.no}_S', f'{block.no}_E')

      pre_block = block
      print("set pre_block: ", block.no)

    g.layout(prog='dot')  # 绘图类型
    g.draw('pyg1.png')  # 绘制
