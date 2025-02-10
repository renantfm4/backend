import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database.database import SessionLocal 
from ..core.security import get_password_hash

# Importe os modelos definidos (User, Role, UnidadeSaude, Paciente, Atendimento, TermoConsentimento,
# SaudeGeral, AvaliacaoFototipo, RegistroLesoes, RegistroLesoesImagens)
from .models import (
    User,
    Role,
    UnidadeSaude,
    Paciente,
    Atendimento,
    TermoConsentimento,
    SaudeGeral,
    AvaliacaoFototipo,
    RegistroLesoes,
    RegistroLesoesImagens,
)


# Lista de possíveis locais para as lesões
LESOES_LOCAIS = ["Face", "Braço", "Perna", "Tronco", "Mão", "Pé"]

# Função auxiliar para gerar datas de nascimento aleatórias (entre 1950 e 2010)
def random_birthdate():
    start_date = date(1950, 1, 1)
    end_date = date(2010, 12, 31)
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)

# Função auxiliar para gerar valores válidos para AvaliacaoFototipo
def random_avaliacao_fototipo():
    return AvaliacaoFototipo(
        cor_pele=random.choice([0, 2, 4, 8, 12, 16, 20]),
        cor_olhos=random.choice([0, 1, 2, 3, 4]),
        cor_cabelo=random.choice([0, 1, 2, 3, 4]),
        quantidade_sardas=random.choice([0, 1, 2, 3]),
        reacao_sol=random.choice([0, 2, 4, 6, 8]),
        bronzeamento=random.choice([0, 2, 4, 6]),
        sensibilidade_solar=random.choice([0, 1, 2, 3, 4]),
    )

# Função auxiliar para gerar um registro de saúde geral
def random_saude_geral():
    return SaudeGeral(
        doencas_cronicas=random.choice([True, False]),
        hipertenso=random.choice([True, False]),
        diabetes=random.choice([True, False]),
        cardiopatia=random.choice([True, False]),
        outras_doencas="Hipertensão leve" if random.choice([True, False]) else None,
        diagnostico_cancer=random.choice([True, False]),
        tipo_cancer="Carcinoma basocelular" if random.choice([True, False]) else None,
        uso_medicamentos=random.choice([True, False]),
        medicamentos="Losartana 50mg" if random.choice([True, False]) else None,
        possui_alergia=random.choice([True, False]),
        alergias="Pólen" if random.choice([True, False]) else None,
        ciruturgias_dermatologicas=random.choice([True, False]),
        tipo_procedimento="Peeling químico" if random.choice([True, False]) else None,
        pratica_atividade_fisica=random.choice([True, False]),
        frequencia_atividade_fisica=random.choice(["Diária", "Frequente", "Moderada", "Ocasional"]),
    )


