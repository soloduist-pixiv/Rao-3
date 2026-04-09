<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    default: '',
  },
  isLoggedIn: {
    type: Boolean,
    default: false,
  },
  isMember: {
    type: Boolean,
    default: false,
  },
  navAlpha: {
    type: Number,
    default: 0.2,
  },
})

const emit = defineEmits(['logout'])
const isSolid = computed(() => props.navAlpha >= 0.28)
</script>

<template>
  <header class="top-nav" :class="{ 'top-nav--solid': isSolid }">
    <div class="top-nav__inner">
      <div class="brand-group">
        <div class="brand-dot"></div>
        <div class="brand-text">
          <strong>创业导航台</strong>
          <span>Student Venture Hub</span>
        </div>
      </div>

      <div class="user-panel">
        <div class="username" :title="username || '未登录用户'">
          {{ username || '未登录用户' }}
        </div>
        <span v-if="isLoggedIn" class="member-pill" :class="isMember ? 'member-pill--on' : 'member-pill--off'">
          {{ isMember ? '会员' : '普通用户' }}
        </span>

        <transition name="status-fade" mode="out-in">
          <span v-if="isLoggedIn" key="in" class="status-pill status-pill--on">
            <i></i>
            在线
          </span>
          <span v-else key="out" class="status-pill status-pill--off">
            <i></i>
            离线
          </span>
        </transition>

        <button v-if="isLoggedIn" class="ui-button ui-button--ghost" type="button" @click="emit('logout')">登出</button>
      </div>
    </div>
  </header>
</template>
