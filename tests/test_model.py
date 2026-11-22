"""model 模块的单元测试。"""
from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from typing import List, Tuple, cast

from animalclassification.model import (
    all_animals,
    animals_in,
    categories,
    diet_of,
    find_animal,
    is_vertebrate,
    match_items,
    quiz_items,
)


_EXPECTED_CATEGORIES: Tuple[str, ...] = (
    "鱼类",
    "两栖类",
    "爬行类",
    "鸟类",
    "哺乳类",
    "昆虫",
    "蛛形类",
    "甲壳类",
    "软体类",
    "环节类",
    "棘皮类",
)

_VERTEBRATES: Tuple[str, ...] = ("鱼类", "两栖类", "爬行类", "鸟类", "哺乳类")


class DataTests(unittest.TestCase):
    """数据规模与完整性测试。"""

    def test_total_at_least_seventy(self) -> None:
        self.assertGreaterEqual(len(all_animals()), 70)

    def test_total_count(self) -> None:
        self.assertEqual(len(all_animals()), 87)

    def test_category_order(self) -> None:
        self.assertEqual(categories(), list(_EXPECTED_CATEGORIES))

    def test_vertebrates_come_first(self) -> None:
        self.assertEqual(categories()[:5], list(_VERTEBRATES))

    def test_invertebrate_categories(self) -> None:
        self.assertEqual(categories()[5:], ["昆虫", "蛛形类", "甲壳类", "软体类", "环节类", "棘皮类"])

    def test_vertebrate_sizes(self) -> None:
        for category in _VERTEBRATES:
            with self.subTest(category=category):
                self.assertGreaterEqual(len(animals_in(category)), 8)

    def test_invertebrate_sizes(self) -> None:
        for category in categories()[5:]:
            with self.subTest(category=category):
                self.assertGreaterEqual(len(animals_in(category)), 4)

    def test_categories_are_unique(self) -> None:
        names = categories()
        self.assertEqual(len(names), len(set(names)))

    def test_animal_names_are_unique(self) -> None:
        names = [animal.name for animal in all_animals()]
        self.assertEqual(len(names), len(set(names)))

    def test_aliases_do_not_conflict(self) -> None:
        keys: List[str] = []
        for animal in all_animals():
            keys.append(animal.name.casefold())
            for alias in animal.aliases:
                keys.append(alias.casefold())
        self.assertEqual(len(keys), len(set(keys)))

    def test_diets_are_valid(self) -> None:
        for animal in all_animals():
            with self.subTest(animal=animal.name):
                self.assertIn(animal.diet, ("草食", "肉食", "杂食"))

    def test_text_fields_are_non_empty(self) -> None:
        for animal in all_animals():
            with self.subTest(animal=animal.name):
                self.assertTrue(animal.name.strip())
                self.assertTrue(animal.category.strip())
                self.assertTrue(animal.diet.strip())
                self.assertTrue(animal.habitat.strip())
                self.assertTrue(animal.fact.strip())

    def test_aliases_are_tuples(self) -> None:
        for animal in all_animals():
            with self.subTest(animal=animal.name):
                self.assertIsInstance(animal.aliases, tuple)
                for alias in animal.aliases:
                    self.assertTrue(alias.strip())

    def test_some_animals_have_no_alias(self) -> None:
        empty = [animal.name for animal in all_animals() if not animal.aliases]
        self.assertIn("企鹅", empty)

    def test_animals_are_frozen(self) -> None:
        animal = all_animals()[0]
        with self.assertRaises(FrozenInstanceError):
            animal.name = "新名称"  # type: ignore[misc]

    def test_all_animals_returns_fresh_list(self) -> None:
        first = all_animals()
        first.pop()
        self.assertEqual(len(all_animals()), 87)

    def test_categories_returns_fresh_list(self) -> None:
        first = categories()
        first.pop()
        self.assertEqual(len(categories()), 11)

    def test_is_vertebrate_matches_category_order(self) -> None:
        for index, category in enumerate(categories()):
            with self.subTest(category=category):
                self.assertEqual(is_vertebrate(category), index < 5)