async def populate_db():
    async with SessionLocal() as session:

        # 1. Criação das unidades de saúde
        unidade1 = UnidadeSaude(
            nome_unidade_saude="Unidade de Saúde Central",
            nome_localizacao="Rua das Flores, 123 - Centro, São Paulo",
            codigo_unidade_saude="USC001",
            cidade_unidade_saude="São Paulo",
            is_active=True
        )
        unidade2 = UnidadeSaude(
            nome_unidade_saude="Posto de Saúde do Norte",
            nome_localizacao="Avenida Brasil, 456 - Bairro Alto, Rio de Janeiro",
            codigo_unidade_saude="PSN002",
            cidade_unidade_saude="Rio de Janeiro",
            is_active=True
        )
        unidade3 = UnidadeSaude(
            nome_unidade_saude="Clínica Vida",
            nome_localizacao="Travessa das Acácias, 789 - Zona Sul, Belo Horizonte",
            codigo_unidade_saude="CV003",
            cidade_unidade_saude="Belo Horizonte",
            is_active=True
        )
        session.add_all([unidade1, unidade2, unidade3])
        await session.commit()  # Para garantir que as unidades tenham um id

        # 2. Criação dos papéis (roles)
        role_admin = Role(name="Admin", nivel_acesso=3)
        role_supervisor = Role(name="Supervisor", nivel_acesso=2)
        role_pesquisador = Role(name="Pesquisador", nivel_acesso=1)
        session.add_all([role_admin, role_supervisor, role_pesquisador])
        await session.commit()  # Para garantir que os roles tenham um id

        # 3. Criação de usuários (pelo menos 5) e associação com uma unidade de saúde
        # Observação: cada usuário pode ter mais de um papel, mas neste exemplo cada um terá apenas 1.
        usuario1 = User(
            nome_usuario="admin_brasil",
            email="admin@exemplo.com",
            cpf="11111111111",
            senha_hash=get_password_hash("admin123"),
            is_active=True,
            roles=[role_admin],
            unidadeSaude=[unidade1]
        )
        usuario2 = User(
            nome_usuario="supervisor_rj",
            email="sup.rj@exemplo.com",
            cpf="22222222222",
            senha_hash=get_password_hash("supervisor123"),
            is_active=True,
            roles=[role_supervisor],
            unidadeSaude=[unidade2]
        )
        usuario3 = User(
            nome_usuario="pesq_sp",
            email="pesq.sp@exemplo.com",
            cpf="33333333333",
            senha_hash=get_password_hash("pesquisador123"),
            is_active=True,
            roles=[role_pesquisador],
            unidadeSaude=[unidade1]
        )
        usuario4 = User(
            nome_usuario="pesq_bh",
            email="pesq.bh@exemplo.com",
            cpf="44444444444",
            senha_hash=get_password_hash("pesquisador123"),
            is_active=True,
            roles=[role_pesquisador],
            unidadeSaude=[unidade3]
        )
        usuario5 = User(
            nome_usuario="supervisor_bh",
            email="sup.bh@exemplo.com",
            cpf="55555555555",
            senha_hash=get_password_hash("supervisor123"),
            is_active=True,
            roles=[role_supervisor],
            unidadeSaude=[unidade3]
        )
        session.add_all([usuario1, usuario2, usuario3, usuario4, usuario5])
        await session.commit()

        usuarios = [usuario1, usuario2, usuario3, usuario4, usuario5]

        # 4. Criação de 10 pacientes e seus atendimentos com registro de lesões e imagens
        nomes_pacientes = [
            "Ana Silva", "Bruno Souza", "Carla Pereira", "Daniel Oliveira", "Elisa Costa",
            "Fernando Almeida", "Gabriela Martins", "Henrique Rodrigues", "Isabela Gomes", "João Lima"
        ]
        # Lista de locais para lesões (será utilizada sequencialmente)
        locais_lesao = [
            "Braço esquerdo", "Face", "Perna direita", "Costas", "Mão direita",
            "Abdômen", "Pescoço", "Ombro", "Joelho", "Tornozelo"
        ]
        local_lesao_index = 0

        for i in range(10):
            # Criar paciente
            paciente = Paciente(
                nome_paciente=nomes_pacientes[i],
                data_nascimento=date(1980 + i, (i % 12) + 1, (i % 28) + 1),
                sexo=random.choice(["M", "F", "NB", "NR", "O"]),
                sexo_outro="",
                cpf_paciente=f"{11111111111 + i:011d}",
                num_cartao_sus=f"{100000000000000 + i}",
                endereco_paciente=f"Rua Exemplo, {100 + i} - Bairro Exemplo, Cidade Exemplo",
                telefone_paciente=f"1198765432{i}",
                email_paciente=f"{nomes_pacientes[i].split()[0].lower()}@exemplo.com",
                autoriza_pesquisa=True
            )
            session.add(paciente)
            await session.commit()  # Para obter o id do paciente

            # Seleciona um usuário para o atendimento (de forma cíclica)
            usuario_atendimento = usuarios[i % len(usuarios)]
            # Cria um TermoConsentimento
            termo = TermoConsentimento(
                arquivo_url=f"http://exemplo.com/consentimento_{i+1}.pdf"
            )
            session.add(termo)
            await session.commit()

            # Cria um objeto SaudeGeral com dados fictícios
            saude_geral = SaudeGeral(
                doencas_cronicas=random.choice([True, False]),
                hipertenso=random.choice([True, False]),
                diabetes=random.choice([True, False]),
                cardiopatia=random.choice([True, False]),
                outras_doencas="Nenhuma",
                diagnostico_cancer=random.choice([True, False]),
                tipo_cancer="",
                uso_medicamentos=random.choice([True, False]),
                medicamentos="Nenhum",
                possui_alergia=random.choice([True, False]),
                alergias="Nenhuma",
                ciruturgias_dermatologicas=random.choice([True, False]),
                tipo_procedimento="",
                pratica_atividade_fisica=random.choice([True, False]),
                frequencia_atividade_fisica=random.choice(["Diária", "Frequente", "Moderada", "Ocasional"])
            )
            session.add(saude_geral)
            await session.commit()

            # Cria um objeto AvaliacaoFototipo com valores válidos conforme as restrições
            avaliacao_fototipo = AvaliacaoFototipo(
                cor_pele=4,              # (por exemplo, 4 está na lista [0,2,4,8,12,16,20])
                cor_olhos=2,             # (na lista [0,1,2,3,4])
                cor_cabelo=1,            # (na lista [0,1,2,3,4])
                quantidade_sardas=1,     # (na lista [0,1,2,3])
                reacao_sol=4,            # (na lista [0,2,4,6,8])
                bronzeamento=2,          # (na lista [0,2,4,6])
                sensibilidade_solar=1    # (na lista [0,1,2,3,4])
            )
            session.add(avaliacao_fototipo)
            await session.commit()

            # Cria o atendimento relacionando os objetos acima
            atendimento = Atendimento(
                paciente_id=paciente.id,
                user_id=usuario_atendimento.id,
                termo_consentimento_id=termo.id,
                saude_geral_id=saude_geral.id,
                avaliacao_fototipo_id=avaliacao_fototipo.id
                # data_atendimento é gerado automaticamente
            )
            session.add(atendimento)
            await session.commit()

            # Para cada paciente, cria entre 0 e 3 registros de lesões (cada um com uma imagem associada)
            num_lesoes = i % 4  # varia de 0 a 3 de forma previsível
            for j in range(num_lesoes):
                # Seleciona um local para a lesão (garante variedade)
                local = locais_lesao[local_lesao_index % len(locais_lesao)]
                local_lesao_index += 1
                registro_lesao = RegistroLesoes(
                    local_lesao=local,
                    descricao_lesao=f"Lesão observada no {local.lower()} com sinais de cicatrização.",
                    atendimento_id=atendimento.id
                )
                session.add(registro_lesao)
                await session.commit()

                # Cria uma imagem associada a este registro de lesão
                imagem = RegistroLesoesImagens(
                    arquivo_url=f"http://exemplo.com/imagens/lesao_{paciente.id}_{j+1}.jpg",
                    registro_lesoes_id=registro_lesao.id
                )
                session.add(imagem)
                await session.commit()