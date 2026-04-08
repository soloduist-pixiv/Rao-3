<script setup>
import { computed } from 'vue'

const props = defineProps({
  analysis: {
    type: Object,
    default: null,
  },
})

const fieldLabels = {
  industry_primary: '一级行业',
  industry_secondary: '二级细分',
  budget: '投入预算',
  rent_term: '场地租期',
  rent_mode: '场地形式',
  manpower: '人力规模',
  time_input: '时间投入',
  profit_per_customer: '单客收益',
  target_audience: '目标人群',
  has_channel: '渠道条件',
  differentiation: '差异化',
  differentiation_type: '优势类型',
  payback_period: '回本周期',
}

const scoreRows = computed(() => {
  const scores = props.analysis?.field_scores || {}
  return Object.keys(fieldLabels).map((key) => {
    const item = scores[key] || {}
    return {
      key,
      label: fieldLabels[key],
      comment: item.comment || '暂无',
      score: Number.isFinite(item.score) ? item.score : 0,
    }
  })
})

const totalScore = computed(() => props.analysis?.total_score ?? 0)
const overallComment = computed(() => props.analysis?.overall_comment || '暂无结果')

const radarSize = 360
const radarCenter = radarSize / 2
const radarRadius = 122
const radarLevels = [0.2, 0.4, 0.6, 0.8, 1]

function getRadarPoint(index, ratio, count) {
  const angle = -Math.PI / 2 + (index * Math.PI * 2) / count
  const radius = radarRadius * ratio
  return {
    x: radarCenter + Math.cos(angle) * radius,
    y: radarCenter + Math.sin(angle) * radius,
  }
}

const radarGridPolygons = computed(() => {
  const count = Math.max(scoreRows.value.length, 3)
  return radarLevels.map((level) =>
    scoreRows.value
      .map((_, index) => {
        const point = getRadarPoint(index, level, count)
        return `${point.x},${point.y}`
      })
      .join(' '),
  )
})

const radarAxisLines = computed(() => {
  const count = Math.max(scoreRows.value.length, 3)
  return scoreRows.value.map((_, index) => {
    const point = getRadarPoint(index, 1, count)
    return {
      x1: radarCenter,
      y1: radarCenter,
      x2: point.x,
      y2: point.y,
    }
  })
})

const radarDataPolygon = computed(() => {
  const count = Math.max(scoreRows.value.length, 3)
  return scoreRows.value
    .map((row, index) => {
      const point = getRadarPoint(index, Math.max(0, Math.min(1, row.score / 100)), count)
      return `${point.x},${point.y}`
    })
    .join(' ')
})

const radarDataDots = computed(() => {
  const count = Math.max(scoreRows.value.length, 3)
  return scoreRows.value.map((row, index) => {
    const point = getRadarPoint(index, Math.max(0, Math.min(1, row.score / 100)), count)
    return { ...point, label: row.label, score: row.score }
  })
})

const radarLabels = computed(() => {
  const count = Math.max(scoreRows.value.length, 3)
  return scoreRows.value.map((row, index) => {
    const point = getRadarPoint(index, 1.14, count)
    const anchor = point.x > radarCenter + 8 ? 'start' : point.x < radarCenter - 8 ? 'end' : 'middle'
    return { ...point, label: row.label, anchor }
  })
})

