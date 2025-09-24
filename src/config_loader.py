# src/config_loader.py
import os
import tomllib

from pydantic import BaseModel
from typing import Any, Dict
from pathlib import Path

class LLMConfig(BaseModel):
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.0
    max_tokens: int = 2048

class AppConfig(BaseModel):
    llm: LLMConfig

def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = get_project_root()


def _get_config_path() -> Path:
    root = PROJECT_ROOT
    config_path = root / "config" / "config.toml"
    if config_path.exists():
        return config_path
    example_path = root / "config" / "config.example.toml"
    if example_path.exists():
        return example_path
    raise FileNotFoundError("No configuration file found in config directory")

def _resolve_env_prefix(v: Any) -> Any:
    # 不是字符串：无需处理
    if not isinstance(v, str):
        return v
    # 不以 'env:' 开头：原样返回
    if not v.startswith("env:"):
        return v

    # 取出变量名并去掉空格
    var_name = v[len("env:"):].strip()
    if not var_name:
        raise ValueError("配置中使用了 'env:' 但未提供变量名，例如应为 'env:OPENAI_API_KEY'。")

    # 查环境变量
    if var_name not in os.environ:
        raise ValueError(f"配置里写了 env:{var_name}，但环境变量 {var_name} 未设置。")
    return os.environ[var_name]



def _postprocess_env(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归地把 dict 里所有字符串都跑一遍 _resolve_env_prefix。
    TODO: 遍历字典和嵌套结构（dict/list），返回新字典。
    """
    raw_config = d
    base_llm = raw_config.get("llm", {})

    default_settings = {
        "model": base_llm.get("model"),
        "base_url": base_llm.get("base_url"),
        "api_key": base_llm.get("api_key"),
        "max_tokens": base_llm.get("max_tokens", 4096),
        "temperature": base_llm.get("temperature", 1.0),
    }


    return default_settings

def load_config() -> AppConfig:
    """
    读取 TOML 文件，把 'env:' 前缀替换为真实环境变量值，并返回 AppConfig。
    TODO: 用 tomllib 读取，再用 _postprocess_env 处理，然后 AppConfig.model_validate。
    """
    config_path = _get_config_path()
    with config_path.open("rb") as f:
        default_settings = _postprocess_env(tomllib.load(f))
        return AppConfig(**default_settings)
