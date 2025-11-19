# Hopper API Tests

Este diretório contém os testes unitários e de integração da API Hopper.

## Estrutura

- `conftest.py` - Configurações e fixtures do pytest
- `test_auth_service.py` - Testes do serviço de autenticação
- `test_user_service.py` - Testes do serviço de usuários
- `test_group_service.py` - Testes do serviço de grupos
- `test_powerbi_service.py` - Testes do serviço Power BI
- `test_airflow_service.py` - Testes do serviço Airflow
- `test_auth_controller.py` - Testes dos endpoints de autenticação
- `test_user_controller.py` - Testes dos endpoints de usuários
- `test_group_controller.py` - Testes dos endpoints de grupos

## Executando os testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src --cov-report=html

# Executar testes específicos
pytest tests/test_auth_service.py

# Executar com mais verbosidade
pytest -v
```

## Cobertura de Código

Os testes cobrem:
- Services (lógica de negócio)
- Controllers (endpoints da API)
- Autenticação e autorização
- Integração com APIs externas (mocked)
