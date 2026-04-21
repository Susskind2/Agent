"""Service layer for document upload and listing."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import DeepAgentSettings, get_settings
from etl import ETLPipeline
from infrastructure.database.models import Document, DocumentChunk
from infrastructure.vectordb.milvus_client import MilvusManager
from models.schemas import DocumentInfo, DocumentUploadResponse
from rag.embeddings import get_embedding_model


class DocumentService:
    """Coordinate ETL, persistence, and vector ingestion for uploaded documents."""

    def __init__(self, settings: DeepAgentSettings | None = None) -> None:
        self.settings = settings or get_settings()

    async def upload_document(
        self,
        *,
        file: UploadFile,
        session: AsyncSession,
    ) -> DocumentUploadResponse:
        """Persist an uploaded file, run ETL, and write chunks/vector metadata."""
        upload_root = Path("uploads")
        upload_root.mkdir(parents=True, exist_ok=True)

        doc_id = str(uuid.uuid4())
        safe_name = file.filename or "unnamed"
        destination = upload_root / f"{doc_id}_{safe_name}"

        try:
            raw = await file.read()
            await asyncio.to_thread(destination.write_bytes, raw)
        except Exception as exc:
            logger.exception("保存上传文件失败: {}", exc)
            raise HTTPException(status_code=500, detail=f"保存文件失败: {exc!s}") from exc

        pipeline = ETLPipeline()
        try:
            etl = await pipeline.run_bytes(raw, filename=safe_name, mime_type=file.content_type)
        except Exception as exc:
            logger.exception("ETL 失败: {}", exc)
            raise HTTPException(status_code=422, detail=f"文档解析失败: {exc!s}") from exc

        document = Document(
            id=doc_id,
            filename=safe_name,
            mime_type=file.content_type,
            storage_path=str(destination),
            status="ready",
            meta={"chunk_count": len(etl.chunks)},
        )
        session.add(document)

        chunk_rows: list[DocumentChunk] = []
        for index, chunk_text in enumerate(etl.chunks):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                chunk_index=index,
                content=chunk_text[:65000],
                vector_id=None,
                meta=None,
            )
            session.add(chunk)
            chunk_rows.append(chunk)

        try:
            await self._ingest_vectors(doc_id=doc_id, chunks=chunk_rows, chunk_texts=etl.chunks)
        except Exception as exc:
            # ETL text is still useful even when embeddings or Milvus are temporarily unavailable.
            logger.warning("向量入库失败，继续保留文本分块结果: {}", exc)
            document.status = "ready_partial"
            document.meta = {**(document.meta or {}), "vector_error": str(exc)}

        await session.commit()
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=safe_name,
            status=document.status,
            chunk_count=len(etl.chunks),
            message="上传成功，文本分块已入库；若 Milvus 可用则已完成向量化",
        )

    async def list_documents(self, *, session: AsyncSession) -> list[DocumentInfo]:
        """List uploaded document metadata from the database."""
        try:
            result = await session.execute(select(Document).order_by(Document.created_at.desc()))
            rows = result.scalars().all()
            return [
                DocumentInfo(
                    id=document.id,
                    filename=document.filename,
                    mime_type=document.mime_type,
                    status=document.status,
                    created_at=document.created_at.isoformat() if document.created_at else None,
                )
                for document in rows
            ]
        except Exception as exc:
            logger.exception("查询文档列表失败: {}", exc)
            raise HTTPException(status_code=500, detail=f"查询失败: {exc!s}") from exc

    async def _ingest_vectors(
        self,
        *,
        doc_id: str,
        chunks: list[DocumentChunk],
        chunk_texts: list[str],
    ) -> None:
        """Write document chunk vectors into Milvus when embeddings are available."""
        if not chunk_texts:
            return

        embedder = get_embedding_model(self.settings.embedding_model_name)
        vectors = await asyncio.to_thread(embedder.embed_documents, chunk_texts)
        if not vectors:
            return

        milvus = MilvusManager(
            host=self.settings.milvus_host,
            port=str(self.settings.milvus_port),
            user=self.settings.milvus_user or None,
            password=self.settings.milvus_password or None,
        )
        await milvus.create_collection(self.settings.milvus_collection_name, dim=len(vectors[0]))
        metadata = [
            {
                "id": chunk.id,
                "text": chunk.content,
                "document_id": doc_id,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]
        vector_ids = await milvus.insert(self.settings.milvus_collection_name, vectors, metadata)
        for chunk, vector_id in zip(chunks, vector_ids):
            chunk.vector_id = vector_id
