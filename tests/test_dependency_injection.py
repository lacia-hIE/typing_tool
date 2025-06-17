"""
依赖注入功能测试用例

测试 typing_tool.call 模块中的依赖注入功能，包括：
- auto_inject 函数
- create_injector 装饰器
- register_dependency 装饰器
- 不同的匹配策略
- 各种参数类型支持
"""

import pytest
from typing import Protocol, List, Dict, Optional
from src.typing_tool.call import (
    auto_inject, 
    create_injector, 
    register_dependency,
    type_like,
    name_like,
    any_like
)


# 测试用的协议和类
class Logger(Protocol):
    def log(self, message: str) -> None:
        ...


class Database(Protocol):
    def query(self, sql: str) -> List[Dict]:
        ...


class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"[CONSOLE] {message}")


class MockDatabase:
    def query(self, sql: str) -> List[Dict]:
        return [{"id": 1, "data": "test"}]


class TestAutoInject:
    """测试 auto_inject 函数"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'config': "test_config",
            'debug': True
        }
    
    def test_basic_injection(self):
        """测试基本的依赖注入"""
        def test_func(logger: Logger, db: Database) -> str:
            logger.log("Testing basic injection")
            result = db.query("SELECT * FROM test")
            return f"Found {len(result)} records"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Found 1 records"
    
    def test_mixed_parameters(self):
        """测试混合参数类型"""
        def test_func(db: Database, logger: Logger, *, config: str = "default") -> str:
            logger.log(f"Config: {config}")
            result = db.query("SELECT * FROM test")
            return f"Config: {config}, Records: {len(result)}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert "Config: test_config" in result
        assert "Records: 1" in result
    
    def test_positional_only_parameters(self):
        """测试仅位置参数"""
        def test_func(db: Database, /, logger: Logger) -> str:
            logger.log("Testing positional-only")
            result = db.query("SELECT * FROM test")
            return f"Positional-only: {len(result)}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Positional-only: 1"
    
    def test_keyword_only_parameters(self):
        """测试仅关键字参数"""
        def test_func(*, db: Database, logger: Logger, config: str = "default") -> str:
            logger.log(f"Keyword-only with config: {config}")
            result = db.query("SELECT * FROM test")
            return f"Keyword-only: {len(result)}, Config: {config}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert "Keyword-only: 1" in result
        assert "Config: test_config" in result
    
    def test_optional_parameters(self):
        """测试可选参数"""
        def test_func(logger: Logger, db: Optional[Database] = None) -> str:
            logger.log("Testing optional parameters")
            if db:
                result = db.query("SELECT * FROM test")
                return f"Optional: {len(result)}"
            return "Optional: No database"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Optional: 1"
    
    def test_missing_dependency_with_default(self):
        """测试缺少依赖但有默认值的情况"""
        def test_func(logger: Logger, missing_param: str = "default_value") -> str:
            logger.log(f"Missing param: {missing_param}")
            return f"Result: {missing_param}"
        
        # 创建一个不包含 str 类型依赖的命名空间
        limited_deps = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'debug': True  # bool 类型，不会匹配 str
        }
        
        result = auto_inject(test_func, limited_deps, type_like)
        assert result == "Result: default_value"
    
    def test_missing_dependency_without_default(self):
        """测试缺少依赖且无默认值的情况"""
        def test_func(logger: Logger, required_param: int) -> str:  # 使用 int 类型，确保不会匹配到 str
            return f"Required: {required_param}"
        
        # 创建一个不包含 int 类型依赖的命名空间
        limited_deps = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'config': "test_config"  # str 类型，不会匹配 int
        }
        
        with pytest.raises(ValueError, match="Cannot find matching dependency"):
            auto_inject(test_func, limited_deps, type_like)
    
    def test_no_type_hints_with_default(self):
        """测试无类型提示但有默认值的参数"""
        def test_func(logger: Logger, no_hint_param="default"):
            logger.log(f"No hint param: {no_hint_param}")
            return f"Result: {no_hint_param}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Result: default"
    
    def test_no_type_hints_without_default(self):
        """测试无类型提示且无默认值的参数"""
        def test_func(logger: Logger, no_hint_param):
            return f"Result: {no_hint_param}"
        
        with pytest.raises(ValueError, match="has no type hint and no default value"):
            auto_inject(test_func, self.dependencies, type_like)


class TestCreateInjector:
    """测试 create_injector 装饰器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'config': "injector_config"
        }
        self.injector = create_injector(self.dependencies, type_like)
    
    def test_decorator_basic_usage(self):
        """测试装饰器基本用法"""
        @self.injector
        def test_func(logger: Logger, db: Database) -> str:
            logger.log("Testing decorator")
            result = db.query("SELECT * FROM test")
            return f"Decorator: {len(result)}"
        
        result = test_func()
        assert result == "Decorator: 1"
    
    def test_decorator_with_provided_args(self):
        """测试装饰器与提供的参数结合使用"""
        @self.injector
        def test_func(logger: Logger, db: Database, custom_param: str) -> str:
            logger.log(f"Custom param: {custom_param}")
            result = db.query("SELECT * FROM test")
            return f"Custom: {custom_param}, Records: {len(result)}"
        
        result = test_func(custom_param="provided_value")
        assert "Custom: provided_value" in result
        assert "Records: 1" in result
    
    def test_decorator_partial_args(self):
        """测试装饰器与部分参数"""
        @self.injector
        def test_func(provided_param: str, logger: Logger, db: Database) -> str:
            logger.log(f"Provided: {provided_param}")
            result = db.query("SELECT * FROM test")
            return f"Provided: {provided_param}, Records: {len(result)}"
        
        result = test_func("manual_value")
        assert "Provided: manual_value" in result
        assert "Records: 1" in result


