<template>
  <div class="home-container">
    <!-- Premium Animated Background -->
    <div class="bg-mesh"></div>
    <div class="bg-vignette"></div>
    
    <!-- Navigation Bar -->
    <nav class="navbar">
      <div class="nav-brand">
        <div class="logo-symbol">M</div>
        <span class="brand-text">MIROFISH</span>
      </div>
      <div class="nav-actions">
        <router-link to="/integration" class="nav-link glass-link">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
          {{ $t('nav.researchHub') }}
        </router-link>
        <LanguageSwitcher class="glass-switcher" />
        <a href="https://github.com/666ghj/MiroFish" target="_blank" class="github-icon glass-icon">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.041-1.412-4.041-1.412-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
        </a>
      </div>
    </nav>

    <main class="main-content">
      <!-- Centered Hero Section -->
      <header class="hero-center">
        <h1 class="hero-title-main">
          {{ $t('home.heroTitle1') }}<br/>
          <span class="gradient-text-alt">{{ $t('home.heroTitle2') }}</span>
        </h1>
        <p class="hero-subtitle-alt">
          {{ $t('home.tagline') }}
        </p>
      </header>

      <!-- Glassmorphic Interaction Area -->
      <section class="interaction-area-center">
        <div 
          class="glass-card main-input-wrapper" 
          :class="{ 'is-focused': isInputFocused, 'has-content': formData.simulationRequirement.length > 0 || files.length > 0 }"
        >
          <!-- Selected Files Display -->
          <div v-if="files.length > 0" class="file-chip-container">
            <TransitionGroup name="chip">
              <div v-for="(file, index) in files" :key="file.name + index" class="file-chip">
                <span class="chip-icon">📄</span>
                <span class="chip-name">{{ file.name }}</span>
                <button @click="removeFile(index)" class="chip-close">&times;</button>
              </div>
            </TransitionGroup>
          </div>

          <div class="input-container-inner">
            <button 
              class="action-icon-btn upload-trigger" 
              @click="triggerFileInput" 
              :title="$t('home.dragToUpload')"
            >
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14" stroke-linecap="round"/>
              </svg>
            </button>
            
            <textarea
              v-model="formData.simulationRequirement"
              :placeholder="$t('home.promptPlaceholder')"
              class="chat-textarea"
              @focus="isInputFocused = true"
              @blur="isInputFocused = false"
              ref="textareaRef"
              rows="1"
              @input="adjustTextareaHeight"
            ></textarea>

            <button 
              class="submit-circle-btn" 
              :disabled="!canSubmit || loading"
              @click="startSimulation"
            >
              <svg v-if="!loading" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="white" stroke-width="3">
                <path d="M12 19V5M5 12l7-7 7 7" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div v-else class="tiny-loader"></div>
            </button>
          </div>

          <!-- Hidden Input -->
          <input
            ref="fileInput"
            type="file"
            multiple
            accept=".pdf,.md,.txt"
            @change="handleFileSelect"
            style="display: none"
          />
        </div>

        <!-- Drop Overlay -->
        <Transition name="fade">
          <div v-if="isDragOver" class="glass-drop-overlay" @dragleave="isDragOver = false" @drop.prevent="handleDrop" @dragover.prevent>
            <div class="drop-ui-content">
              <div class="pulse-circle">📥</div>
              <h3>{{ $t('home.dragToUpload') }}</h3>
            </div>
          </div>
        </Transition>
      </section>

      <!-- Premium Sample Cards -->
      <section class="samples-container">
        <div class="samples-grid-layout">
          <div 
            v-for="(sample, i) in samples" 
            :key="i" 
            class="glass-sample-card" 
            @click="fillSample(sample)"
          >
            <div class="sample-head">
              <span class="sample-emoji">{{ sample.icon }}</span>
              <span class="sample-tag">{{ $t('common.ready') }}</span>
            </div>
            <h4>{{ sample.title }}</h4>
            <p>{{ sample.desc }}</p>
            <div class="sample-arrow">→</div>
          </div>
        </div>
      </section>

      <!-- History Section -->
      <section class="history-integration">
        <HistoryDatabase />
      </section>
    </main>

    <footer class="premium-footer">
      <div class="footer-left">
        <span class="pulse-dot"></span>
        {{ $t('home.systemReady') }}
      </div>
      <div class="footer-right">
        {{ $t('home.engineBadge') }}
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const router = useRouter()
const formData = ref({ simulationRequirement: '' })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const isInputFocused = ref(false)
const fileInput = ref(null)
const textareaRef = ref(null)

