<script setup>
import { computed, reactive, ref } from 'vue'

const props = defineProps({
  apiBase: {
    type: String,
    default: '',
  },
  accessToken: {
    type: String,
    default: '',
  },
})
const emit = defineEmits(['analyzed'])

const reportMessage = ref('')
const reportError = ref('')
const isSubmitting = ref(false)

const industryOptions = [
  {
    label: '计算机行业',
    value: 'computer',
    children: ['后端方向', '前端方向', '人工智能方向', '产品运营方向'],
  },
  {
    label: '教育培训',
    value: 'education',
    children: ['技能培训', '考试辅导', '兴趣课程'],
  },
  {
    label: '电商零售',
    value: 'retail',
    children: ['校园电商', '社群团购', '二手交易'],
  },
  {
    label: '文化创意',
    value: 'creative',
    children: ['自媒体内容', '设计服务', '文创产品'],
  },
]

const reportForm = reactive({
  industryPrimary: '',
  industrySecondary: '',
  budget: '',
  rentTerm: '',
  rentMode: '',
  manpower: '',
  time投入: '',
  profitPerCustomer: '',
  targetAudience: '',
  hasChannel: '',
  differentiation: '',
  differentiationType: '',
  paybackPeriod: '',
})

const secondIndustryOptions = computed(() => {
  const target = industryOptions.find((item) => item.value === reportForm.industryPrimary)
  return target ? target.children : []
})

function onIndustryPrimaryChange() {
  reportForm.industrySecondary = ''
}

function resetNotice() {
  reportMessage.value = ''
  reportError.value = ''
}