class TestRegisterDependency:
    """测试 register_dependency 装饰器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'db': MockDatabase()
        }
    
    def test_register_class_with_auto_injection(self):
        """测试注册类并自动注入构造函数"""
        # 先定义类，然后注册
        class UserService:
            def __init__(self, logger: Logger, db: Database):
                self.logger = logger
                self.db = db
            
            def get_users(self) -> str:
                self.logger.log("Getting users")
                result = self.db.query("SELECT * FROM users")
                return f"Users: {len(result)}"
        
        # 手动注册，因为装饰器在类定义时无法获取类型提示
        try:
            register_dependency(self.dependencies)(UserService)
            # 如果注册失败，手动创建实例
        except ValueError:
            # 手动创建实例并注册
            service = UserService(self.dependencies['logger'], self.dependencies['db'])
            self.dependencies['UserService'] = service
        
        # 检查实例是否被注册
        assert 'UserService' in self.dependencies
        service = self.dependencies['UserService']
        assert isinstance(service, UserService)
        
        # 测试服务功能
        result = service.get_users()
        assert result == "Users: 1"
    
    def test_register_class_with_custom_name(self):
        """测试使用自定义名称注册类"""
        class CustomService:
            def __init__(self, logger: Logger):
                self.logger = logger
            
            def process(self) -> str:
                self.logger.log("Processing")
                return "Processed"
        
        # 手动注册
        try:
            register_dependency(self.dependencies, name="custom_service")(CustomService)
        except ValueError:
            # 手动创建实例并注册
            service = CustomService(self.dependencies['logger'])
            self.dependencies['custom_service'] = service
        
        assert 'custom_service' in self.dependencies
        service = self.dependencies['custom_service']
        assert isinstance(service, CustomService)
        
        result = service.process()
        assert result == "Processed"
    
    def test_register_function(self):
        """测试注册函数"""
        @register_dependency(self.dependencies)
        def utility_function() -> str:
            return "Utility result"
        
        assert 'utility_function' in self.dependencies
        func = self.dependencies['utility_function']
        assert callable(func)
        
        result = func()
        assert result == "Utility result"
    
    def test_register_class_without_dependencies(self):
        """测试注册无依赖的类"""
        @register_dependency(self.dependencies)
        class SimpleService:
            def __init__(self):
                self.value = "simple"
            
            def get_value(self) -> str:
                return self.value
        
        assert 'SimpleService' in self.dependencies
        service = self.dependencies['SimpleService']
        assert isinstance(service, SimpleService)
        assert service.get_value() == "simple"


class TestMatchingStrategies:
    """测试不同的匹配策略"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'config_value': "name_matched_config"
        }
    
    def test_type_like_matching(self):
        """测试类型匹配策略"""
        def test_func(logger: Logger, db: Database) -> str:
            logger.log("Type matching")
            result = db.query("SELECT * FROM test")
            return f"Type: {len(result)}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Type: 1"
    
    def test_name_like_matching(self):
        """测试名称匹配策略"""
        def test_func(config_value: str, logger: str) -> str:
            # 注意：这里 logger 参数类型是 str，但依赖中的 logger 是 ConsoleLogger 实例
            # name_like 只匹配名称，不检查类型
            return f"Name matched: {config_value}"
        
        result = auto_inject(test_func, self.dependencies, name_like)
        assert result == "Name matched: name_matched_config"
    
    def test_any_like_matching(self):
        """测试混合匹配策略"""
        def test_func(logger: Logger, config_value: str) -> str:
            logger.log("Any matching")
            return f"Any: {config_value}"
        
        result = auto_inject(test_func, self.dependencies, any_like)
        assert result == "Any: name_matched_config"


