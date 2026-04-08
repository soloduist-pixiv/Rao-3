<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  apiBase: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['success'])

const isSubmitting = ref(false)
const message = ref('')
const error = ref('')

const form = reactive({
  username: '',
  password: '',
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

  isSubmitting.value = true

  try {
    const res = await fetch(`${props.apiBase}/login`, {
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

    message.value = result?.message || '登录成功'
    emit('success', {
      accessToken: result?.data?.access_token || '',
      username: form.username.trim(),
      isMember: Boolean(result?.data?.is_member),
    })
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
      <h2>欢迎回来</h2>
      <p>登录后即可进入创业诊断工作台</p>
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

      <button class="primary-btn" :disabled="isSubmitting" type="submit">
        {{ isSubmitting ? '提交中...' : '立即登录' }}
      </button>
    </form>

    <p v-if="message" class="message success">{{ message }}</p>
    <p v-if="error" class="message error">{{ error }}</p>
  </section>
</template>