const curvePoints = computed(() => {
  const cost = Array.isArray(props.analysis?.time_cost_points) ? props.analysis.time_cost_points : []
  const profit = Array.isArray(props.analysis?.time_profit_points) ? props.analysis.time_profit_points : []
  const safeCost = cost
    .map((point) => ({ x: Number(point?.x), y: Number(point?.y) }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
  const safeProfit = profit
    .map((point) => ({ x: Number(point?.x), y: Number(point?.y) }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
  safeCost.sort((a, b) => a.x - b.x)
  safeProfit.sort((a, b) => a.x - b.x)
  return {
    cost: safeCost,
    profit: safeProfit,
  }
})

const curveChart = computed(() => {
  const costPoints = curvePoints.value.cost
  const profitPoints = curvePoints.value.profit
  if (!costPoints.length || !profitPoints.length) {
    return null
  }

  const width = 860
  const height = 360
  const padding = { top: 20, right: 24, bottom: 42, left: 62 }
  const allX = [...costPoints, ...profitPoints].map((item) => item.x)
  const allY = [...costPoints, ...profitPoints].map((item) => item.y)
  const minX = Math.min(...allX)
  const maxX = Math.max(...allX)
  const maxY = Math.max(...allY, 1)

  const xScale = (value) =>
    padding.left + ((value - minX) / Math.max(1, maxX - minX)) * (width - padding.left - padding.right)
  const yScale = (value) =>
    height - padding.bottom - (value / maxY) * (height - padding.top - padding.bottom)

  const buildPath = (points) =>
    points
      .map((point, index) => `${index === 0 ? 'M' : 'L'} ${xScale(point.x).toFixed(2)} ${yScale(point.y).toFixed(2)}`)
      .join(' ')

  const xTicks = costPoints.map((point) => ({
    value: point.x,
    x: xScale(point.x),
  }))
  const yTicks = Array.from({ length: 6 }).map((_, index) => {
    const value = (maxY / 5) * index
    return {
      value: Math.round(value),
      y: yScale(value),
    }
  })

  const seriesLength = Math.min(costPoints.length, profitPoints.length)
  let paybackPoint = null
  for (let index = 0; index < seriesLength; index += 1) {
    const costPoint = costPoints[index]
    const profitPoint = profitPoints[index]
    const currentDiff = profitPoint.y - costPoint.y
    if (currentDiff >= 0) {
      if (index === 0) {
        paybackPoint = {
          x: Number(costPoint.x.toFixed(2)),
          y: Number(costPoint.y.toFixed(2)),
        }
      } else {
        const prevCost = costPoints[index - 1]
        const prevProfit = profitPoints[index - 1]
        const prevDiff = prevProfit.y - prevCost.y
        const ratio = prevDiff === currentDiff ? 0 : (0 - prevDiff) / (currentDiff - prevDiff)
        const safeRatio = Math.max(0, Math.min(1, ratio))
        const crossX = prevCost.x + (costPoint.x - prevCost.x) * safeRatio
        const crossY = prevCost.y + (costPoint.y - prevCost.y) * safeRatio
        paybackPoint = {
          x: Number(crossX.toFixed(2)),
          y: Number(crossY.toFixed(2)),
        }
      }
      break
    }
  }

  return {
    width,
    height,
    padding,
    costPath: buildPath(costPoints),
    profitPath: buildPath(profitPoints),
    costDots: costPoints.map((point) => ({ ...point, cx: xScale(point.x), cy: yScale(point.y) })),
    profitDots: profitPoints.map((point) => ({ ...point, cx: xScale(point.x), cy: yScale(point.y) })),
    xTicks,
    yTicks,
    paybackPoint: paybackPoint
      ? {
          ...paybackPoint,
          cx: xScale(paybackPoint.x),
          cy: yScale(paybackPoint.y),
        }
      : null,
  }
})
</script>

<template>
  <section class="analysis-wrap">
    <h2>创业分析结果</h2>
    <section class="summary-grid">
      <article class="bento-card score-card">
        <h3>综合得分</h3>
        <strong>{{ totalScore }}</strong>
        <p>满分 100</p>
      </article>
      <article class="bento-card summary-card">
        <h3>综合结论</h3>
        <p>{{ overallComment }}</p>
      </article>
    </section>

    <section class="chart-grid">
      <article class="bento-card radar-card">
        <h3>维度雷达图</h3>
        <svg :viewBox="`0 0 ${radarSize} ${radarSize}`" class="radar-svg" role="img" aria-label="维度雷达图">
          <polygon
            v-for="(polygon, idx) in radarGridPolygons"
            :key="`grid-${idx}`"
            :points="polygon"
            fill="none"
            stroke="rgba(148, 163, 184, 0.45)"
            stroke-width="1"
          />
          <line
            v-for="(line, idx) in radarAxisLines"
            :key="`axis-${idx}`"
            :x1="line.x1"
            :y1="line.y1"
            :x2="line.x2"
            :y2="line.y2"
            stroke="rgba(148, 163, 184, 0.4)"
            stroke-width="1"
          />
          <polygon :points="radarDataPolygon" fill="rgba(56, 189, 248, 0.24)" stroke="#38bdf8" stroke-width="2" />
          <circle
            v-for="(dot, idx) in radarDataDots"
            :key="`dot-${idx}`"
            :cx="dot.x"
            :cy="dot.y"
            r="3.2"
            fill="#22d3ee"
          />
          <text
            v-for="(label, idx) in radarLabels"
            :key="`label-${idx}`"
            :x="label.x"
            :y="label.y"
            :text-anchor="label.anchor"
            dominant-baseline="middle"
            class="radar-label"
          >
            {{ label.label }}
          </text>
        </svg>
      </article>

      <article class="bento-card line-card">
        <h3>时间-成本 / 时间-利润</h3>
        <svg
          v-if="curveChart"
          :viewBox="`0 0 ${curveChart.width} ${curveChart.height}`"
          class="line-svg"
          role="img"
          aria-label="时间成本利润曲线图"
        >
          <line
            v-for="(tick, idx) in curveChart.yTicks"
            :key="`y-grid-${idx}`"
            :x1="curveChart.padding.left"
            :x2="curveChart.width - curveChart.padding.right"
            :y1="tick.y"
            :y2="tick.y"
            stroke="rgba(148, 163, 184, 0.28)"
            stroke-width="1"
          />
          <line
            :x1="curveChart.padding.left"
            :x2="curveChart.padding.left"
            :y1="curveChart.padding.top"
            :y2="curveChart.height - curveChart.padding.bottom"
            stroke="rgba(148, 163, 184, 0.5)"
            stroke-width="1.2"
          />
          <line
            :x1="curveChart.padding.left"
            :x2="curveChart.width - curveChart.padding.right"
            :y1="curveChart.height - curveChart.padding.bottom"
            :y2="curveChart.height - curveChart.padding.bottom"
            stroke="rgba(148, 163, 184, 0.5)"
            stroke-width="1.2"
          />
          <path :d="curveChart.costPath" fill="none" stroke="#f59e0b" stroke-width="2.4" />
          <path :d="curveChart.profitPath" fill="none" stroke="#22c55e" stroke-width="2.4" />
          <circle v-for="(dot, idx) in curveChart.costDots" :key="`cost-dot-${idx}`" :cx="dot.cx" :cy="dot.cy" r="3" fill="#f59e0b" />
          <circle
            v-for="(dot, idx) in curveChart.profitDots"
            :key="`profit-dot-${idx}`"
            :cx="dot.cx"
            :cy="dot.cy"
            r="3"
            fill="#22c55e"
          />
          <line
            v-if="curveChart.paybackPoint"
            :x1="curveChart.paybackPoint.cx"
            :x2="curveChart.paybackPoint.cx"
            :y1="curveChart.paybackPoint.cy"
            :y2="curveChart.height - curveChart.padding.bottom"
            stroke="#f43f5e"
            stroke-width="1.4"
            stroke-dasharray="5 5"
          />
          <line
            v-if="curveChart.paybackPoint"
            :x1="curveChart.padding.left"
            :x2="curveChart.paybackPoint.cx"
            :y1="curveChart.paybackPoint.cy"
            :y2="curveChart.paybackPoint.cy"
            stroke="#f43f5e"
            stroke-width="1.4"
            stroke-dasharray="5 5"
          />
          <circle
            v-if="curveChart.paybackPoint"
            :cx="curveChart.paybackPoint.cx"
            :cy="curveChart.paybackPoint.cy"
            r="5.2"
            fill="#f43f5e"
            stroke="#fecdd3"
            stroke-width="1.5"
          />
          <text
            v-if="curveChart.paybackPoint"
            :x="Math.min(curveChart.width - curveChart.padding.right - 60, curveChart.paybackPoint.cx + 8)"
            :y="Math.max(curveChart.padding.top + 14, curveChart.paybackPoint.cy - 10)"
            class="payback-label"
          >
            回本点 {{ curveChart.paybackPoint.x }}天
          </text>
          <text
            v-for="(tick, idx) in curveChart.xTicks"
            :key="`x-tick-${idx}`"
            :x="tick.x"
            :y="curveChart.height - 16"
            text-anchor="middle"
            class="axis-label"
          >
            {{ tick.value }}天
          </text>
          <text
            v-for="(tick, idx) in curveChart.yTicks"
            :key="`y-tick-${idx}`"
            :x="curveChart.padding.left - 10"
            :y="tick.y"
            text-anchor="end"
            dominant-baseline="middle"
            class="axis-label"
          >
            {{ tick.value }}
          </text>
          <text :x="curveChart.width / 2" :y="curveChart.height - 2" text-anchor="middle" class="axis-title">时间（天）</text>
          <text
            :x="18"
            :y="curveChart.height / 2"
            text-anchor="middle"
            class="axis-title"
            transform="rotate(-90 18, 180)"
          >
            金额
          </text>
        </svg>
        <p v-else class="empty-tip">暂无曲线数据</p>
        <p v-if="curveChart?.paybackPoint" class="payback-tip">
          预计在第 {{ curveChart.paybackPoint.x }} 天达到回本点（利润首次超过成本）。
        </p>
        <p v-else-if="curveChart" class="payback-tip payback-tip--pending">
          当前周期内尚未出现回本点。
        </p>
        <div class="legend-row">
          <span><i class="legend-dot legend-dot--cost"></i>成本曲线</span>
          <span><i class="legend-dot legend-dot--profit"></i>利润曲线</span>
          <span><i class="legend-dot legend-dot--payback"></i>回本点</span>
        </div>
      </article>
    </section>

    <section class="field-grid">
      <article v-for="row in scoreRows" :key="row.key" class="bento-card row-card">
        <div class="row-title">
          <span>{{ row.label }}</span>
          <strong>{{ row.score }}</strong>
        </div>
        <p>{{ row.comment }}</p>
      </article>
    </section>
  </section>
</template>

<style scoped>
.analysis-wrap {
  width: 100%;
}

.analysis-wrap h2 {
  margin: 0 0 20px;
  font-size: clamp(1.25rem, 1.05rem + 0.9vw, 1.75rem);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.field-grid {
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
}

.score-card {
  grid-column: span 4;
}

.summary-card {
  grid-column: span 8;
}

.radar-card {
  grid-column: span 5;
}

.line-card {
  grid-column: span 7;
}

.score-card strong {
  display: block;
  font-size: 2rem;
  margin: 8px 0;
  color: #ecfeff;
}

.score-card p,
.summary-card p,
.row-card p {
  margin: 0;
  color: rgba(226, 232, 240, 0.92);
}

.radar-svg,
.line-svg {
  width: 100%;
  height: auto;
  display: block;
}

.radar-label {
  fill: rgba(241, 245, 249, 0.9);
  font-size: 11px;
}

.axis-label {
  fill: rgba(226, 232, 240, 0.86);
  font-size: 11px;
}

.axis-title {
  fill: rgba(226, 232, 240, 0.95);
  font-size: 12px;
  font-weight: 600;
}

.payback-label {
  fill: #ffe4e6;
  font-size: 11px;
  font-weight: 700;
}

.legend-row {
  margin-top: 10px;
  display: flex;
  gap: 18px;
  color: rgba(226, 232, 240, 0.92);
  font-size: 0.86rem;
}

.legend-row span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}

.legend-dot--cost {
  background: #f59e0b;
}

.legend-dot--profit {
  background: #22c55e;
}

.legend-dot--payback {
  background: #f43f5e;
}

.empty-tip {
  margin: 10px 0 0;
  color: rgba(226, 232, 240, 0.85);
}

.payback-tip {
  margin: 10px 0 0;
  color: rgba(254, 226, 226, 0.95);
  font-size: 0.86rem;
}

.payback-tip--pending {
  color: rgba(226, 232, 240, 0.92);
}

.row-card {
  grid-column: span 4;
}

.row-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.row-title strong {
  color: #a5f3fc;
}

@media (max-width: 992px) {
  .score-card,
  .summary-card,
  .radar-card,
  .line-card,
  .row-card {
    grid-column: span 6;
  }
}

@media (max-width: 640px) {
  .summary-grid,
  .chart-grid,
  .field-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .score-card,
  .summary-card,
  .radar-card,
  .line-card,
  .row-card {
    grid-column: span 1;
  }
}
</style>
