<div align="center">

# typing_tool

_**Typing_Tool** 是一个 Python 类型工具_


 [![CodeFactor](https://www.codefactor.io/repository/github/lacia-hIE/typing_tool/badge)](https://www.codefactor.io/repository/github/lacia-hIE/typing_tool)
 [![GitHub](https://img.shields.io/github/license/lacia-hIE/typing_tool)](https://github.com/lacia-hIE/typing_tool/blob/master/LICENSE)
 [![CodeQL](https://github.com/lacia-hIE/typing_tool/workflows/CodeQL/badge.svg)](https://github.com/lacia-hIE/typing_tool/blob/master/.github/workflows/codeql.yml)

</div>

## 功能



## 安装

```sh
pip install typing_tool
```

Or

```sh
pdm add typing_tool
```

## 入门指南

typing_tool 是一个用于增强 Python 类型检查能力的工具库。特别地，它扩展了 isinstance 和 issubclass 函数的能力，使其能够处理更复杂的类型检查需求。

## 支持类型

### like_isinstance

* 基础类型 str/int/...
* 容器泛型 list[T]/dict[K, V]/...
* Union 类型类型
* Type 
* TypeVar 类型变量
* 泛型类 Generic[T]
* Annotated/Field 注解类型
* Protocol 协议类型
* Protocol[T] 泛型协议类型
* TypedDict 字典类型
* dataclass 数据类
* dataclass[T] 泛型数据类

### like_issubclass

* 基础类型 str/int
* 容器泛型 list[T]/dict[K, V]
* Union 类型类型
* NewType 新类型
* Type 
* TypeVar 类型变量
* 泛型类 Generic[T]
* Protocol 协议类型
* Protocol[T] 泛型协议类型

### Check Config

* depth: 设置类型检查的最大深度
* max_sample: 设置最大采样数
* protocol_type_strict: 是否严格检查 Protocol 类型
* dataclass_type_strict: 是否严格检查 dataclass 类型

### 自动重载

```python

from typing_tool import auto_overload

@overload
def process(response: None) -> None:
    return None
@overload
def process(responsel: int, response2: str) -> tuple[int, str]:
    return response1, response2
@overload
def process(response: bytes) -> str:
    return response.decode()
@auto_convert
def process(*args, **kwargs) -> Any: ...
assert process(None) is None
assert process(1, "2") == (1, "2")
assert process(b"test") == "test"
```

### 注意

* NewType 无法在运行时进行 like_isinstance