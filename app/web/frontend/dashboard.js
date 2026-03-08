/* ============================================================
   灵辑 MindScribe · AI 产品经理全链路数据看板 · JS
   ============================================================ */

// ============================================================
// 工具函数
// ============================================================
function updateTime() {
  const el = document.getElementById('updateTime');
  if (!el) return;
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  el.textContent = `数据更新于 ${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}
updateTime();
setInterval(updateTime, 1000);

// ============================================================
// 北极星指标数据
// ============================================================
const polarStarData = [
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

const polarContainer = document.getElementById('polarMetrics');
polarStarData.forEach(item => {
  const chip = document.createElement('div');
  chip.className = 'polar-metric-chip';
  chip.innerHTML = `
    <span class="polar-chip-name">${item.name}</span>
    <span class="polar-chip-value">${item.value}</span>
    <span class="polar-chip-delta ${item.up ? 'up' : 'down'}">${item.delta}</span>
  `;
  polarContainer.appendChild(chip);
});

// ============================================================
// Chart.js 全局默认配置
// ============================================================
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 11;

// ============================================================
// 工具函数：生成近N天的日期标签
// ============================================================
function genDayLabels(n) {
  const labels = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    labels.push(`${d.getMonth()+1}/${d.getDate()}`);
  }
  return labels;
}

function genRandArr(len, min, max, smooth = true) {
  const arr = [];
  let cur = (min + max) / 2;
  for (let i = 0; i < len; i++) {
    if (smooth) {
      cur += (Math.random() - 0.45) * (max - min) * 0.12;
      cur = Math.max(min, Math.min(max, cur));
    } else {
      cur = min + Math.random() * (max - min);
    }
    arr.push(Math.round(cur * 10) / 10);
  }
  return arr;
}

// ============================================================
// 一、入口层图表
// ============================================================

// DAU/MAU 趋势
new Chart(document.getElementById('dauChart'), {
  type: 'line',
  data: {
    labels: genDayLabels(30),
    datasets: [
      {
        label: 'DAU',
        data: genRandArr(30, 10000, 14000),
        borderColor: '#6c63ff',
        backgroundColor: 'rgba(108,99,255,0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
      {
        label: 'MAU（日均）',
        data: genRandArr(30, 80000, 95000).map(v => Math.round(v / 7)),
        borderColor: 'rgba(108,99,255,0.4)',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 1.5,
        borderDash: [4, 3],
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: v => v >= 1000 ? (v/1000).toFixed(1)+'k' : v } }
    }
  }
});

// 渠道来源分布
new Chart(document.getElementById('channelChart'), {
  type: 'doughnut',
  data: {
    labels: ['自然搜索', '应用商店', '社交媒体', '付费投放', '口碑推荐', '其他'],
    datasets: [{
      data: [32, 24, 18, 14, 9, 3],
      backgroundColor: ['#6c63ff','#a78bfa','#06b6d4','#f59e0b','#10b981','#475569'],
      borderWidth: 0,
      hoverOffset: 6,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` } }
    },
    cutout: '62%',
  }
});

// 新用户激活漏斗
new Chart(document.getElementById('funnelChart'), {
  type: 'bar',
  data: {
    labels: ['曝光', '点击', '落地页', '注册', '功能激活', '首次提问'],
    datasets: [{
      label: '转化人数',
      data: [100000, 38000, 23500, 18200, 13300, 12480],
      backgroundColor: [
        'rgba(108,99,255,0.7)',
        'rgba(108,99,255,0.62)',
        'rgba(108,99,255,0.54)',
        'rgba(108,99,255,0.46)',
        'rgba(108,99,255,0.38)',
        'rgba(108,99,255,0.9)',
      ],
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x.toLocaleString()} 人` } }
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: v => v >= 1000 ? (v/1000).toFixed(0)+'k' : v } },
      y: { grid: { display: false } }
    }
  }
});

// ============================================================
// 二、交互层图表
// ============================================================

// 对话轮次分布
new Chart(document.getElementById('roundsChart'), {
  type: 'bar',
  data: {
    labels: ['1轮', '2轮', '3轮', '4轮', '5轮', '6-10轮', '10轮+'],
    datasets: [{
      label: '会话占比',
      data: [22, 19.7, 16.3, 12.8, 9.2, 12.6, 7.4],
      backgroundColor: [
        'rgba(6,182,212,0.4)',
        'rgba(6,182,212,0.5)',
        'rgba(6,182,212,0.6)',
        'rgba(6,182,212,0.7)',
        'rgba(6,182,212,0.8)',
        'rgba(6,182,212,0.9)',
        'rgba(6,182,212,1.0)',
      ],
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}%` } }
    },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: v => v + '%' } }
    }
  }
});

