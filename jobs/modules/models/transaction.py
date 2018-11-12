
class Transaction:

    def __init__(self, row_key=None, transaction_id=None, nostro_sort_code=None, nostro_account_number=None, amount=None, receiver_sort_code=None, receiver_account_number=None, receiver_name=None, reference=None, sender_name=None, status=None, rejection_reason=None):
        self._row_key = row_key
        self._transaction_id = transaction_id
        self._nostro_sort_code = nostro_sort_code
        self._nostro_account_number = nostro_account_number
        self._amount = amount
        self._receiver_sort_code = receiver_sort_code
        self._receiver_account_number = receiver_account_number
        self._receiver_name = receiver_name
        self._reference = reference
        self._sender_name = sender_name
        self._status = status
        self._rejection_reason = rejection_reason

    @property
    def row_key(self):
        return self._row_key

    @row_key.setter
    def row_key(self, value):
        self._row_key = value

    @property
    def transaction_id(self):
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self._transaction_id = value

    @property
    def nostro_sort_code(self):
        return self._nostro_sort_code

    @nostro_sort_code.setter
    def nostro_sort_code(self, value):
        self._nostro_sort_code = value

    @property
    def nostro_account_number(self):
        return self._nostro_account_number

    @nostro_account_number.setter
    def nostro_account_number(self, value):
        self._nostro_account_number = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def receiver_sort_code(self):
        return self._receiver_sort_code

    @receiver_sort_code.setter
    def receiver_sort_code(self, value):
        self._receiver_sort_code = value

    @property
    def receiver_account_number(self):
        return self._receiver_account_number

    @receiver_account_number.setter
    def receiver_account_number(self, value):
        self._receiver_account_number = value

    @property
    def receiver_name(self):
        return self._receiver_name

    @receiver_name.setter
    def receiver_name(self, value):
        self._receiver_name = value

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value

    @property
    def sender_name(self):
        return self._sender_name

    @sender_name.setter
    def sender_name(self, value):
        self._sender_name = value

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
