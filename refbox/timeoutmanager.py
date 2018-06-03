from uwh.gamemanager import TimeoutState

class TimeoutManager(object):
    def __init__(self, var, team_timeout_duration):
        var.set("START")
        self._text = var
        self._team_timeout_duration = team_timeout_duration
        self._clock_at_timeout = None
        self._reset_handlers = []

    def ready_to_start(self):
        return self._text.get() == "START" or self._text.get() == "RESET"

    def ready_to_resume(self):
        return self._text.get() == "RESUME"

    def set_game_over(self, mgr):
        self._text.set("RESET")
        mgr.setGameStateGameOver()
        mgr.setGameClockRunning(False)
        mgr.setGameClock(0)
        mgr.deleteAllPenalties()

    def add_reset_handler(self, callback):
        self._reset_handlers += [callback]

    def click(self, mgr, half_play_duration, state):
        if mgr.gameStateGameOver():
            mgr.setBlackScore(0)
            mgr.setWhiteScore(0)
            mgr.setGameStatePreGame()
            mgr.setGameClock(half_play_duration)
            mgr.deleteAllPenalties()
            for handler in self._reset_handlers:
                handler()
            self._text.set("START")
            return

        if mgr.gameStatePreGame():
            mgr.setGameStateFirstHalf()

        if mgr.timeoutStateNone() and state != TimeoutState.none:
            self._clock_at_timeout = mgr.gameClock()
            mgr.pauseOutstandingPenalties()
            mgr.setGameClockRunning(False)
            if state == TimeoutState.ref:
                mgr.setTimeoutStateRef()
            elif state == TimeoutState.penalty_shot:
                mgr.setTimeoutStatePenaltyShot()
            elif state == TimeoutState.white:
                mgr.setTimeoutStateWhite()
                mgr.setGameClock(self._team_timeout_duration)
                mgr.setGameClockRunning(True)
            elif state == TimeoutState.black:
                mgr.setTimeoutStateBlack()
                mgr.setGameClock(self._team_timeout_duration)
                mgr.setGameClockRunning(True)
            self._text.set('RESUME')
            return

        mgr.setGameClockRunning(True)
        if self._clock_at_timeout is not None:
            mgr.setGameClock(self._clock_at_timeout)
            self._clock_at_timeout = None
        mgr.restartOutstandingPenalties()
        mgr.setTimeoutStateNone()
        self._text.set('TIMEOUT')
