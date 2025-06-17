import inspect
from functools import wraps
from collections import ChainMap
from typing import Any, Callable, get_type_hints, Mapping

from .type_utils import like_isinstance


class ParamInterface:
    def __init__(self, name: str, param: inspect.Parameter):
        self.name = name
        self.param = param


def type_like(
    arg: ParamInterface,
    name: str,
    obj: Any,
):
    return like_isinstance(obj, arg.param.annotation)


def name_like(
    arg: ParamInterface,
    name: str,
    obj: Any,
):
    return name == arg.name


def any_like(
    arg: ParamInterface,
    name: str,
    obj: Any,
):
    return name_like(arg, name, obj) or type_like(arg, name, obj)


def auto_inject(
    func: Callable,
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
) -> Any:
    """
    自动依赖注入函数

    通过分析函数的类型提示，从命名空间中自动查找并注入匹配的依赖项。

    Args:
        func: 需要调用的函数
        namespace: 包含可用依赖项的命名空间字典
        like: 判断依赖项是否匹配的函数，默认使用type_like

    Returns:
        函数执行的结果

    Raises:
        ValueError: 当无法找到匹配的依赖项或参数绑定失败时
        TypeError: 当参数绑定类型不匹配时
    """
    # 获取函数签名
    is_class = inspect.isclass(func)
    if is_class:
        sig = inspect.signature(func.__init__)
    else:
        sig = inspect.signature(func)
    # 获取类型提示
    hints = get_type_hints(func, include_extras=True)

    # 存储最终的参数
    positional_args = []
    keyword_args = {}

    # 对于类，获取第一个参数名（通常是实例参数如 self, this, instance 等）
    first_param_name = None
    if is_class:
        param_names = list(sig.parameters.keys())
        if param_names:
            first_param_name = param_names[0]

    # 遍历函数的每个参数
    for param_name, param in sig.parameters.items():
        # 如果是类的 __init__ 方法，跳过第一个参数（实例参数）
        if is_class and param_name == first_param_name:
            continue
            
        # 获取参数的类型提示
        param_type = hints.get(param_name) or param.annotation

        # 如果没有类型提示，检查是否有默认值
        if param_type is None or param_type is inspect.Parameter.empty:
            # 特殊处理：跳过 *args 和 **kwargs 参数
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.default == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter '{param_name}' has no type hint and no default value"
                )
            continue

        # 在命名空间中查找匹配的依赖项
        found_dependency = None

        if isinstance(namespace, ChainMap):
            for mapping in reversed(namespace.maps):
                for k, v in mapping.items():
                    if like(ParamInterface(param_name, param), k, v):
                        found_dependency = v
                        break
        else:
            for name, obj in namespace.items():
                if like(ParamInterface(param_name, param), name, obj):
                    found_dependency = obj
                    break

        if found_dependency is not None:
            # 根据参数类型决定如何传递
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                # 仅位置参数
                positional_args.append(found_dependency)
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                # 仅关键字参数
                keyword_args[param_name] = found_dependency
            elif param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                # 位置或关键字参数，优先使用关键字形式
                keyword_args[param_name] = found_dependency
            else:
                keyword_args[param_name] = found_dependency
        elif param.default == inspect.Parameter.empty:
            # 如果没有找到依赖项且没有默认值，抛出错误
            raise ValueError(
                f"Cannot find matching dependency for parameter '{param_name}' (type: {param_type})"
            )

    # 对于类，我们需要直接调用类构造器，不需要验证 __init__ 的参数绑定
    if is_class:
        # 直接调用类构造器
        return func(*positional_args, **keyword_args)
    else:
        # 对于普通函数，使用sig.bind来验证参数绑定
        try:
            # 先尝试绑定位置参数和关键字参数
            if positional_args and keyword_args:
                bound_args = sig.bind(*positional_args, **keyword_args)
            elif positional_args:
                bound_args = sig.bind(*positional_args)
            elif keyword_args:
                bound_args = sig.bind(**keyword_args)
            else:
                bound_args = sig.bind()

            # 应用默认值
            bound_args.apply_defaults()

        except TypeError as e:
            raise TypeError(f"Parameter binding failed: {str(e)}")

        # 调用函数
        return func(*bound_args.args, **bound_args.kwargs)


def create_injector(
    namespace: dict[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
) -> Callable[[Callable], Callable]:
    """
    创建一个依赖注入装饰器

    Args:
        namespace: 包含可用依赖项的命名空间字典

    Returns:
        装饰器函数
    """

    def injector(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果提供了参数，需要创建一个临时的命名空间包含这些参数
            if args or kwargs:
                # 获取函数签名并绑定已提供的参数
                sig = inspect.signature(func)
                try:
                    bound_args = sig.bind_partial(*args, **kwargs)
                    bound_args.apply_defaults()

                    # 使用 ChainMap 创建分层命名空间，已提供的参数优先级更高
                    temp_namespace = ChainMap(bound_args.arguments, namespace)

                    # 使用临时命名空间进行注入
                    return auto_inject(func, temp_namespace, like)
                except TypeError:
                    # 如果绑定失败，直接使用auto_inject
                    return auto_inject(func, namespace, like)
            else:
                # 没有提供参数，直接使用auto_inject
                return auto_inject(func, namespace, like)

        return wrapper

    return injector


def register_dependency(
    namespace: dict[str, Any],
    name: str | None = None,
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
):
    """
    依赖注册装饰器

    Args:
        namespace: 要注册到的命名空间
        name: 可选的依赖名称，如果不提供则使用类名或函数名

    Returns:
        装饰器函数
    """

    def decorator(cls_or_func):
        dependency_name = (
            name
            if name is not None
            else getattr(cls_or_func, "__name__", str(cls_or_func))
        )

        # 如果是类，创建实例；如果是函数，直接使用
        if inspect.isclass(cls_or_func):
            # 尝试自动注入类的构造函数
            try:
                instance = auto_inject(cls_or_func, namespace, like)
                namespace[dependency_name] = instance
            except (ValueError, TypeError):
                # 如果无法自动注入，尝试手动创建实例
                try:
                    # 检查构造函数是否需要参数
                    sig = inspect.signature(cls_or_func.__init__)
                    params = [p for name, p in sig.parameters.items() if name != "self"]
                    if not params:
                        # 无参构造函数
                        instance = cls_or_func()
                        namespace[dependency_name] = instance
                    else:
                        # 有参数但无法注入，抛出错误
                        raise ValueError(
                            f"Cannot create instance of {cls_or_func.__name__}: unable to inject dependencies and no default constructor available"
                        )
                except Exception as e:
                    raise ValueError(
                        f"Failed to create instance of {cls_or_func.__name__}: {str(e)}"
                    )
        else:
            namespace[dependency_name] = cls_or_func

        return cls_or_func

    return decorator
