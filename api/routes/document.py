# -*- coding: utf-8 -*-
"""文档管理 API：上传与列表。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import get_async_session
from models.schemas import DocumentInfo, DocumentUploadResponse
from services.documents import DocumentService

router = APIRouter(tags=["documents"])
_document_service = DocumentService()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(..., description="上传的文件"),
    session: AsyncSession = Depends(get_async_session),
) -> DocumentUploadResponse:
    """上传文档并执行 ETL 分块后写入数据库。"""
    return await _document_service.upload_document(file=file, session=session)


@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents(
    session: AsyncSession = Depends(get_async_session),
) -> list[DocumentInfo]:
    """列出已入库文档元数据。"""
    return await _document_service.list_documents(session=session)
