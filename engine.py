
class AviatorEngine:

    def __init__(self):
        self.history = []

    def add_round(self, multiplier):
        try:
            value = float(multiplier)

            if value > 0:
                self.history.append(value)

            if len(self.history) > 200:
                self.history.pop(0)

        except (ValueError, TypeError):
            pass

    def analyze(self):

        if len(self.history) < 10:
            return {
                "signal": "WAIT",
                "confidence": 0,
                "level": "INSUFFICIENT DATA",
                "rounds": len(self.history),
                "reason": "At least 10 historical rounds are required."
            }

        recent = self.history[-10:]

        average = sum(recent) / len(recent)

        low_count = sum(
            1 for x in recent if x < 2.0
        )

        high_count = sum(
            1 for x in recent if x >= 2.0
        )

        changes = []

        for i in range(1, len(recent)):
            changes.append(
                abs(recent[i] - recent[i - 1])
            )

        volatility = (
            sum(changes) / len(changes)
            if changes else 0
        )

        score = 50

        if average < 1.8:
            score += 10

        if low_count >= 7:
            score += 10

        if high_count >= 3:
            score -= 5

        if volatility > 3:
            score -= 5

        score = max(0, min(95, score))

        if score >= 75:
            signal = "HIGHER-RISK"
            level = "HIGH"

        elif score >= 60:
            signal = "CAUTION"
            level = "MEDIUM"

        else:
            signal = "WAIT"
            level = "LOW"

        return {
            "signal": signal,
            "confidence": score,
            "level": level,
            "rounds": len(self.history),
            "average": round(average, 2),
            "low_rounds": low_count,
            "high_rounds": high_count,
            "volatility": round(volatility, 2)
        }


engine = AviatorEngine()
