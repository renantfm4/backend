from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import io
from fastapi import UploadFile

processor = AutoImageProcessor.from_pretrained("Anwarkh1/Skin_Cancer-Image_Classification")
model = AutoModelForImageClassification.from_pretrained("Anwarkh1/Skin_Cancer-Image_Classification")

async def classificar_imagem_pele(file: UploadFile) -> str:
    try:
        conteudo = await file.read()
        imagem = Image.open(io.BytesIO(conteudo)).convert("RGB")
        imagem = imagem.resize((224, 224))
        inputs = processor(images=imagem, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()

        predicted_label = model.config.id2label[predicted_class_idx]

        return predicted_label
    except Exception as e:
        print(f"Erro ao classificar a imagem: {str(e)}")
        return "Erro ao classificar a imagem"