class FindAnimalTests(unittest.TestCase):
    """find_animal 查询测试。"""

    def test_find_by_name(self) -> None:
        self.assertEqual(find_animal("鲸").category, "哺乳类")

    def test_find_strips_whitespace(self) -> None:
        self.assertEqual(find_animal("  鲸  ").name, "鲸")

    def test_find_by_alias(self) -> None:
        self.assertEqual(find_animal("大熊猫").name, "熊猫")

    def test_find_by_second_alias(self) -> None:
        self.assertEqual(find_animal("娃娃鱼").name, "大鲵")

    def test_find_rejects_non_string(self) -> None:
        with self.assertRaises(TypeError):
            find_animal(None)  # type: ignore[arg-type]

    def test_find_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            find_animal("")

    def test_find_rejects_blank(self) -> None:
        with self.assertRaises(ValueError):
            find_animal("   ")

    def test_find_rejects_unknown(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            find_animal("恐龙")
        self.assertIn("未找到动物", str(ctx.exception))

    def test_unknown_message_lists_category_count(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            find_animal("恐龙")
        self.assertIn("可用类别共 11 个", str(ctx.exception))

    def test_unknown_message_lists_animal_count(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            find_animal("恐龙")
        self.assertIn("动物共 87 种", str(ctx.exception))

    def test_find_rejects_category_name(self) -> None:
        with self.assertRaises(ValueError):
            find_animal("哺乳类")


class AnimalsInTests(unittest.TestCase):
    """animals_in 查询测试。"""

    def test_returns_animals_of_category(self) -> None:
        items = animals_in("鱼类")
        self.assertEqual(len(items), 9)
        self.assertEqual(items[0].name, "鲫鱼")
        self.assertTrue(all(animal.category == "鱼类" for animal in items))

    def test_accepts_category_alias(self) -> None:
        self.assertEqual(
            [animal.name for animal in animals_in("兽类")],
            [animal.name for animal in animals_in("哺乳类")],
        )

    def test_accepts_second_alias(self) -> None:
        self.assertEqual(len(animals_in("鱼纲")), 9)

    def test_returns_copy(self) -> None:
        items = animals_in("鸟类")
        items.clear()
        self.assertEqual(len(animals_in("鸟类")), 9)

    def test_rejects_unknown_category(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            animals_in("恐龙类")
        self.assertIn("未知类别", str(ctx.exception))
        self.assertIn("哺乳类", str(ctx.exception))

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            animals_in("")

    def test_rejects_non_string(self) -> None:
        with self.assertRaises(TypeError):
            animals_in(123)  # type: ignore[arg-type]

    def test_rejects_animal_name(self) -> None:
        with self.assertRaises(ValueError):
            animals_in("鲸")


class IsVertebrateTests(unittest.TestCase):
    """is_vertebrate 判断测试。"""

    def test_fish_is_vertebrate(self) -> None:
        self.assertTrue(is_vertebrate("鱼类"))

    def test_insect_is_invertebrate(self) -> None:
        self.assertFalse(is_vertebrate("昆虫"))

    def test_alias_is_supported(self) -> None:
        self.assertTrue(is_vertebrate("兽类"))

    def test_invertebrate_alias_is_supported(self) -> None:
        self.assertFalse(is_vertebrate("棘皮"))

    def test_unknown_category_rejected(self) -> None:
        with self.assertRaises(ValueError):
            is_vertebrate("不存在的类别")

    def test_empty_rejected(self) -> None:
        with self.assertRaises(ValueError):
            is_vertebrate("")

    def test_non_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            is_vertebrate(None)  # type: ignore[arg-type]


class DietTests(unittest.TestCase):
    """diet_of 测试。"""

    def test_whale_is_carnivore(self) -> None:
        self.assertEqual(diet_of("鲸"), "肉食")

    def test_rabbit_is_herbivore(self) -> None:
        self.assertEqual(diet_of("兔子"), "草食")

    def test_ant_is_omnivore(self) -> None:
        self.assertEqual(diet_of("蚂蚁"), "杂食")

    def test_accepts_alias(self) -> None:
        self.assertEqual(diet_of("娃娃鱼"), "肉食")

    def test_unknown_rejected(self) -> None:
        with self.assertRaises(ValueError):
            diet_of("恐龙")

    def test_non_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            diet_of(42)  # type: ignore[arg-type]


class QuizTests(unittest.TestCase):
    """quiz_items 测试。"""

    def test_returns_requested_count(self) -> None:
        self.assertEqual(len(quiz_items(10, seed=5)), 10)

    def test_count_one(self) -> None:
        self.assertEqual(len(quiz_items(1, seed=1)), 1)

    def test_count_forty(self) -> None:
        self.assertEqual(len(quiz_items(40, seed=1)), 40)

    def test_item_shape(self) -> None:
        item = quiz_items(1, seed=3)[0]
        self.assertEqual(set(item.keys()), {"question", "options", "answer", "explanation"})
        self.assertIsInstance(item["question"], str)
        self.assertIsInstance(item["answer"], str)
        self.assertIsInstance(item["explanation"], str)

    def test_options_are_four_unique(self) -> None:
        for item in quiz_items(20, seed=7):
            options = cast(List[str], item["options"])
            self.assertEqual(len(options), 4)
            self.assertEqual(len(set(options)), 4)

    def test_answer_in_options(self) -> None:
        for item in quiz_items(20, seed=9):
            options = cast(List[str], item["options"])
            answer = cast(str, item["answer"])
            self.assertIn(answer, options)

    def test_answer_is_known_category(self) -> None:
        for item in quiz_items(40, seed=11):
            self.assertIn(cast(str, item["answer"]), categories())

    def test_distractors_are_other_categories(self) -> None:
        for item in quiz_items(20, seed=13):
            answer = cast(str, item["answer"])
            options = cast(List[str], item["options"])
            self.assertEqual(len([option for option in options if option != answer]), 3)
            for option in options:
                self.assertIn(option, categories())

    def test_explanation_mentions_answer(self) -> None:
        for item in quiz_items(10, seed=11):
            answer = cast(str, item["answer"])
            explanation = cast(str, item["explanation"])
            self.assertIn(answer, explanation)

    def test_deterministic_with_seed(self) -> None:
        self.assertEqual(quiz_items(10, seed=5), quiz_items(10, seed=5))

    def test_questions_are_unique(self) -> None:
        questions = [cast(str, item["question"]) for item in quiz_items(40, seed=2)]
        self.assertEqual(len(questions), len(set(questions)))

    def test_count_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            quiz_items(0)

    def test_count_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            quiz_items(-1)

    def test_count_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            quiz_items(41)
        self.assertIn("1 到 40", str(ctx.exception))

    def test_count_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items("10")  # type: ignore[arg-type]

    def test_count_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(True)

    def test_count_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(2.5)  # type: ignore[arg-type]

    def test_count_none_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(None)  # type: ignore[arg-type]

    def test_seed_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(3, seed="5")  # type: ignore[arg-type]

    def test_seed_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(3, seed=True)

    def test_seed_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(3, seed=1.5)  # type: ignore[arg-type]

    def test_negative_seed_allowed(self) -> None:
        self.assertEqual(len(quiz_items(2, seed=-7)), 2)

    def test_group_vertebrate(self) -> None:
        for item in quiz_items(20, seed=3, group="脊椎"):
            self.assertTrue(is_vertebrate(cast(str, item["answer"])))

    def test_group_invertebrate(self) -> None:
        for item in quiz_items(20, seed=3, group="无脊椎"):
            self.assertFalse(is_vertebrate(cast(str, item["answer"])))

    def test_group_full_name_accepted(self) -> None:
        self.assertEqual(len(quiz_items(5, seed=1, group="脊椎动物")), 5)

    def test_group_invertebrate_count_forty(self) -> None:
        items = quiz_items(40, seed=4, group="无脊椎")
        self.assertEqual(len(items), 40)
        for item in items:
            self.assertFalse(is_vertebrate(cast(str, item["answer"])))

    def test_group_invalid_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            quiz_items(3, group="海洋")
        self.assertIn("脊椎", str(ctx.exception))

    def test_group_empty_rejected(self) -> None:
        with self.assertRaises(ValueError):
            quiz_items(3, group="   ")

    def test_group_non_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            quiz_items(3, group=1)  # type: ignore[arg-type]


class MatchTests(unittest.TestCase):
    """match_items 测试。"""

    def test_returns_requested_count(self) -> None:
        self.assertEqual(len(match_items(10, seed=3)), 10)

    def test_count_twenty(self) -> None:
        self.assertEqual(len(match_items(20, seed=3)), 20)

    def test_pairs_are_tuples(self) -> None:
        for pair in match_items(5, seed=1):
            self.assertIsInstance(pair, tuple)
            self.assertEqual(len(pair), 2)

    def test_animals_are_unique(self) -> None:
        animals = [animal for animal, _ in match_items(20, seed=4)]
        self.assertEqual(len(animals), len(set(animals)))

    def test_deterministic_with_seed(self) -> None:
        self.assertEqual(match_items(10, seed=3), match_items(10, seed=3))

    def test_pairs_are_correct(self) -> None:
        for animal, category in match_items(20, seed=6):
            self.assertEqual(find_animal(animal).category, category)

    def test_count_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            match_items(0)

    def test_count_too_large_rejected(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            match_items(21)
        self.assertIn("1 到 20", str(ctx.exception))

    def test_count_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_items(True)

    def test_count_float_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_items(2.0)  # type: ignore[arg-type]

    def test_seed_string_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_items(3, seed="x")  # type: ignore[arg-type]

    def test_seed_bool_rejected(self) -> None:
        with self.assertRaises(TypeError):
            match_items(3, seed=False)


if __name__ == "__main__":
    unittest.main()
