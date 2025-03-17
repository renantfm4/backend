from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...database.database import get_db
from ...core.hierarchy import require_role, RoleEnum
from ...database import models
from ...database.schemas import PacienteCreateSchema, TermoConsentimentoCreateSchema, SaudeGeralCreateSchema, AvaliacaoFototipoCreateSchema, RegistroLesoesCreateSchema, RegistroLesoesCreateSchema, LocalLesaoSchema, HistoricoCancerPeleCreateSchema, FatoresRiscoProtecaoCreateSchema, InvestigacaoLesoesSuspeitasCreateSchema, InformacoesCompletasCreateSchema
from ...utils.minio import upload_to_minio

router = APIRouter()

@router.post("/cadastrar-paciente", status_code=201)
async def cadastrar_paciente(
    paciente_data: PacienteCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    # Check if patient already exists
    stmt = select(models.Paciente).filter(models.Paciente.cpf_paciente == paciente_data.cpf_paciente)
    result = await db.execute(stmt)
    existing_paciente = result.scalars().first()

    if existing_paciente:
        raise HTTPException(status_code=400, detail="Paciente já cadastrado")

    # Create new patient
    new_paciente = models.Paciente(
        nome_paciente=paciente_data.nome_paciente,
        data_nascimento=paciente_data.data_nascimento,
        sexo=paciente_data.sexo,
        sexo_outro=paciente_data.sexo_outro,
        cpf_paciente=paciente_data.cpf_paciente,
        num_cartao_sus=paciente_data.num_cartao_sus,
        endereco_paciente=paciente_data.endereco_paciente,
        telefone_paciente=paciente_data.telefone_paciente,
        email_paciente=paciente_data.email_paciente,
        autoriza_pesquisa=paciente_data.autoriza_pesquisa,
        id_usuario_criacao=current_user.id
    )
    
    db.add(new_paciente)
    await db.commit()
    await db.refresh(new_paciente)
    
    return {
        "id": new_paciente.id,
        "nome_paciente": new_paciente.nome_paciente,
        "data_nascimento": new_paciente.data_nascimento,
        "sexo": new_paciente.sexo,
        "sexo_outro": new_paciente.sexo_outro,
        "cpf_paciente": new_paciente.cpf_paciente,
        "num_cartao_sus": new_paciente.num_cartao_sus,
        "endereco_paciente": new_paciente.endereco_paciente,
        "telefone_paciente": new_paciente.telefone_paciente,
        "email_paciente": new_paciente.email_paciente,
        "autoriza_pesquisa": new_paciente.autoriza_pesquisa
    }

@router.post("/cadastrar-atendimento", status_code=201)
async def cadastrar_atendimento(
    paciente_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    stmt = select(models.Paciente).filter(models.Paciente.id == paciente_id)
    result = await db.execute(stmt)
    paciente = result.scalars().first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    stmt_unidade = select(models.UnidadeSaude).join(models.User.unidadeSaude).filter(
        models.User.id == current_user.id
    )
    result_unidade = await db.execute(stmt_unidade)
    unidade_saude = result_unidade.scalars().first()

    if not unidade_saude:
        raise HTTPException(status_code=403, detail="Usuário não está associado a nenhuma unidade de saúde")

    new_atendimento = models.Atendimento(
        paciente_id=paciente_id,
        user_id=current_user.id,
        unidade_saude_id=unidade_saude.id,
        id_usuario_criacao=current_user.id
    )

    db.add(new_atendimento)
    await db.commit()
    await db.refresh(new_atendimento)

    return {
        "id": new_atendimento.id,
        "paciente_id": paciente.id,
        "nome_paciente": paciente.nome_paciente,
        "cpf_paciente": paciente.cpf_paciente,
        "data_atendimento": new_atendimento.data_atendimento,
        "unidade_saude_id": unidade_saude.id,
        "unidade_saude_nome": unidade_saude.nome_unidade_saude
    }


@router.get("/cadastrar-atendimento")
async def get_paciente_by_cpf(
    cpf_paciente: str = Query(..., description="CPF do paciente"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    stmt = select(models.Paciente).filter(models.Paciente.cpf_paciente == cpf_paciente)
    result = await db.execute(stmt)
    paciente = result.scalars().first()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    return {
        "id": paciente.id,
        "nome_paciente": paciente.nome_paciente,
        "cpf_paciente": paciente.cpf_paciente,
        "data_nascimento": paciente.data_nascimento,
        "sexo": paciente.sexo,
        "sexo_outro": paciente.sexo_outro,
        "num_cartao_sus": paciente.num_cartao_sus,
        "endereco_paciente": paciente.endereco_paciente,
        "telefone_paciente": paciente.telefone_paciente,
        "email_paciente": paciente.email_paciente,
        "autoriza_pesquisa": paciente.autoriza_pesquisa
    }



@router.post("/cadastrar-termo-consentimento") 
async def cadastrar_termo_consentimento( 
    atendimento_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):

    # Verifica se o atendimento existe
    stmt = select(models.Atendimento).filter(models.Atendimento.id == atendimento_id)
    result = await db.execute(stmt)
    atendimento = result.scalars().first()

    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    
    if atendimento.termo_consentimento_id:
        raise HTTPException(status_code=400, detail="Atendimento já possui um termo de consentimento")

    arquivo_metadata = await upload_to_minio(file, folder_name="termos-consentimento")

    new_termo = models.TermoConsentimento(
        arquivo_url=arquivo_metadata["url"],
    )

    db.add(new_termo)
    await db.commit()
    await db.refresh(new_termo)

    # Associa o termo ao atendimento
    atendimento.termo_consentimento_id = new_termo.id
    await db.commit()
    await db.refresh(atendimento)

    return {
        "message": "Termo de Consentimento cadastrado com sucesso!",
        "termo_consentimento": {
            "id": new_termo.id,
            "arquivo_url": arquivo_metadata["url"]
        }
    }

@router.post("/cadastrar-informacoes-completas")
async def cadastrar_informacoes_completas(
    dados: InformacoesCompletasCreateSchema,
    atendimento_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    # 1. Buscar o atendimento
    stmt = select(models.Atendimento).filter(models.Atendimento.id == atendimento_id)
    result = await db.execute(stmt)
    atendimento = result.scalars().first()
    
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")

    # Para armazenar no final quais registros foram criados
    saude_geral_criado = None
    fototipo_criado = None
    historico_cancer_criado = None
    fatores_risco_criado = None
    investigacao_lesoes_criada = None

    # 2. Se vier "saude_geral" no payload, faz a criação:
    if dados.saude_geral:
        if atendimento.saude_geral_id:
            raise HTTPException(status_code=400, detail="Atendimento já possui informações de Saúde Geral")
        
        new_saude_geral = models.SaudeGeral(
            doencas_cronicas=dados.saude_geral.doencas_cronicas,
            hipertenso=dados.saude_geral.hipertenso,
            diabetes=dados.saude_geral.diabetes,
            cardiopatia=dados.saude_geral.cardiopatia,
            outras_doencas=dados.saude_geral.outras_doencas,
            diagnostico_cancer=dados.saude_geral.diagnostico_cancer,
            tipo_cancer=dados.saude_geral.tipo_cancer,
            uso_medicamentos=dados.saude_geral.uso_medicamentos,
            medicamentos=dados.saude_geral.medicamentos,
            possui_alergia=dados.saude_geral.possui_alergia,
            alergias=dados.saude_geral.alergias,
            ciruturgias_dermatologicas=dados.saude_geral.ciruturgias_dermatologicas,
            tipo_procedimento=dados.saude_geral.tipo_procedimento,
            pratica_atividade_fisica=dados.saude_geral.pratica_atividade_fisica,
            frequencia_atividade_fisica=dados.saude_geral.frequencia_atividade_fisica
        )
        db.add(new_saude_geral)
        await db.commit()
        await db.refresh(new_saude_geral)

        atendimento.saude_geral_id = new_saude_geral.id
        saude_geral_criado = new_saude_geral

    # 3. Avaliação de fototipo
    if dados.avaliacao_fototipo:
        # Validar os campos
        valid_cor_pele = [0, 2, 4, 8, 12, 16, 20]
        valid_cor_olhos = [0, 1, 2, 3, 4]
        valid_cor_cabelo = [0, 1, 2, 3, 4]
        valid_quantidade_sardas = [0, 1, 2, 3]
        valid_reacao_sol = [0, 2, 4, 6, 8]
        valid_bronzeamento = [0, 2, 4, 6]
        valid_sensibilidade_solar = [0, 1, 2, 3, 4]

        if dados.avaliacao_fototipo.cor_pele not in valid_cor_pele:
            raise HTTPException(status_code=400, detail="Valor inválido para cor_pele")
        if dados.avaliacao_fototipo.cor_olhos not in valid_cor_olhos:
            raise HTTPException(status_code=400, detail="Valor inválido para cor_olhos")
        if dados.avaliacao_fototipo.cor_cabelo not in valid_cor_cabelo:
            raise HTTPException(status_code=400, detail="Valor inválido para cor_cabelo")
        if dados.avaliacao_fototipo.quantidade_sardas not in valid_quantidade_sardas:
            raise HTTPException(status_code=400, detail="Valor inválido para quantidade_sardas")
        if dados.avaliacao_fototipo.reacao_sol not in valid_reacao_sol:
            raise HTTPException(status_code=400, detail="Valor inválido para reacao_sol")
        if dados.avaliacao_fototipo.bronzeamento not in valid_bronzeamento:
            raise HTTPException(status_code=400, detail="Valor inválido para bronzeamento")
        if dados.avaliacao_fototipo.sensibilidade_solar not in valid_sensibilidade_solar:
            raise HTTPException(status_code=400, detail="Valor inválido para sensibilidade_solar")

        if atendimento.avaliacao_fototipo_id:
            raise HTTPException(status_code=400, detail="Atendimento já possui avaliação de fototipo")

        new_fototipo = models.AvaliacaoFototipo(
            cor_pele=dados.avaliacao_fototipo.cor_pele,
            cor_olhos=dados.avaliacao_fototipo.cor_olhos,
            cor_cabelo=dados.avaliacao_fototipo.cor_cabelo,
            quantidade_sardas=dados.avaliacao_fototipo.quantidade_sardas,
            reacao_sol=dados.avaliacao_fototipo.reacao_sol,
            bronzeamento=dados.avaliacao_fototipo.bronzeamento,
            sensibilidade_solar=dados.avaliacao_fototipo.sensibilidade_solar
        )
        db.add(new_fototipo)
        await db.commit()
        await db.refresh(new_fototipo)

        atendimento.avaliacao_fototipo_id = new_fototipo.id
        fototipo_criado = new_fototipo

    # 4. Histórico de câncer de pele
    if dados.historico_cancer_pele:
        if atendimento.historico_cancer_pele_id:
            raise HTTPException(status_code=400, detail="Atendimento já possui histórico de câncer de pele")

        new_historico = models.HistoricoCancerPele(
            historico_familiar=dados.historico_cancer_pele.historico_familiar,
            grau_parentesco=dados.historico_cancer_pele.grau_parentesco,
            tipo_cancer_familiar=dados.historico_cancer_pele.tipo_cancer_familiar,
            tipo_cancer_familiar_outro=dados.historico_cancer_pele.tipo_cancer_familiar_outro,
            diagnostico_pessoal=dados.historico_cancer_pele.diagnostico_pessoal,
            tipo_cancer_pessoal=dados.historico_cancer_pele.tipo_cancer_pessoal,
            tipo_cancer_pessoal_outro=dados.historico_cancer_pele.tipo_cancer_pessoal_outro,
            lesoes_precancerigenas=dados.historico_cancer_pele.lesoes_precancerigenas,
            tratamento_lesoes=dados.historico_cancer_pele.tratamento_lesoes,
            tipo_tratamento=dados.historico_cancer_pele.tipo_tratamento,
            tipo_tratamento_outro=dados.historico_cancer_pele.tipo_tratamento_outro
        )
        db.add(new_historico)
        await db.commit()
        await db.refresh(new_historico)

        atendimento.historico_cancer_pele_id = new_historico.id
        historico_cancer_criado = new_historico

    # 5. Fatores de risco e proteção
    if dados.fatores_risco_protecao:
        if atendimento.fatores_risco_protecao_id:
            raise HTTPException(status_code=400, detail="Atendimento já possui fatores de risco e proteção")

        new_fatores = models.FatoresRiscoProtecao(
            exposicao_solar_prolongada=dados.fatores_risco_protecao.exposicao_solar_prolongada,
            frequencia_exposicao_solar=dados.fatores_risco_protecao.frequencia_exposicao_solar,
            queimaduras_graves=dados.fatores_risco_protecao.queimaduras_graves,
            quantidade_queimaduras=dados.fatores_risco_protecao.quantidade_queimaduras,
            uso_protetor_solar=dados.fatores_risco_protecao.uso_protetor_solar,
            fator_protecao_solar=dados.fatores_risco_protecao.fator_protecao_solar,
            uso_chapeu_roupa_protecao=dados.fatores_risco_protecao.uso_chapeu_roupa_protecao,
            bronzeamento_artificial=dados.fatores_risco_protecao.bronzeamento_artificial,
            checkups_dermatologicos=dados.fatores_risco_protecao.checkups_dermatologicos,
            frequencia_checkups=dados.fatores_risco_protecao.frequencia_checkups,
            participacao_campanhas_prevencao=dados.fatores_risco_protecao.participacao_campanhas_prevencao
        )
        db.add(new_fatores)
        await db.commit()
        await db.refresh(new_fatores)

        atendimento.fatores_risco_protecao_id = new_fatores.id
        fatores_risco_criado = new_fatores

    # 6. Investigação de lesões suspeitas
    if dados.investigacao_lesoes_suspeitas:
        if atendimento.investigacao_lesoes_suspeitas_id:
            raise HTTPException(status_code=400, detail="Atendimento já possui investigação de lesões suspeitas")

        new_investigacao = models.InvestigacaoLesoesSuspeitas(
            mudanca_pintas_manchas=dados.investigacao_lesoes_suspeitas.mudanca_pintas_manchas,
            sintomas_lesoes=dados.investigacao_lesoes_suspeitas.sintomas_lesoes,
            tempo_alteracoes=dados.investigacao_lesoes_suspeitas.tempo_alteracoes,
            caracteristicas_lesoes=dados.investigacao_lesoes_suspeitas.caracteristicas_lesoes,
            consulta_medica=dados.investigacao_lesoes_suspeitas.consulta_medica,
            diagnostico_lesoes=dados.investigacao_lesoes_suspeitas.diagnostico_lesoes
        )
        db.add(new_investigacao)
        await db.commit()
        await db.refresh(new_investigacao)

        atendimento.investigacao_lesoes_suspeitas_id = new_investigacao.id
        investigacao_lesoes_criada = new_investigacao

    # Salvar as associações do atendimento de forma final
    await db.commit()
    await db.refresh(atendimento)

    return {
        "message": "Informações cadastradas com sucesso!",
        "saude_geral": saude_geral_criado,
        "avaliacao_fototipo": fototipo_criado,
        "historico_cancer_pele": historico_cancer_criado,
        "fatores_risco_protecao": fatores_risco_criado,
        "investigacao_lesoes_suspeitas": investigacao_lesoes_criada
    }



@router.get("/listar-atendimentos-usuario-logado")
async def listar_atendimentos_usuario_logado(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):

    stmt = (
        select(models.Atendimento, models.Paciente.nome_paciente, models.Paciente.cpf_paciente)
        .join(models.Paciente, models.Atendimento.paciente_id == models.Paciente.id)
        .filter(models.Atendimento.user_id == current_user.id)
    )
    
    result = await db.execute(stmt)
    atendimentos = result.all()

    if not atendimentos:
        raise HTTPException(status_code=404, detail="Nenhum atendimento encontrado para este usuário.")

    atendimentos_list = [
        {
            "id": atendimento.Atendimento.id,
            "data_atendimento": atendimento.Atendimento.data_atendimento,
            "paciente_id": atendimento.Atendimento.paciente_id,
            "nome_paciente": atendimento.nome_paciente,
            "cpf_paciente": atendimento.cpf_paciente,
            "termo_consentimento_id": atendimento.Atendimento.termo_consentimento_id,
            "saude_geral_id": atendimento.Atendimento.saude_geral_id,
            "avaliacao_fototipo_id": atendimento.Atendimento.avaliacao_fototipo_id
        }
        for atendimento in atendimentos
    ]

    return atendimentos_list

@router.post("/cadastrar-lesao")
async def cadastrar_lesao(
    atendimento_id: int = Form(...),
    local_lesao_id: int = Form(...),
    descricao_lesao: str = Form(...),
    files: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    # Verify atendimento exists
    stmt = select(models.Atendimento).filter(models.Atendimento.id == atendimento_id)
    result = await db.execute(stmt)
    atendimento = result.scalars().first()

    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    
    # Verify local_lesao_id exists
    stmt_local = select(models.LocalLesao).filter(models.LocalLesao.id == local_lesao_id)
    result_local = await db.execute(stmt_local)
    local_lesao = result_local.scalar_one_or_none()
    
    if not local_lesao:
        raise HTTPException(status_code=404, detail="Local de lesão não encontrado")

    # Create new lesion with foreign key to LocalLesao
    new_lesao = models.RegistroLesoes(
        local_lesao_id=local_lesao_id,
        descricao_lesao=descricao_lesao,
        atendimento_id=atendimento.id
    )
    db.add(new_lesao)
    await db.commit()
    await db.refresh(new_lesao)

    imagens_urls = []
    if files:      
        for file in files:
            try:
                # Upload da imagem para o MinIO
                arquivo_metadata = await upload_to_minio(file, folder_name="imagens-lesoes")
                imagens_urls.append(arquivo_metadata["url"])

                # Cria o registro da imagem no banco
                new_imagem = models.RegistroLesoesImagens(
                    arquivo_url=arquivo_metadata["url"],  # Just use the URL string, not the entire dict
                    registro_lesoes_id=new_lesao.id
                )
                db.add(new_imagem)
            except Exception as e:
                # Log the error but continue with other files
                print(f"Erro ao fazer upload da imagem {file.filename}: {str(e)}")
                continue
                
        await db.commit()

    return {
        "message": "Lesão e imagens cadastradas com sucesso!",
        "lesao": {
            "id": new_lesao.id,
            "local_lesao_id": new_lesao.local_lesao_id,
            "local_lesao_nome": local_lesao.nome,
            "descricao_lesao": new_lesao.descricao_lesao,
        },
        "imagens": imagens_urls
    }


@router.get("/listar-lesoes/{atendimento_id}")
async def listar_lesoes(
    atendimento_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.PESQUISADOR))
):
    stmt = (
        select(models.RegistroLesoes)
        .filter(models.RegistroLesoes.atendimento_id == atendimento_id)
    )
    result = await db.execute(stmt)
    lesoes = result.scalars().all()

    if not lesoes:
        raise HTTPException(status_code=404, detail="Nenhuma lesão encontrada para este atendimento.")

    lesoes_list = []

    for lesao in lesoes:
        # Obtendo imagens associadas à lesão
        stmt_imagens = (
            select(models.RegistroLesoesImagens)
            .filter(models.RegistroLesoesImagens.registro_lesoes_id == lesao.id)
        )
        result_imagens = await db.execute(stmt_imagens)
        imagens = result_imagens.scalars().all()
        
        # Get local lesao name if available
        local_lesao_name = None
        if lesao.local_lesao_id:
            stmt_local = select(models.LocalLesao).filter(models.LocalLesao.id == lesao.local_lesao_id)
            result_local = await db.execute(stmt_local)
            local_obj = result_local.scalar_one_or_none()
            if local_obj:
                local_lesao_name = local_obj.nome

        lesoes_list.append({
            "id": lesao.id,
            "local_lesao_id": lesao.local_lesao_id,
            "local_lesao_nome": local_lesao_name,
            "descricao_lesao": lesao.descricao_lesao,
            "imagens": [imagem.arquivo_url for imagem in imagens]
        })

    return lesoes_list

@router.get("/locais-lesao", response_model=List[LocalLesaoSchema])
async def get_locais_lesao(db: AsyncSession = Depends(get_db)):
    stmt = select(models.LocalLesao)
    result = await db.execute(stmt)
    locais = result.scalars().all()
    return locais
