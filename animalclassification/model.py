"""动物分类的数据模型、查询与练习生成函数。

数据覆盖脊椎动物五个类群（鱼类、两栖类、爬行类、鸟类、哺乳类）
与无脊椎动物六个类群（昆虫、蛛形类、甲壳类、软体类、环节类、棘皮类），
共 87 种代表动物。本模块只依赖 Python 标准库。
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Animal",
    "all_animals",
    "categories",
    "find_animal",
    "animals_in",
    "is_vertebrate",
    "diet_of",
    "quiz_items",
    "match_items",
]


@dataclass(frozen=True)
class Animal:
    """一种动物的分类信息。

    aliases 允许为空元组；其余字段均需为非空字符串。
    """

    name: str
    category: str
    diet: str
    habitat: str
    fact: str
    aliases: Tuple[str, ...]


_VERTEBRATE_CATEGORIES: Tuple[str, ...] = (
    "鱼类",
    "两栖类",
    "爬行类",
    "鸟类",
    "哺乳类",
)

_INVERTEBRATE_CATEGORIES: Tuple[str, ...] = (
    "昆虫",
    "蛛形类",
    "甲壳类",
    "软体类",
    "环节类",
    "棘皮类",
)

_CATEGORY_ORDER: Tuple[str, ...] = _VERTEBRATE_CATEGORIES + _INVERTEBRATE_CATEGORIES

_CATEGORY_ALIASES: Dict[str, Tuple[str, ...]] = {
    "鱼类": ("鱼纲", "鱼"),
    "两栖类": ("两栖动物", "蛙类"),
    "爬行类": ("爬行动物", "爬虫类"),
    "鸟类": ("鸟纲", "鸟"),
    "哺乳类": ("哺乳动物", "兽类"),
    "昆虫": ("昆虫纲", "六足类"),
    "蛛形类": ("蛛形纲", "蜘蛛类", "蛛形"),
    "甲壳类": ("甲壳纲", "虾蟹类", "甲壳"),
    "软体类": ("软体动物", "贝类", "软体"),
    "环节类": ("环节动物", "蚯蚓类", "环节"),
    "棘皮类": ("棘皮动物", "海星类", "棘皮"),
}

_DIETS: Tuple[str, ...] = ("草食", "肉食", "杂食")

_ANIMALS: Tuple[Animal, ...] = (
    # 鱼类（9 种）
    Animal("鲫鱼", "鱼类", "杂食", "淡水湖泊、池塘", "耐低氧，冬季可潜伏在泥中越冬", ("鲫",)),
    Animal("鲤鱼", "鱼类", "杂食", "淡水河湖", "口边有两对须，能探测水底食物", ("鲤",)),
    Animal("草鱼", "鱼类", "草食", "淡水江河、湖泊", "成年后几乎只吃水草，是典型的草食性鱼类", ("鲩鱼",)),
    Animal("鲢鱼", "鱼类", "草食", "淡水河流、水库", "靠鳃耙滤食浮游植物，被称为水体清道夫", ("白鲢",)),
    Animal("鲨鱼", "鱼类", "肉食", "海洋", "骨骼由软骨构成，一生能不断更换牙齿", ("沙鱼",)),
    Animal("鳕鱼", "鱼类", "肉食", "冷水海域", "下颌有一根须，用来在海底搜寻食物", ("大头鱼",)),
    Animal("鲈鱼", "鱼类", "肉食", "近海、河口", "背鳍硬棘锋利，捕食时能迅速冲刺", ("花鲈",)),
    Animal("带鱼", "鱼类", "肉食", "深海", "身体侧扁如带，靠波浪式摆动向前游动", ("刀鱼",)),
    Animal("金鱼", "鱼类", "杂食", "人工水池、水族箱", "由鲫鱼长期人工选育而来，品种繁多", ("金鲫",)),
    # 两栖类（9 种）
    Animal("青蛙", "两栖类", "肉食", "稻田、池塘", "幼体蝌蚪用鳃呼吸，成体用肺和皮肤呼吸", ("田鸡",)),
    Animal("蟾蜍", "两栖类", "肉食", "潮湿陆地、草丛", "皮肤粗糙有疣粒，能分泌毒液防御天敌", ("癞蛤蟆",)),
    Animal("大鲵", "两栖类", "肉食", "山溪、岩洞", "叫声像婴儿啼哭，因此被称为娃娃鱼", ("娃娃鱼",)),
    Animal("蝾螈", "两栖类", "肉食", "溪流、林下", "肢体断裂后能再生出新的肢体", ("火螈",)),
    Animal("雨蛙", "两栖类", "肉食", "树叶、灌木", "趾端有吸盘，能攀附在叶片上", ("树蟾",)),
    Animal("牛蛙", "两栖类", "肉食", "池塘、沼泽", "雄性叫声洪亮似牛哞，体型较大", ("美国青蛙",)),
    Animal("树蛙", "两栖类", "肉食", "热带雨林树冠", "趾间有蹼，能在树间滑翔", ("飞蛙",)),
    Animal("虎纹蛙", "两栖类", "肉食", "稻田、沟渠", "背部有虎斑状花纹，是国家二级保护动物", ("泥蛙",)),
    Animal("东方铃蟾", "两栖类", "肉食", "山间溪流", "受惊时翻转身体露出鲜艳腹面警告天敌", ("铃蟾",)),
    # 爬行类（9 种）
    Animal("蜥蜴", "爬行类", "肉食", "灌丛、岩石", "遇险时可断尾逃生，尾巴能重新长出", ("四脚蛇",)),
    Animal("蛇", "爬行类", "肉食", "森林、草原、农田", "靠下颌骨交替移动，吞下比头大的猎物", ("长虫",)),
    Animal("乌龟", "爬行类", "杂食", "河流、池塘", "背甲由肋骨和脊椎融合而成", ("草龟",)),
    Animal("鳄鱼", "爬行类", "肉食", "热带河流、沼泽", "咬合力极强，但张口的力量相对较弱", ("鳄",)),
    Animal("壁虎", "爬行类", "肉食", "房屋墙壁、树皮", "脚趾有特殊刚毛，能吸附在光滑表面", ("守宫",)),
    Animal("变色龙", "爬行类", "肉食", "热带雨林", "皮肤色素细胞能随情绪和环境改变颜色", ("避役",)),
    Animal("玳瑁", "爬行类", "杂食", "珊瑚礁、海洋", "背甲花纹美丽，是濒危保护动物", ("十三鳞",)),
    Animal("蟒蛇", "爬行类", "肉食", "热带雨林、沼泽", "无毒，用身体缠绕使猎物窒息", ("蚺蛇",)),
    Animal("棱皮龟", "爬行类", "肉食", "远洋", "是体型最大的海龟，背甲为革质而非硬壳", ("革龟",)),
    # 鸟类（9 种）
    Animal("麻雀", "鸟类", "杂食", "城镇、农田", "常在地面跳跃前进，喜欢集群活动", ("家雀",)),
    Animal("鸽子", "鸟类", "草食", "城市广场、岩壁", "能利用地磁场和太阳方位辨别方向", ("家鸽",)),
    Animal("老鹰", "鸟类", "肉食", "山地、草原", "视力约为人类的四到五倍", ("鹰",)),
    Animal("企鹅", "鸟类", "肉食", "南极海岸", "翅膀特化成鳍状，能在水下高速游泳", ()),
    Animal("鸵鸟", "鸟类", "杂食", "非洲草原", "是现存最大的鸟，不会飞但奔跑时速可达七十公里", ("非洲鸵鸟",)),
    Animal("丹顶鹤", "鸟类", "杂食", "湿地、芦苇荡", "头顶裸露皮肤呈鲜红色，并不是羽毛", ("仙鹤",)),
    Animal("鹦鹉", "鸟类", "草食", "热带森林", "能模仿人类说话，脚趾两前两后便于抓握", ("鹦哥",)),
    Animal("孔雀", "鸟类", "杂食", "热带林地", "雄鸟尾上覆羽展开形成眼斑求偶", ("蓝孔雀",)),
    Animal("猫头鹰", "鸟类", "肉食", "森林、农田", "颈部能旋转约二百七十度，飞行时几乎无声", ("鸮",)),
    # 哺乳类（9 种）
    Animal("鲸", "哺乳类", "肉食", "海洋", "用肺呼吸，鼻孔位于头顶，需定期浮出水面换气", ("鲸鱼",)),
    Animal("蝙蝠", "哺乳类", "肉食", "山洞、屋檐", "唯一能真正飞行的哺乳动物，靠回声定位导航", ()),
    Animal("大象", "哺乳类", "草食", "热带草原、森林", "长鼻有数万块肌肉，能卷起树枝也能感知震动", ("象",)),
    Animal("老虎", "哺乳类", "肉食", "森林、灌丛", "每只老虎的条纹都独一无二，像指纹一样", ("虎",)),
    Animal("人类", "哺乳类", "杂食", "全球各地", "大脑发达，能制造和使用复杂工具", ("智人",)),
    Animal("海豚", "哺乳类", "肉食", "海洋", "用回声定位捕食，群体之间有复杂的交流方式", ()),
    Animal("熊猫", "哺乳类", "草食", "竹林", "属于食肉目，却主要以竹子为食", ("大熊猫",)),
    Animal("袋鼠", "哺乳类", "草食", "澳大利亚草原", "育儿袋中的幼崽出生时只有花生米大小", ("大袋鼠",)),
    Animal("兔子", "哺乳类", "草食", "草原、农田", "门齿终身生长，需要不断啃咬东西磨牙", ("家兔",)),
    # 昆虫（7 种）
    Animal("蜜蜂", "昆虫", "草食", "花丛、蜂巢", "通过八字舞告诉同伴蜜源的方向和距离", ("蜂",)),
    Animal("蚂蚁", "昆虫", "杂食", "土壤、树干", "能举起超过自身体重数十倍的物体", ("蚁",)),
    Animal("蝴蝶", "昆虫", "草食", "花园、草地", "用足感知味道，翅膀上的鳞片构成彩色花纹", ("蝶",)),
    Animal("蜻蜓", "昆虫", "肉食", "池塘、溪流", "复眼由上万只小眼组成，飞行时能悬停", ("蜻蛉",)),
    Animal("蝗虫", "昆虫", "草食", "农田、草原", "后腿发达，成群迁飞时可日行上百公里", ("蚂蚱",)),
    Animal("蝉", "昆虫", "草食", "树上、林地", "幼虫在地下生活多年，成虫鸣叫求偶", ("知了",)),
    Animal("螳螂", "昆虫", "肉食", "草丛、灌木", "前足特化为捕捉足，交配后雌性有时会吃掉雄性", ("刀螂",)),
    # 蛛形类（7 种）
    Animal("蜘蛛", "蛛形类", "肉食", "屋檐、草丛", "多数种类的丝强度高于同粗细的钢丝", ("蛛",)),
    Animal("蝎子", "蛛形类", "肉食", "沙漠、石缝", "尾部毒针用于捕猎和自卫，幼蝎会爬到母背上", ("蝎",)),
    Animal("蜱虫", "蛛形类", "肉食", "草丛、林地", "吸血时身体可以膨胀数十倍", ("壁虱",)),
    Animal("螨虫", "蛛形类", "杂食", "床褥、土壤", "体长常小于一毫米，肉眼难以看清", ("螨",)),
    Animal("捕鸟蛛", "蛛形类", "肉食", "热带雨林", "体型大，能捕食昆虫甚至小型脊椎动物", ("食鸟蛛",)),
    Animal("盲蛛", "蛛形类", "肉食", "潮湿林地", "身体不分头胸腹，腿极长但并不是真正的蜘蛛", ("长腿蛛",)),
    Animal("狼蛛", "蛛形类", "肉食", "草丛、地面", "不结网，靠视力和速度追捕猎物", ("地蛛",)),
    # 甲壳类（7 种）
    Animal("虾", "甲壳类", "杂食", "江河、海洋", "靠腹部快速屈伸后退，逃避天敌", ("青虾",)),
    Animal("螃蟹", "甲壳类", "杂食", "河口、滩涂", "横着走是因为关节只能向两侧弯曲", ("蟹",)),
    Animal("龙虾", "甲壳类", "肉食", "海底岩礁", "触角发达，可感知水流和气味", ("大龙虾",)),
    Animal("寄居蟹", "甲壳类", "杂食", "海岸、潮间带", "会寻找空螺壳保护柔软的腹部，并随生长换壳", ("寄生蟹",)),
    Animal("潮虫", "甲壳类", "杂食", "潮湿落叶、石下", "属于甲壳类，却生活在陆地上，用伪气管呼吸", ("鼠妇",)),
    Animal("磷虾", "甲壳类", "杂食", "南大洋", "成群生活，是蓝鲸等海洋动物的重要食物", ("南极虾",)),
    Animal("水蚤", "甲壳类", "草食", "池塘、湖泊", "体长约一到三毫米，靠触角划水跳跃前进", ("溞",)),
    # 软体类（7 种）
    Animal("蜗牛", "软体类", "草食", "花园、潮湿草地", "齿舌上有上万颗微小牙齿，用来刮食植物", ("陆螺",)),
    Animal("章鱼", "软体类", "肉食", "海洋岩礁", "有八条腕足和三个心脏，能改变体色伪装", ("八爪鱼",)),
    Animal("乌贼", "软体类", "肉食", "近海", "遇险时喷出墨汁迷惑天敌，被称为海中火箭", ("墨鱼",)),
    Animal("蛤蜊", "软体类", "杂食", "沙滩、泥滩", "用斧足钻沙，靠水管滤食水中浮游生物", ("花蛤",)),
    Animal("扇贝", "软体类", "杂食", "浅海海底", "依靠贝壳开合喷水推进，部分种类有数十只小眼", ("海扇",)),
    Animal("牡蛎", "软体类", "杂食", "河口礁石", "能分泌珍珠质包裹异物，形成珍珠", ("生蚝",)),
    Animal("鱿鱼", "软体类", "肉食", "海洋", "身体呈火箭形，靠喷水推进快速游动", ("枪乌贼",)),
    # 环节类（7 种）
    Animal("蚯蚓", "环节类", "杂食", "土壤", "吞食泥土中的有机物，能改良土壤结构", ("曲蟮",)),
    Animal("水蛭", "环节类", "肉食", "淡水水域", "唾液含有抗凝血物质，曾被用于医疗", ("蚂蟥",)),
    Animal("沙蚕", "环节类", "肉食", "潮间带泥沙", "生殖期会变换体色并游向海面", ("海蜈蚣",)),
    Animal("沙蠋", "环节类", "杂食", "沙滩", "用触手收集沙中有机碎屑，排出成堆沙粪", ("沙虫",)),
    Animal("仙女虫", "环节类", "杂食", "淡水底泥", "身体细长透明，是水质监测的指示生物", ("白虫",)),
    Animal("缨鳃虫", "环节类", "杂食", "潮间带泥沙", "住在自己分泌的黏质管中，只露出触手取食", ("管沙蚕",)),
    Animal("颤蚓", "环节类", "杂食", "淡水底泥", "身体不停摆动以增加呼吸水流，常被用作鱼饲料", ("红虫",)),
    # 棘皮类（7 种）
    Animal("海星", "棘皮类", "肉食", "珊瑚礁、潮间带", "腕足断裂后能再生，部分种类可分裂繁殖", ("星鱼",)),
    Animal("海胆", "棘皮类", "草食", "岩礁、海藻林", "体表棘刺可防御天敌，管足用于移动和吸附", ("海栗",)),
    Animal("海参", "棘皮类", "杂食", "海底沙泥", "遇险时会把内脏喷出迷惑天敌，之后再生", ("刺参",)),
    Animal("海百合", "棘皮类", "肉食", "深海、珊瑚礁", "外形像植物，其实是动物，用羽状腕足滤食", ("海羽",)),
    Animal("蛇尾", "棘皮类", "肉食", "海底岩缝", "五条细长腕足灵活卷曲，英文名意为脆星", ("阳遂足",)),
    Animal("海盘车", "棘皮类", "肉食", "潮间带岩礁", "是海星的一种，腕足短而粗，再生能力强", ("多棘海盘车",)),
    Animal("海苹果", "棘皮类", "杂食", "珊瑚礁沙底", "受惊时喷出黏性管状物自卫", ()),
)


def _validate_animals(animals: Sequence[Animal]) -> None:
    """校验动物数据的结构与字段；类型错误抛 TypeError，取值错误抛 ValueError。"""
    if not isinstance(animals, (list, tuple)):
        raise TypeError("动物数据必须是列表或元组")
    seen: Dict[str, str] = {}
    for index, animal in enumerate(animals):
        if not isinstance(animal, Animal):
            raise TypeError("第 %d 个元素不是 Animal" % (index + 1))
        for field_name in ("name", "category", "diet", "habitat", "fact"):
            value = getattr(animal, field_name)
            if not isinstance(value, str):
                raise TypeError("第 %d 个动物的 %s 必须是字符串" % (index + 1, field_name))
            if not value.strip():
                raise ValueError("第 %d 个动物的 %s 不能为空" % (index + 1, field_name))
        if animal.category not in _CATEGORY_ORDER:
            raise ValueError("未知类别：%s" % animal.category)
        if animal.diet not in _DIETS:
            raise ValueError("动物「%s」的食性必须是：%s" % (animal.name, "、".join(_DIETS)))
        if not isinstance(animal.aliases, tuple):
            raise TypeError("动物「%s」的 aliases 必须是元组" % animal.name)
        for alias in animal.aliases:
            if not isinstance(alias, str):
                raise TypeError("动物「%s」的别名必须是字符串" % animal.name)
            if not alias.strip():
                raise ValueError("动物「%s」的别名不能为空" % animal.name)
        keys = (animal.name,) + animal.aliases
        for key in keys:
            lowered = key.casefold()
            if lowered in seen:
                raise ValueError(
                    "名称或别名「%s」重复出现在「%s」与「%s」中"
                    % (key, seen[lowered], animal.name)
                )
            seen[lowered] = animal.name


def _validate_dataset() -> None:
    """校验数据规模：脊椎每类至少 8 种，无脊椎每类至少 4 种，总数至少 70。"""
    total = len(_ANIMALS)
    if total < 70:
        raise ValueError("动物总数至少需要 70 种，当前只有 %d 种" % total)
    for category in _CATEGORY_ORDER:
        count = sum(1 for animal in _ANIMALS if animal.category == category)
        minimum = 8 if category in _VERTEBRATE_CATEGORIES else 4
        if count < minimum:
            raise ValueError("类别「%s」至少需要 %d 种动物" % (category, minimum))


_validate_animals(_ANIMALS)
_validate_dataset()


def _require_text(value: str, label: str) -> str:
    """校验非空字符串；类型错误抛 TypeError，空值抛 ValueError。"""
    if not isinstance(value, str):
        raise TypeError("%s必须是字符串" % label)
    text = value.strip()
    if not text:
        raise ValueError("%s不能为空" % label)
    return text


def _resolve_category(name: str) -> str:
    """把类别名称或类别别名解析为标准类别名称。"""
    text = _require_text(name, "类别名称")
    lowered = text.casefold()
    for category in _CATEGORY_ORDER:
        if category.casefold() == lowered:
            return category
    for category in _CATEGORY_ORDER:
        for alias in _CATEGORY_ALIASES[category]:
            if alias.casefold() == lowered:
                return category
    raise ValueError(
        "未知类别「%s」；可用类别：%s"
        % (text, "、".join(_CATEGORY_ORDER))
    )


def _validate_count(count: int, minimum: int, maximum: int, label: str) -> int:
    """校验数量参数；bool 视为类型错误。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("%s 必须是整数" % label)
    if count < minimum or count > maximum:
        raise ValueError("%s 必须在 %d 到 %d 之间" % (label, minimum, maximum))
    return count


