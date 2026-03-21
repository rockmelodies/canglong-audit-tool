from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException, status

from app.models.schemas import ModelConnection, ModelConnectionUpsert, ModelSettingsResponse


def _mask_api_key(api_key: str | None) -> str | None:
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}...{api_key[-4:]}"


@dataclass
class StoredModel:
    id: str
    display_name: str
    provider: str
    model_slug: str
    description: str
    base_url: str
    api_key: str | None
    enabled: bool
    is_default: bool
    editable: bool
    capability_tags: list[str]

    def to_schema(self) -> ModelConnection:
        api_key_set = bool(self.api_key)
        configured = bool(self.base_url.strip() and self.model_slug.strip() and api_key_set and self.enabled)
        return ModelConnection(
            id=self.id,
            displayName=self.display_name,
            provider=self.provider,
            modelSlug=self.model_slug,
            description=self.description,
            baseUrl=self.base_url,
            apiKeySet=api_key_set,
            apiKeyPreview=_mask_api_key(self.api_key),
            enabled=self.enabled,
            isDefault=self.is_default,
            editable=self.editable,
            status="configured" if configured else "incomplete",
            setupHint=(
                "Ready for agent tasks."
                if configured
                else "Add a base URL, model id, and API key, then enable this model."
            ),
            capabilityTags=self.capability_tags,
        )


class ModelSettingsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._models: list[StoredModel] = [
            StoredModel(
                id="model-gpt54",
                display_name="GPT-5.4",
                provider="OpenAI",
                model_slug="gpt-5.4",
                description="Default general-purpose model for audit orchestration and tool use.",
                base_url="https://api.openai.com/v1",
                api_key=None,
                enabled=False,
                is_default=False,
                editable=True,
                capability_tags=["default", "tool-calling", "audit"],
            ),
            StoredModel(
                id="model-opus46",
                display_name="Claude Opus 4.6",
                provider="Anthropic",
                model_slug="claude-opus-4-6",
                description="Second-pass long-context review for guardrails and contradiction analysis.",
                base_url="https://api.anthropic.com",
                api_key=None,
                enabled=False,
                is_default=False,
                editable=True,
                capability_tags=["review", "long-context"],
            ),
            StoredModel(
                id="model-custom-compatible",
                display_name="Custom OpenAI-Compatible Endpoint",
                provider="Custom",
                model_slug="your-model-name",
                description="Bring your own endpoint for self-hosted or gateway-routed general models.",
                base_url="http://localhost:11434/v1",
                api_key=None,
                enabled=False,
                is_default=False,
                editable=True,
                capability_tags=["custom", "private", "openai-compatible"],
            ),
        ]

    def _build_response(self) -> ModelSettingsResponse:
        models = [item.to_schema() for item in self._models]
        usable_models = [item for item in models if item.status == "configured"]
        default_model = next((item for item in models if item.isDefault), None)
        has_usable = bool(default_model and default_model.status == "configured")
        if has_usable:
            next_action = "Go to Workspace and click the green Start Audit button on a repository card."
        else:
            next_action = "Configure a default model first, then add or sync a repository before starting an audit."

        return ModelSettingsResponse(
            recommendedModelId="model-gpt54",
            hasUsableModel=has_usable,
            defaultModelLabel=default_model.displayName if default_model else None,
            nextAction=next_action,
            guidance=[
                "Configure one default general-purpose model first.",
                "Use a long-context reviewer or multimodal model only when the task clearly benefits from it.",
                "Custom self-hosted endpoints should expose an OpenAI-compatible API when possible.",
            ],
            models=models,
        )

    def list_settings(self) -> ModelSettingsResponse:
        with self._lock:
            return self._build_response()

    def update_model(self, model_id: str, payload: ModelConnectionUpsert) -> ModelConnection:
        with self._lock:
            model = next((item for item in self._models if item.id == model_id), None)
            if not model:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model configuration not found")

            model.display_name = payload.displayName
            model.provider = payload.provider
            model.model_slug = payload.modelSlug
            model.description = payload.description
            model.base_url = payload.baseUrl
            if payload.apiKey:
                model.api_key = payload.apiKey
            model.enabled = payload.enabled
            model.capability_tags = payload.capabilityTags
            return model.to_schema()

    def create_model(self, payload: ModelConnectionUpsert) -> ModelConnection:
        with self._lock:
            model = StoredModel(
                id=f"model-{uuid4().hex[:8]}",
                display_name=payload.displayName,
                provider=payload.provider,
                model_slug=payload.modelSlug,
                description=payload.description,
                base_url=payload.baseUrl,
                api_key=payload.apiKey,
                enabled=payload.enabled,
                is_default=False,
                editable=True,
                capability_tags=payload.capabilityTags,
            )
            self._models.insert(0, model)
            return model.to_schema()

    def set_default(self, model_id: str) -> ModelConnection:
        with self._lock:
            target = next((item for item in self._models if item.id == model_id), None)
            if not target:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model configuration not found")

            for item in self._models:
                item.is_default = item.id == model_id
            return target.to_schema()


model_settings_store = ModelSettingsStore()
