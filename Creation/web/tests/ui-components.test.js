import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import LoginForm from '../src/components/LoginForm.vue'
import RegisterForm from '../src/components/RegisterForm.vue'
import TopNavBar from '../src/components/TopNavBar.vue'

describe('TopNavBar', () => {
  it('在登录时展示在线状态与登出按钮', () => {
    const wrapper = mount(TopNavBar, {
      props: {
        username: 'Alex',
        isLoggedIn: true,
        isMember: true,
        navAlpha: 0.4,
      },
    })
    expect(wrapper.text()).toContain('在线')
    expect(wrapper.text()).toContain('登出')
    expect(wrapper.find('.top-nav').classes()).toContain('top-nav--solid')
  })

  it('未登录时展示离线状态', () => {
    const wrapper = mount(TopNavBar, {
      props: {
        username: '',
        isLoggedIn: false,
        isMember: false,
        navAlpha: 0.1,
      },
    })
    expect(wrapper.text()).toContain('离线')
  })
})

describe('LoginForm', () => {
  it('为空时提交显示错误信息', async () => {
    const wrapper = mount(LoginForm, {
      props: { apiBase: '' },
    })
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('用户名和密码不能为空')
  })

  it('服务端失败时显示后端消息', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ message: '账号或密码错误' }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(LoginForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('demo')
    await wrapper.findAll('input')[1].setValue('123456')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('账号或密码错误')
    vi.unstubAllGlobals()
  })

  it('成功登录后触发 success 事件', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        data: { access_token: 'token', is_member: true },
      }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const wrapper = mount(LoginForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('alice')
    await wrapper.findAll('input')[1].setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.emitted('success')).toBeTruthy()
    vi.unstubAllGlobals()
  })

  it('请求异常时提示连接失败', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network')))
    const wrapper = mount(LoginForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('alice')
    await wrapper.findAll('input')[1].setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('无法连接后端服务')
    vi.unstubAllGlobals()
  })
})

describe('RegisterForm', () => {
  it('密码不一致时显示错误信息', async () => {
    const wrapper = mount(RegisterForm, {
      props: { apiBase: '' },
    })
    await wrapper.findAll('input')[0].setValue('demo')
    await wrapper.findAll('input')[1].setValue('123456')
    await wrapper.findAll('input')[2].setValue('654321')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('两次密码输入不一致')
  })

  it('服务端失败时显示错误信息', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ message: '用户已存在' }),
      }),
    )
    const wrapper = mount(RegisterForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('demo')
    await wrapper.findAll('input')[1].setValue('123456')
    await wrapper.findAll('input')[2].setValue('123456')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('用户已存在')
    vi.unstubAllGlobals()
  })

  it('注册成功后触发 registered 事件', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ message: '注册成功' }),
      }),
    )
    const wrapper = mount(RegisterForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('demo')
    await wrapper.findAll('input')[1].setValue('123456')
    await wrapper.findAll('input')[2].setValue('123456')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.emitted('registered')).toBeTruthy()
    vi.unstubAllGlobals()
  })

  it('请求异常时提示连接失败', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network')))
    const wrapper = mount(RegisterForm, {
      props: { apiBase: '/api' },
    })
    await wrapper.findAll('input')[0].setValue('demo')
    await wrapper.findAll('input')[1].setValue('123456')
    await wrapper.findAll('input')[2].setValue('123456')
    await wrapper.find('form').trigger('submit.prevent')
    expect(wrapper.text()).toContain('无法连接后端服务')
    vi.unstubAllGlobals()
  })
})
