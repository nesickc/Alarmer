# Alarmer: project rules

Start with [docs/spec.md](docs/spec.md) for what the system does, [docs/plan.md](docs/plan.md) for what comes next,
and [docs/adr/](docs/adr/README.md) for why. Architecture changes come with a new or superseding ADR in the same PR.

## Never put secrets in the repository

**The repository is public.** Anything committed should be treated as published forever: deleting it later doesn't
remove it from history, forks or caches.

Never commit, and never write into a tracked file:

* **API keys and tokens.** Telegram `api_id`/`api_hash`, Firebase service-account keys, `google-services.json`, FCM
  server keys, GitHub tokens, any third-party API key.
* **Passwords and codes.** Account passwords, 2FA passwords, Telegram login codes, recovery codes.
* **Authentication data.** Telethon `*.session` files, cookies, OAuth/refresh tokens, Android signing keystores and
  their passwords.
* **Account identifiers tied to these**, such as the phone number of the pipeline's Telegram account.

This covers code, tests and fixtures, docs and examples, logs, commit messages, issues and PR descriptions.

### How to handle them

* Secrets live only in git-ignored places: `pipeline/.env`, `secrets/`, keystores kept outside the repo. Code reads
  them from environment variables or those files.
* Commit only templates with obvious placeholders (`.env.example` with `TELEGRAM_API_HASH=<your api_hash>`).
* Before every commit, check the staged diff for anything secret-looking. If a new kind of secret file appears, add it
  to `.gitignore` in the same change.
* **If a secret gets committed or pushed**, treat it as compromised. Revoke or rotate it first, then remove it from
  history. Don't just delete it in a new commit.
* Logins that need codes or passwords (Telethon, Firebase, signing) are done by the developer in their own terminal.
  Claude never asks for, types or stores those credentials.
