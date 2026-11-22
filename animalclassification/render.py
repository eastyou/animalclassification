"""把动物分类数据渲染为纯 SVG 分类树与可打印的 HTML 页面。

所有动态文本都会经过 :func:`html.escape` 转义；页面自带 A4 打印样式。
"""
from __future__ import annotations

import html
from typing import Dict, List, Sequence, Tuple

from animalclassification.model import (
    Animal,
    animals_in,
    categories,
    is_vertebrate,
)

__all__ = ["tree_svg", "poster_html", "quiz_html", "match_html"]


_STYLE = """
:root {
  --ink: #1f2933;
  --muted: #52606d;
  --line: #d9e2ec;
  --vert: #2f855a;
  --vert-soft: #e6f4ea;
  --invert: #2b6cb0;
  --invert-soft: #e6f0fa;
  --paper: #ffffff;
  --bg: #f5f7fa;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 28px 16px 48px;
  background: var(--bg);
  color: var(--ink);
  font-family: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.7;
}
.page { width: 100%; max-width: 960px; margin: 0 auto; }
.page-header { text-align: center; margin-bottom: 24px; }
.page-header h1 { margin: 0 0 6px; font-size: 30px; letter-spacing: 1px; }
.subtitle { margin: 0; color: var(--muted); }
.tree-section { margin: 24px 0 30px; padding: 14px 16px 6px; background: var(--paper); border: 1px solid var(--line); border-radius: 12px; }
.tree-section h2 { margin: 0 0 8px; font-size: 20px; }
.tree { width: 100%; overflow-x: auto; }
.tree svg { display: block; width: 100%; height: auto; }
.group-section { margin: 28px 0; }
.group-section h2 { margin: 0 0 14px; padding-left: 10px; border-left: 5px solid var(--line); font-size: 22px; }
.vertebrate h2 { color: var(--vert); border-color: var(--vert); }
.invertebrate h2 { color: var(--invert); border-color: var(--invert); }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.card { background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; }
.vertebrate .card { border-top: 4px solid var(--vert); }
.invertebrate .card { border-top: 4px solid var(--invert); }
.card h3 { margin: 0 0 6px; font-size: 19px; }
.tag { display: inline-block; margin-left: 8px; padding: 0 8px; border-radius: 999px; font-size: 12px; font-weight: 400; vertical-align: middle; }
.vertebrate .tag { color: var(--vert); background: var(--vert-soft); }
.invertebrate .tag { color: var(--invert); background: var(--invert-soft); }
.meta { margin: 0 0 6px; color: var(--muted); font-size: 13px; }
.chips { margin: 6px 0 0; }
.animal { display: inline-block; margin: 2px 4px 2px 0; padding: 1px 8px; border: 1px solid var(--line); border-radius: 999px; background: #fbfdff; font-size: 12px; }
.table-section { margin: 32px 0; }
.table-section h2 { margin: 0 0 12px; font-size: 22px; }
table { width: 100%; border-collapse: collapse; background: var(--paper); font-size: 12.5px; }
th, td { border: 1px solid var(--line); padding: 7px 9px; vertical-align: top; text-align: left; }
th { background: #eef2f7; }
.footer { margin-top: 36px; text-align: center; color: var(--muted); font-size: 12px; }
.quiz-item, .match-col { background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: 16px 18px; margin-bottom: 14px; }
.question { margin: 0 0 10px; font-weight: 600; }
.number { margin-right: 6px; }
.options { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 6px 18px; }
.option { padding: 4px 0; }
.label { display: inline-block; width: 22px; color: var(--muted); font-weight: 600; }
.answer-line { margin: 10px 0 0; color: var(--muted); }
.answer { margin: 10px 0 2px; color: var(--vert); }
.explanation { margin: 0; color: var(--muted); font-size: 13px; }
.match-hint { color: var(--muted); margin: 0 0 18px; }
.match-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.match-col h2 { margin: 0 0 10px; font-size: 17px; }
.match-col ol { list-style: none; margin: 0; padding: 0; }
.match-col li { padding: 6px 0; border-bottom: 1px dashed var(--line); }
.match-col li:last-child { border-bottom: none; }
.blank { color: var(--muted); margin-right: 6px; }
@page { size: A4 }
@page { margin: 14mm; }
@media print {
  body { background: #ffffff; padding: 0; }
  .page { max-width: none; }
  .card, .quiz-item, .match-col, .table-section, .tree-section { break-inside: avoid; }
  .card, .quiz-item, .match-col { box-shadow: none; }
  .option { border-bottom: 1px dotted #cbd2d9; }
  a { color: inherit; text-decoration: none; }
}
"""


