from .type_utils import like_isinstance
from .typevar import (
    check_typevar_model as like_issubclass,
    TypeVarModel,
    gen_typevar_model,
    infer_generic_type,
    iter_deep_type,
    extract_typevar_mapping,
)
from .overload import auto_overload
from .config import CheckConfig
from .call import (
    create_injector,
    auto_inject,
    name_like,
    type_like,
    any_like,
    register_dependency,
)
