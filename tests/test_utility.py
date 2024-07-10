from pydantic import BaseModel
from typing import Set


class TestModel(BaseModel):
    id: int
    name: str


def comparison(model_a: BaseModel, model_b: BaseModel, ignore_attributes: list[str]) -> bool:
    dict_a = model_a.model_dump()
    dict_b = model_b.model_dump()

    keys = set(dict_a.keys())
    keys.update(dict_b)

    equal = True
    for key in keys:
        if not key in ignore_attributes:
            if key in dict_a:
                a = dict_a[key]
            else:
                equal = False
                break

            if key in dict_b:
                b = dict_b[key]
            else:
                equal = False
                break
            
            if not a == b:
                print(a)
                print(b)
                equal = False
                break

    return equal


def test_true():
    assert comparison(TestModel(id=1, name="a"),
                      TestModel(id=1, name="a"), []) == True


def test_true_id():
    assert comparison(TestModel(id=1, name="a"),
                      TestModel(id=2, name="a"), ['id']) == True


def test_false():
    assert comparison(TestModel(id=1, name="a"),
                      TestModel(id=2, name="a"), []) == False
