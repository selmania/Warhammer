"""Shopping Advisor — LLM-powered chat backend for terrain material guidance.

Uses the Anthropic Claude API for natural conversation, enriched with:
  - The DIY alternatives knowledge base
  - Live product search results from online retailers
  - The terrain materials database from the board designer
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field
from typing import Optional

import anthropic

from .diy_alternatives import (
    DIY_ALTERNATIVES,
    get_alternatives_for,
    get_alternatives_summary,
    search_alternatives,
    format_alternative,
)

# Import the shared product search engine and terrain knowledge
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from warhammer_board_agent.product_search import ProductSearchEngine, ProductResult
from warhammer_board_agent.terrain import MATERIALS, TERRAIN_FEATURES, describe_feature


# ---------------------------------------------------------------------------
# System prompt — gives the LLM its personality and knowledge
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are the **Warhammer Terrain Shopping Advisor** — a friendly, knowledgeable expert \
who helps hobbyists find the best materials to build custom Warhammer tabletop terrain.

Your core personality:
- Enthusiastic about terrain building and always encouraging
- Budget-conscious — you actively suggest cheaper alternatives
- Creative — you love DIY hacks using household and scavenged materials
- Practical — you give specific, actionable advice with tips

You have access to these tools which are called automatically:
1. **product_search** — searches online hobby retailers (Amazon, eBay, Miniature Market, etc.)
2. **diy_alternatives** — a database of household/scavenged substitutes for commercial materials
3. **terrain_info** — details about terrain features including materials and construction tips

When responding:
- If someone asks about a material, ALWAYS mention both commercial options AND DIY alternatives
- Include approximate prices for commercial products
- Give specific tips — not vague advice
- When suggesting DIY alternatives, explain where to find the materials and how to use them
- If someone asks about a terrain feature (mountains, rivers, etc.), explain how to build it
- Be conversational and fun — you're chatting with a fellow hobbyist
- Use markdown formatting for readability
- Keep responses focused and practical — avoid rambling

## Your Knowledge Base — DIY Alternatives:

{diy_knowledge}

## Commercial Materials Reference:

{materials_knowledge}
"""


def _build_system_prompt() -> str:
    """Build the system prompt with injected knowledge bases."""
    diy_knowledge = get_alternatives_summary()

    mat_lines = []
    for key, mat in MATERIALS.items():
        mat_lines.append(
            f"- **{mat.name}**: {mat.description} "
            f"(typical price: {mat.typical_price_range})"
        )
    materials_knowledge = "\n".join(mat_lines)

    return SYSTEM_PROMPT.format(
        diy_knowledge=diy_knowledge,
        materials_knowledge=materials_knowledge,
    )