def _validate_seed(seed: Optional[int]) -> Optional[int]:
    """校验随机种子；None 表示不固定种子，bool 视为类型错误。"""
    if seed is None:
        return None
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("随机种子 seed 必须是整数或 None")
    return seed


def _validate_group(group: Optional[str]) -> Optional[bool]:
    """把分组参数解析为 True（脊椎）/ False（无脊椎）/ None（全部）。"""
    if group is None:
        return None
    if not isinstance(group, str):
        raise TypeError("group 必须是字符串或 None")
    text = group.strip()
    if not text:
        raise ValueError("group 不能为空")
    mapping: Dict[str, bool] = {
        "脊椎": True,
        "脊椎动物": True,
        "无脊椎": False,
        "无脊椎动物": False,
    }
    if text not in mapping:
        raise ValueError("group 仅支持「脊椎」或「无脊椎」")
    return mapping[text]


def all_animals() -> List[Animal]:
    """返回全部动物（按类别顺序）的新列表。"""
    return list(_ANIMALS)


def categories() -> List[str]:
    """返回全部类别名称：脊椎动物五类在前，无脊椎动物类群在后。"""
    return list(_CATEGORY_ORDER)


def find_animal(query: str) -> Animal:
    """按动物名称或别名精确匹配动物；未知时抛出 ValueError。"""
    text = _require_text(query, "动物名称")
    lowered = text.casefold()
    for animal in _ANIMALS:
        if animal.name.casefold() == lowered:
            return animal
    for animal in _ANIMALS:
        for alias in animal.aliases:
            if alias.casefold() == lowered:
                return animal
    raise ValueError(
        "未找到动物「%s」；可用类别共 %d 个、动物共 %d 种"
        % (text, len(_CATEGORY_ORDER), len(_ANIMALS))
    )


