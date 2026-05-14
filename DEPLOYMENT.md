# Deployment: Vercel (frontend) + backend terpisah

Repositori: [github.com/biezz-2/Mirofish-Psychology](https://github.com/biezz-2/Mirofish-Psychology).

**Panduan sangat lengkap (Bahasa Indonesia):** [docs/PANDUAN_LENGKAP.md](docs/PANDUAN_LENGKAP.md) — termasuk langkah import GitHub ke Vercel, variabel `VITE_API_BASE_URL`, dan opsi hosting backend.

MiroFish upstream memakai **Vue 3 (Vite) + Flask**. Frontend adalah **static SPA**; backend Flask cocok dijalankan sebagai **container** (Dockerfile di root) di Fly.io, Railway, Render, atau Google Cloud Run.

## 1. Frontend (Vercel)

1. [vercel.com/new](https://vercel.com/new) → Import **`biezz-2/Mirofish-Psychology`**.
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Output Directory:** `dist`
5. **Environment Variables** (Production + Preview): `VITE_API_BASE_URL` = URL backend publik (**tanpa** trailing slash). Lihat `frontend/src/api/index.js`.
6. SPA: [frontend/vercel.json](frontend/vercel.json) → rewrite ke `index.html` (route `/integration`).

## 2. Backend (Fly / Railway / Cloud Run)

1. Gunakan image dari [Dockerfile](Dockerfile) (Python 3.11 + uv) atau jalankan `uv sync` + `python run.py` di Linux dengan Python **3.11–3.12** (disarankan; dependensi `camel-oasis` tidak mendukung Python 3.14).
2. Set environment sama seperti [.env.example](.env.example) (LLM, Zep, Notion, Google, dll.).
3. **CORS** sudah `*` untuk `/api/*` di Flask; untuk produksi bisa dipersempit ke domain Vercel di `backend/app/__init__.py` jika perlu.

## 3. Windows / Python 3.14 (tanpa uv)

Gunakan [backend/requirements-minimal.txt](backend/requirements-minimal.txt) (tanpa OASIS/camel) untuk API + fitur PRD; simulasi penuh tetap lewat Docker.

```text
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements-minimal.txt
set PYTHONPATH=%CD%
.venv\Scripts\python run.py
```

## 4. Pengujian

```text
npm run test
```

Menjalankan pytest backend + Vitest frontend (lihat [package.json](package.json)).