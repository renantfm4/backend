import torch
from torchvision import transforms, models
from PIL import Image
from fastapi import UploadFile
import io

# Carrega o modelo completo salvo com torch.save(model)
model = models.resnet18(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, 2)

model.load_state_dict(
    torch.load("app/utils/data/skin_cancer_resnet18_version1.pt", map_location="cpu")
)
model.eval()

# transformação da imagem
transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])


async def classificar_tipo_lesao(file_content: bytes) -> str:
    try:
        imagem = Image.open(io.BytesIO(file_content)).convert("RGB")
        input_tensor = transform(imagem).unsqueeze(0)

        with torch.no_grad():
            output = model(input_tensor)
            pred = torch.argmax(output, dim=1).item()

        return "benigno" if pred == 0 else "maligno"

    except Exception as e:
        print(f"Erro ao classificar a imagem: {str(e)}")
        return "Erro ao classificar a imagem"
