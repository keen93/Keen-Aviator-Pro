

from flask import Flask, render_template, jsonify, request
from datetime import datetime

from engine import engine
from performance import init_performance_table, save_signal, get_signal_count, get_signal_history

from database import (
    init_database,
    add_round,
    get_recent_rounds,
    get_round_count,
    reset_rounds,
    get_connection
)

app = Flask(__name__)

init_database()
init_performance_table()

for multiplier in get_recent_rounds(200):
    engine.add_round(multiplier)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "time": datetime.now().strftime("%H:%M:%S"),
        "engine": "Keen AI",
        "mode": "ANALYSIS",
        "rounds": get_round_count()
    })


@app.route("/api/round", methods=["POST"])
def add_new_round():
    try:
        data = request.get_json(silent=True) or {}
        multiplier = data.get("multiplier")

        if multiplier is None:
            return jsonify({
                "success": False,
                "error": "Multiplier is required"
            }), 400

        value = float(multiplier)

        if value <= 0:
            return jsonify({
                "success": False,
                "error": "Multiplier must be greater than 0"
            }), 400

        add_round(value)
        engine.add_round(value)

        return jsonify({
            "success": True,
            "multiplier": value,
            "rounds": get_round_count()
        })

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Invalid multiplier"
        }), 400


@app.route("/api/signal")
def signal():
    result = engine.analyze()
    result["time"] = datetime.now().strftime("%H:%M:%S")

    return jsonify(result)

    if result.get("rounds", 0) >= 10:
        save_signal(result)

    return jsonify(result)

@app.route("/api/record-signal", methods=["POST"])
def record_signal():
    result = engine.analyze()

    if result.get("rounds", 0) < 10:
        return jsonify({
            "success": False,
            "error": "At least 10 rounds are required"
        }), 400

    save_signal(result)

    return jsonify({
        "success": True,
        "signal": result
    })
@app.route("/api/record-outcome", methods=["POST"])
def record_outcome():
    try:
        data = request.get_json(silent=True) or {}

        signal_id = data.get("signal_id")
        outcome = data.get("outcome")
        multiplier = data.get("multiplier")

        if signal_id is None or outcome is None or multiplier is None:
            return jsonify({
                "success": False,
                "error": "signal_id, outcome and multiplier are required"
            }), 400

        from performance import record_outcome as save_outcome

        updated = save_outcome(
            signal_id,
            outcome,
            multiplier
        )

        if updated == 0:
            return jsonify({
                "success": False,
                "error": "Signal not found or already completed"
            }), 404

        return jsonify({
            "success": True,
            "signal_id": int(signal_id),
            "outcome": str(outcome).upper(),
            "multiplier": float(multiplier)
        })

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Invalid outcome data"
        }), 400
@app.route("/api/performance")
def performance():
    return jsonify({
        "count": get_signal_count(),
        "signals": get_signal_history(50)
    })


@app.route("/api/history")
def history():
    return jsonify({
        "rounds": get_recent_rounds(50),
        "count": get_round_count()
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    reset_rounds()
    engine.history.clear()

    return jsonify({
        "success": True,
        "rounds": 0,
        "message": "Round history cleared"
    })


if __name__ == "__main__":
    print()
    print("======================================")
    print("       KEEN AVIATOR PRO")
    print("       Analysis Engine")
    print("======================================")
    print()
    print("Saved rounds:", get_round_count())
    print()
    print("Open in your browser:")
    print("http://127.0.0.1:5000")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