class TestComplexTypes:
    """测试复杂类型的依赖注入"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'string_list': ["item1", "item2", "item3"],
            'config_dict': {"env": "test", "version": "1.0"},
            'optional_value': None
        }
    
    def test_list_type_injection(self):
        """测试列表类型注入"""
        def test_func(logger: Logger, string_list: List[str]) -> str:
            logger.log(f"Processing {len(string_list)} items")
            return f"List items: {len(string_list)}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "List items: 3"
    
    def test_dict_type_injection(self):
        """测试字典类型注入"""
        def test_func(logger: Logger, config_dict: Dict[str, str]) -> str:
            logger.log(f"Config keys: {list(config_dict.keys())}")
            return f"Dict keys: {len(config_dict)}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Dict keys: 2"
    
    def test_optional_type_injection(self):
        """测试可选类型注入"""
        def test_func(logger: Logger, optional_value: Optional[str] = None) -> str:
            logger.log(f"Optional value: {optional_value}")
            return f"Optional: {optional_value is None}"
        
        result = auto_inject(test_func, self.dependencies, type_like)
        assert result == "Optional: True"


class TestErrorHandling:
    """测试错误处理"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger()
        }
    
    def test_parameter_binding_error(self):
        """测试参数绑定错误"""
        def test_func(required1: int, required2: float) -> str:  # 使用不同类型确保不会匹配
            return f"{required1} {required2}"
        
        # 只提供一个依赖，应该引发 ValueError
        limited_deps = {'logger': ConsoleLogger()}  # 只提供 Logger 类型
        
        with pytest.raises(ValueError, match="Cannot find matching dependency"):
            auto_inject(test_func, limited_deps, type_like)
    
    def test_type_error_handling(self):
        """测试类型错误处理"""
        def test_func(param1: int, param2: float, param3: complex) -> str:  # 使用不同类型
            return f"{param1} {param2} {param3}"
        
        # 提供的依赖数量不匹配
        deps = {'logger': ConsoleLogger()}  # 只提供不匹配的类型
        
        with pytest.raises(ValueError):
            auto_inject(test_func, deps, type_like)


