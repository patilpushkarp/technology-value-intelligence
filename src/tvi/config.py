"""Configuration loader and schema definition for Technology Value Intelligence."""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseModel, Field


class ProjectSettings(BaseModel):
    name: str = "Technology Value Intelligence"
    version: str = "1.0.0"
    random_seed: int = 42
    currency: str = "INR"
    currency_symbol: str = "₹"
    reporting_year: int = 2024


class DataSettings(BaseModel):
    business_units: int = 10
    capabilities: int = 25
    services: int = 18
    applications: int = 50
    technologies: int = 35
    vendors: int = 10
    projects: int = 40
    months: int = 12
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    generated_dir: str = "data/generated"


class DatabaseSettings(BaseModel):
    path: str = "database/technology_value_intelligence.duckdb"


class GraphSettings(BaseModel):
    output_dir: str = "graph_output"
    default_format: str = "graphml"


class LLMSettings(BaseModel):
    enabled: bool = False
    provider: str = "ollama"
    model: str = "llama3"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.0


class Config(BaseModel):
    project: ProjectSettings = Field(default_factory=ProjectSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    graph: GraphSettings = Field(default_factory=GraphSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)


def get_project_root() -> Path:
    """Find the root directory of the project containing config.yaml."""
    candidates = [
        Path.cwd(),
        Path.cwd().parent,
        Path(__file__).resolve().parent.parent.parent,
    ]
    for candidate in candidates:
        if (candidate / "config.yaml").exists():
            return candidate.resolve()
    return Path.cwd().resolve()


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file or return defaults.

    Args:
        config_path: Path to config.yaml. Defaults to finding config.yaml
                     in current working directory or repo root.

    Returns:
        Config: Validated pydantic configuration model.
    """
    if config_path is None:
        # Search common locations
        candidates = [
            Path("config.yaml"),
            Path(__file__).resolve().parent.parent.parent / "config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = str(candidate)
                break

    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f) or {}
            return Config(**raw_data)
    return Config()


def load_ontology(ontology_path: Optional[str] = None) -> Dict[str, Any]:
    """Load ontology specification from ontology.yaml.

    Args:
        ontology_path: Path to ontology.yaml.

    Returns:
        Dict[str, Any]: Raw ontology definition dictionary.
    """
    if ontology_path is None:
        candidates = [
            Path("ontology.yaml"),
            Path(__file__).resolve().parent.parent.parent / "ontology.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                ontology_path = str(candidate)
                break

    if ontology_path and Path(ontology_path).exists():
        with open(ontology_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}
