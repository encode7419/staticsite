from enum import Enum
from htmlnode import LeafNode
import re
class TextType(Enum):
    TEXT = 'text (plain)'
    BOLD = 'bold'
    ITALIC = 'italic'
    CODE_TEXT = 'code text'
    LINK = 'link'
    IMAGES = 'alt text'

class BlockType(Enum):
    PARAGRAPH = 'paragraph'
    HEADING = 'heading'
    CODE = 'code'
    QUOTE = 'quote'
    UNORDERED_LIST = 'unordered_list'
    ORDERED_LIST = 'ordered_list'

def block_to_block_type(block):
    lines = block.split("\n")
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        is_quote = True
        for line in lines:
            if not line.startswith(">"):
                is_quote = False
                break
        if is_quote:
            return BlockType.QUOTE
    if block.startswith("- "):
        is_unordered = True
        for line in lines:
            if not line.startswith("- "):
                is_unordered = False
                break
        if is_unordered:
            return BlockType.UNORDERED_LIST
    if block.startswith("1. "):
        is_ordered = True
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                is_ordered = False
                break
            i += 1
        if is_ordered:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH





class TextNode():

    def __init__(self, text, text_type, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode('b',text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode('i',text_node.text)
    elif text_node.text_type == TextType.CODE_TEXT:
        return LeafNode('code',text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode('a',text_node.text, {'href': text_node.url})
    elif text_node.text_type == TextType.IMAGES:
        return LeafNode('img',"", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception('error')


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        split_string = node.text.split(delimiter)
        if len(split_string) % 2 == 0:
            raise Exception('invalid markdown syntax')
        for i,part in enumerate(split_string):
            if part == '':
                continue
            if i % 2 == 0:
                nodes = TextNode(part, TextType.TEXT)
                new_nodes.append(nodes)
            else:
                nodes = TextNode(part, text_type)
                new_nodes.append(nodes)
    return new_nodes

def extract_markdown_images(text):
    images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return images
def extract_markdown_links(text):
    links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return links

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        images = extract_markdown_images(node.text)
        original_text = node.text
        if not images:
            new_nodes.append(node)
            continue
        for alt, url in images:
            sections = original_text.split(f"![{alt}]({url})", 1)
            original_text = sections[1]
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGES, url=url))
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        original_text = node.text
        if not links:
            new_nodes.append(node)
            continue
        for alt_text, link in links:
            sections = original_text.split(f"[{alt_text}]({link})", 1)
            original_text = sections[1]
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.LINK, url=link))
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT),]
    nodes = split_nodes_delimiter(nodes, '**', TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, '_', TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, '`', TextType.CODE_TEXT)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