def _escape(value: str) -> str:
    """转义动态文本，并校验其类型。"""
    if not isinstance(value, str):
        raise TypeError("待转义内容必须是字符串")
    return html.escape(value, quote=True)


def _require_title(title: str) -> str:
    """校验并返回去除首尾空白的标题。"""
    if not isinstance(title, str):
        raise TypeError("标题必须是字符串")
    text = title.strip()
    if not text:
        raise ValueError("标题不能为空")
    return text


def _page(title: str, body: str) -> str:
    """拼装完整的 HTML 文档。"""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + _escape(title) + "</title>\n"
        "<style>" + _STYLE + "</style>\n"
        "</head>\n"
        "<body>\n"
        '<main class="page">\n' + body + "\n</main>\n"
        "</body>\n"
        "</html>\n"
    )


def _svg_text(
    x: int,
    y: int,
    text: str,
    size: int,
    weight: str = "400",
    fill: str = "#1f2933",
) -> str:
    """生成一行居中的 SVG 文本。"""
    return (
        '<text x="%d" y="%d" text-anchor="middle" font-size="%d" '
        'font-weight="%s" fill="%s">%s</text>'
    ) % (x, y, size, weight, fill, _escape(text))


def _child_row(
    category_names: Sequence[str],
    center_x: int,
    color: str,
    soft: str,
) -> List[str]:
    """渲染一级分类下方的一排二级类别方块与连接线。"""
    if not category_names:
        return []
    box_width = 74
    box_height = 58
    gap = 10
    top = 232
    bus_y = 204
    total_width = len(category_names) * box_width + (len(category_names) - 1) * gap
    first_center = int(round(center_x - total_width / 2.0 + box_width / 2.0))
    centers = [first_center + index * (box_width + gap) for index in range(len(category_names))]
    parts: List[str] = [
        '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
        % (centers[0], bus_y, centers[-1], bus_y, color)
    ]
    for center, category in zip(centers, category_names):
        x = center - box_width // 2
        count = len(animals_in(category))
        parts.append(
            '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>'
            % (center, bus_y, center, top, color)
        )
        parts.append(
            '<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s"/>'
            % (x, top, box_width, box_height, soft, color)
        )
        parts.append(_svg_text(center, top + 23, category, 14, "700", color))
        parts.append(_svg_text(center, top + 42, "%d 种" % count, 11, "400", "#52606d"))
    return parts


def tree_svg() -> str:
    """返回脊椎动物五类与无脊椎动物类群的两级分类树 SVG。"""
    vertebrates = [category for category in categories() if is_vertebrate(category)]
    invertebrates = [category for category in categories() if not is_vertebrate(category)]
    vert_count = sum(len(animals_in(category)) for category in vertebrates)
    invert_count = sum(len(animals_in(category)) for category in invertebrates)
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 312" '
        'width="100%" role="img" aria-label="动物分类树">',
        '<style>text{font-family:"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;}</style>',
        '<rect x="0" y="0" width="1000" height="312" fill="#ffffff"/>',
        '<rect x="430" y="12" width="140" height="42" rx="21" fill="#334e68"/>',
        _svg_text(500, 39, "动物", 16, "700", "#ffffff"),
        '<line x1="500" y1="54" x2="500" y2="88" stroke="#9fb3c8" stroke-width="2"/>',
        '<line x1="250" y1="88" x2="750" y2="88" stroke="#9fb3c8" stroke-width="2"/>',
    ]
    parents: Tuple[Tuple[int, str, str, str, str], ...] = (
        (250, "脊椎动物", "%d 类 · %d 种" % (len(vertebrates), vert_count), "#2f855a", "#e6f4ea"),
        (750, "无脊椎动物", "%d 类 · %d 种" % (len(invertebrates), invert_count), "#2b6cb0", "#e6f0fa"),
    )
    for center, label, count_text, color, soft in parents:
        parts.append(
            '<line x1="%d" y1="88" x2="%d" y2="116" stroke="%s" stroke-width="2"/>'
            % (center, center, color)
        )
        parts.append(
            '<rect x="%d" y="116" width="240" height="46" rx="10" fill="%s" stroke="%s"/>'
            % (center - 120, soft, color)
        )
        parts.append(_svg_text(center, 137, label, 15, "700", color))
        parts.append(_svg_text(center, 154, count_text, 11, "400", "#52606d"))
        parts.append(
            '<line x1="%d" y1="162" x2="%d" y2="204" stroke="%s" stroke-width="2"/>'
            % (center, center, color)
        )
    parts.extend(_child_row(vertebrates, 250, "#2f855a", "#e6f4ea"))
    parts.extend(_child_row(invertebrates, 750, "#2b6cb0", "#e6f0fa"))
    parts.append("</svg>")
    return "\n".join(parts)


