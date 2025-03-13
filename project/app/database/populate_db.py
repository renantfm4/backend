import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.database.database import SessionLocal 
from ..core.security import get_password_hash

# Importe os modelos definidos (User, Role, UnidadeSaude, Paciente, Atendimento, TermoConsentimento,
# SaudeGeral, AvaliacaoFototipo, RegistroLesoes, RegistroLesoesImagens, LocalLesao)
from .models import (
    User,
    Role,
    UnidadeSaude,
    Paciente,
    Atendimento,
    TermoConsentimento,
    SaudeGeral,
    AvaliacaoFototipo,
    HistoricoCancerPele,
    FatoresRiscoProtecao,
    InvestigacaoLesoesSuspeitas,
    RegistroLesoes,
    RegistroLesoesImagens,
    LocalLesao,
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
            fl_ativo=True
        )
        unidade2 = UnidadeSaude(
            nome_unidade_saude="Posto de Saúde do Norte",
            nome_localizacao="Avenida Brasil, 456 - Bairro Alto, Rio de Janeiro",
            codigo_unidade_saude="PSN002",
            cidade_unidade_saude="Rio de Janeiro",
            fl_ativo=True
        )
        unidade3 = UnidadeSaude(
            nome_unidade_saude="Clínica Vida",
            nome_localizacao="Travessa das Acácias, 789 - Zona Sul, Belo Horizonte",
            codigo_unidade_saude="CV003",
            cidade_unidade_saude="Belo Horizonte",
            fl_ativo=True
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
            fl_ativo=True,
            roles=[role_admin],
            unidadeSaude=[unidade1]
        )
        usuario2 = User(
            nome_usuario="supervisor_rj",
            email="sup.rj@exemplo.com",
            cpf="22222222222",
            senha_hash=get_password_hash("supervisor123"),
            fl_ativo=True,
            roles=[role_supervisor],
            unidadeSaude=[unidade2]
        )
        usuario3 = User(
            nome_usuario="pesq_sp",
            email="pesq.sp@exemplo.com",
            cpf="33333333333",
            senha_hash=get_password_hash("pesquisador123"),
            fl_ativo=True,
            roles=[role_pesquisador],
            unidadeSaude=[unidade1]
        )
        usuario4 = User(
            nome_usuario="pesq_bh",
            email="pesq.bh@exemplo.com",
            cpf="44444444444",
            senha_hash=get_password_hash("pesquisador123"),
            fl_ativo=True,
            roles=[role_pesquisador],
            unidadeSaude=[unidade3]
        )
        usuario5 = User(
            nome_usuario="supervisor_bh",
            email="sup.bh@exemplo.com",
            cpf="55555555555",
            senha_hash=get_password_hash("supervisor123"),
            fl_ativo=True,
            roles=[role_supervisor],
            unidadeSaude=[unidade3]
        )
        session.add_all([usuario1, usuario2, usuario3, usuario4, usuario5])
        await session.commit()

        usuarios = [usuario1, usuario2, usuario3, usuario4, usuario5]

        # 3. Criação dos locais de lesão
        local1 = LocalLesao(nome="Face")
        local2 = LocalLesao(nome="Tronco")
        local3 = LocalLesao(nome="Membros Superiores")
        local4 = LocalLesao(nome="Membros Inferiores")
        session.add_all([local1, local2, local3, local4])
        await session.commit()  # Insere os locais na tabela

        # Recupera os locais para uso na criação dos registros de lesão
        result = await session.execute(select(LocalLesao))
        locais_lesao = result.scalars().all()
        local_lesao_index = 0

        # Supondo que a lista de nomes dos pacientes já esteja definida
        nomes_pacientes = [
            "João da Silva", "Maria Souza", "Pedro Oliveira", "Ana Costa", 
            "Carlos Mendes", "Beatriz Rocha", "Rafael Lima", "Fernanda Dias", 
            "Lucas Pires", "Juliana Almeida"
        ]
        # Supondo que os usuários já foram criados e estão disponíveis
        result = await session.execute(select(User))
        usuarios = result.scalars().all()

        from datetime import date
        import random

        for i in range(10):
            # Cria um paciente
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
                cor_pele=4,              # valor válido conforme a restrição [0,2,4,8,12,16,20]
                cor_olhos=2,             # valor válido na lista [0,1,2,3,4]
                cor_cabelo=1,            # valor válido na lista [0,1,2,3,4]
                quantidade_sardas=1,     # valor válido na lista [0,1,2,3]
                reacao_sol=4,            # valor válido na lista [0,2,4,6,8]
                bronzeamento=2,          # valor válido na lista [0,2,4,6]
                sensibilidade_solar=1    # valor válido na lista [0,1,2,3,4]
            )
            session.add(avaliacao_fototipo)
            await session.commit()

            
            # Cria um objeto HistoricoCancerPele com valores fictícios
            tem_historico_familiar = random.choice([True, False])
            historico_cancer_pele = HistoricoCancerPele(
                historico_familiar=tem_historico_familiar,
                grau_parentesco=random.choice(['Pai', 'Mãe', 'Avô/Avó', 'Irmão/Irmã', 'Outro']) if tem_historico_familiar else None,
                tipo_cancer_familiar=random.choice(['Melanoma', 'Carcinoma Basocelular', 'Carcinoma Espinocelular', 'Outro']) if tem_historico_familiar else None,
                tipo_cancer_familiar_outro="Cancer de pele raro" if tem_historico_familiar and random.choice([True, False]) else None,
                
                diagnostico_pessoal=random.choice([True, False]),
                tipo_cancer_pessoal=random.choice(['Melanoma', 'Carcinoma Basocelular', 'Carcinoma Espinocelular', 'Outro']) if random.choice([True, False]) else None,
                tipo_cancer_pessoal_outro=None,
                
                lesoes_precancerigenas=random.choice([True, False]),
                tratamento_lesoes=random.choice([True, False]),
                tipo_tratamento=random.choice(['Cirurgia', 'Crioterapia', 'Radioterapia', 'Outro']) if random.choice([True, False]) else None,
                tipo_tratamento_outro=None
            )
            session.add(historico_cancer_pele)
            await session.commit()
            
            # Cria um objeto FatoresRiscoProtecao com valores fictícios
            exposicao_solar = random.choice([True, False])
            fatores_risco_protecao = FatoresRiscoProtecao(
                exposicao_solar_prolongada=exposicao_solar,
                frequencia_exposicao_solar=random.choice(['Diariamente', 'Algumas vezes por semana', 'Ocasionalmente']) if exposicao_solar else None,
                
                queimaduras_graves=random.choice([True, False]),
                quantidade_queimaduras=random.choice(['1-2', '3-5', 'Mais de 5']) if random.choice([True, False]) else None,
                
                uso_protetor_solar=random.choice([True, False]),
                fator_protecao_solar=random.choice(['15', '30', '50', '70', '100 ou mais']) if random.choice([True, False]) else None,
                
                uso_chapeu_roupa_protecao=random.choice([True, False]),
                
                bronzeamento_artificial=random.choice([True, False]),
                
                checkups_dermatologicos=random.choice([True, False]),
                frequencia_checkups=random.choice(['Anualmente', 'A cada 6 meses', 'Outro']) if random.choice([True, False]) else None,
                frequencia_checkups_outro=None,
                
                participacao_campanhas_prevencao=random.choice([True, False])
            )
            session.add(fatores_risco_protecao)
            await session.commit()
            
            # Cria um objeto InvestigacaoLesoesSuspeitas com valores fictícios
            investigacao_lesoes = InvestigacaoLesoesSuspeitas(
                mudanca_pintas_manchas=random.choice([True, False]),
                sintomas_lesoes=random.choice([True, False]),
                
                tempo_alteracoes=random.choice(['Menos de 1 mês', '1-3 meses', '3-6 meses', 'Mais de 6 meses']) if random.choice([True, False]) else None,
                
                caracteristicas_lesoes=random.choice([True, False]),
                
                consulta_medica=random.choice([True, False]),
                diagnostico_lesoes="Lesão benigna, apenas monitoramento recomendado" if random.choice([True, False]) else None
            )
            session.add(investigacao_lesoes)
            await session.commit()



            # Cria o atendimento relacionando os objetos acima
            atendimento = Atendimento(
                paciente_id=paciente.id,
                user_id=usuario_atendimento.id,
                termo_consentimento_id=termo.id,
                saude_geral_id=saude_geral.id,
                avaliacao_fototipo_id=avaliacao_fototipo.id,
                unidade_saude_id=usuario_atendimento.unidadeSaude[0].id
            )
            session.add(atendimento)
            await session.commit()

            # Para cada paciente, cria entre 0 e 3 registros de lesões (cada um com uma imagem associada)
            num_lesoes = i % 4  # varia de 0 a 3 de forma previsível
            for j in range(num_lesoes):
                # Seleciona um local para a lesão garantindo variedade
                local = locais_lesao[local_lesao_index % len(locais_lesao)]
                local_lesao_index += 1
                registro_lesao = RegistroLesoes(
                    local_lesao_id=local.id,  # Utiliza o id do local predefinido
                    descricao_lesao=f"Lesão observada na região {local.nome} com sinais de cicatrização.",
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
                