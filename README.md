# animalclassification

[![CI](https://github.com/eastyou/animalclassification/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/animalclassification/actions/workflows/ci.yml)
[![MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

面向师生的动物分类查询与练习工具：收录脊椎动物五类、无脊椎动物六类共 87 种动物，零第三方依赖。

## 功能

- **数据齐全**：鱼类、两栖类、爬行类、鸟类、哺乳类各 9 种，昆虫、蛛形类、甲壳类、软体类、环节类、棘皮类各 7 种。
- **精确查询**：按中文名或别名查找动物，按类别名或类别别名列出动物，未知输入给出中文提示。
- **食性判断**：查询每种动物的食性（草食 / 肉食 / 杂食）与栖息环境。
- **四选一练习**：随机生成「某动物属于哪一类」，干扰项来自其他类别且互不重复，支持固定随机种子与脊椎 / 无脊椎分组。
- **配对练习**：生成动物与类别的配对题，类别自动去重并按字母编号。
- **可打印页面**：内置纯 SVG 两级分类树、类别卡片、动物明细表，带 `@media print` 与 A4 页面设置。
- **兼容性**：仅用 Python 标准库，兼容 Python 3.9.6 与 3.15.2。

## 安装

```bash
pip install -e .
```

安装后可直接使用 `animalclassification` 命令，也可以 `python -m animalclassification` 运行。

## 命令行示例

```bash
# 查看一种动物的分类信息
animalclassification info 鲸

# 列出某个类别下的动物（支持别名，如 兽类、鱼纲、棘皮）
animalclassification list 鸟类

# 查看全部类别
animalclassification categories

# 查询食性
animalclassification diet 熊猫

# 生成 10 道四选一练习，固定随机种子并保存为 HTML
animalclassification quiz --count 10 --seed 5 -o examples/quiz.html

# 只出脊椎动物的题目
animalclassification quiz --count 20 --seed 7 --group 脊椎

# 生成 8 组配对练习
animalclassification match --count 8 --seed 3 -o examples/match.html

# 生成完整分类海报
animalclassification poster -o examples/poster.html
```

`info 鲸` 的输出示例：

```text
名称：鲸
类别：哺乳类（脊椎动物）
食性：肉食
栖息环境：海洋
特征或趣闻：用肺呼吸，鼻孔位于头顶，需定期浮出水面换气
别名：鲸鱼
```

## 库用法

```python
from animalclassification import (
    all_animals,
    animals_in,
    categories,
    diet_of,
    find_animal,
    is_vertebrate,
    quiz_items,
    match_items,
    poster_html,
)

print(len(all_animals()))          # 87
print(categories())                # 脊椎五类在前，无脊椎类群在后
print(find_animal("娃娃鱼").name)   # 大鲵
print(diet_of("鲸"))               # 肉食
print(is_vertebrate("棘皮类"))      # False
print(len(animals_in("兽类")))      # 9

items = quiz_items(5, seed=2026, group="无脊椎")
pairs = match_items(8, seed=3)
html = poster_html(all_animals())
```

所有公共函数都带类型注解：类型错误抛 `TypeError`，取值错误抛 `ValueError`，错误消息为中文。

## 示例页

- [分类海报（分类树 + 类别卡片 + 87 种动物明细）](examples/poster.html)
- [四选一练习（10 题，答题用，不含答案）](examples/quiz.html)
- [动物—类别配对练习（8 组）](examples/match.html)

## 测试

```bash
python3 -m unittest discover -s tests -v
```

真实结果：**182 个 unittest 测试全部通过**，且两套解释器测试数量一致。

| 解释器 | 结果 |
| --- | --- |
| Python 3.9.6（`/usr/bin/python3`） | `Ran 182 tests ... OK` |
| Python 3.15.2（`python3`） | `Ran 182 tests ... OK` |

CI 在 Ubuntu / macOS / Windows 的 Python 3.10、3.13 上运行，并额外覆盖 Ubuntu 22.04 + Python 3.9。

## 许可

MIT © 2026 eastyou