def _require_animal_fields(animal: Animal, index: int) -> None:
    """校验单个 Animal 的字段类型与取值。"""
    for field_name in ("name", "category", "diet", "habitat", "fact"):
        value = getattr(animal, field_name)
        if not isinstance(value, str):
            raise TypeError("第 %d 个动物的 %s 必须是字符串" % (index + 1, field_name))
        if not value.strip():
            raise ValueError("第 %d 个动物的 %s 不能为空" % (index + 1, field_name))
    if animal.category not in categories():
        raise ValueError("第 %d 个动物的类别未知：%s" % (index + 1, animal.category))
    if not isinstance(animal.aliases, tuple):
        raise TypeError("第 %d 个动物的 aliases 必须是元组" % (index + 1))
    for alias in animal.aliases:
        if not isinstance(alias, str):
            raise TypeError("第 %d 个动物的别名必须是字符串" % (index + 1))
        if not alias.strip():
            raise ValueError("第 %d 个动物的别名不能为空" % (index + 1))


def _coerce_animals(animals: Sequence[Animal]) -> List[Animal]:
    """把可迭代对象转换为 Animal 列表并逐个校验。"""
    if isinstance(animals, (str, bytes)):
        raise TypeError("animals 必须是 Animal 的序列")
    try:
        items = list(animals)
    except TypeError as exc:
        raise TypeError("animals 必须是 Animal 的序列") from exc
    if not items:
        raise ValueError("动物列表不能为空")
    for index, animal in enumerate(items):
        if not isinstance(animal, Animal):
            raise TypeError("第 %d 个元素不是 Animal" % (index + 1))
        _require_animal_fields(animal, index)
    return items


def _diet_summary(items: Sequence[Animal]) -> str:
    """生成「草食 1 · 肉食 2 · 杂食 3」形式的食性统计。"""
    parts: List[str] = []
    for diet in ("草食", "肉食", "杂食"):
        count = sum(1 for animal in items if animal.diet == diet)
        if count:
            parts.append("%s %d" % (diet, count))
    return " · ".join(parts)


def _category_card(category: str, items: Sequence[Animal]) -> str:
    """渲染单个类别的动物卡片。"""
    kind = "脊椎动物" if is_vertebrate(category) else "无脊椎动物"
    habitats: List[str] = []
    for animal in items:
        if animal.habitat not in habitats:
            habitats.append(animal.habitat)
    chips = "".join('<span class="animal">%s</span>' % _escape(animal.name) for animal in items)
    return (
        '<article class="card">'
        "<h3>%s<span class=\"tag\">%s</span></h3>"
        '<p class="meta">%d 种 · 食性：%s</p>'
        '<p class="meta">栖息环境：%s</p>'
        '<p class="chips">%s</p>'
        "</article>"
    ) % (
        _escape(category),
        _escape(kind),
        len(items),
        _escape(_diet_summary(items)),
        _escape("、".join(habitats)),
        chips,
    )


def _group_section(heading: str, css_class: str, cards: Sequence[str]) -> str:
    """渲染脊椎动物或无脊椎动物的卡片区。"""
    if not cards:
        return ""
    return (
        '<section class="group-section %s">'
        "<h2>%s</h2>"
        '<div class="cards">%s</div>'
        "</section>"
    ) % (css_class, _escape(heading), "".join(cards))


