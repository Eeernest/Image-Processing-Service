from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies.admin_dependency import AdminServiceDep
from app.dependencies.permit_dependency import CurrentAdminDep
from app.models.account_model import AccountRole
from app.schemas.admin_schema import AdminRead

router = APIRouter()

@router.get("/view_all_accounts", response_model=list[AdminRead])
async def view_all_accounts(
  admin: CurrentAdminDep,
  service: AdminServiceDep,
  offset: int = 0,
  limit: Annotated[int, Query(le=100)] = 100,
  is_active: bool | None = None,
  is_deleted: bool | None = None
):
  return await service.view_all_accounts(offset, limit, is_active, is_deleted)

@router.patch("/delete_account", response_model=AdminRead)
async def delete_account(admin: CurrentAdminDep, service: AdminServiceDep, id: int):
  return await service.delete_account(id)

@router.patch("/change_account_role", response_model=AdminRead)
async def change_account_role(admin: CurrentAdminDep, service: AdminServiceDep, id: int, user_role: AccountRole):
  return await service.change_account_role(id, user_role)