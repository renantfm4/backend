import torch
import numpy as np
from PIL import Image, UnidentifiedImageError
from piq import brisque
import io


def avaliar_qualidade_imagem(image_data: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        img_array = np.array(img).astype(np.float32) / 255.0
        
        img_tensor = torch.tensor(img_array).permute(2, 0, 1).unsqueeze(0)
        
        if img_tensor.shape[2] < 50 or img_tensor.shape[3] < 50:
            return {
                "erro": "A imagem é muito pequena para avaliação de qualidade.",
                "score": None,
                "qualidade": "erro"
            }

        brisque_score = brisque(img_tensor).item()

        if brisque_score < 25:
            qualidade = "boa"
        elif 20 <= brisque_score < 50:
            qualidade = "ruim"
        else:
            qualidade = "péssima"

        return {
            "score": round(brisque_score, 2),
            "qualidade": qualidade
        }
    except UnidentifiedImageError:
        return {
            "erro": "A imagem fornecida está corrompida ou em formato inválido.",
            "score": None,
            "qualidade": "erro"
        }
    except Exception as e:
        return {
            "erro": str(e),
            "score": None,
            "qualidade": "erro"
        }
