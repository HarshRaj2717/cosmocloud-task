from dataclasses import dataclass
from typing import Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from config.database import collection
from models.students import Student
from schema.schemas import list_serialize, serialize_student

router = APIRouter()


@dataclass
class AddressPatch:
    city: Optional[str] = None
    country: Optional[str] = None


class StudentPatch(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[AddressPatch] = None


@router.post("/students", response_model=dict, status_code=201)
async def create_student(student: Student):
    insert_result = collection.insert_one(student.model_dump())
    cur_id = str(insert_result.inserted_id)
    return {"id": cur_id}


@router.get("/students", response_model=dict)
async def list_students(
    country: Optional[str] = Query(None), age: Optional[int] = Query(None)
):
    filter = {}
    if country:
        filter["address.country"] = {"$regex": f"^{country}$", "$options": "i"}
    if age:
        filter["age"] = {"$gte": age}
    students = list_serialize(collection.find(filter))
    return {"data": students}


@router.get("/students/{id}", response_model=Student)
async def get_student_by_id(id: str):
    student = collection.find_one({"_id": ObjectId(id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return serialize_student(student).student


@router.patch("/students/{id}", response_model=None, status_code=204)
async def update_student(id: str, student: StudentPatch):
    existing_student = collection.find_one({"_id": ObjectId(id)})
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    updated_data = {}
    if student.name:
        updated_data["name"] = student.name
    if student.age:
        updated_data["age"] = student.age
    if student.address:
        updated_data["address"] = {
            "city": (
                student.address.city
                if student.address.city
                else existing_student["address"]["city"]
            ),
            "country": (
                student.address.country
                if student.address.country
                else existing_student["address"]["country"]
            ),
        }

    collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})


@router.delete("/students/{id}", response_model=dict)
async def delete_student(id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {}