const samples = [
  {
    icon: '📊',
    title: 'Analisis Krisis Sentimen',
    desc: 'Simulasikan reaksi publik terhadap kebocoran data di Reddit.',
    prompt: 'Simulasikan reaksi publik di Reddit terhadap insiden kebocoran data pengguna. Fokus pada sentimen kemarahan, tuntutan hukum, dan penyebaran misinformasi.'
  },
  {
    icon: '🗳️',
    title: 'Prediksi Opini Publik',
    desc: 'Amati pergeseran opini pemilih muda terhadap kebijakan ekonomi baru.',
    prompt: 'Bagaimana narasi kebijakan ekonomi "Kesejahteraan Hijau" mempengaruhi opini pemilih muda usia 18-25 tahun di platform mikro-blogging dalam 30 hari ke depan?'
  },
  {
    icon: '☕',
    title: 'Dinamika Tren Gaya Hidup',
    desc: 'Simulasikan tren boikot produk di kalangan konsumen sadar sosial.',
    prompt: 'Simulasikan penyebaran gerakan boikot terhadap produk kopi global karena isu etis, dan bagaimana komunitas lokal menanggapi dalam simulasi 100 agen.'
  }
]

const canSubmit = computed(() => formData.value.simulationRequirement.trim() !== '' && files.value.length > 0)

const adjustTextareaHeight = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 240) + 'px'
}

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (e) => addFiles(Array.from(e.target.files))

const handleDrop = (e) => {
  isDragOver.value = false
  addFiles(Array.from(e.dataTransfer.files))
}

const addFiles = (newFiles) => {
  const valid = newFiles.filter(f => ['pdf', 'md', 'txt'].includes(f.name.split('.').pop().toLowerCase()))
  files.value.push(...valid)
}

const removeFile = (i) => files.value.splice(i, 1)

const fillSample = (sample) => {
  formData.value.simulationRequirement = sample.prompt
  setTimeout(adjustTextareaHeight, 0)
}

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}

onMounted(() => {
  window.addEventListener('dragenter', (e) => {
    if (e.dataTransfer.types.includes('Files')) {
      isDragOver.value = true
    }
  })
})
</script>

<style scoped>
/* 
  MIROFISH PREMIUM DESIGN SYSTEM
  Based on Glassmorphism & High-Contrast Typography
*/

.home-container {
  min-height: 100vh;
  background-color: #0c0c0e;
  color: #fff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* --- Animated Background Mesh --- */
.bg-mesh {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(255, 69, 0, 0.15) 0%, transparent 40%),
    radial-gradient(circle at 80% 70%, rgba(0, 122, 255, 0.1) 0%, transparent 40%),
    radial-gradient(circle at 50% 50%, rgba(88, 86, 214, 0.08) 0%, transparent 60%);
  filter: blur(80px);
  animation: mesh-float 20s ease-in-out infinite alternate;
}

@keyframes mesh-float {
  0% { transform: scale(1) translate(0, 0); }
  100% { transform: scale(1.1) translate(2%, 2%); }
}

.bg-vignette {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  background: radial-gradient(circle at center, transparent 0%, rgba(12, 12, 14, 0.8) 100%);
  pointer-events: none;
}

