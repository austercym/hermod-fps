
class ConfirmedTransaction:

    def __init__(self, row_key=None, status=None, rejection_reason=None):
        self._row_key = row_key
        self._status = status
        self._rejection_reason = rejection_reason

    @property
    def row_key(self):
        return self._row_key

    @row_key.setter
    def row_key(self, value):
        self._row_key = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def rejection_reason(self):
        return self._rejection_reason

    @rejection_reason.setter
    def rejection_reason(self, value):
        self._rejection_reason = value
