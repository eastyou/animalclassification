"""render 模块的单元测试。"""
from __future__ import annotations

import unittest
from typing import Dict, List, Tuple

from animalclassification.model import Animal, all_animals, categories, quiz_items
from animalclassification.render import match_html, poster_html, quiz_html, tree_svg


def _hostile_animal() -> Animal:
    """构造含 HTML 特殊字符的动物，用于转义测试。"""
    return Animal(
        name="<b>测试兽</b>",
        category="哺乳类",
        diet="杂食",
        habitat="<i>洞穴</i>",
        fact="<script>趣闻</script>",
        aliases=("<em>别名</em>",),
    )


class TreeSvgTests(unittest.TestCase):
    """tree_svg 测试。"""

    def test_returns_svg(self) -> None:
        text = tree_svg()
        self.assertTrue(text.startswith("<svg"))
        self.assertTrue(text.endswith("</svg>"))

    def test_contains_namespace_and_viewbox(self) -> None:
        text = tree_svg()
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', text)
        self.assertIn('viewBox="0 0 1000 312"', text)

    def test_contains_accessibility_attributes(self) -> None:
        text = tree_svg()
        self.assertIn('role="img"', text)
        self.assertIn('aria-label="动物分类树"', text)

    def test_contains_all_categories(self) -> None:
        text = tree_svg()
        for category in categories():
            with self.subTest(category=category):
                self.assertIn(category, text)

    def test_contains_two_level_labels(self) -> None:
        text = tree_svg()
        self.assertIn("脊椎动物", text)
        self.assertIn("无脊椎动物", text)

    def test_contains_counts(self) -> None:
        text = tree_svg()
        self.assertIn("9 种", text)
        self.assertIn("7 种", text)
        self.assertIn("5 类 · 45 种", text)
        self.assertIn("6 类 · 42 种", text)

    def test_has_no_invalid_numbers(self) -> None:
        text = tree_svg()
        self.assertNotIn("None", text)
        self.assertNotIn("nan", text)

    def test_is_deterministic(self) -> None:
        self.assertEqual(tree_svg(), tree_svg())


class PosterTests(unittest.TestCase):
    """poster_html 测试。"""

    def test_returns_html_document(self) -> None:
        text = poster_html(all_animals())
        self.assertTrue(text.startswith("<!DOCTYPE html>"))
        self.assertIn("</html>", text)

    def test_contains_title(self) -> None:
        text = poster_html(all_animals())
        self.assertIn("<title>动物分类海报</title>", text)
        self.assertIn("<h1>动物分类海报</h1>", text)

    def test_contains_tree(self) -> None:
        text = poster_html(all_animals())
        self.assertIn('class="tree"', text)
        self.assertIn("<svg", text)
        self.assertIn("动物分类树", text)

    def test_contains_all_categories(self) -> None:
        text = poster_html(all_animals())
        for category in categories():
            with self.subTest(category=category):
                self.assertIn(category, text)

    def test_contains_animal_samples(self) -> None:
        text = poster_html(all_animals())
        for name in ("鲸", "青蛙", "鲨鱼", "章鱼", "海星"):
            with self.subTest(name=name):
                self.assertIn(name, text)

    def test_contains_animal_count(self) -> None:
        text = poster_html(all_animals())
        self.assertIn("87 种动物 · 11 个类别", text)

    def test_contains_detail_table(self) -> None:
        text = poster_html(all_animals())
        self.assertIn("动物明细表（87 种）", text)
        self.assertIn("<th>特征 / 趣闻</th>", text)
        self.assertIn("<th>别名</th>", text)

    def test_contains_print_styles(self) -> None:
        text = poster_html(all_animals())
        self.assertIn("@media print", text)
        self.assertIn("@page { size: A4", text)

    def test_escapes_animal_fields(self) -> None:
        text = poster_html([_hostile_animal()])
        self.assertNotIn("<b>测试兽</b>", text)
        self.assertNotIn("<i>洞穴</i>", text)
        self.assertNotIn("<script>趣闻</script>", text)
        self.assertNotIn("<em>别名</em>", text)
        self.assertIn("&lt;b&gt;测试兽&lt;/b&gt;", text)
        self.assertIn("&lt;i&gt;洞穴&lt;/i&gt;", text)
        self.assertIn("&lt;script&gt;趣闻&lt;/script&gt;", text)
        self.assertIn("&lt;em&gt;别名&lt;/em&gt;", text)

    def test_supports_partial_list(self) -> None:
        text = poster_html([_hostile_animal()])
        self.assertIn("1 种动物 · 1 个类别", text)
        self.assertIn("动物明细表（1 种）", text)

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            poster_html([])

    def test_rejects_none(self) -> None:
        with self.assertRaises(TypeError):
            poster_html(None)  # type: ignore[arg-type]

    def test_rejects_string(self) -> None:
        with self.assertRaises(TypeError):
            poster_html("不是动物")  # type: ignore[arg-type]

    def test_rejects_non_animal_element(self) -> None:
        with self.assertRaises(TypeError):
            poster_html(["不是动物"])  # type: ignore[list-item]

    def test_rejects_unknown_category(self) -> None:
        animal = Animal("测试", "未知类", "草食", "某地", "某特征", ())
        with self.assertRaises(ValueError):
            poster_html([animal])

    def test_rejects_non_tuple_aliases(self) -> None:
        animal = Animal("测试", "哺乳类", "草食", "某地", "某特征", ["别名"])  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            poster_html([animal])

    def test_footer_credit(self) -> None:
        text = poster_html(all_animals())
        self.assertIn("2026 eastyou", text)


