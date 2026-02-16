# appointment.py
from datetime import datetime


class Appointment:
    """Minimal appointment record that only tracks patient + datetime + short code."""

    def __init__(self, patient_id, dt_str, code=None):
        if not patient_id or not isinstance(patient_id, str):
            raise ValueError("Appointment: patient_id must be a non-empty string")

        self.patient_id = patient_id
        self.dt = self._parse_datetime(dt_str)
        self.code = code

    @staticmethod
    def _parse_datetime(dt_str):
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except Exception as e:
            raise ValueError("Appointment: datetime must be 'YYYY-MM-DD HH:MM'") from e

    def key_minutes(self):
        """Key used by BST: minutes since epoch (integer)."""
        return int(self.dt.timestamp() // 60)

    def datetime_str(self):
        return self.dt.strftime("%Y-%m-%d %H:%M")

    def __str__(self):
        s = self.datetime_str()
        code = self.code or "-----"
        return f"Appt[{code}] {s} pid={self.patient_id}"
