# Igreja API (Django + DRF)

Projeto base **pronto para escalar** para uma igreja com centenas de congregações.

## ✅ O que vem pronto

- Autenticação **JWT** (SimpleJWT)
- **Roles** (RBAC) via modelo `Role` (DB) e M2M em `User`
- Endpoints de auth compatíveis com o seu Flutter:
  - `POST /api/auth/login/`
  - `POST /api/auth/forgot-password/`
  - `GET /api/auth/me/`
- Swagger/OpenAPI:
  - `GET /api/schema/`
  - `GET /api/docs/` (Swagger UI)
- Admin Django em `.../admin/`
- Modelos e Admin separados por módulos (scalável)
- Configuração para **MySQL** via `.env` (com fallback para SQLite)

---

## Estrutura

```
config/
  settings.py
  urls.py
apps/
  accounts/
    models/ (user.py, role.py)
    admin/  (user_admin.py, role_admin.py)
    serializers/
    management/commands/seed_initial.py
  church/
    models/ (church.py, congregation.py)
    admin/  (church_admin.py, congregation_admin.py)
  api/
    views/auth_views.py
    urls.py
```

---

## Setup rápido (SQLite)

1) Crie e ative seu venv

2) Instale dependências:

```bash
pip install -r requirements.txt
```

> Se você ainda não vai usar MySQL, pode comentar `mysqlclient` no `requirements.txt`.

3) Migrações + seed:

```bash
python manage.py migrate
python manage.py seed_initial
```

4) Rode:

```bash
python manage.py runserver
```

- Admin: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/api/docs/`

Usuário admin padrão criado pelo seed:
- **email**: `admin@igreja.com`
- **senha**: `admin123`

---

## Configurar MySQL

1) Copie `.env.example` para `.env` e ajuste:

```env
DB_ENGINE=mysql
DB_NAME=igreja_api
DB_USER=root
DB_PASSWORD=senha
DB_HOST=127.0.0.1
DB_PORT=3306
```

2) Instale dependências do `mysqlclient` no sistema:

### Windows
- Instale o MySQL (ou MariaDB) + Build Tools
- Ou use `PyMySQL` (alternativa) se preferir evitar `mysqlclient`

### Linux (Debian/Ubuntu)
```bash
sudo apt-get install -y python3-dev default-libmysqlclient-dev build-essential
```

3) Instale deps e rode:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial
python manage.py runserver
```

---

## Contrato da API (para o Flutter)

### Login
`POST /api/auth/login/`

Body:
```json
{
  "email": "admin@igreja.com",
  "password": "admin123"
}
```

Response:
```json
{
  "tokens": {
    "access": "...",
    "refresh": "...",
    "accessToken": "...",
    "refreshToken": "..."
  },
  "user": {
    "id": 1,
    "name": "Administrador",
    "email": "admin@igreja.com",
    "roles": ["admin"],
    "congregation_name": "Sede - Centro"
  }
}
```

### Me
`GET /api/auth/me/`

Header:
`Authorization: Bearer <accessToken>`

### Forgot password
`POST /api/auth/forgot-password/`

Body:
```json
{ "email": "admin@igreja.com" }
```

---

## Próximos módulos que você pode plugar
- Membros, Pastores/Líderes, Ministérios
- Eventos e Escalas
- Financeiro (ofertas/dízimos)
- Multi-igrejas (rede) + permissões por congregação

# igreja_api
