# 迁移指引

## 技术栈约束
- 样式栈：Tailwind CSS（通过 `@tailwind` 与 `@layer` 驱动）
- 禁止：Styled-components / Emotion 混用

## 旧类名映射与废弃建议
| 旧类名 | 新类名 | 状态 |
| --- | --- | --- |
| `primary-btn` | `ui-button ui-button--primary` | 废弃 |
| `ghost-btn` | `ui-button ui-button--ghost` | 废弃 |
| `glass-card` | `ui-card` | 废弃 |
| `auth-switch` | `ui-tabs` | 废弃 |
| `tabs` | `ui-tabs` | 废弃 |
| `tabs button.active` | `ui-tabs__item is-active` | 废弃 |
| `top-nav`（旧视觉） | `top-nav`（新视觉） | 保留并重定义 |

## 文件结构变更
- 新增：`src/styles/tokens.css`
- 新增：`src/styles/theme.css`
- 新增：`src/styles/components.css`
- 新增：`src/styles/layout.css`
- 新增：`src/styles/motion.css`
- 更新：`src/style.css` 仅负责样式入口与导入
- 删除：各 Vue 文件内 `<style>` 块，统一外置

## 主题扩展接口
- 默认主题：`data-theme="light"`
- 可扩展主题：`data-theme="dark"` 或品牌主题 `data-theme="brand-x"`
- 新主题仅需覆写 `theme.css` 变量，无需改组件结构

## 回滚建议
- 如需快速回滚，保留 `design/tokens.json` 与新样式目录，切回旧 `App.vue` 模板即可。
