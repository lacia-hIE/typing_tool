<div align="center">

# typing_tool

_**Typing_Tool** 是一个 Python 类型工具_


 [![CodeFactor](https://www.codefactor.io/repository/github/lacia-hIE/typing_tool/badge)](https://www.codefactor.io/repository/github/lacia-hIE/typing_tool)
 [![GitHub](https://img.shields.io/github/license/lacia-hIE/typing_tool)](https://github.com/lacia-hIE/typing_tool/blob/master/LICENSE)
 [![CodeQL](https://github.com/lacia-hIE/typing_tool/workflows/CodeQL/badge.svg)](https://github.com/lacia-hIE/typing_tool/blob/master/.github/workflows/codeql.yml)

</div>

## 功能

- **类型检查增强**: 扩展 isinstance 和 issubclass 函数，支持复杂类型检查
- **自动重载**: 基于类型提示的函数重载功能
- **依赖注入**: 基于类型提示的自动依赖注入系统

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

* `depth`: 设置类型检查的最大深度，默认值为 `5`
* `max_sample`: 设置最大采样数，默认值为 `-1`
* `protocol_type_strict`: 是否严格检查 `Protocol` 类型，默认值为 `False`
* `dataclass_type_strict`: 是否严格检查 `dataclass` 类型，默认值为 `False`

### 自动重载

```python
from typing import Any
from typing_extensions import overload
from typing_tool import auto_overload

@overload
def process(response: None) -> None:
    return None
@overload
def process(response1: int, response2: str) -> tuple[int, str]:
    return response1, response2
@overload
def process(response: bytes) -> str:
    return response.decode()
@auto_overload()
def process(*args, **kwargs) -> Any: ...

assert process(None) is None
assert process(1, "2") == (1, "2")
assert process(b"test") == "test"
```

### 依赖注入

typing_tool 提供了强大的依赖注入功能，支持基于类型提示的自动依赖解析和注入。

#### 基本用法

```python
from typing_tool import auto_inject, create_injector, register_dependency

# 定义服务
class Logger:
    def log(self, message: str):
        print(f"[LOG] {message}")

class Database:
    def query(self, sql: str):
        return [{"id": 1, "data": "test"}]

# 创建依赖容器
dependencies = {
    'logger': Logger(),
    'db': Database()
}

# 使用 auto_inject 直接调用
def process_data(logger: Logger, db: Database):
    logger.log("Processing data...")
    return db.query("SELECT * FROM users")

result = auto_inject(process_data, dependencies)
```

#### 装饰器方式

```python
# 创建注入器装饰器
injector = create_injector(dependencies)

@injector
def service_function(logger: Logger, db: Database):
    logger.log("Service called")
    return db.query("SELECT * FROM products")

# 直接调用，依赖会自动注入
result = service_function()
```

#### 依赖注册

```python
# 使用装饰器注册依赖
@register_dependency(dependencies)
class UserService:
    def __init__(self, logger: Logger, db: Database):
        self.logger = logger
        self.db = db
    
    def get_users(self):
        self.logger.log("Getting users...")
        return self.db.query("SELECT * FROM users")

# UserService 实例会自动创建并注册到依赖容器中
```

#### 匹配策略

typing_tool 支持多种依赖匹配策略：

- `type_like`: 基于类型匹配（默认）
- `name_like`: 基于参数名匹配  
- `any_like`: 类型或名称匹配（参数优先）

```python
from typing_tool import name_like, any_like

# 使用名称匹配
name_injector = create_injector(dependencies, like=name_like)

# 使用混合匹配
any_injector = create_injector(dependencies, like=any_like)
```

### 注意

* NewType 无法在运行时进行 like_isinstance
* 依赖注入功能需要函数参数有明确的类型提示
* 支持位置参数、关键字参数和混合参数类型
