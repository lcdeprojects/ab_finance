# 🚀 Guia de Setup: AB Finance no Railway

Este documento explica como configurar o projeto **AB Finance** no Railway utilizando **PostgreSQL** e as melhores práticas de segurança.

## 1. Preparação Inicial
1. Conecte seu repositório GitHub ao [Railway](https://railway.app).
2. Clique em **"New Project"** -> **"Deploy from GitHub repo"**.
3. Selecione o repositório `ab_finance`.

## 2. Adicionando o Banco de Dados (PostgreSQL)
1. No seu projeto no Railway, clique em **"New"** -> **"Database"** -> **"Add PostgreSQL"**.
2. O Railway criará automaticamente um banco e disponibilizará a variável `DATABASE_URL`.
3. O código já está configurado para ler essa variável automaticamente.

## 3. Variáveis de Ambiente (Configurações)
No painel do serviço **Web** (seu projeto Django), vá em **Variables** e adicione:

| Variável | Valor Sugerido | Descrição |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(Gere uma string longa e aleatória)* | Chave de segurança do Django. |
| `DEBUG` | `False` | **Obrigatório** em produção. |
| `ALLOWED_HOSTS` | `*.railway.app` | Permite o domínio padrão do Railway. |
| `CSRF_TRUSTED_ORIGINS` | `https://*.railway.app` | Segurança para formulários via HTTPS. |

## 4. Automação de Migrações
O arquivo `Procfile` já contém o comando de release para rodar as migrações automaticamente a cada deploy:
```
release: python manage.py migrate
web: gunicorn finance_system.wsgi
```

## 5. Rotinas de Segurança e Backup
O Railway oferece backups automáticos para o PostgreSQL:

1. **Backups Automáticos**: No painel do PostgreSQL, vá em **Settings** -> **Backups**. O Railway mantém backups diários por padrão.
2. **Logs de Auditoria**: Ative os logs no painel do serviço para monitorar acessos suspeitos.
3. **SSL Forçado**: O projeto está configurado para usar `CSRF_TRUSTED_ORIGINS` com HTTPS. Garanta que o domínio final também use HTTPS.

## 6. Comandos Úteis
Se precisar rodar comandos manualmente no servidor local ou via Railway CLI:
- `python manage.py collectstatic`: (Já automatizado no Dockerfile).
- `python manage.py createsuperuser`: Use o console do Railway para criar seu primeiro acesso administrativo.

---
*AB Finance - Sistema de Gestão Financeira Premium*
