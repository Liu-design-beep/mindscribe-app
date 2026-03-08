/* ============================================================
   灵辑 MindScribe · 数据看板嵌入模块
   负责：① 侧边栏按钮交互  ② 看板 HTML 内容注入  ③ 图表初始化
   ============================================================ */

(function () {
  'use strict';

  // ============================================================
  // 工具函数
  // ============================================================
  function genDayLabels(n) {
    const labels = [];
    for (let i = n - 1; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      labels.push((d.getMonth() + 1) + '/' + d.getDate());
    }
    return labels;
  }

  function genRandArr(len, min, max) {
    const arr = [];
    let cur = (min + max) / 2;
    for (let i = 0; i < len; i++) {
      cur += (Math.random() - 0.45) * (max - min) * 0.12;
      cur = Math.max(min, Math.min(max, cur));
      arr.push(Math.round(cur * 10) / 10);
    }
    return arr;
  }

  // ============================================================
  // 看板完整 HTML 模板
  // ============================================================
  function getDashboardHTML() {
    return `
<!-- 北极星指标横幅 -->
<div class="polar-star-banner" id="polarBanner">
  <div class="polar-label"><span class="star-icon">★</span> 北极星指标 · 12 项核心 KPI</div>
  <div class="polar-metrics" id="polarMetrics"></div>
</div>

<!-- 主体 -->
<div class="dashboard-main">

  <!-- ① 入口层 -->
  <section class="layer-section" id="layer-entry">
    <div class="layer-header entry-header">
      <div class="layer-tag">01</div>
      <div class="layer-info">
        <div class="layer-title">入口层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">用户怎么来？</span></div>
        <div class="layer-subtitle">流量获取 → 渠道转化 → 功能激活 · 追踪用户从曝光到首次使用的完整漏斗</div>
      </div>
      <div class="layer-flow">进 →</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card entry-card">
        <div class="kpi-label">日活用户 DAU</div>
        <div class="kpi-value polar-star-metric">12,480</div>
        <div class="kpi-delta positive">↑ 8.3%</div>
        <div class="kpi-sub">较上周</div>
      </div>
      <div class="kpi-card entry-card">
        <div class="kpi-label">月活用户 MAU</div>
        <div class="kpi-value">89,320</div>
        <div class="kpi-delta positive">↑ 12.1%</div>
        <div class="kpi-sub">较上月</div>
      </div>
      <div class="kpi-card entry-card">
        <div class="kpi-label">新用户量（今日）</div>
        <div class="kpi-value">1,847</div>
        <div class="kpi-delta positive">↑ 5.6%</div>
        <div class="kpi-sub">较昨日</div>
      </div>
      <div class="kpi-card entry-card">
        <div class="kpi-label">功能激活率</div>
        <div class="kpi-value">73.2%</div>
        <div class="kpi-delta positive">↑ 2.4%</div>
        <div class="kpi-sub">打开AI功能用户占比</div>
      </div>
      <div class="kpi-card entry-card">
        <div class="kpi-label">首问率</div>
        <div class="kpi-value polar-star-metric">68.5%</div>
        <div class="kpi-delta positive">↑ 3.1%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card entry-card">
        <div class="kpi-label">落地页抵达率</div>
        <div class="kpi-value">61.8%</div>
        <div class="kpi-delta negative">↓ 1.2%</div>
        <div class="kpi-sub">CTR → 落地页</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card wide"><div class="chart-title">DAU/MAU 趋势（近30天）</div><canvas id="db_dauChart" height="120"></canvas></div>
      <div class="chart-card"><div class="chart-title">渠道来源分布</div><canvas id="db_channelChart" height="180"></canvas></div>
      <div class="chart-card"><div class="chart-title">新用户激活漏斗</div><canvas id="db_funnelChart" height="180"></canvas></div>
    </div>
  </section>

  <!-- ② 交互层 -->
  <section class="layer-section" id="layer-interact">
    <div class="layer-header interact-header">
      <div class="layer-tag">02</div>
      <div class="layer-info">
        <div class="layer-title">交互层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">用户真的在用吗？</span></div>
        <div class="layer-subtitle">会话深度 → 行为质量 → 满意信号 · 衡量用户与灵辑 AI 的真实互动质量</div>
      </div>
      <div class="layer-flow">问 →</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card interact-card">
        <div class="kpi-label">日均会话数</div>
        <div class="kpi-value">34,210</div>
        <div class="kpi-delta positive">↑ 6.7%</div>
        <div class="kpi-sub">较上周</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">人均会话数</div>
        <div class="kpi-value">2.74</div>
        <div class="kpi-delta positive">↑ 0.3</div>
        <div class="kpi-sub">次/天</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">多轮对话占比</div>
        <div class="kpi-value">58.3%</div>
        <div class="kpi-delta positive">↑ 4.2%</div>
        <div class="kpi-sub">3轮以上</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">平均对话时长</div>
        <div class="kpi-value">4.8 min</div>
        <div class="kpi-delta positive">↑ 0.6 min</div>
        <div class="kpi-sub">较上周</div>
      </div>
      <div class="kpi-card interact-card alert-card">
        <div class="kpi-label">中断率</div>
        <div class="kpi-value" style="color:var(--warn)">18.4%</div>
        <div class="kpi-delta negative">↑ 1.1%</div>
        <div class="kpi-sub">问一半退出</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">复制率</div>
        <div class="kpi-value polar-star-metric">42.6%</div>
        <div class="kpi-delta positive">↑ 3.8%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">点赞率</div>
        <div class="kpi-value">31.2%</div>
        <div class="kpi-delta positive">↑ 2.1%</div>
        <div class="kpi-sub">有用反馈</div>
      </div>
      <div class="kpi-card interact-card">
        <div class="kpi-label">重新生成率</div>
        <div class="kpi-value">12.7%</div>
        <div class="kpi-delta positive">↑ 0.8%</div>
        <div class="kpi-sub">不满意重试</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">对话轮次分布</div><canvas id="db_roundsChart" height="180"></canvas></div>
      <div class="chart-card"><div class="chart-title">用户行为信号分布</div><canvas id="db_behaviorChart" height="180"></canvas></div>
      <div class="chart-card"><div class="chart-title">输入方式占比</div><canvas id="db_inputTypeChart" height="180"></canvas></div>
    </div>
  </section>

  <!-- ③ AI 核心层 -->
  <section class="layer-section" id="layer-ai">
    <div class="layer-header ai-header">
      <div class="layer-tag">03</div>
      <div class="layer-info">
        <div class="layer-title">AI 核心层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">模型 &amp; 效果</span></div>
        <div class="layer-subtitle">模型效果 → 生成质量 → 性能体验 · AI PM 最核心的技术+产品结合指标</div>
      </div>
      <div class="layer-flow">答 →</div>
    </div>
    <div class="sub-section-title" style="border-left-color:var(--ai-color)">模型效果指标</div>
    <div class="metrics-grid">
      <div class="kpi-card ai-card">
        <div class="kpi-label">意图识别准确率</div>
        <div class="kpi-value">94.7%</div>
        <div class="kpi-delta positive">↑ 1.3%</div>
        <div class="kpi-sub">ADD/SUMMARY/DELETE 等</div>
      </div>
      <div class="kpi-card ai-card">
        <div class="kpi-label">回答有用率</div>
        <div class="kpi-value polar-star-metric">87.3%</div>
        <div class="kpi-delta positive">↑ 2.8%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card ai-card alert-card">
        <div class="kpi-label">幻觉率</div>
        <div class="kpi-value polar-star-metric" style="color:var(--warn)">3.2%</div>
        <div class="kpi-delta positive">↓ 0.5%</div>
        <div class="kpi-sub">★ 北极星指标（越低越好）</div>
      </div>
      <div class="kpi-card ai-card">
        <div class="kpi-label">上下文理解正确率</div>
        <div class="kpi-value">91.4%</div>
        <div class="kpi-delta positive">↑ 1.9%</div>
        <div class="kpi-sub">多轮记忆命中</div>
      </div>
      <div class="kpi-card ai-card">
        <div class="kpi-label">拒绝率 / 安全拦截率</div>
        <div class="kpi-value polar-star-metric">1.8%</div>
        <div class="kpi-delta positive">↓ 0.3%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card ai-card">
        <div class="kpi-label">多轮记忆命中率</div>
        <div class="kpi-value">88.6%</div>
        <div class="kpi-delta positive">↑ 3.2%</div>
        <div class="kpi-sub">上下文连贯性</div>
      </div>
    </div>
    <div class="sub-section-title" style="border-left-color:var(--ai-color);margin-top:8px">生成质量指标</div>
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">生成质量六维雷达</div><canvas id="db_qualityRadar" height="200"></canvas></div>
      <div class="chart-card">
        <div class="chart-title">性能体验指标</div>
        <div class="perf-metrics">
          <div class="perf-item"><span class="perf-label">首包响应时间 <span class="star-tag">★</span></span><div class="perf-bar-wrap"><div class="perf-bar good-bar" style="width:75%;background:linear-gradient(90deg,#10b981,rgba(16,185,129,0.5))"></div></div><span class="perf-value good-value">1.24s</span></div>
          <div class="perf-item"><span class="perf-label">平均生成耗时</span><div class="perf-bar-wrap"><div class="perf-bar" style="width:55%;background:linear-gradient(90deg,#a855f7,rgba(168,85,247,0.5))"></div></div><span class="perf-value">3.87s</span></div>
          <div class="perf-item"><span class="perf-label">超时率</span><div class="perf-bar-wrap"><div class="perf-bar warn-bar" style="width:8%"></div></div><span class="perf-value warn-value">0.8%</span></div>
          <div class="perf-item"><span class="perf-label">失败率 / 报错率</span><div class="perf-bar-wrap"><div class="perf-bar warn-bar" style="width:5%"></div></div><span class="perf-value warn-value">0.5%</span></div>
          <div class="perf-item"><span class="perf-label">并发稳定性</span><div class="perf-bar-wrap"><div class="perf-bar good-bar" style="width:99.6%;background:linear-gradient(90deg,#10b981,rgba(16,185,129,0.5))"></div></div><span class="perf-value good-value">99.6%</span></div>
        </div>
      </div>
      <div class="chart-card"><div class="chart-title">响应耗时分布（ms）</div><canvas id="db_latencyChart" height="200"></canvas></div>
    </div>
    <!-- F2K 评测体系 -->
    <div class="sub-section-title" style="border-left-color:var(--ai-color);margin-top:8px">灵辑专属 · F2K 评测体系指标</div>
    <div class="f2k-grid">
      <div class="f2k-card write-domain">
        <div class="f2k-domain-title">写入域 · 数据结构化能力</div>
        <div class="f2k-metrics">
          <div class="f2k-item"><span class="f2k-name">分类准确率</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:93.1%"></div></div><span class="f2k-val good-f2k">93.1%<span class="f2k-target">目标 &gt;90%</span></span></div>
          <div class="f2k-item"><span class="f2k-name">语义概括度</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:88%"></div></div><span class="f2k-val good-f2k">0.88<span class="f2k-target">目标 &gt;0.85</span></span></div>
          <div class="f2k-item"><span class="f2k-name">去重查准率</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:99.2%"></div></div><span class="f2k-val good-f2k">99.2%<span class="f2k-target">目标 &gt;99%</span></span></div>
          <div class="f2k-item"><span class="f2k-name">增量融合成功率</span><div class="f2k-bar-wrap"><div class="f2k-bar warn-bar" style="width:78.4%"></div></div><span class="f2k-val warn-f2k">78.4%<span class="f2k-target">目标 &gt;80%</span></span></div>
        </div>
      </div>
      <div class="f2k-card read-domain">
        <div class="f2k-domain-title">读取域 · 检索与召回能力</div>
        <div class="f2k-metrics">
          <div class="f2k-item"><span class="f2k-name">模糊查询召回率@3</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:87.3%"></div></div><span class="f2k-val good-f2k">87.3%<span class="f2k-target">目标 &gt;85%</span></span></div>
          <div class="f2k-item"><span class="f2k-name">上下文完整性</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:91.2%"></div></div><span class="f2k-val good-f2k">91.2%<span class="f2k-target">目标 &gt;90%</span></span></div>
          <div class="f2k-item"><span class="f2k-name">多跳聚合准确率</span><div class="f2k-bar-wrap"><div class="f2k-bar good-bar" style="width:82.1%"></div></div><span class="f2k-val good-f2k">82.1%<span class="f2k-target">目标 &gt;80%</span></span></div>
          <div class="f2k-item"><span class="f2k-name">幻觉率（RAG）</span><div class="f2k-bar-wrap"><div class="f2k-bar warn-bar" style="width:3.2%"></div></div><span class="f2k-val good-f2k">3.2%<span class="f2k-target">目标 &lt;5%</span></span></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ④ 功能层 -->
  <section class="layer-section" id="layer-feature">
    <div class="layer-header feature-header">
      <div class="layer-tag">04</div>
      <div class="layer-info">
        <div class="layer-title">功能层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">AI 功能有没有价值？</span></div>
        <div class="layer-subtitle">功能渗透 → 任务完成 → 用户满意 · 评估灵辑各 AI 功能的实际使用价值</div>
      </div>
      <div class="layer-flow">用 →</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card feature-card">
        <div class="kpi-label">功能渗透率（核心）</div>
        <div class="kpi-value polar-star-metric">71.4%</div>
        <div class="kpi-delta positive">↑ 4.6%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card feature-card">
        <div class="kpi-label">任务成功率</div>
        <div class="kpi-value polar-star-metric">82.9%</div>
        <div class="kpi-delta positive">↑ 2.3%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card feature-card">
        <div class="kpi-label">一次成功率</div>
        <div class="kpi-value">67.8%</div>
        <div class="kpi-delta positive">↑ 3.5%</div>
        <div class="kpi-sub">无需修正</div>
      </div>
      <div class="kpi-card feature-card">
        <div class="kpi-label">有用率</div>
        <div class="kpi-value polar-star-metric">87.3%</div>
        <div class="kpi-delta positive">↑ 2.8%</div>
        <div class="kpi-sub">★ 点赞/(点赞+点踩)</div>
      </div>
      <div class="kpi-card feature-card">
        <div class="kpi-label">NPS 净推荐值</div>
        <div class="kpi-value">+42</div>
        <div class="kpi-delta positive">↑ 6</div>
        <div class="kpi-sub">较上季度</div>
      </div>
      <div class="kpi-card feature-card">
        <div class="kpi-label">平均修正次数</div>
        <div class="kpi-value">1.3 次</div>
        <div class="kpi-delta positive">↓ 0.2</div>
        <div class="kpi-sub">越低越好</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card wide"><div class="chart-title">各 AI 功能使用渗透率（灵辑功能模块）</div><canvas id="db_featurePenetrationChart" height="200"></canvas></div>
      <div class="chart-card"><div class="chart-title">负面反馈类型分布</div><canvas id="db_feedbackChart" height="200"></canvas></div>
    </div>
  </section>

  <!-- ⑤ 留存层 -->
  <section class="layer-section" id="layer-retain">
    <div class="layer-header retain-header">
      <div class="layer-tag">05</div>
      <div class="layer-info">
        <div class="layer-title">留存层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">用户为什么不走？</span></div>
        <div class="layer-subtitle">留存曲线 → 粘性指标 → 流失分析 · 判断灵辑是否成为用户的长期习惯</div>
      </div>
      <div class="layer-flow">留 →</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card retain-card">
        <div class="kpi-label">次日留存率</div>
        <div class="kpi-value">48.2%</div>
        <div class="kpi-delta positive">↑ 2.1%</div>
        <div class="kpi-sub">较上周</div>
      </div>
      <div class="kpi-card retain-card">
        <div class="kpi-label">7日留存率</div>
        <div class="kpi-value polar-star-metric">31.6%</div>
        <div class="kpi-delta positive">↑ 1.8%</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card retain-card">
        <div class="kpi-label">30日留存率</div>
        <div class="kpi-value">18.4%</div>
        <div class="kpi-delta positive">↑ 1.3%</div>
        <div class="kpi-sub">月留存</div>
      </div>
      <div class="kpi-card retain-card">
        <div class="kpi-label">日均提问数</div>
        <div class="kpi-value polar-star-metric">5.7 次</div>
        <div class="kpi-delta positive">↑ 0.4</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card retain-card">
        <div class="kpi-label">高价值用户占比</div>
        <div class="kpi-value">23.8%</div>
        <div class="kpi-delta positive">↑ 1.6%</div>
        <div class="kpi-sub">高频使用用户</div>
      </div>
      <div class="kpi-card retain-card">
        <div class="kpi-label">功能粘性用户</div>
        <div class="kpi-value">34.1%</div>
        <div class="kpi-delta positive">↑ 2.9%</div>
        <div class="kpi-sub">核心功能依赖</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card wide"><div class="chart-title">用户留存曲线（新用户队列）</div><canvas id="db_retentionChart" height="140"></canvas></div>
      <div class="chart-card"><div class="chart-title">流失原因分析</div><canvas id="db_churnChart" height="200"></canvas></div>
    </div>
  </section>

  <!-- ⑥ 商业化层 -->
  <section class="layer-section" id="layer-biz">
    <div class="layer-header biz-header">
      <div class="layer-tag">06</div>
      <div class="layer-info">
        <div class="layer-title">商业化层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">ToC + ToB 变现</span></div>
        <div class="layer-subtitle">付费转化 → 收入健康 → 成本控制 · 验证灵辑商业模式的可持续性</div>
      </div>
      <div class="layer-flow">转 →</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card biz-card">
        <div class="kpi-label">付费转化率</div>
        <div class="kpi-value">6.8%</div>
        <div class="kpi-delta positive">↑ 0.7%</div>
        <div class="kpi-sub">免费→付费</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">ARPU</div>
        <div class="kpi-value polar-star-metric">¥18.4</div>
        <div class="kpi-delta positive">↑ ¥1.2</div>
        <div class="kpi-sub">★ 北极星指标</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">ARPPU</div>
        <div class="kpi-value">¥270.6</div>
        <div class="kpi-delta positive">↑ ¥18</div>
        <div class="kpi-sub">付费用户均值</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">会员渗透率</div>
        <div class="kpi-value">8.3%</div>
        <div class="kpi-delta positive">↑ 0.9%</div>
        <div class="kpi-sub">订阅用户占比</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">单用户推理成本</div>
        <div class="kpi-value polar-star-metric">¥0.032</div>
        <div class="kpi-delta positive">↓ ¥0.004</div>
        <div class="kpi-sub">★ 北极星指标（越低越好）</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">商业化健康度</div>
        <div class="kpi-value" style="color:var(--positive)">2.87x</div>
        <div class="kpi-delta positive">↑ 0.23x</div>
        <div class="kpi-sub">收入 / 模型成本</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">复购率</div>
        <div class="kpi-value">71.4%</div>
        <div class="kpi-delta positive">↑ 3.2%</div>
        <div class="kpi-sub">续费/复购</div>
      </div>
      <div class="kpi-card biz-card">
        <div class="kpi-label">成本回收周期</div>
        <div class="kpi-value">4.2 月</div>
        <div class="kpi-delta positive">↓ 0.3月</div>
        <div class="kpi-sub">CAC 回收</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card wide"><div class="chart-title">月收入 vs 模型成本趋势</div><canvas id="db_revenueChart" height="160"></canvas></div>
      <div class="chart-card"><div class="chart-title">付费用户分层</div><canvas id="db_payTierChart" height="200"></canvas></div>
    </div>
  </section>

  <!-- ⑦ 安全合规层 -->
  <section class="layer-section" id="layer-safety">
    <div class="layer-header safety-header">
      <div class="layer-tag">07</div>
      <div class="layer-info">
        <div class="layer-title">安全合规层 <span style="font-size:16px;font-weight:400;color:var(--text-secondary)">AI PM 必背</span></div>
        <div class="layer-subtitle">内容安全 → 合规风险 → 用户投诉 · 灵辑 AI 内容生成的安全底线指标</div>
      </div>
      <div class="layer-flow">守 ✓</div>
    </div>
    <div class="metrics-grid">
      <div class="kpi-card safety-card">
        <div class="kpi-label">违规内容拦截率</div>
        <div class="kpi-value" style="color:var(--positive)">99.7%</div>
        <div class="kpi-delta positive">↑ 0.1%</div>
        <div class="kpi-sub">安全过滤</div>
      </div>
      <div class="kpi-card safety-card">
        <div class="kpi-label">有害生成率</div>
        <div class="kpi-value" style="color:var(--positive)">0.03%</div>
        <div class="kpi-delta positive">↓ 0.01%</div>
        <div class="kpi-sub">越低越好</div>
      </div>
      <div class="kpi-card safety-card">
        <div class="kpi-label">用户投诉率</div>
        <div class="kpi-value">0.18%</div>
        <div class="kpi-delta positive">↓ 0.02%</div>
        <div class="kpi-sub">较上月</div>
      </div>
      <div class="kpi-card safety-card">
        <div class="kpi-label">审核响应时长</div>
        <div class="kpi-value">2.4h</div>
        <div class="kpi-delta positive">↓ 0.3h</div>
        <div class="kpi-sub">平均处理时长</div>
      </div>
      <div class="kpi-card safety-card alert-card">
        <div class="kpi-label">隐私合规风险点</div>
        <div class="kpi-value" style="color:var(--warn)">3 项</div>
        <div class="kpi-delta positive">↓ 1</div>
        <div class="kpi-sub">待处理风险</div>
      </div>
    </div>
    <div class="charts-row">
      <div class="chart-card wide"><div class="chart-title">安全拦截趋势（近30天）</div><canvas id="db_safetyChart" height="140"></canvas></div>
      <div class="chart-card"><div class="chart-title">违规类型分布</div><canvas id="db_violationChart" height="200"></canvas></div>
    </div>
  </section>

</div><!-- /dashboard-main -->

<!-- 底部 -->
<footer class="dashboard-footer">
  <div class="footer-content">
    <span class="footer-logo">★ 灵辑 MindScribe</span>
    <span class="footer-desc">AI 产品经理全链路数据看板 · 数据均为虚拟演示数据，仅供参考</span>
    <span class="footer-framework">数据框架基于 F2K 评测体系 v1.2</span>
  </div>
</footer>
`;
  }

  // ============================================================
  // 北极星指标数据
  // ============================================================
  var polarStarData = [
    { name: 'DAU', value: '12,480', delta: '+8.3%', up: true },
    { name: '首问率', value: '68.5%', delta: '+3.1%', up: true },
    { name: '日均提问数', value: '5.7次', delta: '+0.4', up: true },
    { name: '有用率', value: '87.3%', delta: '+2.8%', up: true },
    { name: '7日留存', value: '31.6%', delta: '+1.8%', up: true },
    { name: '任务成功率', value: '82.9%', delta: '+2.3%', up: true },
    { name: '响应耗时', value: '1.24s', delta: '-0.08s', up: true },
    { name: '幻觉率', value: '3.2%', delta: '-0.5%', up: true },
    { name: '拒绝率', value: '1.8%', delta: '-0.3%', up: true },
    { name: '复制/复用率', value: '42.6%', delta: '+3.8%', up: true },
    { name: '功能渗透率', value: '71.4%', delta: '+4.6%', up: true },
    { name: 'ARPU & 单用户成本', value: '¥18.4 / ¥0.032', delta: '+¥1.2', up: true },
  ];

  // ============================================================
  // 初始化所有图表
  // ============================================================
  function initCharts() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js 未加载，跳过图表初始化');
      return;
    }

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 11;

    var days30 = genDayLabels(30);

    // DAU/MAU 趋势
    new Chart(document.getElementById('db_dauChart'), {
      type: 'line',
      data: {
        labels: days30,
        datasets: [
          { label: 'DAU', data: genRandArr(30, 10000, 14000), borderColor: '#6c63ff', backgroundColor: 'rgba(108,99,255,0.08)', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 },
          { label: 'MAU（日均）', data: genRandArr(30, 11000, 13000), borderColor: 'rgba(108,99,255,0.4)', fill: false, tension: 0.4, pointRadius: 0, borderWidth: 1.5, borderDash: [4,3] }
        ]
      },
      options: { responsive: true, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } }, tooltip: { mode: 'index', intersect: false } }, scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: function(v){ return v>=1000?(v/1000).toFixed(1)+'k':v; } } } } }
    });

    // 渠道来源
    new Chart(document.getElementById('db_channelChart'), {
      type: 'doughnut',
      data: { labels: ['自然搜索','应用商店','社交媒体','付费投放','口碑推荐','其他'], datasets: [{ data: [32,24,18,14,9,3], backgroundColor: ['#6c63ff','#a78bfa','#06b6d4','#f59e0b','#10b981','#475569'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } } }, cutout: '62%' }
    });

    // 激活漏斗
    new Chart(document.getElementById('db_funnelChart'), {
      type: 'bar',
      data: { labels: ['曝光','点击','落地页','注册','功能激活','首次提问'], datasets: [{ data: [100000,38000,23500,18200,13300,12480], backgroundColor: ['rgba(108,99,255,0.7)','rgba(108,99,255,0.62)','rgba(108,99,255,0.54)','rgba(108,99,255,0.46)','rgba(108,99,255,0.38)','rgba(108,99,255,0.9)'], borderRadius: 4, borderSkipped: false }] },
      options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: function(v){ return v>=1000?(v/1000).toFixed(0)+'k':v; } } }, y: { grid: { display: false } } } }
    });

    // 对话轮次
    new Chart(document.getElementById('db_roundsChart'), {
      type: 'bar',
      data: { labels: ['1轮','2轮','3轮','4轮','5轮','6-10轮','10轮+'], datasets: [{ data: [22,19.7,16.3,12.8,9.2,12.6,7.4], backgroundColor: ['rgba(6,182,212,0.4)','rgba(6,182,212,0.5)','rgba(6,182,212,0.6)','rgba(6,182,212,0.7)','rgba(6,182,212,0.8)','rgba(6,182,212,0.9)','rgba(6,182,212,1.0)'], borderRadius: 4, borderSkipped: false }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: function(v){ return v+'%'; } } } } }
    });

    // 行为信号雷达
    new Chart(document.getElementById('db_behaviorChart'), {
      type: 'radar',
      data: { labels: ['点赞','复制','重新生成','点踩','中断退出','分享'], datasets: [{ data: [31.2,42.6,12.7,5.8,18.4,8.3], backgroundColor: 'rgba(6,182,212,0.15)', borderColor: '#06b6d4', pointBackgroundColor: '#06b6d4', pointRadius: 4, borderWidth: 2 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { r: { grid: { color: 'rgba(255,255,255,0.06)' }, angleLines: { color: 'rgba(255,255,255,0.06)' }, ticks: { display: false }, pointLabels: { font: { size: 11 } } } } }
    });

    // 输入方式
    new Chart(document.getElementById('db_inputTypeChart'), {
      type: 'pie',
      data: { labels: ['文字输入','语音输入','图片上传','文件导入'], datasets: [{ data: [68.4,14.2,10.8,6.6], backgroundColor: ['#06b6d4','#a78bfa','#f59e0b','#10b981'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } } } }
    });

    // 质量雷达
    new Chart(document.getElementById('db_qualityRadar'), {
      type: 'radar',
      data: { labels: ['完整度','相关性','逻辑性','事实正确性','可读性','时效性'], datasets: [{ label: '当前版本', data: [91,89,87,93,88,82], backgroundColor: 'rgba(168,85,247,0.15)', borderColor: '#a855f7', pointBackgroundColor: '#a855f7', pointRadius: 4, borderWidth: 2 }, { label: '上月基线', data: [87,85,84,90,85,79], backgroundColor: 'rgba(168,85,247,0.05)', borderColor: 'rgba(168,85,247,0.35)', pointBackgroundColor: 'rgba(168,85,247,0.5)', pointRadius: 3, borderWidth: 1.5, borderDash: [4,3] }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12 } } }, scales: { r: { min: 70, max: 100, grid: { color: 'rgba(255,255,255,0.06)' }, angleLines: { color: 'rgba(255,255,255,0.06)' }, ticks: { display: false }, pointLabels: { font: { size: 11 } } } } }
    });

    // 耗时分布
    new Chart(document.getElementById('db_latencyChart'), {
      type: 'bar',
      data: { labels: ['<500ms','500-1s','1-2s','2-3s','3-5s','5-10s','>10s'], datasets: [{ data: [8.2,18.4,32.6,21.3,13.8,4.9,0.8], backgroundColor: ['#10b981','#34d399','#6c63ff','#a78bfa','#f59e0b','#f97316','#ef4444'], borderRadius: 4, borderSkipped: false }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: function(v){ return v+'%'; } } } } }
    });

    // 功能渗透率
    new Chart(document.getElementById('db_featurePenetrationChart'), {
      type: 'bar',
      data: { labels: ['碎片笔记整理','文档总结(SUMMARY)','意图识别对话','内容添加(ADD)','文档查询(QUERY)','多文档管理','知识库检索(RAG)','去重检测','章节提取','开发者模式'], datasets: [{ data: [71.4,68.2,64.8,82.3,58.6,47.2,38.9,31.4,26.7,18.3], backgroundColor: ['rgba(245,158,11,0.85)','rgba(245,158,11,0.78)','rgba(245,158,11,0.71)','rgba(245,158,11,0.64)','rgba(245,158,11,0.57)','rgba(245,158,11,0.50)','rgba(245,158,11,0.43)','rgba(245,158,11,0.36)','rgba(245,158,11,0.29)','rgba(245,158,11,0.22)'], borderRadius: 4, borderSkipped: false }] },
      options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { color: 'rgba(255,255,255,0.04)' }, max: 100, ticks: { callback: function(v){ return v+'%'; } } }, y: { grid: { display: false }, ticks: { font: { size: 11 } } } } }
    });

    // 负面反馈
    new Chart(document.getElementById('db_feedbackChart'), {
      type: 'doughnut',
      data: { labels: ['回答不准确','速度太慢','功能不够用','理解偏差','界面难用','其他'], datasets: [{ data: [34,22,18,14,8,4], backgroundColor: ['#ef4444','#f97316','#f59e0b','#a855f7','#06b6d4','#475569'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } } }, cutout: '60%' }
    });

    // 留存曲线
    new Chart(document.getElementById('db_retentionChart'), {
      type: 'line',
      data: { labels: ['Day1','Day2','Day3','Day7','Day14','Day21','Day30'], datasets: [{ label: '本月新用户', data: [100,72.4,61.8,48.2,38.6,32.1,28.4], borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.08)', fill: true, tension: 0.4, pointRadius: 4, borderWidth: 2 }, { label: '上月新用户', data: [100,68.2,57.4,44.8,35.2,28.9,24.6], borderColor: 'rgba(16,185,129,0.4)', fill: false, tension: 0.4, pointRadius: 3, borderWidth: 1.5, borderDash: [4,3] }] },
      options: { responsive: true, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } }, tooltip: { mode: 'index', intersect: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, min: 0, max: 100, ticks: { callback: function(v){ return v+'%'; } } } } }
    });

    // 流失原因
    new Chart(document.getElementById('db_churnChart'), {
      type: 'bar',
      data: { labels: ['回答不好用','速度慢','功能少','太贵/限制多','界面难用','找到替代品'], datasets: [{ data: [38.4,22.1,16.8,12.3,7.2,3.2], backgroundColor: 'rgba(16,185,129,0.6)', borderRadius: 4, borderSkipped: false }] },
      options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: function(v){ return v+'%'; } } }, y: { grid: { display: false } } } }
    });

    // 收入 vs 成本
    new Chart(document.getElementById('db_revenueChart'), {
      type: 'bar',
      data: { labels: ['9月','10月','11月','12月','1月','2月','3月'], datasets: [{ label: '月收入（万元）', data: [8.2,10.4,13.8,16.2,19.4,22.8,26.4], backgroundColor: 'rgba(249,115,22,0.7)', borderRadius: 4, borderSkipped: false, yAxisID: 'y' }, { label: '模型成本（万元）', data: [3.8,4.6,5.8,6.4,7.2,8.1,9.2], backgroundColor: 'rgba(249,115,22,0.25)', borderRadius: 4, borderSkipped: false, yAxisID: 'y' }, { label: '商业化健康度', data: [2.16,2.26,2.38,2.53,2.69,2.81,2.87], type: 'line', borderColor: '#fbbf24', backgroundColor: 'transparent', tension: 0.4, pointRadius: 4, borderWidth: 2, yAxisID: 'y2' }] },
      options: { responsive: true, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } }, tooltip: { mode: 'index', intersect: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.04)' }, position: 'left', ticks: { callback: function(v){ return v+'万'; } } }, y2: { position: 'right', grid: { display: false }, min: 1.5, max: 4, ticks: { callback: function(v){ return v+'x'; } } } } }
    });

    // 付费分层
    new Chart(document.getElementById('db_payTierChart'), {
      type: 'doughnut',
      data: { labels: ['免费用户','基础会员','专业会员','企业版'], datasets: [{ data: [91.7,5.4,2.1,0.8], backgroundColor: ['#334155','#f97316','#fbbf24','#10b981'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } } }, cutout: '60%' }
    });

    // 安全拦截趋势
    new Chart(document.getElementById('db_safetyChart'), {
      type: 'line',
      data: { labels: days30, datasets: [{ label: '拦截次数', data: genRandArr(30,120,280), borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.08)', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 }, { label: '有害生成（次）', data: genRandArr(30,2,8), borderColor: '#f97316', fill: false, tension: 0.4, pointRadius: 0, borderWidth: 1.5, borderDash: [4,3] }] },
      options: { responsive: true, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } }, tooltip: { mode: 'index', intersect: false } }, scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } }, y: { grid: { color: 'rgba(255,255,255,0.04)' } } } }
    });

    // 违规类型
    new Chart(document.getElementById('db_violationChart'), {
      type: 'bar',
      data: { labels: ['色情/暴力','政治敏感','虚假信息','隐私泄露','版权侵犯','其他'], datasets: [{ data: [42,28,19,14,8,5], backgroundColor: ['#ef4444','#f97316','#f59e0b','#a855f7','#06b6d4','#475569'], borderRadius: 4, borderSkipped: false }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(255,255,255,0.04)' } } } }
    });
  }

  // ============================================================
  // 注入北极星指标 chips
  // ============================================================
  function renderPolarChips() {
    var container = document.getElementById('polarMetrics');
    if (!container) return;
    polarStarData.forEach(function(item) {
      var chip = document.createElement('div');
      chip.className = 'polar-metric-chip';
      chip.innerHTML =
        '<span class="polar-chip-name">' + item.name + '</span>' +
        '<span class="polar-chip-value">' + item.value + '</span>' +
        '<span class="polar-chip-delta ' + (item.up ? 'up' : 'down') + '">' + item.delta + '</span>';
      container.appendChild(chip);
    });
  }

  // ============================================================
  // 打开 / 关闭看板
  // ============================================================
  var chartsInited = false;

  function openDashboard() {
    var overlay = document.getElementById('dashboard-fullscreen');
    if (!overlay) return;

    // 注入 HTML（只注入一次）
    var inner = document.getElementById('dashboard-inner');
    if (inner && inner.innerHTML.trim() === '') {
      inner.innerHTML = getDashboardHTML();
    }

    overlay.classList.remove('hidden');
    overlay.classList.add('dashboard-entering');
    setTimeout(function() { overlay.classList.remove('dashboard-entering'); }, 400);

    // 渲染北极星 chips
    renderPolarChips();

    // 初始化图表（只初始化一次）
    if (!chartsInited) {
      setTimeout(function() {
        initCharts();
        chartsInited = true;
      }, 100);
    }

    // 禁止背景滚动
    document.body.style.overflow = 'hidden';
  }

  function closeDashboard() {
    var overlay = document.getElementById('dashboard-fullscreen');
    if (!overlay) return;
    overlay.classList.add('dashboard-leaving');
    setTimeout(function() {
      overlay.classList.remove('dashboard-leaving');
      overlay.classList.add('hidden');
      document.body.style.overflow = '';
    }, 300);
  }

  // ============================================================
  // 绑定事件
  // ============================================================
  function bindEvents() {
    // 侧边栏按钮
    var dashBtn = document.getElementById('dashboard-btn');
    if (dashBtn) {
      dashBtn.addEventListener('click', function() {
        openDashboard();
      });
    }

    // 返回按钮
    var backBtn = document.getElementById('dashboard-back-btn');
    if (backBtn) {
      backBtn.addEventListener('click', function() {
        closeDashboard();
      });
    }
  }

  // ============================================================
  // 入口：DOM 就绪后初始化
  // ============================================================
  function init() {
    bindEvents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
