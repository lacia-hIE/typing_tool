import inspect
from typing import TypeVar
from functools import wraps
from collections import ChainMap
from typing import Any, Callable, get_type_hints, Mapping

from .type_utils import like_isinstance

T = TypeVar("T")


class ParamInterface:
    def __init__(self, name: str, param: inspect.Parameter, annotation: Any):
        self.name = name
        self.param = param
        self.annotation = annotation


def type_like(
    arg: ParamInterface,
    name: str,
    obj: Any,
):
    return like_isinstance(obj, arg.annotation)


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
    func: Callable[..., T],
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
) -> T:
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
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
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
                    if like(ParamInterface(param_name, param, param_type), k, v):
                        found_dependency = v
                        break
        else:
            for name, obj in namespace.items():
                if like(ParamInterface(param_name, param, param_type), name, obj):
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
    inject_methods: bool = True,
    method_filter: Callable[[str, Callable], bool] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    创建一个依赖注入装饰器

    Args:
        namespace: 包含可用依赖项的命名空间字典
        like: 判断依赖项是否匹配的函数，默认使用type_like
        inject_methods: 是否为类的方法也进行依赖注入，默认为True
        method_filter: 可选的方法过滤器函数，用于决定哪些方法需要注入
                      函数签名: (method_name: str, method: Callable) -> bool
                      返回True表示需要注入，False表示跳过

    Returns:
        装饰器函数
    """

    def injector(func: Callable[..., T]) -> Callable[..., T]:
        # 如果装饰的是类，需要特殊处理
        if inspect.isclass(func):
            return _create_injected_class(
                func, namespace, like, inject_methods, method_filter
            )
        else:
            # 对于函数，使用原来的逻辑
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


def _create_injected_class(
    original_class: type,
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
    inject_methods: bool = True,
    method_filter: Callable[[str, Callable], bool] | None = None,
) -> type:
    """
    创建一个注入后的类，保持原始类的类型提示

    Args:
        original_class: 原始类
        namespace: 依赖项命名空间
        like: 匹配函数
        inject_methods: 是否注入方法
        method_filter: 方法过滤器

    Returns:
        注入后的类
    """
    # 保存原始的 __new__ 和 __init__ 方法
    original_new = original_class.__new__
    original_init = original_class.__init__

    def injected_new(cls, *args, **kwargs):
        # 如果提供了参数，需要创建一个临时的命名空间包含这些参数
        if args or kwargs:
            # 获取类的 __init__ 签名并绑定已提供的参数
            sig = inspect.signature(original_init)
            try:
                bound_args = sig.bind_partial(None, *args, **kwargs)  # None 代表 self
                bound_args.apply_defaults()
                # 移除 self 参数
                arguments = {
                    k: v for k, v in bound_args.arguments.items() if k != "self"
                }

                # 使用 ChainMap 创建分层命名空间，已提供的参数优先级更高
                temp_namespace = ChainMap(arguments, dict(namespace))

                # 直接进行依赖注入并创建实例
                instance = _inject_and_create_instance(
                    cls, temp_namespace, like, original_init
                )
                return instance
            except TypeError:
                # 如果绑定失败，直接使用原始命名空间进行注入
                instance = _inject_and_create_instance(
                    cls, namespace, like, original_init
                )
                return instance
        else:
            # 没有提供参数，直接使用原始命名空间进行注入
            instance = _inject_and_create_instance(cls, namespace, like, original_init)
            return instance

    def injected_init(self, *args, **kwargs):
        # 如果实例已经通过依赖注入初始化，跳过
        if hasattr(self, "_injected_initialized"):
            return
        # 否则调用原始的 __init__ 方法
        original_init(self, *args, **kwargs)

    # 保持原始 __init__ 的签名和类型提示
    injected_init.__signature__ = inspect.signature(original_init)
    injected_init.__annotations__ = getattr(original_init, "__annotations__", {})

    # 替换类的 __new__ 和 __init__ 方法
    original_class.__new__ = staticmethod(injected_new)
    original_class.__init__ = injected_init

    # 如果启用了方法注入，为类的方法添加依赖注入
    if inject_methods:
        _inject_class_methods(original_class, namespace, like, method_filter)

    return original_class


def _inject_and_create_instance(
    cls: Any,
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
    original_init: Callable | None = None,
) -> Any:
    """
    为类进行依赖注入并创建实例的辅助函数

    Args:
        cls: 要创建实例的类
        namespace: 依赖项命名空间
        like: 匹配函数

    Returns:
        创建的实例
    """
    # 获取 __init__ 方法的签名
    init_method = original_init if original_init is not None else cls.__init__
    sig = inspect.signature(init_method)
    # 获取类型提示
    hints = get_type_hints(init_method, include_extras=True)

    # 存储最终的参数
    positional_args = []
    keyword_args = {}

    # 获取第一个参数名（通常是 self）
    param_names = list(sig.parameters.keys())
    first_param_name = param_names[0] if param_names else None

    # 遍历函数的每个参数
    for param_name, param in sig.parameters.items():
        # 跳过第一个参数（self）
        if param_name == first_param_name:
            continue

        # 获取参数的类型提示
        param_type = hints.get(param_name) or param.annotation

        # 如果没有类型提示，检查是否有默认值
        if param_type is None or param_type is inspect.Parameter.empty:
            # 特殊处理：跳过 *args 和 **kwargs 参数
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
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
                    if like(ParamInterface(param_name, param, param_type), k, v):
                        found_dependency = v
                        break
                if found_dependency is not None:
                    break
        else:
            for name, obj in namespace.items():
                if like(ParamInterface(param_name, param, param_type), name, obj):
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

    # 使用 object.__new__ 创建实例，避免递归调用
    instance = object.__new__(cls)

    # 手动调用 __init__ 方法
    init_method(instance, *positional_args, **keyword_args)

    # 标记实例已经初始化，避免重复初始化
    instance._injected_initialized = True

    return instance


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


def _inject_class_methods(
    cls: type,
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
    method_filter: Callable[[str, Callable], bool] | None = None,
) -> None:
    """
    为类的方法添加依赖注入

    Args:
        cls: 要处理的类
        namespace: 依赖项命名空间
        like: 匹配函数
        method_filter: 方法过滤器函数
    """
    # 获取类的所有方法，需要检查类的 __dict__ 以正确识别装饰器
    for attr_name, attr in cls.__dict__.items():
        if attr_name.startswith("_"):
            # 跳过私有方法和特殊方法
            continue

        # 检查是否是方法（包括实例方法、类方法、静态方法）
        if not (
            inspect.isfunction(attr)
            or inspect.ismethod(attr)
            or isinstance(attr, (staticmethod, classmethod))
        ):
            continue

        # 获取实际的函数对象
        if isinstance(attr, staticmethod):
            actual_func = attr.__func__
            is_static = True
            is_class = False
        elif isinstance(attr, classmethod):
            actual_func = attr.__func__
            is_static = False
            is_class = True
        else:
            actual_func = attr
            is_static = False
            is_class = False

        # 应用方法过滤器 - 如果有过滤器且方法不在允许列表中，跳过
        if method_filter and not method_filter(attr_name, actual_func):
            continue

        # 检查方法是否需要依赖注入（有类型提示的参数）
        if not _method_needs_injection(actual_func, is_static, is_class):
            continue

        # 创建注入后的方法
        injected_method = _create_injected_method(
            actual_func, namespace, like, is_static, is_class
        )

        # 替换原方法
        if is_static:
            setattr(cls, attr_name, staticmethod(injected_method))
        elif is_class:
            setattr(cls, attr_name, classmethod(injected_method))
        else:
            setattr(cls, attr_name, injected_method)


def _method_needs_injection(
    func: Callable,
    is_static: bool = False,
    is_class: bool = False,
) -> bool:
    """
    检查方法是否需要依赖注入

    Args:
        func: 要检查的函数
        is_static: 是否是静态方法
        is_class: 是否是类方法

    Returns:
        是否需要依赖注入
    """
    try:
        sig = inspect.signature(func)
        hints = get_type_hints(func, include_extras=True)

        # 获取需要跳过的第一个参数名
        param_names = list(sig.parameters.keys())
        skip_first = not is_static  # 静态方法不跳过第一个参数

        has_injectable_params = False

        for i, (param_name, param) in enumerate(sig.parameters.items()):
            # 跳过第一个参数（self 或 cls），除非是静态方法
            if skip_first and i == 0:
                continue

            # 获取参数的类型提示
            param_type = hints.get(param_name) or param.annotation

            # 如果有类型提示，说明可能需要注入
            if param_type is not None and param_type is not inspect.Parameter.empty:
                has_injectable_params = True
                break

        return has_injectable_params
    except Exception:
        return False


def _create_injected_method(
    original_func: Callable,
    namespace: Mapping[str, Any],
    like: Callable[[ParamInterface, str, Any], bool] = type_like,
    is_static: bool = False,
    is_class: bool = False,
) -> Callable:
    """
    创建注入后的方法

    Args:
        original_func: 原始方法
        namespace: 依赖项命名空间
        like: 匹配函数
        is_static: 是否是静态方法
        is_class: 是否是类方法

    Returns:
        注入后的方法
    """

    @wraps(original_func)
    def injected_method(*args, **kwargs):
        # 获取函数签名
        sig = inspect.signature(original_func)
        hints = get_type_hints(original_func, include_extras=True)

        # 存储最终的参数
        final_args = list(args)
        final_kwargs = dict(kwargs)

        # 确定需要跳过的参数数量
        skip_count = 0 if is_static else 1  # 静态方法不跳过，其他方法跳过第一个参数

        # 获取参数列表
        param_list = list(sig.parameters.items())

        # 遍历需要处理的参数
        for i, (param_name, param) in enumerate(param_list):
            # 跳过已经被位置参数填充的参数
            if i < len(args):
                continue

            # 跳过已经被关键字参数填充的参数
            if param_name in kwargs:
                continue

            # 跳过第一个参数（self 或 cls），除非是静态方法
            if i < skip_count:
                continue

            # 获取参数的类型提示
            param_type = hints.get(param_name) or param.annotation

            # 如果没有类型提示，跳过
            if param_type is None or param_type is inspect.Parameter.empty:
                continue

            # 在命名空间中查找匹配的依赖项
            found_dependency = None

            if isinstance(namespace, ChainMap):
                for mapping in reversed(namespace.maps):
                    for k, v in mapping.items():
                        if like(ParamInterface(param_name, param, param_type), k, v):
                            found_dependency = v
                            break
                    if found_dependency is not None:
                        break
            else:
                for name, obj in namespace.items():
                    if like(ParamInterface(param_name, param, param_type), name, obj):
                        found_dependency = obj
                        break

            # 如果找到依赖项，添加到参数中
            if found_dependency is not None:
                final_kwargs[param_name] = found_dependency

        # 调用原始方法
        return original_func(*final_args, **final_kwargs)

    return injected_method
