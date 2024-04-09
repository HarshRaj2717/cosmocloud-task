from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


@dataclass
class Address:
    city: str
    country: str


@dataclass
class AddressPatch:
    city: Optional[str] = None
    country: Optional[str] = None


# TODO put this Model in a different file ??
# TODO check how these FastAPI files must be structured,
# these might follow the django style only for more stuff
class Student(BaseModel):
    name: str
    age: int
    address: Address


class StudentPatch(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[AddressPatch] = None


# TODO (replace with MongoDB implementation)
# TODO maybe this needs to go into a different file too
database: dict[str, Student] = {}


@router.post("/students", response_model=dict, status_code=201)
async def create_student(student: Student):
    new_student = Student(
        name=student.name.lower(),
        age=student.age,
        address=Address(
            city=student.address.city.lower(),
            country=student.address.country.lower(),
        ),
    )
    cur_id = str(len(database) + 1)
    database[cur_id] = new_student
    return {"id": cur_id}


@router.get("/students", response_model=dict)
async def list_students(
    country: Optional[str] = Query(None), age: Optional[int] = Query(None)
):
    # TODO this will need to be fetched from the mongodb database...
    # TODO can this be optimized ??
    filtered_students: list[dict] = []
    for cur_id in database:
        cur_student: Student = database[cur_id]
        if country is not None and cur_student.address.country != country.lower():
            continue
        if age is not None and cur_student.age < age:
            continue
        filtered_students.append({"name": cur_student.name, "age": cur_student.age})
    return {"data": filtered_students}


@router.get("/students/{id}", response_model=Student)
async def get_student_by_id(id: str):
    # TODO this will need to be fetched from the mongodb database...
    cur_student: Optional[Student] = database.get(id)
    if not cur_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return cur_student


@router.patch("/students/{id}", response_model=None, status_code=204)
async def update_student(id: str, student: StudentPatch):
    # TODO this will need to be patched in the mongodb database...
    if not database.get(id):
        raise HTTPException(status_code=404, detail="Student not found")

    name: str = database[id].name
    if student.name != None:
        name = student.name.lower()

    age: int = database[id].age
    if student.age != None:
        age = student.age

    city: str = database[id].address.city
    country: str = database[id].address.country
    if student.address != None:
        if student.address.city != None:
            city = student.address.city.lower()
        if student.address.country != None:
            country = student.address.country.lower()

    database[id] = Student(
        name=name,
        age=age,
        address=Address(city=city, country=country),
    )


@router.delete("/students/{id}", response_model=dict)
async def delete_student(id: str):
    # TODO this will need to be deleted from the mongodb database...
    if not database.get(id):
        raise HTTPException(status_code=404, detail="Student not found")
    del database[id]
    return {}