// 用户行为信号分布
new Chart(document.getElementById('behaviorChart'), {
  type: 'radar',
  data: {
    labels: ['点赞', '复制', '重新生成', '点踩', '中断退出', '分享'],
    datasets: [{
      label: '行为信号占比',
      data: [31.2, 42.6, 12.7, 5.8, 18.4, 8.3],
      backgroundColor: 'rgba(6,182,212,0.15)',
      borderColor: '#06b6d4',
      pointBackgroundColor: '#06b6d4',
      pointRadius: 4,
      borderWidth: 2,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      r: {
        grid: { color: 'rgba(255,255,255,0.06)' },
        angleLines: { color: 'rgba(255,255,255,0.06)' },
        ticks: { display: false },
        pointLabels: { font: { size: 11 } }
      }
    }
  }
});

// 输入方式占比
new Chart(document.getElementById('inputTypeChart'), {
  type: 'pie',
  data: {
    labels: ['文字输入', '语音输入', '图片上传', '文件导入'],
    datasets: [{
      data: [68.4, 14.2, 10.8, 6.6],
      backgroundColor: ['#06b6d4', '#a78bfa', '#f59e0b', '#10b981'],
      borderWidth: 0,
      hoverOffset: 6,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` } }
    }
  }
});

// ============================================================
// 三、AI 核心层图表
// ============================================================

// 生成质量六维雷达
new Chart(document.getElementById('qualityRadar'), {
  type: 'radar',
  data: {
    labels: ['完整度', '相关性', '逻辑性', '事实正确性', '可读性', '时效性'],
    datasets: [
      {
        label: '当前版本',
        data: [91, 89, 87, 93, 88, 82],
        backgroundColor: 'rgba(168,85,247,0.15)',
        borderColor: '#a855f7',
        pointBackgroundColor: '#a855f7',
        pointRadius: 4,
        borderWidth: 2,
      },
      {
        label: '上月基线',
        data: [87, 85, 84, 90, 85, 79],
        backgroundColor: 'rgba(168,85,247,0.05)',
        borderColor: 'rgba(168,85,247,0.35)',
        pointBackgroundColor: 'rgba(168,85,247,0.5)',
        pointRadius: 3,
        borderWidth: 1.5,
        borderDash: [4, 3],
      }
    ]
  },
  options: {
    responsive: true,
    plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12 } } },
    scales: {
      r: {
        min: 70, max: 100,
        grid: { color: 'rgba(255,255,255,0.06)' },
        angleLines: { color: 'rgba(255,255,255,0.06)' },
        ticks: { stepSize: 10, display: false },
        pointLabels: { font: { size: 11 } }
      }
    }
  }
});

// 响应耗时分布
new Chart(document.getElementById('latencyChart'), {
  type: 'bar',
  data: {
    labels: ['<500ms', '500-1s', '1-2s', '2-3s', '3-5s', '5-10s', '>10s'],
    datasets: [{
      label: '请求占比',
      data: [8.2, 18.4, 32.6, 21.3, 13.8, 4.9, 0.8],
      backgroundColor: [
        '#10b981','#34d399','#6c63ff','#a78bfa','#f59e0b','#f97316','#ef4444'
      ],
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y}%` } }
    },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: v => v + '%' } }
    }
  }
});

// ============================================================
// 四、功能层图表
// ============================================================

// 各 AI 功能渗透率
new Chart(document.getElementById('featurePenetrationChart'), {
  type: 'bar',
  data: {
    labels: [
      '碎片笔记整理', '文档总结(SUMMARY)', '意图识别对话', '内容添加(ADD)',
      '文档查询(QUERY)', '多文档管理', '知识库检索(RAG)', '去重检测',
      '章节提取', '开发者模式'
    ],
    datasets: [{
      label: '功能渗透率',
      data: [71.4, 68.2, 64.8, 82.3, 58.6, 47.2, 38.9, 31.4, 26.7, 18.3],
      backgroundColor: [
        'rgba(245,158,11,0.85)',
        'rgba(245,158,11,0.78)',
        'rgba(245,158,11,0.71)',
        'rgba(245,158,11,0.64)',
        'rgba(245,158,11,0.57)',
        'rgba(245,158,11,0.50)',
        'rgba(245,158,11,0.43)',
        'rgba(245,158,11,0.36)',
        'rgba(245,158,11,0.29)',
        'rgba(245,158,11,0.22)',
      ],
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x}%` } }
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, max: 100, ticks: { callback: v => v + '%' } },
      y: { grid: { display: false }, ticks: { font: { size: 11 } } }
    }
  }
});

// 负面反馈类型分布
new Chart(document.getElementById('feedbackChart'), {
  type: 'doughnut',
  data: {
    labels: ['回答不准确', '速度太慢', '功能不够用', '理解偏差', '界面难用', '其他'],
    datasets: [{
      data: [34, 22, 18, 14, 8, 4],
      backgroundColor: ['#ef4444','#f97316','#f59e0b','#a855f7','#06b6d4','#475569'],
      borderWidth: 0,
      hoverOffset: 6,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` } }
    },
    cutout: '60%',
  }
});

// ============================================================
// 五、留存层图表
// ============================================================

