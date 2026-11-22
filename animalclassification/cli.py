"""命令行接口：查询动物、列出类别、生成分类树与可打印练习。"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional, Sequence

from animalclassification import __version__
from animalclassification.model import (
    Animal,
    all_animals,
    animals_in,
    categories,
    diet_of,
    find_animal,
    is_vertebrate,
    match_items,
    quiz_items,
)
from animalclassification.render import match_html, poster_html, quiz_html


def _ensure_utf8_console() -> None:
    """尽量把标准输出/错误切换为 UTF-8，失败时保持原状。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not callable(reconfigure):
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            continue


def _write_text(path: str, content: str) -> None:
    """以 UTF-8 写入文件，必要时创建父目录；OSError 转为中文 ValueError。"""
    if not isinstance(path, str):
        raise TypeError("输出路径必须是字符串")
    text = path.strip()
    if not text:
        raise ValueError("输出路径不能为空")
    if not isinstance(content, str):
        raise TypeError("输出内容必须是字符串")
    directory = os.path.dirname(os.path.abspath(text))
    try:
        os.makedirs(directory, exist_ok=True)
        with open(text, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except OSError as exc:
        raise ValueError("无法写入文件「%s」：%s" % (text, exc)) from exc


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="animalclassification",
        description="动物分类：脊椎动物五类与无脊椎类群查询、判断与练习页",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="animalclassification %s" % __version__,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="命令", required=True)

    info_parser = subparsers.add_parser("info", help="查看某种动物的分类信息")
    info_parser.add_argument("animal", help="动物中文名或别名")

    list_parser = subparsers.add_parser("list", help="列出某个类别下的动物")
    list_parser.add_argument("category", help="类别名称或类别别名")

    subparsers.add_parser("categories", help="列出全部类别")

    diet_parser = subparsers.add_parser("diet", help="查询某种动物的食性")
    diet_parser.add_argument("animal", help="动物中文名或别名")

    quiz_parser = subparsers.add_parser("quiz", help="生成四选一练习题")
    quiz_parser.add_argument("--count", type=int, default=10, help="题目数量（1-40，默认 10）")
    quiz_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    quiz_parser.add_argument(
        "--group",
        default=None,
        help="限定分组：脊椎 或 无脊椎",
    )
    quiz_parser.add_argument("-o", "--output", default=None, help="保存 HTML 的路径")

    match_parser = subparsers.add_parser("match", help="生成动物—类别配对练习")
    match_parser.add_argument("--count", type=int, default=10, help="配对数量（1-20，默认 10）")
    match_parser.add_argument("--seed", type=int, default=None, help="随机种子")
    match_parser.add_argument("-o", "--output", default=None, help="保存 HTML 的路径")

    poster_parser = subparsers.add_parser("poster", help="生成动物分类海报")
    poster_parser.add_argument("-o", "--output", default=None, help="保存 HTML 的路径")

    return parser


def _animal_kind(animal: Animal) -> str:
    """返回动物所属的大类说明。"""
    return "脊椎动物" if is_vertebrate(animal.category) else "无脊椎动物"


def _cmd_info(query: str) -> int:
    """输出某种动物的分类信息。"""
    animal = find_animal(query)
    aliases = "、".join(animal.aliases) if animal.aliases else "无"
    lines: List[str] = [
        "名称：%s" % animal.name,
        "类别：%s（%s）" % (animal.category, _animal_kind(animal)),
        "食性：%s" % animal.diet,
        "栖息环境：%s" % animal.habitat,
        "特征或趣闻：%s" % animal.fact,
        "别名：%s" % aliases,
    ]
    print("\n".join(lines))
    return 0


def _cmd_list(category: str) -> int:
    """输出指定类别下的动物列表。"""
    items = animals_in(category)
    if not items:
        raise ValueError("类别「%s」下没有收录动物" % category.strip())
    resolved = items[0].category
    print("类别：%s（%d 种）" % (resolved, len(items)))
    for index, animal in enumerate(items, 1):
        print(
            "  %d. %s（%s｜%s）"
            % (index, animal.name, animal.diet, animal.habitat)
        )
    return 0


