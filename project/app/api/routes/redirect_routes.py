from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/redirect", response_class=HTMLResponse)
async def redirect_to_app(token: str, source: str):

    app_link = f"dermalert://{source}?token={token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Redirecionando para o aplicativo</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script>
                window.onload = function() {{
                    // Tentar abrir o app
                    window.location.href = "{app_link}";
                    
                    // Fallback após um delay caso o app não esteja instalado
                    setTimeout(function() {{
                        // Pode redirecionar para a App Store/Play Store ou página de download
                        // window.location.href = "https://play.google.com/store/apps/details?id=com.yourapp";
                    }}, 2000);
                }}
            </script>
        </head>
        <body>
            <div style="text-align: center; margin-top: 50px;">
                <h2>Redirecionando para o aplicativo DermAlert...</h2>
                <p>Se o redirecionamento não funcionar automaticamente, <a href="{app_link}">clique aqui</a>.</p>
            </div>
        </body>
    </html>
    """

    return html_content
