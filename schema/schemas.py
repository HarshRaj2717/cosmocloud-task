from dataclasses import dataclass

from models.students import Student


@dataclass
class SerializedStudent:
    id: str
    student: Student


def serialize_student(data: dict) -> SerializedStudent:
    """Serialize mongo's dictionary to Student object."""
    cur_id = data.pop("_id")
    return SerializedStudent(id=cur_id, student=Student.model_validate(data))


def list_serialize(students) -> list[dict]:
    data: list[dict] = []

    for i in students:
        cur_student = serialize_student(i).student
        data.append({"name": cur_student.name, "age": cur_student.age})

    return data
