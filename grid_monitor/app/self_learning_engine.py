class SelfLearningEngine:
    """
    Adaptive execution decision engine.
    Learns from previous outcomes.
    """

    def __init__(self):
        self.success_count = 0
        self.delay_count = 0

    def update_learning(self, delayed: bool):
        if delayed:
            self.delay_count += 1
        else:
            self.success_count += 1

    def adaptive_threshold(self):
        """
        Adjust behavior based on history
        """

        total = self.success_count + self.delay_count

        if total == 0:
            return 0.5

        delay_ratio = self.delay_count / total

        # If we delay too often, reduce sensitivity
        if delay_ratio > 0.7:
            return 0.3
        elif delay_ratio < 0.3:
            return 0.7
        else:
            return 0.5