# ---------------------------------------------------------------------------
# Tool definitions for the Claude API
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "product_search",
        "description": (
            "Search online hobby retailers (Amazon, eBay, Miniature Market, Games Workshop, etc.) "
            "for terrain building products. Returns product titles, prices, and URLs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, e.g. 'XPS foam 2 inch insulation board' or 'static grass 6mm'",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "diy_alternatives",
        "description": (
            "Look up DIY and household alternatives for commercial terrain materials. "
            "Search by commercial material name or by a general query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Material name or search term, e.g. 'XPS foam', 'flock', 'water effects'",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "terrain_info",
        "description": (
            "Get detailed information about a terrain feature type including materials needed "
            "and construction tips. Available features: mountain, hill, dry_riverbed, river, "
            "forest, ruins, crater, rocky_outcrops, desert_dunes, bridge."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "Terrain feature key, e.g. 'mountain', 'dry_riverbed', 'ruins'",
                },
            },
            "required": ["feature"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

_search_engine = ProductSearchEngine(rate_limit_seconds=1.0)


def _execute_tool(name: str, input_data: dict) -> str:
    """Execute a tool call and return the result as a string."""
    if name == "product_search":
        query = input_data.get("query", "")
        results = _search_engine.search_products(query, limit_per_source=3)
        if not results:
            return "No products found for this search. Try different keywords."
        lines = []
        for r in results[:10]:
            lines.append(f"• **{r.title}** — {r.price} ({r.source})\n  {r.url}")
        return "\n".join(lines)

    elif name == "diy_alternatives":
        query = input_data.get("query", "")
        # Try exact material match first, then free-text search
        alts = get_alternatives_for(query)
        if not alts:
            alts = search_alternatives(query)
        if not alts:
            return f"No DIY alternatives found for '{query}'. Try a broader search term."
        return "\n\n".join(format_alternative(a) for a in alts)

    elif name == "terrain_info":
        feature = input_data.get("feature", "")
        info = describe_feature(feature)
        feat = TERRAIN_FEATURES.get(feature)
        if feat:
            tips = "\n".join(f"  {i}. {t}" for i, t in enumerate(feat.construction_tips, 1))
            info += f"\nConstruction Tips:\n{tips}"
        return info

    return f"Unknown tool: {name}"


# ---------------------------------------------------------------------------
# Chat session
# ---------------------------------------------------------------------------

@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str


@dataclass
class ShoppingAdvisor:
    """Manages a conversation with the Claude-powered shopping advisor."""

    api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    history: list[ChatMessage] = field(default_factory=list)
    _client: Optional[anthropic.Anthropic] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            self._client = anthropic.Anthropic(api_key=key)

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def set_api_key(self, key: str) -> None:
        self.api_key = key
        self._client = anthropic.Anthropic(api_key=key)

    def chat(self, user_message: str) -> str:
        """Send a message and get a response. Handles tool calls automatically."""
        if not self._client:
            reply = self._fallback_response(user_message)
            self.history.append(ChatMessage(role="user", content=user_message))
            self.history.append(ChatMessage(role="assistant", content=reply))
            return reply

        self.history.append(ChatMessage(role="user", content=user_message))

        # Build messages for the API
        messages = [{"role": m.role, "content": m.content} for m in self.history]

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=_build_system_prompt(),
                tools=TOOLS,
                messages=messages,
            )

            # Handle tool use loop
            while response.stop_reason == "tool_use":
                # Collect all content from the response
                assistant_content = response.content
                messages.append({"role": "assistant", "content": assistant_content})

                # Execute each tool call
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        result = _execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({"role": "user", "content": tool_results})

                # Continue the conversation
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    system=_build_system_prompt(),
                    tools=TOOLS,
                    messages=messages,
                )

            # Extract final text response
            text_parts = [b.text for b in response.content if hasattr(b, "text")]
            assistant_reply = "\n".join(text_parts)

            self.history.append(ChatMessage(role="assistant", content=assistant_reply))
            return assistant_reply

        except anthropic.APIError as e:
            return f"API error: {e}. Please check your API key and try again."
        except Exception as e:
            return f"Error: {e}"

    def _fallback_response(self, user_message: str) -> str:
        """Provide helpful responses without an API key using the knowledge base directly."""
        query = user_message.lower()
        parts: list[str] = []

        # Check for terrain feature questions
        for key, feat in TERRAIN_FEATURES.items():
            if key in query or feat.name.lower() in query:
                parts.append(f"## {feat.name}\n\n{describe_feature(key)}")
                tips = "\n".join(f"{i}. {t}" for i, t in enumerate(feat.construction_tips, 1))
                parts.append(f"### Construction Tips\n{tips}")
                break

        # Check for DIY alternative matches
        alts = search_alternatives(user_message)
        if alts:
            parts.append("## DIY Alternatives\n")
            for a in alts[:5]:
                parts.append(format_alternative(a))

        # Check for material matches
        for key, mat in MATERIALS.items():
            if key.replace("_", " ") in query or mat.name.lower() in query:
                parts.append(
                    f"## {mat.name}\n"
                    f"{mat.description}\n"
                    f"**Typical price:** {mat.typical_price_range}\n"
                )
                # Also find DIY alternatives for this material
                mat_alts = get_alternatives_for(mat.name)
                if mat_alts:
                    parts.append("### Cheaper DIY Alternatives:")
                    for a in mat_alts:
                        parts.append(format_alternative(a))
                break

        if parts:
            parts.insert(0, "*Running in offline mode (no API key). "
                         "Set your ANTHROPIC_API_KEY for full conversational AI.*\n")
            return "\n\n".join(parts)

        # Generic helpful response
        return (
            "*Running in offline mode (no API key). "
            "Set your ANTHROPIC_API_KEY for full conversational AI.*\n\n"
            "I can help with terrain materials! Try asking about:\n"
            "- Specific materials: *\"What can I use instead of XPS foam?\"*\n"
            "- Terrain features: *\"How do I build a mountain?\"*\n"
            "- DIY alternatives: *\"cheap water effects\"*\n"
            "- Materials: *\"What do I need for a dry riverbed?\"*"
        )

    def reset(self) -> None:
        """Clear conversation history."""
        self.history.clear()
