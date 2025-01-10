from typing import List, Union
from sqlalchemy import insert, column, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql._typing import _ColumnExpressionArgument

from pydantic import BaseModel

import uuid

from sqlalchemy import insert, column,update
from typing import List, Union, Any


async def insert_data(
    session: AsyncSession,
    model: type,
    data: dict,
    ignore_atr: List[str] = [],
    return_atr: Union[str, List[str], None] = None,
    auto_coomit: bool = True
) -> dict:
    """
    Вставляет данные в таблицу и возвращает указанные поля.

    Параметры:
    - session: AsyncSession - сессия SQLAlchemy.
    - model: type - модель ORM.
    - data: dict - данные для вставки.
    - ignore_atr: List[str] - список полей, которые нужно игнорировать.
    - return_atr: Union[str, List[str], None] - поле или список полей для возврата.
    - auto_coomit: bool - автоматическое завершение транзакции

    Возвращает:
    - dict с запрошенными полями.
    """
    stmt = insert(model)

    data_dict = data.copy()
    for atr in ignore_atr:
        data_dict.pop(atr, None)

    if return_atr:
        if isinstance(return_atr, str):
            return_atr_list = [return_atr]
        else:
            return_atr_list = return_atr

        returning_columns = [getattr(model, atr) for atr in return_atr_list]

        result = await session.execute(stmt.returning(*returning_columns).values(**data_dict))
        res = result.fetchone()
        res_dict = dict(zip(return_atr_list, res))
    else:
        await session.execute(stmt.values(**data_dict))
        res_dict = {}

    if auto_coomit:
        await session.commit()

    return res_dict


async def select_data_one_or_none(session: AsyncSession, model: type, return_model: type, *whereclause: _ColumnExpressionArgument[bool]):
    return await select_data_one_or_none_quer(session, return_model, select(model).where(*whereclause))


async def select_data_one_or_none_quer(session: AsyncSession, return_model: type, querty):
    res = await session.execute(querty)
    res = res.one_or_none()

    if res:
        for item in res:
            res = item


        return return_model.model_validate(res, from_attributes=True)
    else:
        return None



async def select_data_arr(session: AsyncSession, model: type, return_model: type, *whereclause: _ColumnExpressionArgument[bool]):
    res = await session.execute(select(model).where(*whereclause))
    res = res.scalars()

    return [return_model.model_validate(item, from_attributes=True) for item in res]


async def select_data_arr_quer(session: AsyncSession, return_model: type, querty):
    res = await session.execute(querty)
    res = res.all()

    ret = []
    for item in res:
        d = {}
        for i, v in enumerate(item):
            if hasattr(v,"__dict__"):
                d.update(v.__dict__)
            else:
                d[item._fields[i]]=v
        ret.append(return_model.model_validate(d, from_attributes=True))
    return ret


async def update_data(session: AsyncSession, model: type, *whereclause: _ColumnExpressionArgument[bool], auto_coomit: bool = True, **kwargs ) -> None:
    await session.execute(
        update(model)
        .where(*whereclause)
        .values(kwargs))
    if auto_coomit:
        await session.commit()
