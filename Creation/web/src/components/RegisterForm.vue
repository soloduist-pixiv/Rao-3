<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  apiBase: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['registered'])

const isSubmitting = ref(false)
const message = ref('')
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

function resetMessage() {
  message.value = ''
  error.value = ''
}

async function submit() {
  resetMessage()

  if (!form.username || !form.password) {
    error.value = '用户名和密码不能为空'
    return
  }

  if (form.password !== form.confirmPassword) {
    error.value = '两次密码输入不一致'
    return
  }

  isSubmitting.value = true

  try {
    const res = await fetch(`${props.apiBase}/login/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.username.trim(),
        password: form.password,
      }),
    })

    const result = await res.json()

    if (!res.ok) {
      error.value = result?.message || '请求失败，请稍后再试'
      return
    }

    message.value = result?.message || '注册成功'
    form.password = ''
    form.confirmPassword = ''
    emit('registered')
  } catch (e) {
    error.value = '无法连接后端服务，请检查后端是否已启动'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-panel">
    <header class="auth-panel__head">
      <h2>创建新账号</h2>
      <p>注册后即可体验完整的创业问卷分析</p>
    </header>

    <form class="auth-form" @submit.prevent="submit">
      <label>
        用户名
        <input v-model="form.username" type="text" placeholder="请输入用户名" @input="resetMessage" />
      </label>

      <label>
        密码
        <input v-model="form.password" type="password" placeholder="请输入密码" @input="resetMessage" />
      </label>

      <label>
        重复密码
        <input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" @input="resetMessage" />
      </label>

      <button class="primary-btn" :disabled="isSubmitting" type="submit">
        {{ isSubmitting ? '提交中...' : '立即注册' }}
      </button>
    </form>

    <p v-if="message" class="message success">{{ message }}</p>
    <p v-if="error" class="message error">{{ error }}</p>
  </section>
</template>
