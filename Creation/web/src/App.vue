<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'
import ReportForm from './components/ReportForm.vue'
import TopNavBar from './components/TopNavBar.vue'
import AnalysisFrom from './analysisFrom.vue'

const apiBase = import.meta.env.VITE_API_BASE || ''

const authMode = ref('login')
const authNotice = ref('')

const isLoggedIn = ref(false)
const username = ref('')
const accessToken = ref('')
const isMember = ref(false)
const analysisResult = ref(null)

const activeTab = ref('report')
const scrollY = ref(0)
const theme = ref('light')
const showDemoModal = ref(false)
const toastList = ref([])

const navAlpha = computed(() => Math.min(0.42, 0.16 + scrollY.value / 900))
const toastPreview = computed(() => toastList.value.slice(0, 3))

function switchMode(mode) {
  authMode.value = mode
  authNotice.value = ''
}

function onLoginSuccess(payload) {
  if (typeof payload === 'string') {
    username.value = '已登录用户'
    accessToken.value = ''
    isMember.value = false
  } else {
    username.value = payload?.username || '已登录用户'
    accessToken.value = payload?.accessToken || ''
    isMember.value = Boolean(payload?.isMember)
  }
  isLoggedIn.value = true
  authNotice.value = ''
}

function onRegistered() {
  authMode.value = 'login'
  authNotice.value = '注册成功，请登录'
  pushToast('注册成功，已切换到登录页', 'success')
}

function logout() {
  isLoggedIn.value = false
  username.value = ''
  accessToken.value = ''
  isMember.value = false
  analysisResult.value = null
  activeTab.value = 'report'
  authMode.value = 'login'
  authNotice.value = ''
}

function onReportAnalyzed(payload) {
  analysisResult.value = payload?.analysis || null
  activeTab.value = 'analysis'
  pushToast('问卷分析完成，已切换到分析结果', 'success')
}

function handleScroll() {
  scrollY.value = window.scrollY || 0
}

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  pushToast(theme.value === 'light' ? '已切换为浅色主题' : '已切换为暗色主题', 'success')
}

function pushToast(text, type = 'success') {
  const id = Date.now() + Math.random()
  toastList.value.unshift({ id, text, type })
  window.setTimeout(() => {
    toastList.value = toastList.value.filter((item) => item.id !== id)
  }, 2600)
}

