"""
AlgoSwing — Strategy Plugin Registry
Strategies are registered here. Adding a new strategy = 1 import + 1 dict entry.
Zero core engine changes required.
"""
from typing import Optional
from loguru import logger

from app.strategies.base import BaseStrategy

# Registry maps strategy_id → strategy class (not instance)
_REGISTRY: dict[str, type[BaseStrategy]] = {}


def register_strategy(strategy_cls: type[BaseStrategy]) -> type[BaseStrategy]:
    """
    Decorator to register a strategy class.

    Usage:
        @register_strategy
        class MyStrategy(BaseStrategy):
            name = "my_strategy"
    """
    strategy_id = strategy_cls.name
    if strategy_id in _REGISTRY:
        logger.warning(f"⚠️  Strategy '{strategy_id}' already registered — overwriting")
    _REGISTRY[strategy_id] = strategy_cls
    logger.debug(f"📌 Strategy registered: {strategy_id} (v{strategy_cls.version})")
    return strategy_cls


def get_strategy(strategy_id: str, config: Optional[dict] = None) -> Optional[BaseStrategy]:
    """
    Retrieve an instantiated strategy by ID.

    Args:
        strategy_id: e.g. "ipo_ath_retest"
        config: Optional config dict to override defaults

    Returns:
        Instantiated strategy, or None if not found.
    """
    cls = _REGISTRY.get(strategy_id)
    if cls is None:
        logger.error(f"❌ Strategy not found: '{strategy_id}'. Available: {list(_REGISTRY.keys())}")
        return None
    return cls(config=config)


def list_strategies() -> list[dict]:
    """Return metadata for all registered strategies."""
    return [
        {
            "id": name,
            "name": cls.name,
            "version": cls.version,
            "description": cls.description,
        }
        for name, cls in _REGISTRY.items()
    ]


def load_all_strategies() -> None:
    """Import all strategy modules to trigger @register_strategy decorators."""
    import importlib
    strategy_modules = [
        "app.strategies.ipo_ath_retest.strategy",
        # Future strategies:
        # "app.strategies.ath_breakout.strategy",
        # "app.strategies.darvas_box.strategy",
    ]
    for module_path in strategy_modules:
        try:
            importlib.import_module(module_path)
            logger.debug(f"✅ Loaded strategy module: {module_path}")
        except ImportError as e:
            logger.error(f"❌ Failed to load strategy module {module_path}: {e}")