def _detail_table(grouped: Dict[str, List[Animal]], total: int) -> str:
    """渲染动物明细表。"""
    rows: List[str] = []
    number = 0
    for category in categories():
        for animal in grouped[category]:
            number += 1
            aliases = "、".join(animal.aliases) if animal.aliases else "—"
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (
                    number,
                    _escape(animal.name),
                    _escape(animal.category),
                    _escape(animal.diet),
                    _escape(animal.habitat),
                    _escape(animal.fact),
                    _escape(aliases),
                )
            )
    return (
        '<section class="table-section">'
        "<h2>动物明细表（%d 种）</h2>"
        "<table><thead><tr>"
        "<th>序号</th><th>动物</th><th>类别</th><th>食性</th>"
        "<th>栖息环境</th><th>特征 / 趣闻</th><th>别名</th>"
        "</tr></thead><tbody>%s</tbody></table>"
        "</section>"
    ) % (total, "".join(rows))


def poster_html(animals: Sequence[Animal]) -> str:
    """渲染动物分类海报：分类树 + 类别卡片 + 动物明细表。"""
    items = _coerce_animals(animals)
    grouped: Dict[str, List[Animal]] = {category: [] for category in categories()}
    for animal in items:
        grouped[animal.category].append(animal)
    vertebrates = [category for category in categories() if is_vertebrate(category)]
    invertebrates = [category for category in categories() if not is_vertebrate(category)]
    vert_cards = [
        _category_card(category, grouped[category])
        for category in vertebrates
        if grouped[category]
    ]
    invert_cards = [
        _category_card(category, grouped[category])
        for category in invertebrates
        if grouped[category]
    ]
    present = sum(1 for category in categories() if grouped[category])
    header = (
        '<header class="page-header"><h1>动物分类海报</h1>'
        '<p class="subtitle">%d 种动物 · %d 个类别 · A4 可打印</p>'
        "</header>"
    ) % (len(items), present)
    body = "\n".join(
        [
            header,
            '<section class="tree-section"><h2>分类树</h2><div class="tree">%s</div></section>'
            % tree_svg(),
            _group_section("脊椎动物", "vertebrate", vert_cards),
            _group_section("无脊椎动物", "invertebrate", invert_cards),
            _detail_table(grouped, len(items)),
            '<footer class="footer">animalclassification · MIT © 2026 eastyou</footer>',
        ]
    )
    return _page("动物分类海报", body)


def _require_field(item: Dict[str, object], key: str, index: int) -> object:
    """读取题目字段；缺失时抛 ValueError。"""
    if key not in item:
        raise ValueError("第 %d 道题缺少字段「%s」" % (index + 1, key))
    return item[key]


def _require_quiz_text(value: object, label: str) -> str:
    """校验题目中的字符串字段。"""
    if not isinstance(value, str):
        raise TypeError("%s必须是字符串" % label)
    text = value.strip()
    if not text:
        raise ValueError("%s不能为空" % label)
    return text


def _quiz_item_block(index: int, item: Dict[str, object], with_answers: bool) -> str:
    """渲染单道四选一题目。"""
    number = index + 1
    question = _require_quiz_text(
        _require_field(item, "question", index), "第 %d 道题的题干" % number
    )
    raw_options = _require_field(item, "options", index)
    if not isinstance(raw_options, (list, tuple)):
        raise TypeError("第 %d 道题的选项必须是列表" % number)
    if len(raw_options) != 4:
        raise ValueError("第 %d 道题必须提供 4 个选项" % number)
    options: List[str] = []
    for option in raw_options:
        options.append(_require_quiz_text(option, "第 %d 道题的选项" % number))
    if len(set(options)) != 4:
        raise ValueError("第 %d 道题的选项不能重复" % number)
    answer = _require_quiz_text(
        _require_field(item, "answer", index), "第 %d 道题的答案" % number
    )
    if answer not in options:
        raise ValueError("第 %d 道题的答案必须出现在选项中" % number)
    explanation = _require_quiz_text(
        _require_field(item, "explanation", index), "第 %d 道题的解析" % number
    )
    labels = ("A", "B", "C", "D")
    option_html = "".join(
        '<li class="option"><span class="label">%s</span>%s</li>'
        % (labels[position], _escape(option))
        for position, option in enumerate(options)
    )
    if with_answers:
        tail = (
            '<p class="answer"><strong>答案：</strong>%s</p>'
            '<p class="explanation"><strong>解析：</strong>%s</p>'
        ) % (_escape(answer), _escape(explanation))
    else:
        tail = '<p class="answer-line">答案：________</p>'
    return (
        '<article class="quiz-item">'
        '<p class="question"><span class="number">%d.</span>%s</p>'
        '<ol class="options">%s</ol>%s'
        "</article>"
    ) % (number, _escape(question), option_html, tail)