onMounted(() => {
  document.documentElement.setAttribute('data-theme', theme.value)
  handleScroll()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="app-shell">
    <aside class="ui-nav-rail">
      <div class="ui-nav-icon is-active">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 12L12 4L20 12V20H4V12Z" stroke="currentColor" stroke-width="1.8"/></svg>
      </div>
      <div class="ui-nav-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M5 7H19M5 12H19M5 17H14" stroke="currentColor" stroke-width="1.8"/></svg>
      </div>
      <div class="ui-nav-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 19V5H20V19H4Z" stroke="currentColor" stroke-width="1.8"/></svg>
      </div>
      <div class="ui-nav-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M5 12H19M12 5V19" stroke="currentColor" stroke-width="1.8"/></svg>
      </div>
      <div class="ui-nav-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 4L4 8L12 12L20 8L12 4ZM4 12L12 16L20 12M4 16L12 20L20 16" stroke="currentColor" stroke-width="1.8"/></svg>
      </div>
      <button class="ui-button ui-button--ghost" type="button" @click="toggleTheme">
        {{ theme === 'light' ? '暗色' : '浅色' }}
      </button>
    </aside>

    <div class="workspace">
      <TopNavBar
        :username="username"
        :is-logged-in="isLoggedIn"
        :is-member="isMember"
        :nav-alpha="navAlpha"
        @logout="logout"
      />

      <section class="hero">
        <h1>大学生创业指导平台</h1>
        <p>从账号接入到问卷采集，构建更有引导性的创业决策体验</p>
      </section>

      <main v-if="!isLoggedIn" class="auth-layout">
        <section class="ui-card auth-card">
          <div class="ui-tabs">
            <button class="ui-tabs__item" :class="{ 'is-active': authMode === 'login' }" @click="switchMode('login')">登录</button>
            <button class="ui-tabs__item" :class="{ 'is-active': authMode === 'register' }" @click="switchMode('register')">注册</button>
          </div>
          <transition name="fade-slide" mode="out-in">
            <LoginForm v-if="authMode === 'login'" key="login" :api-base="apiBase" @success="onLoginSuccess" />
            <RegisterForm v-else key="register" :api-base="apiBase" @registered="onRegistered" />
          </transition>
          <p v-if="authNotice" class="message success">{{ authNotice }}</p>
        </section>
      </main>

      <main v-else class="dashboard-bento">
        <div class="panel-column">
          <section class="ui-card module-card">
            <div class="ui-tabs">
              <button class="ui-tabs__item" :class="{ 'is-active': activeTab === 'report' }" @click="activeTab = 'report'">诊断报告</button>
              <button
                class="ui-tabs__item"
                :class="{ 'is-active': activeTab === 'analysis' }"
                :disabled="!analysisResult"
                @click="activeTab = 'analysis'"
              >
                分析结果
              </button>
              <button class="ui-tabs__item" :class="{ 'is-active': activeTab === 'coming' }" @click="activeTab = 'coming'">创业路径</button>
            </div>
            <p class="token-tip">当前账号：{{ username }}</p>
          </section>

          <section class="ui-card module-card">
            <transition name="fade-slide" mode="out-in">
              <ReportForm
                v-if="activeTab === 'report'"
                key="report"
                :api-base="apiBase"
                :access-token="accessToken"
                @analyzed="onReportAnalyzed"
              />
              <AnalysisFrom v-else-if="activeTab === 'analysis'" key="analysis" :analysis="analysisResult" />
              <section v-else key="coming" class="coming-wrap">
                <h2>创业路径</h2>
                <p>该模块后续开放，当前请先填写“诊断报告”问卷。</p>
                <button class="ui-button ui-button--primary" type="button" @click="showDemoModal = true">查看演示弹窗</button>
              </section>
            </transition>
          </section>
        </div>
      </main>
    </div>

    <transition name="fade-slide">
      <section v-if="showDemoModal" class="ui-modal-mask" @click.self="showDemoModal = false">
        <article class="ui-modal">
          <header class="ui-modal__head">
            <strong>组件演示区</strong>
          </header>
          <div class="ui-modal__body">
            <section class="showcase-grid">
              <div class="ui-card ui-card__body">
                <p>Button</p>
                <div class="showcase-actions">
                  <button class="ui-button ui-button--primary" type="button">Primary</button>
                  <button class="ui-button ui-button--ghost" type="button">Ghost</button>
                  <button class="ui-button ui-button--accent" type="button">Accent</button>
                </div>
              </div>
              <div class="ui-card ui-card__body">
                <p>Input + Tab + Toast</p>
                <input class="ui-input" type="text" placeholder="输入关键词" />
                <div class="ui-tabs showcase-tabs">
                  <button class="ui-tabs__item is-active" type="button">Overview</button>
                  <button class="ui-tabs__item" type="button">Detail</button>
                </div>
                <button class="ui-button ui-button--ghost showcase-toast-btn" type="button" @click="pushToast('这是一个 Toast 示例', 'success')">触发 Toast</button>
              </div>
            </section>
          </div>
          <footer class="ui-modal__foot">
            <button class="ui-button ui-button--ghost" type="button" @click="showDemoModal = false">关闭</button>
            <button class="ui-button ui-button--primary" type="button" @click="showDemoModal = false">确认</button>
          </footer>
        </article>
      </section>
    </transition>

    <div class="ui-toast-stack">
      <transition-group name="toast-fade">
        <article v-for="item in toastPreview" :key="item.id" class="ui-toast" :class="item.type === 'success' ? 'ui-toast--success' : ''">
          {{ item.text }}
        </article>
      </transition-group>
    </div>
  </div>
</template>