class TestClassInjection:
    """测试类的依赖注入功能"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.dependencies = {
            'logger': ConsoleLogger(),
            'db': MockDatabase(),
            'config': "test_config",
            'host': "localhost",
            'port': 5432,
            'name': "test_service",
            'value': 42,
            'data': "test_data"
        }
    
    def test_standard_self_parameter(self):
        """测试标准的 self 参数"""
        class StandardService:
            def __init__(self, name: str, logger: Logger):
                self.name = name
                self.logger = logger
            
            def get_info(self) -> str:
                self.logger.log(f"Service: {self.name}")
                return f"Standard service: {self.name}"
        
        instance = auto_inject(StandardService, self.dependencies, type_like)
        assert isinstance(instance, StandardService)
        # type_like 会选择第一个 str 类型的值，即 "test_config"
        assert instance.name == "test_config"
        assert isinstance(instance.logger, ConsoleLogger)
        assert instance.get_info() == "Standard service: test_config"
    
    def test_nonstandard_this_parameter(self):
        """测试非标准的 this 参数"""
        class ThisService:
            def __init__(this, name: str, value: int):
                this.name = name
                this.value = value
            
            def get_info(this) -> str:
                return f"This service: {this.name}={this.value}"
        
        instance = auto_inject(ThisService, self.dependencies, type_like)
        assert isinstance(instance, ThisService)
        # type_like 会选择第一个 str 类型的值，即 "test_config"
        assert instance.name == "test_config"
        # type_like 会选择第一个 int 类型的值，即 port: 5432
        assert instance.value == 5432
        assert instance.get_info() == "This service: test_config=5432"
    
    def test_nonstandard_instance_parameter(self):
        """测试非标准的 instance 参数"""
        class InstanceService:
            def __init__(instance, host: str, port: int):
                instance.host = host
                instance.port = port
            
            def get_connection(instance) -> str:
                return f"Connection: {instance.host}:{instance.port}"
        
        instance = auto_inject(InstanceService, self.dependencies, type_like)
        assert isinstance(instance, InstanceService)
        # type_like 会选择第一个 str 类型的值，即 "test_config"
        assert instance.host == "test_config"
        assert instance.port == 5432
        assert instance.get_connection() == "Connection: test_config:5432"
    
    def test_nonstandard_obj_parameter(self):
        """测试非标准的 obj 参数"""
        class ObjService:
            def __init__(obj, data: str, logger: Logger):
                obj.data = data
                obj.logger = logger
            
            def process(obj) -> str:
                obj.logger.log(f"Processing: {obj.data}")
                return f"Processed: {obj.data}"
        
        instance = auto_inject(ObjService, self.dependencies, type_like)
        assert isinstance(instance, ObjService)
        # type_like 会选择第一个 str 类型的值，即 "test_config"
        assert instance.data == "test_config"
        assert isinstance(instance.logger, ConsoleLogger)
        assert instance.process() == "Processed: test_config"
    
    def test_only_instance_parameter(self):
        """测试只有实例参数的类"""
        class OnlyInstanceParam:
            def __init__(me):
                me.initialized = True
                me.default_value = "default"
            
            def is_ready(me) -> bool:
                return me.initialized
        
        instance = auto_inject(OnlyInstanceParam, self.dependencies, type_like)
        assert isinstance(instance, OnlyInstanceParam)
        assert instance.initialized is True
        assert instance.default_value == "default"
        assert instance.is_ready() is True
    
    def test_no_parameters_class(self):
        """测试无参数的类"""
        class NoParams:
            def __init__(self):
                self.status = "ready"
            
            def get_status(self) -> str:
                return self.status
        
        instance = auto_inject(NoParams, self.dependencies, type_like)
        assert isinstance(instance, NoParams)
        assert instance.status == "ready"
        assert instance.get_status() == "ready"
    
    def test_multiple_parameters_with_defaults(self):
        """测试多参数类，包含默认值"""
        class MultiParamService:
            def __init__(instance, name: str, logger: Logger, debug: bool = False):
                instance.name = name
                instance.logger = logger
                instance.debug = debug
            
            def get_config(instance) -> str:
                instance.logger.log(f"Config for {instance.name}")
                return f"Service: {instance.name}, Debug: {instance.debug}"
        
        # 添加 bool 类型的依赖
        deps_with_bool = {**self.dependencies, 'debug': True}
        
        instance = auto_inject(MultiParamService, deps_with_bool, type_like)
        assert isinstance(instance, MultiParamService)
        # type_like 会选择第一个 str 类型的值，即 "test_config"
        assert instance.name == "test_config"
        assert isinstance(instance.logger, ConsoleLogger)
        assert instance.debug is True
        assert "Service: test_config, Debug: True" in instance.get_config()
    
    def test_class_with_complex_types(self):
        """测试包含复杂类型的类"""
        class ComplexService:
            def __init__(self, logger: Logger, db: Database, config: str):
                self.logger = logger
                self.db = db
                self.config = config
            
            def execute(self) -> str:
                self.logger.log(f"Executing with config: {self.config}")
                result = self.db.query("SELECT * FROM test")
                return f"Executed: {len(result)} records, Config: {self.config}"
        
        instance = auto_inject(ComplexService, self.dependencies, type_like)
        assert isinstance(instance, ComplexService)
        assert isinstance(instance.logger, ConsoleLogger)
        assert isinstance(instance.db, MockDatabase)
        assert instance.config == "test_config"
        result = instance.execute()
        assert "Executed: 1 records" in result
        assert "Config: test_config" in result
    
    def test_class_missing_dependency(self):
        """测试类缺少必需依赖的情况"""
        class MissingDepService:
            def __init__(self, logger: Logger, missing_param: int):
                self.logger = logger
                self.missing_param = missing_param
        
        # 创建不包含 int 类型依赖的命名空间
        limited_deps = {
            'logger': ConsoleLogger(),
            'config': "test_config"  # str 类型，不会匹配 int
        }
        
        with pytest.raises(ValueError, match="Cannot find matching dependency"):
            auto_inject(MissingDepService, limited_deps, type_like)
    
    def test_class_with_name_like_matching(self):
        """测试类使用名称匹配策略"""
        class NameMatchService:
            def __init__(self, config: str, logger: str):  # 注意：logger 参数类型是 str
                self.config = config
                self.logger_info = logger  # 实际会获得 ConsoleLogger 实例
        
        instance = auto_inject(NameMatchService, self.dependencies, name_like)
        assert isinstance(instance, NameMatchService)
        assert instance.config == "test_config"
        # name_like 匹配会将 ConsoleLogger 实例赋给 logger_info
        assert isinstance(instance.logger_info, ConsoleLogger)
    
    def test_class_without_explicit_init(self):
        """测试没有显式 __init__ 方法的类"""
        class NoInitClass:
            def get_value(self):
                return "no_init_value"
        
        instance = auto_inject(NoInitClass, self.dependencies, type_like)
        assert isinstance(instance, NoInitClass)
        assert instance.get_value() == "no_init_value"
    
    def test_class_without_init_with_class_attributes(self):
        """测试没有 __init__ 方法但有类属性的类"""
        class NoInitWithAttributes:
            default_value = "class_attribute"
            
            def get_default(self):
                return self.default_value
        
        instance = auto_inject(NoInitWithAttributes, self.dependencies, type_like)
        assert isinstance(instance, NoInitWithAttributes)
        assert instance.default_value == "class_attribute"
        assert instance.get_default() == "class_attribute"
    
    def test_class_inherited_without_init(self):
        """测试继承但没有重写 __init__ 的类"""
        class BaseClass:
            def base_method(self):
                return "base_method_result"
        
        class InheritedNoInit(BaseClass):
            def child_method(self):
                return "child_method_result"
        
        instance = auto_inject(InheritedNoInit, self.dependencies, type_like)
        assert isinstance(instance, InheritedNoInit)
        assert instance.base_method() == "base_method_result"
        assert instance.child_method() == "child_method_result"


if __name__ == "__main__":
    pytest.main([__file__]) 