async function submitReport() {
  resetNotice()

  if (!props.accessToken) {
    reportError.value = '登录信息已失效，请重新登录后提交'
    return
  }

  isSubmitting.value = true
  try {
    const response = await fetch(`${props.apiBase}/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${props.accessToken}`,
      },
      body: JSON.stringify(reportForm),
    })
    const rawText = await response.text()
    let result = {}
    if (rawText) {
      try {
        result = JSON.parse(rawText)
      } catch (parseError) {
        result = {}
      }
    }

    if (!response.ok) {
      reportError.value = result?.message || `提交失败（${response.status}），请稍后再试`
      return
    }

    reportMessage.value = '提交成功，正在给您返回分析'
    emit('analyzed', {
      reportId: result?.data?.report_id ?? 0,
      username: result?.data?.username ?? '',
      analysis: result?.data?.analysis ?? null,
    })
  } catch (error) {
    reportError.value = '无法连接后端服务，请检查服务是否已启动'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="report-form-wrap">
    <h2>创业调查问卷</h2>
    <form class="report-form" @submit.prevent="submitReport">
      <article class="bento-card size-2x1">
        <h3>行业选择</h3>
        <div class="field-grid">
          <label>
            1. 您想要创业的行业方向（一级）
            <select v-model="reportForm.industryPrimary" @change="onIndustryPrimaryChange">
              <option value="">请选择一级行业</option>
              <option v-for="item in industryOptions" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </label>

          <label>
            1.1 行业细分方向（二级）
            <select v-model="reportForm.industrySecondary" :disabled="!reportForm.industryPrimary">
              <option value="">请选择二级方向</option>
              <option v-for="item in secondIndustryOptions" :key="item" :value="item">
                {{ item }}
              </option>
            </select>
          </label>
        </div>
      </article>

      <article class="bento-card size-1x1">
        <h3>预算与周期</h3>
        <label>
          2. 您的成本投入预算
          <select v-model="reportForm.budget">
            <option value="">请选择预算区间</option>
            <option value="0-200">0-200元</option>
            <option value="200-1000">200-1k</option>
            <option value="1000-3000">1k-3k</option>
            <option value="3000-10000">3k-1w</option>
            <option value="10000+">1w以上</option>
          </select>
        </label>
        <label>
          11. 预计回本时间（day）
          <select v-model="reportForm.paybackPeriod">
            <option value="">请选择回本周期</option>
            <option value="10">10天内</option>
            <option value="10-30">10-30天</option>
            <option value="30+">30天以上</option>
          </select>
        </label>
      </article>

      <article class="bento-card size-1x1">
        <h3>场地配置</h3>
        <label>
          3. 场地租金（长期/短期）
          <select v-model="reportForm.rentTerm">
            <option value="">请选择周期</option>
            <option value="long">长期</option>
            <option value="short">短期</option>
          </select>
        </label>
        <label>
          3.1 场地形式（线上/摆摊）
          <select v-model="reportForm.rentMode">
            <option value="">请选择形式</option>
            <option value="online">线上</option>
            <option value="stall">摆摊</option>
          </select>
        </label>
      </article>

      <article class="bento-card size-2x1">
        <h3>团队与产出</h3>
        <div class="field-grid">
          <label>
            4. 人力规模
            <select v-model="reportForm.manpower">
              <option value="">请选择人力</option>
              <option value="1-3">1-3人</option>
              <option value="3-5">3-5人</option>
              <option value="7+">7人以上</option>
            </select>
          </label>

          <label>
            5. 投入时间
            <select v-model="reportForm.time投入">
              <option value="">请选择投入时间</option>
              <option value="11-31">11-31天</option>
              <option value="31+">31天以上</option>
            </select>
          </label>

          <label>
            6. 预期一个顾客能赚多少
            <select v-model="reportForm.profitPerCustomer">
              <option value="">请选择收益区间</option>
              <option value="0-10">0-10</option>
              <option value="10-15">10-15</option>
              <option value="15-20">15-20</option>
              <option value="20-30">20-30</option>
              <option value="30+">30以上</option>
            </select>
          </label>
        </div>
      </article>

      <article class="bento-card size-1x1">
        <h3>目标用户</h3>
        <label>
          7. 目标人群
          <select v-model="reportForm.targetAudience">
            <option value="">请选择目标人群</option>
            <option value="school">同校学生</option>
            <option value="social">社会人员</option>
            <option value="nearby-school">周边高校学生</option>
            <option value="office">周边上班族</option>
          </select>
        </label>
        <label>
          9. 是否有渠道
          <select v-model="reportForm.hasChannel">
            <option value="">请选择</option>
            <option value="yes">有</option>
            <option value="no">无</option>
          </select>
        </label>
      </article>

      <article class="bento-card size-1x2">
        <h3>竞争力</h3>
        <label>
          10. 差异化优势
          <select v-model="reportForm.differentiation">
            <option value="">请选择</option>
            <option value="none">无</option>
            <option value="has">有</option>
          </select>
        </label>

        <label v-if="reportForm.differentiation === 'has'">
          10.1 差异化类型（二级）
          <select v-model="reportForm.differentiationType">
            <option value="">请选择优势类型</option>
            <option value="network">人脉</option>
            <option value="storage">商品存储</option>
            <option value="location">场地位置</option>
            <option value="supply">供应链</option>
          </select>
        </label>
      </article>

      <article class="bento-card size-2x2 submit-card">
        <h3>确认提交</h3>
        <p>完成关键信息后提交，后续将接入自动分析与路径建议。</p>
        <button class="primary-btn" :disabled="isSubmitting" type="submit">
          {{ isSubmitting ? '提交中...' : '提交问卷' }}
        </button>
      </article>
    </form>
    <p v-if="reportMessage" class="message success">{{ reportMessage }}</p>
    <p v-if="reportError" class="message error">{{ reportError }}</p>
  </section>
</template>

<style scoped>
.report-form-wrap {
  width: 100%;
}

.report-form-wrap h2 {
  margin: 0 0 20px;
  font-size: clamp(1.25rem, 1.05rem + 0.9vw, 1.75rem);
}

.report-form {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}

.bento-card {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.34);
  border-radius: 16px;
  padding: 16px;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 12px 34px rgba(35, 55, 94, 0.12);
  transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
  will-change: transform;
}

.bento-card:hover {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 16px 40px rgba(35, 55, 94, 0.2);
  border-color: rgba(99, 102, 241, 0.35);
}

.bento-card h3 {
  margin: 0 0 12px;
  font-size: clamp(1rem, 0.9rem + 0.5vw, 1.2rem);
  font-weight: 700;
}

.size-1x1 {
  grid-column: span 4;
}

.size-1x2 {
  grid-column: span 4;
  grid-row: span 2;
}

.size-2x1 {
  grid-column: span 8;
}

.size-2x2 {
  grid-column: span 8;
  grid-row: span 2;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.submit-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.submit-card p {
  margin: 0 0 12px;
  color: rgba(31, 41, 55, 0.86);
  line-height: 1.55;
}

@media (max-width: 992px) {
  .size-1x1,
  .size-1x2,
  .size-2x1,
  .size-2x2 {
    grid-column: span 6;
    grid-row: span 1;
  }

  .field-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .report-form {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .size-1x1,
  .size-1x2,
  .size-2x1,
  .size-2x2 {
    grid-column: span 1;
  }

  .bento-card {
    padding: 14px;
    border-radius: 14px;
  }
}
</style>
