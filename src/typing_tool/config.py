from dataclasses import dataclass


@dataclass
class CheckConfig:
    depth: int = 10
    max_sample: int = -1
    protocol_type_strict: bool = False
    dataclass_type_strict: bool = False


check_config = CheckConfig()
