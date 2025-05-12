from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import io
import json
import os
from fastapi import UploadFile

# Carrega modelo
processor = AutoImageProcessor.from_pretrained("Anwarkh1/Skin_Cancer-Image_Classification")
model = AutoModelForImageClassification.from_pretrained("Anwarkh1/Skin_Cancer-Image_Classification")

# Carrega o JSON uma única vez
caminho_json = os.path.join(os.path.dirname(__file__), "data", "lesoes.json")
with open(caminho_json, "r", encoding="utf-8") as f:
    descricoes_lesoes = json.load(f)

async def classificar_imagem_pele(file_content: bytes) -> dict:
    try:
        imagem = Image.open(io.BytesIO(file_content)).convert("RGB")
        imagem = imagem.resize((224, 224))
        inputs = processor(images=imagem, return_tensors="pt", padding=True)

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()

        predicted_label = model.config.id2label[predicted_class_idx]

        # Busca no JSON
        info = descricoes_lesoes.get(predicted_label, {
            "nome": "Desconhecido",
            "descricao": "Não foi possível encontrar uma descrição para esta classificação."
        })

        return {
            "classe_original": predicted_label,
            "nome_traduzido": info["nome"],
            "descricao": info["descricao"]
        }
    except Exception as e:
        print(f"Erro ao classificar a imagem: {str(e)}")
        return {
            "classe_original": None,
            "nome_traduzido": "Erro",
            "descricao": "Erro ao classificar a imagem"
        }
