from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional


CanHandle = Callable[[str, Dict[str, Any]], bool]
Handle = Callable[[str, Dict[str, Any]], Any]


@dataclass
class FeatureSpec:
    feature_id: str
    description: str
    can_handle: CanHandle
    handle: Handle
    priority: int = 100


class HappinessProgramManager:
    """
    Orchestrates feature handlers and auto-loads new features from a package.

    To add a new feature automatically:
    1) Create a new module in agents/features/
    2) Expose register(manager) and call manager.register_feature(...)
    """

    def __init__(self, features_package: str = "agents.features") -> None:
        self.features_package = features_package
        self._features: List[FeatureSpec] = []
        self._loaded = False

    def register_feature(self, feature: FeatureSpec) -> None:
        if any(existing.feature_id == feature.feature_id for existing in self._features):
            return
        self._features.append(feature)
        self._features.sort(key=lambda item: item.priority)

    def load_features(self) -> None:
        if self._loaded:
            return

        package = import_module(self.features_package)
        package_paths = getattr(package, "__path__", None)
        if not package_paths:
            self._loaded = True
            return

        for module_info in iter_modules(package_paths):
            if module_info.name.startswith("_"):
                continue
            module_name = f"{self.features_package}.{module_info.name}"
            module = import_module(module_name)
            self._register_from_module(module)

        self._loaded = True

    def _register_from_module(self, module: ModuleType) -> None:
        register_fn = getattr(module, "register", None)
        if callable(register_fn):
            register_fn(self)

    @property
    def feature_ids(self) -> List[str]:
        return [feature.feature_id for feature in self._features]

    @property
    def feature_catalog(self) -> List[Dict[str, str]]:
        return [
            {"feature_id": feature.feature_id, "description": feature.description}
            for feature in self._features
        ]

    def _resolve_feature(self, user_input: str, context: Dict[str, Any]) -> Optional[FeatureSpec]:
        router = context.get("route_feature")
        if callable(router):
            try:
                feature_id = router(user_input, self.feature_catalog)
                if feature_id:
                    selected = next(
                        (feature for feature in self._features if feature.feature_id == feature_id),
                        None,
                    )
                    if selected is not None:
                        return selected
            except Exception:
                pass

        for feature in self._features:
            try:
                if feature.can_handle(user_input, context):
                    return feature
            except Exception:
                continue
        return None

    def handle(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.load_features()
        safe_context = context or {}
        feature = self._resolve_feature(user_input, safe_context)

        if feature is None:
            return {
                "selected_feature": None,
                "result": (
                    "No matching feature found. Add a new module in agents/features "
                    "to extend manager behavior automatically."
                ),
                "available_features": self.feature_ids,
            }

        try:
            result = feature.handle(user_input, safe_context)
            return {
                "selected_feature": feature.feature_id,
                "result": result,
                "available_features": self.feature_ids,
            }
        except Exception as exc:
            return {
                "selected_feature": feature.feature_id,
                "error": str(exc),
                "available_features": self.feature_ids,
            }


def create_default_manager() -> HappinessProgramManager:
    manager = HappinessProgramManager()
    manager.load_features()
    return manager
