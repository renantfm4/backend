from gradio_client import Client, handle_file
from tempfile import NamedTemporaryFile

client = Client("toilaluan/Image-Quality-Assessment")

async def verificar_qualidade_imagem(file_bytes: bytes) -> float:
    with NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(file_bytes)
        temp_path = temp.name

    try:
        result = client.predict(
            image=handle_file(temp_path),
            api_name="/predict"
        )

        # Se resultado for string numérica
        if isinstance(result, str):
            return float(result)
        # Se for dicionário
        elif isinstance(result, dict):
            return float(result.get("quality", 0))
        # Se for apenas número
        elif isinstance(result, (int, float)):
            return float(result)
        else:
            print("Formato inesperado do resultado:", result)
            return 0.0

    except Exception as e:
        print(f"Erro ao verificar qualidade da imagem: {e}")
        return 0.0
