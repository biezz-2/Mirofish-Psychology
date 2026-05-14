import service from './index'

export function getIntegrationStatus() {
  return service.get('/api/integration/config-status')
}

export function previewNotion(databaseId) {
  return service.post('/api/integration/notion/preview', { database_id: databaseId || undefined })
}

export function startSync(payload) {
  return service.post('/api/integration/sync/start', payload || {})
}

export function getSyncJob(jobId) {
  return service.get(`/api/integration/sync/${jobId}`)
}

export function runAnalyze(body) {
  return service.post('/api/research/analyze', body)
}

export function runQuestions(body) {
  return service.post('/api/research/questions', body)
}

export function getQuestionBank() {
  return service.get('/api/research/question-bank')
}

export function llmSmoke(body) {
  return service.post('/api/research/llm-smoke', body || {})
}