def _cmd_categories() -> int:
    """输出全部类别及其动物数量。"""
    names = categories()
    total = len(all_animals())
    print("动物分类：%d 个类别，%d 种动物" % (len(names), total))
    for index, category in enumerate(names, 1):
        kind = "脊椎动物" if is_vertebrate(category) else "无脊椎动物"
        print(
            "  %d. %s（%s，%d 种）"
            % (index, category, kind, len(animals_in(category)))
        )
    return 0


def _cmd_diet(query: str) -> int:
    """输出某种动物的食性。"""
    animal = find_animal(query)
    print("%s是%s动物。" % (animal.name, diet_of(animal.name)))
    return 0


def _item_text(item: Dict[str, object], key: str) -> str:
    """读取题目字符串字段，异常时给出中文错误。"""
    value = item.get(key)
    if not isinstance(value, str):
        raise ValueError("题目数据缺少字段：%s" % key)
    return value


def _item_options(item: Dict[str, object]) -> List[str]:
    """读取题目选项并校验类型。"""
    value = item.get("options")
    if not isinstance(value, list):
        raise ValueError("题目数据缺少选项")
    options: List[str] = []
    for option in value:
        if not isinstance(option, str):
            raise ValueError("题目选项格式错误")
        options.append(option)
    return options


def _cmd_quiz(
    count: int,
    seed: Optional[int],
    group: Optional[str],
    output: Optional[str],
) -> int:
    """生成四选一练习：无输出路径时打印到终端，否则写入 HTML。"""
    items = quiz_items(count, seed, group)
    if output is not None:
        content = quiz_html(items, "动物分类练习", with_answers=False)
        _write_text(output, content)
        print("已生成：%s" % output.strip())
        return 0
    for index, item in enumerate(items, 1):
        print("%d. %s" % (index, _item_text(item, "question")))
        for label, option in zip("ABCD", _item_options(item)):
            print("   %s. %s" % (label, option))
        print("   答案：%s" % _item_text(item, "answer"))
        print("   解析：%s" % _item_text(item, "explanation"))
        print()
    return 0


def _cmd_match(count: int, seed: Optional[int], output: Optional[str]) -> int:
    """生成动物—类别配对练习。"""
    pairs = match_items(count, seed)
    if output is not None:
        content = match_html(pairs, "动物分类配对练习")
        _write_text(output, content)
        print("已生成：%s" % output.strip())
        return 0
    print("动物—类别配对（共 %d 组）" % len(pairs))
    for index, (animal, category) in enumerate(pairs, 1):
        print("%2d. %s —— %s" % (index, animal, category))
    return 0


def _cmd_poster(output: Optional[str]) -> int:
    """生成动物分类海报。"""
    content = poster_html(all_animals())
    if output is not None:
        _write_text(output, content)
        print("已生成：%s" % output.strip())
        return 0
    print(content)
    return 0


def _run(args: Optional[Sequence[str]] = None) -> int:
    """解析参数并分发命令；业务错误由 main 统一处理。"""
    parser = _build_parser()
    namespace = parser.parse_args(args)
    command = namespace.command
    if command == "info":
        return _cmd_info(namespace.animal)
    if command == "list":
        return _cmd_list(namespace.category)
    if command == "categories":
        return _cmd_categories()
    if command == "diet":
        return _cmd_diet(namespace.animal)
    if command == "quiz":
        return _cmd_quiz(namespace.count, namespace.seed, namespace.group, namespace.output)
    if command == "match":
        return _cmd_match(namespace.count, namespace.seed, namespace.output)
    if command == "poster":
        return _cmd_poster(namespace.output)
    parser.error("未知命令：%s" % command)
    return 2


def main(argv: Optional[Sequence[str]] = None) -> int:
    """命令行入口；成功返回 0，输入错误返回 2。"""
    _ensure_utf8_console()
    try:
        return _run(argv)
    except (TypeError, ValueError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
