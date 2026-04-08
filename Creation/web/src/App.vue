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

const navAlpha = computed(() => Math.min(0.42, 0.16 + scrollY.value / 900))

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
}

function handleScroll() {
  scrollY.value = window.scrollY || 0
}

onMounted(() => {
  handleScroll()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="app-shell">
    <TopNavBar
      :username="username"
      :is-logged-in="isLoggedIn"
      :is-member="isMember"
      :nav-alpha="navAlpha"
      @logout="logout"
    />

    <div class="bg-orb orb-a" :style="{ transform: `translate3d(0, ${scrollY * 0.14}px, 0)` }"></div>
    <div class="bg-orb orb-b" :style="{ transform: `translate3d(0, ${scrollY * -0.08}px, 0)` }"></div>

    <section class="hero glass-card">
      <h1>大学生创业指导平台</h1>
      <p>从账号接入到问卷采集，构建更有引导性的创业决策体验</p>
    </section>

    <main v-if="!isLoggedIn" class="auth-layout">
      <section class="glass-card auth-card">
        <div class="auth-switch">
          <button :class="{ active: authMode === 'login' }" @click="switchMode('login')">登录</button>
          <button :class="{ active: authMode === 'register' }" @click="switchMode('register')">注册</button>
        </div>

        <transition name="fade-slide" mode="out-in">
          <LoginForm v-if="authMode === 'login'" key="login" :api-base="apiBase" @success="onLoginSuccess" />
          <RegisterForm v-else key="register" :api-base="apiBase" @registered="onRegistered" />
        </transition>
        <p v-if="authNotice" class="message success">{{ authNotice }}</p>
      </section>
    </main>

    <main v-else class="dashboard-bento">
      <section class="glass-card module-2x1">
        <div class="tabs">
          <button :class="{ active: activeTab === 'report' }" @click="activeTab = 'report'">诊断报告</button>
          <button :class="{ active: activeTab === 'analysis' }" :disabled="!analysisResult" @click="activeTab = 'analysis'">
            分析结果
          </button>
          <button :class="{ active: activeTab === 'coming' }" @click="activeTab = 'coming'">创业路径（待开放）</button>
        </div>
        <p class="token-tip">当前账号：{{ username }}</p>
      </section>

      <section class="glass-card module-2x2 panel-card">
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
          </section>
        </transition>
      </section>

    </main>
  </div>
</template>

<style>
:root {
  color-scheme: light;
}

body {
  margin: 0;
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  color: #eef2ff;
  background: radial-gradient(circle at 20% 20%, #4f46e5 0%, #1f2a68 35%, #0b1026 100%);
}

* {
  box-sizing: border-box;
}

.app-shell {
  min-height: 100vh;
  padding: 96px 20px 24px;
  color: #e5edff;
  position: relative;
  overflow: hidden;
}

.bg-orb {
  position: fixed;
  border-radius: 999px;
  filter: blur(40px);
  pointer-events: none;
  z-index: 0;
  transition: transform 0.25s linear;
}

.orb-a {
  width: 360px;
  height: 360px;
  right: -80px;
  top: 120px;
  background: rgba(96, 165, 250, 0.34);
}

.orb-b {
  width: 300px;
  height: 300px;
  left: -120px;
  top: 460px;
  background: rgba(129, 140, 248, 0.28);
}

.top-nav {
  position: fixed;
  top: 12px;
  left: 12px;
  right: 12px;
  z-index: 20;
  border-radius: 18px;
  background: rgba(13, 23, 56, var(--nav-alpha, 0.2));
  border: 1px solid rgba(255, 255, 255, 0.24);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 14px 38px rgba(3, 8, 25, 0.32);
  transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

.top-nav__inner {
  min-height: 60px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.brand-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(130deg, #38bdf8, #6366f1);
  box-shadow: 0 0 0 5px rgba(56, 189, 248, 0.18);
}

.brand-text {
  display: grid;
  gap: 2px;
}

.brand-text strong {
  font-size: clamp(0.95rem, 0.88rem + 0.3vw, 1.05rem);
  letter-spacing: 0.01em;
}

.brand-text span {
  font-size: 0.75rem;
  color: rgba(219, 234, 254, 0.78);
}

.user-panel {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.username {
  max-width: clamp(110px, 16vw, 220px);
  padding: 6px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 0.88rem;
}

.member-pill {
  min-width: 78px;
  justify-content: center;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.78rem;
  font-weight: 700;
}

.member-pill--on {
  color: #fde68a;
  background: rgba(250, 204, 21, 0.18);
  border: 1px solid rgba(250, 204, 21, 0.38);
}

.member-pill--off {
  color: #bfdbfe;
  background: rgba(59, 130, 246, 0.16);
  border: 1px solid rgba(96, 165, 250, 0.36);
}

.status-pill {
  min-width: 66px;
  justify-content: center;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-pill i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.status-pill--on {
  color: #86efac;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.35);
}

.status-pill--on i {
  background: #4ade80;
}

.status-pill--off {
  color: #fca5a5;
  background: rgba(248, 113, 113, 0.14);
  border: 1px solid rgba(248, 113, 113, 0.34);
}

.status-pill--off i {
  background: #f87171;
}

.hero {
  max-width: 1200px;
  margin: 0 auto 16px;
  position: relative;
  z-index: 1;
}

.hero h1 {
  margin: 0 0 8px;
  font-size: clamp(1.55rem, 1.2rem + 1.2vw, 2.25rem);
  font-weight: 700;
}

.hero p {
  margin: 0;
  font-size: clamp(0.95rem, 0.86rem + 0.4vw, 1.05rem);
  color: rgba(219, 234, 254, 0.88);
}

.glass-card {
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 18px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 18px 44px rgba(5, 10, 28, 0.3);
}

.auth-layout {
  position: relative;
  z-index: 1;
  max-width: 760px;
  margin: 0 auto;
  display: block;
}

.auth-card {
  padding: 20px;
}

.auth-switch {
  display: inline-flex;
  gap: 10px;
  padding: 5px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.12);
  margin-bottom: 16px;
}

.auth-switch button,
.tabs button,
.primary-btn,
.ghost-btn {
  min-height: 44px;
  padding: 10px 16px;
  border-radius: 12px;
  border: 1px solid transparent;
  font-size: 0.92rem;
  cursor: pointer;
  transition: transform 0.24s ease, opacity 0.24s ease, box-shadow 0.24s ease, background 0.24s ease;
}

.auth-switch button,
.tabs button {
  background: rgba(226, 232, 255, 0.2);
  color: #eff6ff;
}

.auth-switch button:hover,
.tabs button:hover,
.ghost-btn:hover,
.primary-btn:hover {
  transform: translateY(-1px);
}

.auth-switch button.active,
.tabs button.active {
  background: linear-gradient(130deg, rgba(59, 130, 246, 0.92), rgba(99, 102, 241, 0.92));
  color: #ffffff;
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.4);
}

.auth-panel__head h2 {
  margin: 0;
  font-size: clamp(1.08rem, 0.95rem + 0.5vw, 1.3rem);
}

.auth-panel__head p {
  margin: 6px 0 14px;
  color: rgba(226, 232, 255, 0.85);
  font-size: 0.9rem;
}

.auth-form {
  display: grid;
  gap: 14px;
}

label {
  display: grid;
  gap: 6px;
  font-size: 0.9rem;
  color: rgba(224, 231, 255, 0.95);
}

input,
select {
  width: 100%;
  min-height: 44px;
  border: 1px solid rgba(165, 180, 252, 0.4);
  border-radius: 12px;
  padding: 0 12px;
  background: rgba(15, 23, 53, 0.28);
  color: #f8fafc;
  outline: none;
}

input::placeholder {
  color: rgba(226, 232, 240, 0.58);
}

input:focus,
select:focus {
  border-color: rgba(99, 102, 241, 0.9);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.primary-btn {
  border: none;
  background: linear-gradient(130deg, #3b82f6, #6366f1);
  color: #fff;
  font-weight: 700;
}

.primary-btn:disabled {
  opacity: 0.74;
  cursor: not-allowed;
}

.ghost-btn {
  background: rgba(15, 23, 53, 0.35);
  border-color: rgba(191, 219, 254, 0.36);
  color: #dbeafe;
}

.dashboard-bento {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}

.module-2x1 {
  grid-column: span 8;
  padding: 16px;
}

.module-2x2 {
  grid-column: span 8;
  padding: 16px;
}

.panel-card {
  min-height: 520px;
}

.tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.token-tip {
  margin: 0;
  font-size: 0.84rem;
  color: rgba(224, 231, 255, 0.88);
}

.coming-wrap h2 {
  margin: 0 0 10px;
  font-size: clamp(1.12rem, 1rem + 0.5vw, 1.35rem);
}

.coming-wrap p {
  margin: 0;
  line-height: 1.6;
  color: rgba(224, 231, 255, 0.88);
}

.message {
  margin: 14px 0 0;
  font-size: 0.9rem;
}

.success {
  color: #86efac;
}

.error {
  color: #fca5a5;
}

.fade-slide-enter-active,
.fade-slide-leave-active,
.status-fade-enter-active,
.status-fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to,
.status-fade-enter-from,
.status-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

@media (max-width: 1024px) {
  .module-2x1,
  .module-2x2 {
    grid-column: span 12;
  }
}

@media (max-width: 720px) {
  .app-shell {
    padding: 86px 12px 16px;
  }

  .top-nav {
    top: 8px;
    left: 8px;
    right: 8px;
    border-radius: 14px;
  }

  .top-nav__inner {
    min-height: 56px;
    padding: 8px 10px;
  }

  .brand-text span {
    display: none;
  }

  .username {
    max-width: 110px;
  }

  .hero,
  .auth-layout,
  .dashboard-bento {
    gap: 12px;
  }
}
</style>
