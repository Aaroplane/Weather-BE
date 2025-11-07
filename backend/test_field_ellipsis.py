from pydantic import BaseModel, Field, ValidationError
from typing import Optional


# PATTERN 1: Required field (...)
class RequiredExample(BaseModel):
    name: str = Field(..., description="Name is required")
    age: int = Field(..., ge=0, description="Age is required and must be >= 0")


# PATTERN 2: Optional with default
class OptionalDefaultExample(BaseModel):
    name: str = Field("Unknown", description="Name with default")
    age: int = Field(0, ge=0, description="Age with default 0")


# PATTERN 3: Optional nullable
class OptionalNullableExample(BaseModel):
    name: Optional[str] = Field(None, description="Name can be None")
    age: Optional[int] = Field(None, ge=0, description="Age can be None")


def test_patterns():
    print("=" * 60)
    print("PATTERN 1: Required Fields (...)")
    print("=" * 60)
    
    # This works:
    try:
        person = RequiredExample(name="Alice", age=30)
        print(f"✅ Success: {person}")
    except ValidationError as e:
        print(f"❌ Failed: {e}")
    
    # This fails (missing required field):
    try:
        person = RequiredExample(name="Bob")  # age missing!
        print(f"✅ Success: {person}")
    except ValidationError as e:
        print(f"❌ Failed: age is required!\n   {e.errors()[0]['msg']}")
    
    print("\n" + "=" * 60)
    print("PATTERN 2: Optional with Default")
    print("=" * 60)
    
    # This works (uses defaults):
    person = OptionalDefaultExample()
    print(f"✅ No args provided: {person}")
    print(f"   name={person.name}, age={person.age}")
    
    # This works (overrides defaults):
    person = OptionalDefaultExample(name="Charlie", age=25)
    print(f"✅ Args provided: {person}")
    
    print("\n" + "=" * 60)
    print("PATTERN 3: Optional Nullable")
    print("=" * 60)
    
    # This works (None values):
    person = OptionalNullableExample()
    print(f"✅ No args: {person}")
    print(f"   name={person.name}, age={person.age}")
    
    # This works (explicit None):
    person = OptionalNullableExample(name=None, age=None)
    print(f"✅ Explicit None: {person}")
    
    # This works (mix of values and None):
    person = OptionalNullableExample(name="Diana", age=None)
    print(f"✅ Mixed: {person}")
    
    print("\n" + "=" * 60)
    print("VALIDATION RULES EXAMPLE")
    print("=" * 60)
    
    # Test ge (greater or equal) validation:
    try:
        person = RequiredExample(name="Eve", age=-5)  # age < 0
        print(f"✅ Success: {person}")
    except ValidationError as e:
        print(f"❌ Failed: age must be >= 0")
        print(f"   Error: {e.errors()[0]['msg']}")


if __name__ == "__main__":
    test_patterns()