# API Reference (Core Endpoints)

## Auth
- `POST /api/auth/signup/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `POST /api/auth/otp/request/`
- `POST /api/auth/otp/verify/`
- `POST /api/auth/token/refresh/`

## Contacts
- `GET/POST /api/contacts/`
- `GET/PUT/PATCH/DELETE /api/contacts/{id}/`
- `GET/POST /api/contacts/groups/`

## Mail Core
- `POST /api/mail/commands/parse/`
- `POST /api/mail/drafts/preview/`
- `POST /api/mail/drafts/confirm/`
- `POST /api/mail/drafts/edit-previous/`
- `GET /api/mail/drafts/`
- `POST /api/mail/actions/resend-last/`
- `GET /api/mail/history/sent/`
- `GET /api/mail/history/commands/`
- `GET /api/mail/insights/dashboard/`

## Templates
- `GET/POST /api/templates/`
- `GET/PUT/PATCH/DELETE /api/templates/{id}/`
- `GET /api/templates/suggest/`
- `POST /api/templates/rewrite/`

## Voice
- `POST /api/voice/transcribe/` (multipart file `audio`)
- `POST /api/voice/confirm/`

## Reminders
- `GET/POST /api/reminders/`
- `GET/PUT/PATCH/DELETE /api/reminders/{id}/`
- `POST /api/reminders/run-due/`

## Health
- `GET /health/`
