from __future__ import annotations

import pytest
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass

from typing_tool import like_isinstance, like_issubclass


class ForwardRefClass:
    """用于测试前向引用的类"""
    
    def __init__(self, value: str):
        self.value = value
    
    def get_child(self) -> ForwardRefClass:
        """返回自身类型的方法"""
        return ForwardRefClass(f"child of {self.value}")
    
    def process_list(self, items: List[ForwardRefClass]) -> List[ForwardRefClass]:
        """处理包含自身类型的列表"""
        return [ForwardRefClass(f"processed {item.value}") for item in items]


class CircularRefA:
    """用于测试循环引用的类A"""
    
    def __init__(self, name: str):
        self.name = name
        self.ref_b: Optional[CircularRefB] = None
    
    def set_ref(self, ref: CircularRefB) -> None:
        self.ref_b = ref


class CircularRefB:
    """用于测试循环引用的类B"""
    
    def __init__(self, value: int):
        self.value = value
        self.ref_a: Optional[CircularRefA] = None
    
    def set_ref(self, ref: CircularRefA) -> None:
        self.ref_a = ref


@dataclass
class DataWithStringAnnotation:
    """使用字符串注解的数据类"""
    items: List[str]
    mapping: Dict[str, int]
    optional_value: Optional[ForwardRefClass]
    union_value: Union[str, int, ForwardRefClass]


def process_forward_ref(item: ForwardRefClass) -> str:
    """使用前向引用作为参数类型的函数"""
    return f"Processing: {item.value}"


def process_complex_annotation(
    items: List[ForwardRefClass],
    mapping: Dict[str, ForwardRefClass],
    optional: Optional[ForwardRefClass] = None
) -> Dict[str, Any]:
    """使用复杂字符串注解的函数"""
    result = {
        "item_count": len(items),
        "mapping_size": len(mapping),
        "has_optional": optional is not None
    }
    return result


@pytest.mark.parametrize("obj, type_, expected", [
    # 测试前向引用类的实例
    (ForwardRefClass("test"), ForwardRefClass, True),
    (ForwardRefClass("test"), "ForwardRefClass", True),  # 字符串类型注解
    ("not a class", ForwardRefClass, False),
    
    # 测试包含前向引用的列表
    ([ForwardRefClass("a"), ForwardRefClass("b")], List[ForwardRefClass], True),
    ([ForwardRefClass("a"), ForwardRefClass("b")], "List[ForwardRefClass]", True),
    (["string", "list"], List[ForwardRefClass], False),
    
    # 测试包含前向引用的字典
    ({"key": ForwardRefClass("value")}, Dict[str, ForwardRefClass], True),
    ({"key": ForwardRefClass("value")}, "Dict[str, ForwardRefClass]", True),
    ({"key": "not_class"}, Dict[str, ForwardRefClass], False),
    
    # 测试可选的前向引用
    (ForwardRefClass("test"), Optional[ForwardRefClass], True),
    (ForwardRefClass("test"), "Optional[ForwardRefClass]", True),
    (None, Optional[ForwardRefClass], True),
    (None, "Optional[ForwardRefClass]", True),
    ("string", Optional[ForwardRefClass], False),
    
    # 测试联合类型的前向引用
    (ForwardRefClass("test"), Union[str, ForwardRefClass], True),
    (ForwardRefClass("test"), "Union[str, ForwardRefClass]", True),
    ("string", Union[str, ForwardRefClass], True),
    ("string", "Union[str, ForwardRefClass]", True),
    (123, Union[str, ForwardRefClass], False),
    
    # 测试循环引用
    (CircularRefA("test"), CircularRefA, True),
    (CircularRefA("test"), "CircularRefA", True),
    (CircularRefB(42), CircularRefB, True),
    (CircularRefB(42), "CircularRefB", True),
    
    # 测试数据类与字符串注解
    (DataWithStringAnnotation(
        items=["a", "b"],
        mapping={"key": 1},
        optional_value=ForwardRefClass("test"),
        union_value="string"
    ), DataWithStringAnnotation, True),
    (DataWithStringAnnotation(
        items=["a", "b"],
        mapping={"key": 1},
        optional_value=ForwardRefClass("test"),
        union_value="string"
    ), "DataWithStringAnnotation", True),
])
def test_like_isinstance_string_annotation(obj, type_, expected):
    """测试字符串注解的like_isinstance功能"""
    if isinstance(type_, str):
        # 对于字符串类型注解，需要在当前模块的全局命名空间中解析
        import sys
        current_module = sys.modules[__name__]
        type_ = eval(type_, current_module.__dict__)
    
    assert like_isinstance(obj, type_) == expected