class QuizRenderTests(unittest.TestCase):
    """quiz_html 测试。"""

    def test_contains_question_count(self) -> None:
        text = quiz_html(quiz_items(3, seed=1), "练习")
        self.assertIn("共 3 道单选题", text)

    def test_hides_answers_by_default(self) -> None:
        text = quiz_html(quiz_items(2, seed=1), "练习")
        self.assertIn("答案：________", text)
        self.assertNotIn('class="answer"', text)
        self.assertNotIn("解析：", text)

    def test_shows_answers_when_requested(self) -> None:
        items = quiz_items(2, seed=1)
        text = quiz_html(items, "练习", with_answers=True)
        self.assertIn('class="answer"', text)
        self.assertIn("解析：", text)
        answer = str(items[0]["answer"])
        self.assertIn(answer, text)

    def test_escapes_dynamic_text(self) -> None:
        item: Dict[str, object] = {
            "question": "<b>问题</b>",
            "options": ["<i>A</i>", "B", "C", "D"],
            "answer": "<i>A</i>",
            "explanation": "<script>解析</script>",
        }
        text = quiz_html([item], "练习", with_answers=True)
        self.assertNotIn("<b>问题</b>", text)
        self.assertNotIn("<i>A</i>", text)
        self.assertNotIn("<script>解析</script>", text)
        self.assertIn("&lt;b&gt;问题&lt;/b&gt;", text)
        self.assertIn("&lt;i&gt;A&lt;/i&gt;", text)
        self.assertIn("&lt;script&gt;解析&lt;/script&gt;", text)

    def test_rejects_empty_items(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html([], "练习")

    def test_rejects_non_dict_item(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(["不是字典"], "练习")  # type: ignore[list-item]

    def test_rejects_missing_field(self) -> None:
        item = {
            "question": "问题",
            "options": ["A", "B", "C", "D"],
            "answer": "A",
        }
        with self.assertRaises(ValueError) as ctx:
            quiz_html([item], "练习")
        self.assertIn("explanation", str(ctx.exception))

    def test_rejects_wrong_option_count(self) -> None:
        item = {
            "question": "问题",
            "options": ["A", "B", "C"],
            "answer": "A",
            "explanation": "解析",
        }
        with self.assertRaises(ValueError):
            quiz_html([item], "练习")

    def test_rejects_duplicate_options(self) -> None:
        item = {
            "question": "问题",
            "options": ["A", "A", "C", "D"],
            "answer": "A",
            "explanation": "解析",
        }
        with self.assertRaises(ValueError):
            quiz_html([item], "练习")

    def test_rejects_answer_not_in_options(self) -> None:
        item = {
            "question": "问题",
            "options": ["A", "B", "C", "D"],
            "answer": "E",
            "explanation": "解析",
        }
        with self.assertRaises(ValueError):
            quiz_html([item], "练习")

    def test_rejects_non_list_options(self) -> None:
        item = {
            "question": "问题",
            "options": "ABCD",
            "answer": "A",
            "explanation": "解析",
        }
        with self.assertRaises(TypeError):
            quiz_html([item], "练习")

    def test_rejects_non_string_option(self) -> None:
        item = {
            "question": "问题",
            "options": [1, "B", "C", "D"],
            "answer": "B",
            "explanation": "解析",
        }
        with self.assertRaises(TypeError):
            quiz_html([item], "练习")

    def test_rejects_non_bool_with_answers(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(quiz_items(1, seed=1), "练习", with_answers="yes")  # type: ignore[arg-type]

    def test_rejects_non_string_title(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(quiz_items(1, seed=1), 123)  # type: ignore[arg-type]

    def test_rejects_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            quiz_html(quiz_items(1, seed=1), "")

    def test_rejects_non_sequence_items(self) -> None:
        with self.assertRaises(TypeError):
            quiz_html(123, "练习")  # type: ignore[arg-type]

    def test_contains_print_styles(self) -> None:
        text = quiz_html(quiz_items(1, seed=1), "练习")
        self.assertIn("@media print", text)
        self.assertIn("@page { size: A4", text)

    def test_question_numbers(self) -> None:
        text = quiz_html(quiz_items(3, seed=2), "练习")
        self.assertIn('<span class="number">1.</span>', text)
        self.assertIn('<span class="number">3.</span>', text)


class MatchRenderTests(unittest.TestCase):
    """match_html 测试。"""

    def test_contains_pairs(self) -> None:
        pairs: List[Tuple[str, str]] = [("青蛙", "两栖类"), ("鲸", "哺乳类")]
        text = match_html(pairs, "配对练习")
        self.assertIn("青蛙", text)
        self.assertIn("鲸", text)
        self.assertIn("两栖类", text)
        self.assertIn("哺乳类", text)
        self.assertIn("共 2 组配对", text)

    def test_groups_are_unique_and_lettered(self) -> None:
        pairs: List[Tuple[str, str]] = [
            ("青蛙", "两栖类"),
            ("牛蛙", "两栖类"),
            ("鲸", "哺乳类"),
        ]
        text = match_html(pairs, "配对练习")
        self.assertEqual(text.count("两栖类"), 1)
        self.assertIn('<span class="label">A.</span>', text)
        self.assertIn('<span class="label">B.</span>', text)

    def test_escapes_dynamic_text(self) -> None:
        pairs: List[Tuple[str, str]] = [("<b>动物</b>", "<i>类别</i>")]
        text = match_html(pairs, "配对练习")
        self.assertNotIn("<b>动物</b>", text)
        self.assertNotIn("<i>类别</i>", text)
        self.assertIn("&lt;b&gt;动物&lt;/b&gt;", text)
        self.assertIn("&lt;i&gt;类别&lt;/i&gt;", text)

    def test_rejects_empty_pairs(self) -> None:
        with self.assertRaises(ValueError):
            match_html([], "配对练习")

    def test_rejects_bad_pair_length(self) -> None:
        with self.assertRaises(ValueError):
            match_html([("青蛙",)], "配对练习")  # type: ignore[list-item]

    def test_rejects_non_tuple_pair(self) -> None:
        with self.assertRaises(TypeError):
            match_html(["青蛙"], "配对练习")  # type: ignore[list-item]

    def test_rejects_duplicate_animal(self) -> None:
        with self.assertRaises(ValueError):
            match_html([("青蛙", "两栖类"), ("青蛙", "两栖类")], "配对练习")

    def test_rejects_non_string_member(self) -> None:
        with self.assertRaises(TypeError):
            match_html([(1, "两栖类")], "配对练习")  # type: ignore[list-item]

    def test_rejects_non_sequence(self) -> None:
        with self.assertRaises(TypeError):
            match_html(123, "配对练习")  # type: ignore[arg-type]

    def test_rejects_non_string_title(self) -> None:
        with self.assertRaises(TypeError):
            match_html([("青蛙", "两栖类")], 123)  # type: ignore[arg-type]

    def test_rejects_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            match_html([("青蛙", "两栖类")], "  ")

    def test_rejects_too_many_groups(self) -> None:
        pairs = [("动物%d" % index, "类别%d" % index) for index in range(27)]
        with self.assertRaises(ValueError):
            match_html(pairs, "配对练习")

    def test_contains_print_styles(self) -> None:
        text = match_html([("青蛙", "两栖类")], "配对练习")
        self.assertIn("@media print", text)
        self.assertIn("@page { size: A4", text)


if __name__ == "__main__":
    unittest.main()