/* --- Navbar --- */
.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  z-index: 100;
  backdrop-filter: blur(10px);
  background: rgba(12, 12, 14, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-symbol {
  width: 32px;
  height: 32px;
  background: #ff4500;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.2rem;
  border-radius: 6px;
  box-shadow: 0 0 20px rgba(255, 69, 0, 0.4);
}

.brand-text {
  font-weight: 700;
  letter-spacing: 2px;
  font-size: 1.1rem;
  color: #fff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  text-decoration: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.nav-link:hover {
  color: #fff;
}

.glass-link {
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.glass-icon {
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s;
}

.glass-icon:hover {
  color: #ff4500;
  transform: translateY(-2px);
}

/* --- Main Content --- */
.main-content {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 0 auto;
  padding: 160px 20px 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* --- Hero Center --- */
.hero-center {
  text-align: center;
  margin-bottom: 60px;
}

.hero-title-main {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 20px;
  letter-spacing: -1.5px;
}

.gradient-text-alt {
  background: linear-gradient(135deg, #fff 0%, #ff4500 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle-alt {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.5);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.5;
}

/* --- Interaction Area --- */
.interaction-area-center {
  width: 100%;
  margin-bottom: 80px;
  position: relative;
}

.main-input-wrapper {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 12px;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.main-input-wrapper.is-focused {
  border-color: rgba(255, 69, 0, 0.4);
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 20px 60px rgba(255, 69, 0, 0.1);
}

.input-container-inner {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 8px;
}

.chat-textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.1rem;
  line-height: 1.6;
  resize: none;
  padding: 10px 4px;
  max-height: 240px;
  outline: none;
  font-family: inherit;
}

.chat-textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.action-icon-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-bottom: 4px;
}

.action-icon-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.submit-circle-btn {
  background: #ff4500;
  border: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
  margin-bottom: 4px;
  box-shadow: 0 4px 15px rgba(255, 69, 0, 0.3);
}

.submit-circle-btn:hover:not(:disabled) {
  transform: scale(1.05);
  background: #ff571a;
  box-shadow: 0 6px 20px rgba(255, 69, 0, 0.5);
}

.submit-circle-btn:disabled {
  background: rgba(255, 255, 255, 0.05);
  cursor: not-allowed;
  box-shadow: none;
}

.submit-circle-btn:disabled svg {
  stroke: rgba(255, 255, 255, 0.1);
}

/* --- File Chips --- */
.file-chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 4px;
}

.file-chip {
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
}

.chip-close {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 2px;
}

.chip-close:hover {
  color: #ff4500;
}

/* --- Sample Cards --- */
.samples-container {
  width: 100%;
  margin-bottom: 100px;
}

.samples-grid-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  width: 100%;
}

.glass-sample-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.glass-sample-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
}

.sample-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sample-emoji {
  font-size: 1.5rem;
}

.sample-tag {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #ff4500;
  font-weight: 700;
  padding: 4px 8px;
  background: rgba(255, 69, 0, 0.1);
  border-radius: 6px;
}

.glass-sample-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #fff;
}

.glass-sample-card p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.5;
  margin-bottom: 20px;
}

.sample-arrow {
  position: absolute;
  bottom: 24px;
  right: 24px;
  color: rgba(255, 255, 255, 0.2);
  font-size: 1.2rem;
  transition: all 0.3s;
}

.glass-sample-card:hover .sample-arrow {
  color: #ff4500;
  transform: translateX(4px);
}

/* --- History Section --- */
.history-integration {
  width: 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 40px;
}

/* --- Footer --- */
.premium-footer {
  position: fixed;
  bottom: 0;
  width: 100%;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.3);
  z-index: 100;
  background: linear-gradient(to top, #0c0c0e 0%, transparent 100%);
  pointer-events: none;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 10px #10b981;
  animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

/* --- Transitions --- */
.chip-enter-active, .chip-leave-active { transition: all 0.3s; }
.chip-enter-from, .chip-leave-to { opacity: 0; transform: translateY(10px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* --- Drop Overlay --- */
.glass-drop-overlay {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: rgba(255, 69, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 2px dashed #ff4500;
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.drop-ui-content {
  text-align: center;
}

.pulse-circle {
  font-size: 3rem;
  margin-bottom: 10px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
  40% {transform: translateY(-10px);}
  60% {transform: translateY(-5px);}
}

/* --- Responsive --- */
@media (max-width: 768px) {
  .hero-title-main { font-size: 2.5rem; }
  .navbar { padding: 0 20px; }
  .main-content { padding-top: 120px; }
  .nav-link span { display: none; }
}

.tiny-loader {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
