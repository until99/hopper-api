# hopper-api

Este é um projeto Python minimalista para uma API.

> **Nota:** Este repositório contém o frontend do projeto Hopper. Os repositórios dos componentes principais estão separados:

- Frontend (aplicação): https://github.com/until99/hopper-app
- Hopper (Landing Page): https://github.com/until99/hopper
- Airflow (ETL / DAGs): https://github.com/until99/hopper-airflow

## Estrutura de Diretórios

- `src/` — Código-fonte principal do projeto
  - `main.py` — Ponto de entrada da aplicação
  - `__init__.py` — Inicialização do módulo
- `pyproject.toml` — Configuração de dependências e build

## Setup Local

1. **Clone o repositório:**

   ```bash
   git clone <url-do-repositorio>
   cd hopper-api
   ```

2. **Instale o uv (requer Python >=3.8):**

   ```bash
   pip install uv
   ```

3. **Instale as dependências do projeto com uv:**

   ```bash
   uv sync
   ```

4. **Rode o servidor de desenvolvimento com uv:**

   ```bash
   uv run src/main.py
   ```

Acesse a API em `http://localhost:8000`.

---

> Para dúvidas ou contribuições, consulte o código em `src/` e o arquivo `pyproject.toml`.