def animals_in(category: str) -> List[Animal]:
    """返回指定类别下的动物列表；支持类别别名。"""
    resolved = _resolve_category(category)
    return [animal for animal in _ANIMALS if animal.category == resolved]


def is_vertebrate(category: str) -> bool:
    """判断类别是否属于脊椎动物；支持类别别名。"""
    resolved = _resolve_category(category)
    return resolved in _VERTEBRATE_CATEGORIES


def diet_of(query: str) -> str:
    """返回指定动物的食性（草食/肉食/杂食）。"""
    return find_animal(query).diet


def _category_pool(vertebrate_only: Optional[bool]) -> List[str]:
    """按分组条件返回可选类别列表。"""
    if vertebrate_only is None:
        return list(_CATEGORY_ORDER)
    if vertebrate_only:
        return list(_VERTEBRATE_CATEGORIES)
    return list(_INVERTEBRATE_CATEGORIES)


def quiz_items(
    count: int,
    seed: Optional[int] = None,
    group: Optional[str] = None,
) -> List[Dict[str, object]]:
    """生成「某动物属于哪一类」的四选一题目。

    count 取值范围为 1 到 40；group 可取「脊椎」或「无脊椎」。
    相同 count、seed、group 会得到相同题目。
    """
    total = _validate_count(count, 1, 40, "题目数量 count")
    random_seed = _validate_seed(seed)
    vertebrate_only = _validate_group(group)
    allowed_categories = _category_pool(vertebrate_only)
    pool = [
        animal
        for animal in _ANIMALS
        if animal.category in allowed_categories
    ]
    rng = random.Random(random_seed)
    rng.shuffle(pool)
    items: List[Dict[str, object]] = []
    for animal in pool[:total]:
        distractors = [
            category
            for category in allowed_categories
            if category != animal.category
        ]
        rng.shuffle(distractors)
        options = distractors[:3] + [animal.category]
        rng.shuffle(options)
        items.append(
            {
                "question": "动物「%s」属于下列哪一类？" % animal.name,
                "options": options,
                "answer": animal.category,
                "explanation": "「%s」属于%s。%s。"
                % (animal.name, animal.category, animal.fact),
            }
        )
    return items


def match_items(
    count: int,
    seed: Optional[int] = None,
) -> List[Tuple[str, str]]:
    """生成动物与类别的配对练习，count 取值范围为 1 到 20。"""
    total = _validate_count(count, 1, 20, "配对数量 count")
    random_seed = _validate_seed(seed)
    pool = list(_ANIMALS)
    rng = random.Random(random_seed)
    rng.shuffle(pool)
    return [(animal.name, animal.category) for animal in pool[:total]]
