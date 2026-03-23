#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.sax
from collections import defaultdict


class TypeCounter(xml.sax.ContentHandler):
    def __init__(self):
        self.type_counts = defaultdict(int)
        # DBLP 所有有效类型
        self.valid_types = {
            "article", "inproceedings", "proceedings",
            "book", "incollection", "phdthesis",
            "mastersthesis", "www"
        }

    def startElement(self, name, attrs):
        if name in self.valid_types:
            self.type_counts[name] += 1


if __name__ == "__main__":
    import sys
    import os

    # 使用你的样本路径
    xml_file = r"C:\datastructure\dblp_sample.xml"

    if not os.path.exists(xml_file):
        print(f"文件不存在: {xml_file}")
        sys.exit(1)

    print(f"正在统计: {xml_file}")
    handler = TypeCounter()
    xml.sax.parse(xml_file, handler)

    print("\n 文献类型统计结果:")
    total = 0
    for typ in sorted(handler.type_counts, key=handler.type_counts.get, reverse=True):
        count = handler.type_counts[typ]
        total += count
        print(f"  {typ:15} : {count:>8,}")

    print(f"\n总计: {total:,} 篇文献")