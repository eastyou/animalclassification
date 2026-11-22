"""动物分类：脊椎动物五类与无脊椎类群查询、判断与练习页。"""
from __future__ import annotations

from typing import List

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
from animalclassification.render import match_html, poster_html, quiz_html, tree_svg

__version__: str = "0.1.0"

__all__: List[str] = [
    "Animal",
    "all_animals",
    "categories",
    "find_animal",
    "animals_in",
    "is_vertebrate",
    "diet_of",
    "quiz_items",
    "match_items",
    "tree_svg",
    "poster_html",
    "quiz_html",
    "match_html",
    "__version__",
]
