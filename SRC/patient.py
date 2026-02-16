# patient.py
from .linked_list import LinkedList

class Patient:
    def __init__(self, patient_id, name, age, gender, phone, medical_notes=""):
        if not patient_id or not isinstance(patient_id, str):
            raise ValueError("Patient: patient_id must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ValueError("Patient: name must be a non-empty string")
        if not isinstance(age, int) or age < 0 or age > 130:
            raise ValueError("Patient: age must be int in range 0..130")
        if gender not in ("M", "F", "O"):
            raise ValueError("Patient: gender must be 'M', 'F', or 'O'")
        if not phone or not isinstance(phone, str):
            raise ValueError("Patient: phone must be a non-empty string")

        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone = phone
        self.medical_notes = medical_notes

        # Mandatory Linked List: per-patient visit history
        self.visit_history = LinkedList()

    def add_visit(self, visit_record):
        self.visit_history.append(visit_record)

    def __str__(self):
        return f"Patient[{self.patient_id}] {self.name}, {self.age}, {self.gender}, {self.phone}"

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "phone": self.phone,
            "medical_notes": self.medical_notes,
            "visit_history": self.visit_history.to_list(),
        }

    @classmethod
    def from_dict(cls, data):
        patient = cls(
            data["patient_id"],
            data["name"],
            data["age"],
            data["gender"],
            data["phone"],
            data.get("medical_notes", ""),
        )
        for record in data.get("visit_history", []):
            patient.add_visit(record)
        return patient
