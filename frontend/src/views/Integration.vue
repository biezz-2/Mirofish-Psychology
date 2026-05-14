<template>
  <div class="min-h-screen bg-mf-bg font-sans text-mf-text">
    <header class="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur-md">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div class="flex items-center gap-4">
          <router-link to="/" class="text-sm font-semibold text-mf-primary hover:underline">MiroFish</router-link>
          <span class="text-slate-400">/</span>
          <span class="text-sm font-medium text-slate-700">{{ $t('integration.title') }}</span>
        </div>
        <div class="flex items-center gap-3">
          <LanguageSwitcher />
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl space-y-8 px-4 py-8">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">{{ $t('integration.title') }}</h1>
        <p class="mt-2 text-slate-600">{{ $t('integration.subtitle') }}</p>
      </div>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('integration.statusTitle') }}</h2>
        <pre class="mt-3 overflow-x-auto rounded-lg bg-slate-50 p-4 text-xs text-slate-700">{{ statusJson }}</pre>
        <button
          type="button"
          class="mt-4 rounded-lg bg-mf-primary px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
          @click="loadStatus"
        >
          {{ $t('integration.refresh') }}
        </button>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('integration.preview') }}</h2>
        <p class="mt-1 text-sm text-slate-500">{{ $t('integration.hintNotion') }}</p>
        <div class="mt-4 flex flex-wrap gap-2">
          <input
            v-model="databaseId"
            type="text"
            placeholder="Notion database ID (optional)"
            class="min-w-[240px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm shadow-sm focus:border-mf-primary focus:outline-none focus:ring-2 focus:ring-blue-200"
          />
          <button
            type="button"
            class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            @click="doPreview"
          >
            {{ $t('integration.preview') }}
          </button>
        </div>
        <pre class="mt-4 max-h-80 overflow-auto rounded-lg bg-slate-50 p-4 text-xs">{{ previewJson }}</pre>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('integration.startSync') }}</h2>
        <div class="mt-4 flex flex-wrap gap-2">
          <input
            v-model="docTitle"
            type="text"
            placeholder="Google Doc title (optional)"
            class="min-w-[200px] flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
          />
          <button
            type="button"
            class="rounded-lg bg-mf-primary px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700"
            @click="doSync"
          >
            {{ $t('integration.startSync') }}
          </button>
        </div>
        <div class="mt-4 flex flex-wrap items-center gap-2">
          <span class="text-sm text-slate-600">{{ $t('integration.jobId') }}:</span>
          <code class="rounded bg-slate-100 px-2 py-1 text-xs">{{ jobId || '—' }}</code>
          <button
            v-if="jobId"
            type="button"
            class="rounded-lg border border-slate-200 px-3 py-1 text-sm hover:bg-slate-50"
            @click="pollJob"
          >
            {{ $t('integration.refresh') }}
          </button>
        </div>
        <pre class="mt-4 max-h-64 overflow-auto rounded-lg bg-slate-50 p-4 text-xs">{{ jobJson }}</pre>
      </section>

      <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-semibold text-slate-800">{{ $t('integration.analyze') }} / {{ $t('integration.questions') }}</h2>
        <textarea
          v-model="analyzePayload"
          rows="6"
          class="mt-4 w-full rounded-lg border border-slate-200 p-3 font-mono text-xs"
          placeholder='{"sample":"value"}'
        />
        <div class="mt-4 flex flex-wrap gap-2">
          <button type="button" class="rounded-lg bg-mf-accent px-4 py-2 text-sm font-medium text-white" @click="doAnalyze">
            {{ $t('integration.analyze') }}
          </button>
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="doQuestions">
            {{ $t('integration.questions') }}
          </button>
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="doBank">
            {{ $t('integration.questionBank') }}
          </button>
          <button type="button" class="rounded-lg border border-slate-200 px-4 py-2 text-sm" @click="doLlmSmoke">
            LLM smoke
          </button>
        </div>
        <pre class="mt-4 max-h-96 overflow-auto rounded-lg bg-slate-50 p-4 text-xs">{{ researchJson }}</pre>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import * as integrationApi from '@/api/integration.js'

const statusJson = ref('—')
const previewJson = ref('—')
const jobJson = ref('—')
const researchJson = ref('—')
const databaseId = ref('')
const docTitle = ref('MiroFish — Ringkasan sinkron')
const jobId = ref('')
const analyzePayload = ref('{\n  "rows": [\n    {"id": 1, "scale": 12, "note": "contoh"}\n  ]\n}')

async function loadStatus() {
  statusJson.value = JSON.stringify((await integrationApi.getIntegrationStatus()).data, null, 2)
}

async function doPreview() {
  previewJson.value = '…'
  try {
    const res = await integrationApi.previewNotion(databaseId.value.trim() || undefined)
    previewJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    previewJson.value = String(e.message || e)
  }
}

async function doSync() {
  jobJson.value = '…'
  try {
    const res = await integrationApi.startSync({
      database_id: databaseId.value.trim() || undefined,
      doc_title: docTitle.value.trim() || undefined
    })
    jobId.value = res.data.job_id
    jobJson.value = JSON.stringify(res.data, null, 2)
    setTimeout(pollJob, 2000)
  } catch (e) {
    jobJson.value = String(e.message || e)
  }
}

async function pollJob() {
  if (!jobId.value) return
  try {
    const res = await integrationApi.getSyncJob(jobId.value)
    jobJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    jobJson.value = String(e.message || e)
  }
}

async function doAnalyze() {
  researchJson.value = '…'
  try {
    let data
    try {
      data = JSON.parse(analyzePayload.value)
    } catch {
      researchJson.value = 'Invalid JSON in payload'
      return
    }
    const res = await integrationApi.runAnalyze({
      data,
      write_google_doc: false
    })
    researchJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    researchJson.value = String(e.message || e)
  }
}

async function doQuestions() {
  researchJson.value = '…'
  try {
    let data
    try {
      data = JSON.parse(analyzePayload.value)
    } catch {
      researchJson.value = 'Invalid JSON in payload'
      return
    }
    const res = await integrationApi.runQuestions({
      data,
      methods: ['foq', 'qualitative', 'quantitative', 'critical'],
      count_per_method: 3
    })
    researchJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    researchJson.value = String(e.message || e)
  }
}

async function doBank() {
  researchJson.value = '…'
  try {
    const res = await integrationApi.getQuestionBank()
    researchJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    researchJson.value = String(e.message || e)
  }
}

async function doLlmSmoke() {
  researchJson.value = '…'
  try {
    const res = await integrationApi.llmSmoke({})
    researchJson.value = JSON.stringify(res.data, null, 2)
  } catch (e) {
    researchJson.value = String(e.message || e)
  }
}

onMounted(() => {
  loadStatus()
})
</script>
