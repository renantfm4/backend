# DermAlert | Backend

A aplicação DermAlert é um aplicativo mobile multiplataforma desenvolvido com React Native, com suporte do Expo, Redux Toolkit para gerenciamento de estado global e React Navigation para navegação entre telas. O app tem como objetivo principal facilitar o registro, avaliação e acompanhamento clínico de pacientes com lesões dermatológicas, especialmente voltado para o apoio ao diagnóstico de câncer de pele.

## Documentação Técnica

Toda a documentação técnica do projeto está disponível na [GitHub Pages do projeto](https://www.dermalert.ai/land/dist/index.html).  

Lá você encontra:

- 📦 Como clonar e rodar o projeto localmente  
- 🚀 Guia de contribuição para colaboradores  
- 📡 Detalhamento das rotas da API backend  
- ⚙️ Estrutura e arquitetura da aplicação  
- 🧪 Boas práticas e padrões adotados  
- 📖 Outras informações técnicas relevantes

Acesse e contribua! 😉

## Como rodar a aplicação


1. Clonar o repositório:

```bash
git clone https://github.com/DermAlert/backend.git
```

Navegar até o diretório do projeto:

```bash
cd backend
```

2. Configurar as variáveis de ambiente:

Renomeie o arquivo .env.example para .env e ajuste os valores conforme as configurações do seu ambiente (podem ser valores aleatórios).

3. Construir e iniciar os contêineres Docker:

```bash
docker-compose up -d --build
```

Este comando irá construir as imagens necessárias e iniciar os serviços definidos no docker-compose.yml em segundo plano.

4. Crie o banco de dados:

Execute o seguinte comando para acessar o contêiner do banco de dados:

```bash
docker-compose exec db psql -U postgres
```

Depois, dentro do prompt do PostgreSQL:

```bash
CREATE DATABASE derma;
\q
```

5. Aplicar as migrações do banco de dados:

```bash
docker-compose exec web poetry run alembic upgrade head
```

Este comando executa as migrações pendentes, garantindo que o esquema do banco de dados esteja atualizado.


## Histórico de Versões

| Versão | Data | Descrição | Autor | Revisor |
| :----: | ---- | --------- | ----- | ------- |
| `1.0`  |10/04/2025| Adiciona descrição, link para gitpage e como rodar aplicação | Izabella Alves |  |