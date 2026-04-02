"""Flask web application for the Shopping Advisor agent."""

from __future__ import annotations

import os

from flask import Flask, render_template, request, jsonify

from .advisor import ShoppingAdvisor

app = Flask(__name__)
advisor = ShoppingAdvisor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    return jsonify({
        "api_configured": advisor.is_configured,
        "message_count": len(advisor.history),
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    reply = advisor.chat(user_message)
    return jsonify({
        "reply": reply,
        "api_configured": advisor.is_configured,
    })


@app.route("/api/set-key", methods=["POST"])
def set_key():
    data = request.get_json()
    key = data.get("api_key", "").strip() if data else ""
    if not key:
        return jsonify({"success": False, "error": "No key provided"}), 400

    try:
        advisor.set_api_key(key)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    advisor.reset()
    return jsonify({"success": True})


def main():
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"\n  ⚔  Warhammer Terrain Shopping Advisor")
    print(f"  ────────────────────────────────────")
    print(f"  Open http://localhost:{port} in your browser")
    print(f"  Set ANTHROPIC_API_KEY env var for AI-powered chat")
    print(f"  Or enter your key in the sidebar\n")
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