def quiz_html(
    items: Sequence[Dict[str, object]],
    title: str,
    with_answers: bool = False,
) -> str:
    """渲染四选一练习题；with_answers 为 True 时附答案与解析。"""
    title_text = _require_title(title)
    if not isinstance(with_answers, bool):
        raise TypeError("with_answers 必须是布尔值")
    if isinstance(items, (str, bytes)):
        raise TypeError("items 必须是题目字典的序列")
    try:
        item_list = list(items)
    except TypeError as exc:
        raise TypeError("items 必须是题目字典的序列") from exc
    if not item_list:
        raise ValueError("题目列表不能为空")
    blocks: List[str] = []
    for index, item in enumerate(item_list):
        if not isinstance(item, dict):
            raise TypeError("第 %d 道题必须是字典" % (index + 1))
        blocks.append(_quiz_item_block(index, item, with_answers))
    header = (
        '<header class="page-header"><h1>%s</h1>'
        '<p class="subtitle">共 %d 道单选题 · 每题只有一个正确选项</p>'
        "</header>"
    ) % (_escape(title_text), len(item_list))
    hint = '<p class="match-hint">答题说明：把正确选项的字母写在题号后的括号内。</p>'
    body = "\n".join(
        [
            header,
            hint,
            "\n".join(blocks),
            '<footer class="footer">animalclassification · MIT © 2026 eastyou</footer>',
        ]
    )
    return _page(title_text, body)


def match_html(pairs: Sequence[Tuple[str, str]], title: str) -> str:
    """渲染动物—类别配对练习（右侧类别按名称排序，避免与左侧对齐）。"""
    title_text = _require_title(title)
    if isinstance(pairs, (str, bytes)):
        raise TypeError("pairs 必须是 (动物, 类别) 元组的序列")
    try:
        pair_list = list(pairs)
    except TypeError as exc:
        raise TypeError("pairs 必须是 (动物, 类别) 元组的序列") from exc
    if not pair_list:
        raise ValueError("配对列表不能为空")
    normalized: List[Tuple[str, str]] = []
    seen_animals: Dict[str, str] = {}
    for index, pair in enumerate(pair_list):
        if not isinstance(pair, (tuple, list)):
            raise TypeError("第 %d 个配对必须是二元组" % (index + 1))
        if len(pair) != 2:
            raise ValueError("第 %d 个配对必须包含动物与类别两个名称" % (index + 1))
        animal = _require_quiz_text(pair[0], "第 %d 个配对的动物名称" % (index + 1))
        category = _require_quiz_text(pair[1], "第 %d 个配对的类别名称" % (index + 1))
        if animal in seen_animals:
            raise ValueError("配对的动物名称重复：%s" % animal)
        seen_animals[animal] = category
        normalized.append((animal, category))
    group_names = sorted({category for _, category in normalized})
    if len(group_names) > 26:
        raise ValueError("配对练习中的类别不能超过 26 个")
    labels = [chr(ord("A") + position) for position in range(len(group_names))]
    left = "".join(
        '<li><span class="blank">（　）</span>%s</li>' % _escape(animal)
        for animal, _ in normalized
    )
    right = "".join(
        '<li><span class="label">%s.</span>%s</li>' % (labels[position], _escape(category))
        for position, category in enumerate(group_names)
    )
    header = (
        '<header class="page-header"><h1>%s</h1>'
        '<p class="subtitle">共 %d 组配对 · 把右侧字母写在左侧括号内</p>'
        "</header>"
    ) % (_escape(title_text), len(normalized))
    body = "\n".join(
        [
            header,
            '<p class="match-hint">将左侧的代表动物与右侧的动物类别配对。</p>',
            '<div class="match-columns">',
            '<section class="match-col"><h2>代表动物</h2><ol>%s</ol></section>' % left,
            '<section class="match-col"><h2>动物类别</h2><ol>%s</ol></section>' % right,
            "</div>",
            '<footer class="footer">animalclassification · MIT © 2026 eastyou</footer>',
        ]
    )
    return _page(title_text, body)