// 用户留存曲线
const retentionLabels = ['Day1','Day2','Day3','Day7','Day14','Day21','Day30'];
new Chart(document.getElementById('retentionChart'), {
  type: 'line',
  data: {
    labels: retentionLabels,
    datasets: [
      {
        label: '本月新用户',
        data: [100, 72.4, 61.8, 48.2, 38.6, 32.1, 28.4],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 2,
      },
      {
        label: '上月新用户',
        data: [100, 68.2, 57.4, 44.8, 35.2, 28.9, 24.6],
        borderColor: 'rgba(16,185,129,0.4)',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 3,
        borderWidth: 1.5,
        borderDash: [4, 3],
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
      tooltip: { mode: 'index', intersect: false, callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y}%` } }
    },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, min: 0, max: 100, ticks: { callback: v => v + '%' } }
    }
  }
});

// 流失原因分析
new Chart(document.getElementById('churnChart'), {
  type: 'bar',
  data: {
    labels: ['回答不好用', '速度慢', '功能少', '太贵/限制多', '界面难用', '找到替代品'],
    datasets: [{
      label: '流失占比',
      data: [38.4, 22.1, 16.8, 12.3, 7.2, 3.2],
      backgroundColor: 'rgba(16,185,129,0.6)',
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x}%` } }
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { callback: v => v + '%' } },
      y: { grid: { display: false } }
    }
  }
});

// ============================================================
// 六、商业化层图表
// ============================================================

// 月收入 vs 模型成本
const months = ['9月','10月','11月','12月','1月','2月','3月'];
new Chart(document.getElementById('revenueChart'), {
  type: 'bar',
  data: {
    labels: months,
    datasets: [
      {
        label: '月收入（万元）',
        data: [8.2, 10.4, 13.8, 16.2, 19.4, 22.8, 26.4],
        backgroundColor: 'rgba(249,115,22,0.7)',
        borderRadius: 4,
        borderSkipped: false,
        yAxisID: 'y',
      },
      {
        label: '模型成本（万元）',
        data: [3.8, 4.6, 5.8, 6.4, 7.2, 8.1, 9.2],
        backgroundColor: 'rgba(249,115,22,0.25)',
        borderRadius: 4,
        borderSkipped: false,
        yAxisID: 'y',
      },
      {
        label: '商业化健康度',
        data: [2.16, 2.26, 2.38, 2.53, 2.69, 2.81, 2.87],
        type: 'line',
        borderColor: '#fbbf24',
        backgroundColor: 'transparent',
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 2,
        yAxisID: 'y2',
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, position: 'left', ticks: { callback: v => v + '万' } },
      y2: { position: 'right', grid: { display: false }, min: 1.5, max: 4, ticks: { callback: v => v + 'x' } }
    }
  }
});

// 付费用户分层
new Chart(document.getElementById('payTierChart'), {
  type: 'doughnut',
  data: {
    labels: ['免费用户', '基础会员', '专业会员', '企业版'],
    datasets: [{
      data: [91.7, 5.4, 2.1, 0.8],
      backgroundColor: ['#334155','#f97316','#fbbf24','#10b981'],
      borderWidth: 0,
      hoverOffset: 6,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 10 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}%` } }
    },
    cutout: '60%',
  }
});

// ============================================================
// 七、安全合规层图表
// ============================================================

// 安全拦截趋势
new Chart(document.getElementById('safetyChart'), {
  type: 'line',
  data: {
    labels: genDayLabels(30),
    datasets: [
      {
        label: '拦截次数',
        data: genRandArr(30, 120, 280),
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
      {
        label: '有害生成（次）',
        data: genRandArr(30, 2, 8),
        borderColor: '#f97316',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 1.5,
        borderDash: [4, 3],
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' } }
    }
  }
});

// 违规类型分布
new Chart(document.getElementById('violationChart'), {
  type: 'bar',
  data: {
    labels: ['色情/暴力', '政治敏感', '虚假信息', '隐私泄露', '版权侵犯', '其他'],
    datasets: [{
      label: '拦截次数',
      data: [42, 28, 19, 14, 8, 5],
      backgroundColor: [
        '#ef4444','#f97316','#f59e0b','#a855f7','#06b6d4','#475569'
      ],
      borderRadius: 4,
      borderSkipped: false,
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} 次` } }
    },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' } }
    }
  }
});

// ============================================================
// 导航高亮（Intersection Observer）
// ============================================================
const sections = document.querySelectorAll('.layer-section');
const navBtns = document.querySelectorAll('.layer-btn');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.id;
      navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('href') === `#${id}`);
      });
    }
  });
}, { threshold: 0.2, rootMargin: '-60px 0px -40% 0px' });

sections.forEach(s => observer.observe(s));

// ============================================================
// 数据刷新动画（模拟实时数据）
// ============================================================
function randomFluctuate(val, range) {
  return (parseFloat(val) + (Math.random() - 0.5) * range).toFixed(1);
}

// 每30秒轻微更新北极星指标数值（模拟实时感）
setInterval(() => {
  const chips = document.querySelectorAll('.polar-chip-value');
  // 只更新 DAU 数值作为示例
  if (chips[0]) {
    const base = 12480;
    const newVal = base + Math.floor((Math.random() - 0.5) * 200);
    chips[0].textContent = newVal.toLocaleString();
  }
}, 30000);
