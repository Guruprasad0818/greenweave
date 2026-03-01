"""
GreenWeave SDK — OpenAI-compatible response models
These dataclasses mirror openai's response objects exactly,
so existing code that accesses response.choices[0].message.content works unchanged.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    role: str
    content: str

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class Choice:
    index: int
    message: Message
    finish_reason: str = "stop"

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class CarbonReceipt:
    """
    GreenWeave extension attached to every response.
    Access via: response.carbon_receipt.co2_saved_g
    """
    mode:                    str   = "UNKNOWN"
    model_used:              str   = ""
    grid_intensity_gco2_kwh: float = 0.0
    co2_this_query_g:        float = 0.0
    co2_saved_g:             float = 0.0
    energy_saved_pct:        float = 0.0
    impact_reduction_pct:    float = 0.0
    latency_ms:              float = 0.0
    cache_hit:               bool  = False
    similarity_score:        Optional[float] = None

    def __str__(self):
        if self.cache_hit:
            return (f"CarbonReceipt(CACHE HIT | CO₂=0.00000g | "
                    f"saved={self.co2_saved_g:.5f}g | 100% energy saved | {self.latency_ms:.0f}ms)")
        return (f"CarbonReceipt(mode={self.mode} | model={self.model_used} | "
                f"CO₂={self.co2_this_query_g:.5f}g | saved={self.co2_saved_g:.4f}g | "
                f"energy={self.energy_saved_pct:.0f}% | {self.latency_ms:.0f}ms)")


@dataclass
class ChatCompletion:
    """
    Mirrors openai.types.chat.ChatCompletion exactly.
    response.choices[0].message.content → works identically.
    response.carbon_receipt             → GreenWeave extension.
    """
    id:             str
    object:         str
    created:        int
    model:          str
    choices:        list
    usage:          Usage
    carbon_receipt: CarbonReceipt = field(default_factory=CarbonReceipt)

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class ChatCompletionChunk:
    """For future streaming support."""
    id:      str
    object:  str = "chat.completion.chunk"
    created: int = 0
    model:   str = ""
    choices: list = field(default_factory=list)
