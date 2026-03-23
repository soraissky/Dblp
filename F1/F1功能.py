import xml.sax
from DblpHandle import DblpHandler

# 1. 解析数据
print("正在解析 DBLP 数据...")
# 创建一个 SAX 解析器
parser = xml.sax.make_parser()

# 关闭命名空间支持
parser.setFeature(xml.sax.handler.feature_namespaces, 0)

# 创建自定义的 handler 实例
handler = DblpHandler()

# 将 handler 绑定到解析器
parser.setContentHandler(handler)

# 开始解析 XML 文件
parser.parse("dblp_sample.xml")


# 查询
while True:
    query = input("\n请输入作者姓名或完整论文标题（输入 'quit' 退出）: ").strip()
    if query.lower() == 'quit':
        break

    # 尝试按作者查找（精确匹配，区分大小写）
    if query in handler.authors:
        print(f"\n作者 '{query}' 的论文列表:")
        for key in handler.authors[query]:
            paper = handler.paper_info.get(key)
            if paper:
                print(f"  • {paper['title']} ({paper.get('year', 'N/A')}) — {paper.get('venue', 'N/A')}")
        print(f"\n作者 '{query}' 的其他合作作者:")

    else:
        # 尝试按标题查找（标准化后匹配）
        clean_query = query.strip().lower()
        if clean_query in handler.titles:
            key = handler.titles[clean_query]
            paper = handler.paper_info[key]
            print("\n论文详情:")
            print(f"  标题: {paper['title']}")
            print(f"  作者: {', '.join(paper['authors'])}")
            print(f"  年份: {paper.get('year', 'N/A')}")
            print(f"  类型: {paper['type']}")
            print(f"  会议/期刊: {paper['venue']}")
            print(f"  ee: {paper.get('ee') or 'miss'}")
        else:
            print("\n未找到匹配的作者或论文。")