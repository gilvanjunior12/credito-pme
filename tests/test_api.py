# -----------------------------------------------------------------------------
# Arquivo de testes com pytest
# Objetivo: validar os endpoints principais da API de Crédito PME.
# -----------------------------------------------------------------------------

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    # Verifica se a rota raiz responde corretamente
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("mensagem") == "API de Crédito PME rodando!"

def test_healthz():
    # Verifica se o healthcheck retorna 200 e o JSON esperado
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_score_ok_mensal():
    # Teste de cálculo de score com faturamento mensal informado
    body = {
        "cnpj": "00.000.000/0001-00",
        "faturamento_mensal": 15000,
        "tempo_atividade_meses": 18,
        "inadimplente": False,
        "setor": "Comercio",
        "empregados": 3,
    }
    r = client.post("/v1/score", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 538
    assert data["aprovado"] is False
    assert data["limite_sugerido"] == 8070

def test_score_ok_usa_alias_anual_e_meses_operando():
    # Teste de cálculo usando faturamento anual e meses_operando
    body = {
        "cnpj": "00.000.000/0001-00",
        "faturamento_anual": 180000,  # equivalente a 15000/mês
        "meses_operando": 18,
        "inadimplente": False,
        "setor": "Comercio",
        "empregados": 3,
    }
    r = client.post("/v1/score", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 538
    assert data["limite_sugerido"] == 8070

def test_score_erro_campos_obrigatorios():
    # Teste quando campos obrigatórios não são enviados
    body = {
        "cnpj": "00.000.000/0001-00",
        "inadimplente": False,
        "setor": "Comercio",
        "empregados": 2,
    }
    r = client.post("/v1/score", json=body)
    assert r.status_code == 422
    data = r.json()
    assert data["error"]["code"] == "validation_error"
    assert "faturamento" in data["error"]["message"].lower()

def test_score_motivos():
    # Teste da rota de motivos (explicações detalhadas)
    body = {
        "cnpj": "00.000.000/0001-00",
        "faturamento_mensal": 15000,
        "tempo_atividade_meses": 18,
        "inadimplente": False,
        "setor": "Comercio",
        "empregados": 3,
    }
    r = client.post("/v1/score/motivos", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["score"] == 538
    assert isinstance(data["breakdown"], list)
    assert len(data["breakdown"]) == 5