@pytest.mark.parametrize("subclass, superclass, expected", [
    # 测试前向引用类的子类检查
    (ForwardRefClass, ForwardRefClass, True),
    (ForwardRefClass, object, True),
    (str, ForwardRefClass, False),
    
    # 测试循环引用类的子类检查
    (CircularRefA, CircularRefA, True),
    (CircularRefA, object, True),
    (CircularRefB, CircularRefB, True),
    (CircularRefB, object, True),
    (CircularRefA, CircularRefB, False),
    
    # 测试数据类的子类检查
    (DataWithStringAnnotation, DataWithStringAnnotation, True),
    (DataWithStringAnnotation, object, True),
    (dict, DataWithStringAnnotation, False),
])
def test_like_issubclass_string_annotation(subclass, superclass, expected):
    """测试字符串注解的like_issubclass功能"""
    assert like_issubclass(subclass, superclass) == expected


def test_function_with_string_annotations():
    """测试具有字符串注解的函数"""
    # 测试前向引用函数
    obj = ForwardRefClass("test")
    result = process_forward_ref(obj)
    assert result == "Processing: test"
    
    # 测试复杂注解函数
    items = [ForwardRefClass("item1"), ForwardRefClass("item2")]
    mapping = {"key": ForwardRefClass("value")}
    optional = ForwardRefClass("optional")
    
    result = process_complex_annotation(items, mapping, optional)
    assert result["item_count"] == 2
    assert result["mapping_size"] == 1
    assert result["has_optional"] is True


def test_circular_reference():
    """测试循环引用的情况"""
    ref_a = CircularRefA("A")
    ref_b = CircularRefB(42)
    
    # 设置循环引用
    ref_a.set_ref(ref_b)
    ref_b.set_ref(ref_a)
    
    # 测试类型检查
    assert like_isinstance(ref_a, CircularRefA)
    assert like_isinstance(ref_b, CircularRefB)
    assert like_isinstance(ref_a.ref_b, Optional[CircularRefB])
    assert like_isinstance(ref_b.ref_a, Optional[CircularRefA])


def test_nested_string_annotations():
    """测试嵌套的字符串注解"""
    # 创建嵌套结构
    inner = ForwardRefClass("inner")
    nested_list = [[inner, ForwardRefClass("nested")]]
    nested_dict = {"outer": {"inner": inner}}
    
    # 测试嵌套列表
    assert like_isinstance(nested_list, List[List[ForwardRefClass]])
    
    # 测试嵌套字典
    assert like_isinstance(nested_dict, Dict[str, Dict[str, ForwardRefClass]])


def test_method_return_annotations():
    """测试方法返回值的字符串注解"""
    obj = ForwardRefClass("parent")
    
    # 测试返回自身类型的方法
    child = obj.get_child()
    assert like_isinstance(child, ForwardRefClass)
    assert child.value == "child of parent"
    
    # 测试返回列表的方法
    items = [ForwardRefClass("item1"), ForwardRefClass("item2")]
    processed = obj.process_list(items)
    assert like_isinstance(processed, List[ForwardRefClass])
    assert len(processed) == 2


if __name__ == "__main__":
    pytest.main([__file__]) 