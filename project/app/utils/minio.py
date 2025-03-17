import os
import io
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
import minio
from minio import Minio
from minio.error import S3Error

def get_minio_client():
    try:
        endpoint = os.getenv("MINIO_ENDPOINT")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")
        minio_secure = os.getenv("MINIO_SECURE") == 'True'
            
        return Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=minio_secure
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao MinIO: {str(e)}")

async def upload_to_minio(file, folder_name, allowed_types=None, max_size_mb=50):
    try:
        minio_bucket = os.getenv("MINIO_BUCKET")
        client = get_minio_client()
        
        # Validação de tipo de arquivo
        if allowed_types and file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não permitido. Tipos aceitos: {', '.join(allowed_types)}"
            )
        
        # Lendo os dados do arquivo
        file_data = await file.read()
        file_size = len(file_data)
        
        # Validação de tamanho
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Tamanho máximo: {max_size_mb}MB"
            )
        
        # Verifica se o bucket existe, caso contrário cria
        if not client.bucket_exists(minio_bucket):
            client.make_bucket(minio_bucket)
            # Configurar políticas do bucket se necessário
        
        # Gera um nome único para o objeto usando UUID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        file_extension = os.path.splitext(file.filename)[1]
        object_name = f"{folder_name}/{folder_name}_{timestamp}_{unique_id}{file_extension}"
        
        # Upload para o MinIO
        client.put_object(
            bucket_name=minio_bucket,
            object_name=object_name,
            data=io.BytesIO(file_data),
            length=file_size,
            content_type=file.content_type
        )
        
        # Gera URL assinada para acesso temporário (7 dias)
        url = client.presigned_get_object(
            bucket_name=minio_bucket, 
            object_name=object_name,
            expires=timedelta(days=7)
        )
        
        # Reposiciona o ponteiro do arquivo para o início (caso precise usar novamente)
        await file.seek(0)
            
        return {
            "url": url,
            "object_name": object_name,
            "bucket": minio_bucket,
            "content_type": file.content_type,
            "size": file_size
        }
    
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no MinIO: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload: {str(e)}")