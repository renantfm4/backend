import torch
from torchvision import models, transforms
from PIL import Image
from fastapi import UploadFile
import io

# Carrega o modelo treinado no do arquivo .pt
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load("./data/skin_cancer_resnet18_version1.pt", map_location='cpu'))
model.eval()

# transformação da imagem
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

async def classificar_tipo_lesao(file: UploadFile) -> str:
    try:
        conteudo = await file.read()
        imagem = Image.open(io.BytesIO(conteudo)).convert("RGB")
        input_tensor = transform(imagem).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            pred = torch.argmax(output, dim=1).item()
        
        return "benigno" if pred == 0 else "maligno"
    
    except Exception as e:
        print(f"Erro ao classificar a imagem: {str(e)}")
        return "Erro ao classificar a imagem"