import xml.sax
from xml.sax.saxutils import unescape
from collections import defaultdict


class DblpHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        #dblp文件前面统计数量8种类型都有，这里设置多个类型
        self.valid_types = {
            "article", "inproceedings", "proceedings",
            "book", "incollection", "phdthesis",
            "mastersthesis", "www"
        }  #使用{}即set(集合），通过哈希查找复杂度很低，对于需要大量查找和比较的xml文件来说很友好

        #核心索引
        self.authors = defaultdict(list)#defaultdict也是字典，但是能够自动创建键并赋予默认值，这样方便管理同一作者的不同作品
        self.authors_friend = defaultdict(list)#再创建一部字典管理合作关系
        self.paper_info = {}                     #用于存放key(key用来存放title，year,journal等数据）
        self.titles = {}                         #建立反向链接，即将文章标题和文章的相关信息链接

        # 解析状态
        self.current_paper = None  # 当前论文的临时字典
        self.current_tag = None  # 当前正在处理的字段名
        self.buffer = ""  # 用于累积 characters（应对分段调用，例如换行和&等逻辑符号）

    def startElement(self, name, attrs): #设置startElement函数， name是当前文档类型，attrs代表属性
        if name in self.valid_types:
                # 开始一篇新论文，检索根标签
            key = attrs.get("key", "")
            if not key:
                return  # 跳过无 key 的条目（一般用不到，但为了防止数据缺失，应当加上）

            self.current_paper = {
                "key": key,
                "type": name,
                "authors": [],
                "title": "",
                "year": "",
                "journal": "",
                "booktitle": "",
                "school": "",
                "publisher": "",
                "ee":""
            }
            self.current_tag = None
            self.buffer = ""
        else:
            # 处理每篇文献的具体标签
            if self.current_paper is not None and name in {
                "author", "title", "year", "journal", "booktitle", "school", "publisher", "ee"
            }:
                self.current_tag = name
                self.buffer = ""  # 清空缓冲区
            else:
                self.current_tag = None
        if len(self.paper_info) % 1000000 == 0 and self.paper_info:
            print(len(self.paper_info) / 1000000)
    def characters(self, content):
        """累积文本内容（SAX 可能多次调用此方法）"""
        if self.current_tag and self.current_paper is not None:
            self.buffer += content

    def endElement(self, name):
        # Step 1: 先处理当前字段的内容
        if self.current_tag is not None and self.current_paper is not None:
            content = self.buffer.strip()
            if content:
                content = unescape(content)
                if self.current_tag == "author":
                    self.current_paper["authors"].append(content)
                elif self.current_tag == "title":
                    if not self.current_paper["title"]:
                        self.current_paper["title"] = content
                elif self.current_tag == "year":
                    if not self.current_paper["year"]:
                        self.current_paper["year"] = content
                elif self.current_tag == "journal":
                    if not self.current_paper["journal"]:
                        self.current_paper["journal"] = content
                elif self.current_tag == "booktitle":
                    if not self.current_paper["booktitle"]:
                        self.current_paper["booktitle"] = content
                elif self.current_tag == "school":
                    if not self.current_paper["school"]:
                        self.current_paper["school"] = content
                elif self.current_tag == "publisher":
                    if not self.current_paper["publisher"]:
                        self.current_paper["publisher"] = content
                elif self.current_tag == "ee":
                    if name == "ee":
                        self.current_paper["ee"] = content

            # 清空当前字段状态
            self.current_tag = None

        # Step 2: 清空 buffer（无论是否处理了内容）
        self.buffer = ""

        # Step 3: 检查是否结束了一篇论文
        local_name = name.split(':')[-1].strip()
        if local_name in self.valid_types and self.current_paper is not None:
            self._finalize_paper()
            self.current_paper = None

    def _finalize_paper(self):
        """完成一篇论文的处理，存入索引"""
        paper = self.current_paper
        key = paper["key"]

        # === 提取 venue === 就可以不用在乎文献类型统一用venue调用文献所在地了
        ptype = paper["type"]
        if ptype == "article":
            venue = paper["journal"] or "Unknown Journal"
        elif ptype in ("inproceedings", "proceedings"):
            venue = paper["booktitle"] or "Unknown Conference"
        elif ptype in ("phdthesis", "mastersthesis"):
            venue = paper["school"] or "Unknown School"
        elif ptype in ("book", "incollection"):
            venue = paper["publisher"] or "Unknown Publisher"
        else:  # www
            venue = "Web Resource"

        # 构建最终论文记录
        record = {
            "title": paper["title"],
            "year": paper["year"],
            "type": ptype,
            "venue": venue,
            "authors": paper["authors"],
            "ee": paper["ee"]
        }

        # 保存到索引
        self.paper_info[key] = record

        # 建立作者索引
        for author in paper["authors"]:
            if author:  # 过滤空字符串
                self.authors[author].append(key)

        # 建立标题索引
        if paper["title"]:
            clean_title = paper["title"].strip().lower()
            if clean_title and clean_title not in self.titles:
                self.titles[clean_title] = key