/**
 * 灵辑 - 智能笔记助手
 * 前端应用核心逻辑
 * 这个文件包含了前端应用的所有JavaScript代码
 */

// 立即执行：确认脚本已加载
console.log('✅ app.js 文件开始执行！');

// ============================================
// 应用状态管理
// ============================================
// 创建一个对象来存储应用的全局状态
const AppState = {
    sessionId: null,  // 会话ID，用于区分不同用户的会话，初始值为null
    currentDocument: '试用文档',  // 当前正在操作的文档名称，默认为"试用文档"（试用模式）
    documents: [],  // 存储所有文档的列表，初始为空数组
    pendingConfirmation: null,  // 存储待用户确认的操作信息，初始为null
    isLoading: false,  // 标记是否正在处理请求，防止重复提交，初始为false
    devModeEnabled: false  // 开发者模式状态，初始为false
};

// ============================================
// DOM元素获取
// ============================================
// 创建一个对象，存储所有需要操作的HTML元素引用
// 这样可以在整个应用中方便地访问这些元素
// 注意：延迟初始化，避免在DOM未加载时访问元素
const elements = {};

/**
 * 初始化DOM元素引用
 * 在DOM加载完成后调用，确保所有元素都已存在
 */
function initElements() {
    // 输入相关 - 获取用户输入框和发送按钮的DOM元素
    elements.userInput = document.getElementById('user-input');
    elements.sendBtn = document.getElementById('send-btn');
    
    // 聊天区域 - 获取显示聊天消息的区域
    elements.chatArea = document.getElementById('chat-area');
    
    // 侧边栏相关 - 获取侧边栏相关的所有元素
    elements.sidebar = document.getElementById('sidebar');
    elements.closeSidebarBtn = document.getElementById('close-sidebar-btn');
    elements.sidebarOverlay = document.getElementById('sidebar-overlay');
    elements.docList = document.getElementById('doc-list');
    
    // 文档信息 - 获取显示当前文档标题的元素
    elements.activeDocTitle = document.getElementById('active-doc-title');
    elements.switchDocBtn = document.getElementById('switch-doc-btn');
    elements.viewDocBtn = document.getElementById('view-doc-btn');
    elements.viewDocumentModal = document.getElementById('view-document-modal');
    elements.viewDocumentTitle = document.getElementById('view-document-title');
    elements.viewDocumentText = document.getElementById('view-document-text');
    elements.closeViewDocumentBtn = document.getElementById('close-view-document-btn');
    
    // 登录按钮
    elements.loginBtn = document.getElementById('login-btn');
    
    // 应用端下载按钮
    elements.downloadAppBtn = document.getElementById('download-app-btn');
    elements.downloadAppTooltip = document.getElementById('download-app-tooltip');
    
    // 对话模式按钮（底部工具栏）
    elements.dialogueModeBtn = document.getElementById('dialogue-mode-btn');
    elements.dialogueModeDropdown = document.getElementById('dialogue-mode-dropdown');
    elements.normalModeItem = document.getElementById('normal-mode-item');
    elements.interviewModeItem = document.getElementById('interview-mode-item');
    elements.interviewModeInfoPanel = document.getElementById('interview-mode-info-panel');
    elements.interviewModeInfoClose = document.getElementById('interview-mode-info-close');
    
    // 调试信息
    console.log('对话模式按钮元素:', elements.dialogueModeBtn);
    console.log('对话模式下拉菜单元素:', elements.dialogueModeDropdown);
    
    // 模型选型按钮
    elements.modelSelectorBtn = document.getElementById('model-selector-btn');
    elements.modelSelectorTooltip = document.getElementById('model-selector-tooltip');
    
    // 附件上传按钮
    elements.attachmentBtn = document.getElementById('attachment-btn');
    elements.attachmentBtnTooltip = document.getElementById('attachment-btn-tooltip');
    
    // 笔记共享按钮
    elements.shareNoteBtn = document.getElementById('share-note-btn');
    elements.shareNoteTooltip = document.getElementById('share-note-tooltip');
    elements.shareNoteModal = document.getElementById('share-note-modal');
    elements.closeShareNoteModal = document.getElementById('close-share-note-modal');
    elements.shareNoteLink = document.getElementById('share-note-link');
    elements.copyShareLinkBtn = document.getElementById('copy-share-link-btn');
    
    // 设置按钮（左侧侧边栏）
    elements.settingsBtn = document.getElementById('settings-btn');
    elements.updateNotificationBtnLeft = document.getElementById('update-notification-btn-left');
    elements.knowledgeBaseBtn = document.getElementById('knowledge-base-btn');
    
    // 开发者模式按钮（左侧侧边栏）
    elements.devModeBtnLeft = document.getElementById('dev-mode-btn-left');
    // 保留顶部栏的开发者模式按钮引用（已隐藏，但保留以防需要）
    elements.devModeBtn = document.getElementById('dev-mode-btn');
    
    // 说明书相关
    elements.manualBtn = document.getElementById('manual-btn');
    elements.manualPanel = document.getElementById('manual-panel');
    elements.closeManualBtn = document.getElementById('close-manual-btn');
    elements.manualContent = document.getElementById('manual-content');
    
    // 更新通知相关
    elements.updateNotificationBtn = document.getElementById('update-notification-btn');
    elements.updateNotificationPanel = document.getElementById('update-notification-panel');
    elements.closeNotificationBtn = document.getElementById('close-notification-btn');
    elements.updateList = document.getElementById('update-list');
    elements.notificationBadge = document.getElementById('notification-badge');
    
    // AI反馈面板相关
    elements.aiFeedbackPanel = document.getElementById('ai-feedback-panel');
    elements.aiFeedbackHeader = document.getElementById('ai-feedback-header');
    elements.aiFeedbackToggle = document.getElementById('ai-feedback-toggle');
    elements.aiFeedbackList = document.getElementById('ai-feedback-list');
    elements.aiFeedbackTime = document.getElementById('ai-feedback-time');
    
    // 标准对话示例面板相关
    elements.examplePanel = document.getElementById('example-panel');
    elements.exampleHeader = document.getElementById('example-header');
    elements.exampleToggle = document.getElementById('example-toggle');
    elements.exampleList = document.getElementById('example-list');
    
    // 连接状态指示器相关
    elements.connectionStatusIndicator = document.getElementById('connection-status-indicator');
    elements.connectionStatusText = document.getElementById('connection-status-text');
    
    // 意见反馈相关
    elements.feedbackBtn = document.getElementById('feedback-btn');
    elements.feedbackModal = document.getElementById('feedback-modal');
    elements.closeFeedbackModal = document.getElementById('close-feedback-modal');
    elements.starRating = document.getElementById('star-rating');
    elements.ratingText = document.getElementById('rating-text');
    elements.feedbackTextarea = document.getElementById('feedback-textarea');
    elements.feedbackSubmitBtn = document.getElementById('feedback-submit-btn');
    elements.feedbackCancelBtn = document.getElementById('feedback-cancel-btn');
    elements.feedbackSuccessPanel = document.getElementById('feedback-success-panel');
    elements.feedbackSuccessClose = document.getElementById('feedback-success-close');
    
    // 处理中logo相关
    elements.processingLogoContainer = document.getElementById('processing-logo-container');
    elements.processingLogo = document.getElementById('processing-logo');
    
    // 语音输入按钮相关
    elements.voiceBtnContainer = document.querySelector('.voice-btn-container');
    elements.voiceBtnTooltip = document.getElementById('voice-btn-tooltip');
    
    // 媒体输入按钮相关（图片、音频、视频）
    // 旧的媒体输入按钮已移除，不再需要
    
    // 模态框相关 - 获取确认对话框相关的所有元素
    elements.confirmationModal = document.getElementById('confirmation-modal');
    elements.modalText = document.getElementById('modal-text');
    elements.confirmYesBtn = document.getElementById('confirm-yes-btn');
    elements.confirmNoBtn = document.getElementById('confirm-no-btn');
    
    // 文档匹配确认对话框相关
    elements.matchConfirmationModal = document.getElementById('match-confirmation-modal');
    elements.matchConfirmationMessage = document.getElementById('match-confirmation-message');
    elements.matchConfirmYesBtn = document.getElementById('match-confirm-yes');
    elements.matchConfirmNewDocBtn = document.getElementById('match-confirm-new-doc');
    elements.matchConfirmCancelBtn = document.getElementById('match-confirm-cancel');
    
    console.log('[初始化] DOM元素引用已初始化');
}

// ============================================
// API配置
// ============================================
// 配置后端API的基础URL和接口路径
const API_CONFIG = {
    // 后端API基础URL
    // 这是后端服务器运行的地址，前端会向这个地址发送请求
    // 本地开发：使用 http://localhost:8001
    // 生产环境：使用 https://mindscribe-api-8zop.onrender.com
    baseURL: 'https://mindscribe-backend-nr7q.onrender.com',  // 生产环境地址
    endpoints: {
        chat: '/api/chat',  // 聊天接口的路径
        documents: '/api/documents'  // 文档列表接口的路径
    }
};

// ============================================
// 工具函数
// ============================================

/**
 * 生成唯一的会话ID
 * 这个函数用于为每个用户会话生成一个唯一的标识符
 * @returns {string} 返回一个唯一的会话ID字符串
 */
function generateSessionId() {
    // 使用当前时间戳和随机字符串组合生成唯一ID
    // Date.now() 获取当前时间戳（毫秒）
    // Math.random().toString(36) 生成随机字符串（36进制）
    // .substr(2, 9) 从第2个字符开始取9个字符，去掉"0."前缀
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * 初始化会话ID
 * 如果还没有会话ID，就生成一个新的
 */
function initSession() {
    // 检查是否为试用模式
    // 演示模式：每次刷新页面时都不使用 session_id
    // 后端会自动创建新的 session
    AppState.sessionId = null;
    console.log('[初始化] 演示模式，不使用 session_id，每次刷新都重置');
    
    // 清理旧的 session_id（如果有）
    // 注意：不要清除 is_trial_mode，否则刷新页面会丢失用户的选择
    localStorage.removeItem('trial_session_id');
    // localStorage.removeItem('is_trial_mode');
}

/**
 * 自动调整文本域高度
 * 根据输入内容自动调整输入框的高度，让用户可以输入多行文本
 * @param {HTMLElement} textarea - 要调整的文本域元素
 */
function autoResizeTextarea(textarea) {
    // 先将高度设置为'auto'，让浏览器计算实际需要的高度
    textarea.style.height = 'auto';
    // 设置高度为内容高度，但不超过80px
    // scrollHeight 是元素内容的实际高度
    // Math.min() 取较小值，限制最大高度为80px
    textarea.style.height = Math.min(textarea.scrollHeight, 80) + 'px';
}

/**
 * 滚动聊天区域到底部（平滑滚动）
 * 当有新消息时，自动滚动到聊天区域底部，让用户看到最新消息
 */
function scrollToBottom() {
    // 使用 scrollTo 方法进行平滑滚动
    elements.chatArea.scrollTo({
        top: elements.chatArea.scrollHeight,  // 滚动到最底部（scrollHeight是内容总高度）
        behavior: 'smooth'  // 使用平滑滚动动画，而不是瞬间跳转
    });
}

// ============================================
// UI更新函数
// ============================================

/**
 * 添加消息到聊天区域
 * 在聊天界面中显示一条新消息（用户消息或AI回复）
 * @param {string} sender - 消息发送者：'user' 或 'ai'
 * @param {string} content - 要显示的消息内容
 * @param {string} type - 消息类型：'text'（普通文本）或 'document'（文档内容）
 */
function addMessageToChat(sender, content, type = 'text', isError = false, isWarning = false) {
    // 创建一个div元素作为消息气泡容器
    const bubble = document.createElement('div');
    // 设置CSS类名，用于样式控制（'chat-bubble user' 或 'chat-bubble ai'）
    // 如果是警告消息，添加warning类；如果是错误消息，添加error类
    let className = `chat-bubble ${sender}`;
    if (isWarning) {
        className += ' warning';
    } else if (isError) {
        className += ' error';
    }
    bubble.className = className;
    
    // 控制台输出：显示每次对话气泡的详细信息
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('💬 创建新消息气泡');
    console.log('发送者:', sender === 'user' ? '👤 用户' : '🤖 AI');
    console.log('消息类型:', type);
    console.log('是否错误消息:', isError ? '❌ 是' : '✅ 否');
    console.log('是否警告消息:', isWarning ? '⚠️ 是' : '✅ 否');
    console.log('CSS类名:', bubble.className);
    console.log('消息内容:', content.substring(0, 100) + (content.length > 100 ? '...' : ''));
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    // 初始状态：透明度为0（不可见），用于淡入动画
    bubble.style.opacity = '0';
    // 初始状态：向下偏移20px并缩小到95%，用于上浮和缩放动画
    bubble.style.transform = 'translateY(20px) scale(0.95)';
    
    // 创建消息包装容器（包含图标和内容）
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    // 创建图标元素
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    const avatarImg = document.createElement('img');
    avatarImg.src = sender === 'user' ? 'user-icon.png' : 'ai-icon.png';
    avatarImg.alt = sender === 'user' ? '用户' : '灵辑';
    avatarImg.className = 'avatar-img';
    avatar.appendChild(avatarImg);
    
    // 创建消息内容容器
    const messageContent = document.createElement('div');
    // 设置消息内容的CSS类名
    messageContent.className = 'message-content';
    
    // 如果是警告消息，立即应用警告样式（黄色）
    if (isWarning) {
        // 使用黄色背景（15%透明度）
        messageContent.style.cssText = 'background: rgba(255, 237, 213, 0.15) !important; color: #b45309 !important; border: 1px solid rgba(255, 193, 7, 0.3) !important;';
    }
    // 如果是错误消息，立即应用错误样式（淡红色）
    else if (isError) {
        // 使用淡红色背景（10%透明度）
        messageContent.style.cssText = 'background: rgba(255, 200, 200, 0.1) !important; color: #dc2626 !important; border: 1px solid rgba(255, 150, 150, 0.2) !important;';
    }
    
    // 判断消息类型
    if (type === 'document') {
        // 如果是文档类型，创建文档内容卡片
        const card = document.createElement('div');
        // 设置文档卡片的CSS类名
        card.className = 'document-content-card';
        // 将文档内容设置为卡片的文本内容
        card.textContent = content;
        // 将卡片添加到消息内容容器中
        messageContent.appendChild(card);
    } else {
        // 如果是普通文本类型，处理文本内容
        // 按换行符分割文本，并过滤掉空行
        const paragraphs = content.split('\n').filter(p => p.trim());
        // 如果没有段落（空内容）
        if (paragraphs.length === 0) {
            // 直接设置文本内容
            messageContent.textContent = content;
        } else {
            // 如果有多个段落，为每个段落创建<p>标签
            paragraphs.forEach(para => {
                // 创建段落元素
                const p = document.createElement('p');
                // 设置段落文本内容
                p.textContent = para;
                // 将段落添加到消息内容容器中
                messageContent.appendChild(p);
            });
        }
    }
    
    // 将图标和内容添加到包装容器中
    messageWrapper.appendChild(avatar);
    messageWrapper.appendChild(messageContent);
    
    // 将消息包装容器添加到气泡容器中
    bubble.appendChild(messageWrapper);
    // 将气泡添加到聊天区域中
    elements.chatArea.appendChild(bubble);
    
    // 如果是警告消息，强制应用警告样式（确保样式正确显示）
    if (isWarning) {
        console.log('🎨 [警告消息] 开始应用警告样式');
        // 使用setTimeout确保DOM完全渲染后再应用样式到所有子元素
        setTimeout(() => {
            const messageContentEl = bubble.querySelector('.message-content');
            if (messageContentEl) {
                // 使用setProperty方法强制应用警告样式（优先级最高，使用黄色）
                messageContentEl.style.setProperty('background', 'rgba(255, 237, 213, 0.15)', 'important');
                messageContentEl.style.setProperty('color', '#b45309', 'important');
                messageContentEl.style.setProperty('border', '1px solid rgba(255, 193, 7, 0.3)', 'important');
                
                const computedStyle = window.getComputedStyle(messageContentEl);
                console.log('🎨 [警告消息] 样式已应用');
                console.log('   - 背景色:', computedStyle.backgroundColor);
                console.log('   - 文字颜色:', computedStyle.color);
                console.log('   - 边框:', computedStyle.border);
                
                // 确保所有文本元素也是黄色/橙色（排除图标）
                const textElements = messageContentEl.querySelectorAll('p, span, div, strong, li');
                console.log('   - 文本元素数量:', textElements.length);
                textElements.forEach(el => {
                    if (!el.classList.contains('avatar-img') && el.tagName.toLowerCase() !== 'img') {
                        el.style.setProperty('color', '#b45309', 'important');
                    }
                });
            } else {
                console.error('❌ [警告消息] 未找到message-content元素！');
            }
        }, 100);
    }
    // 如果是错误消息，强制应用错误样式（确保样式正确显示）
    else if (isError) {
        console.log('🎨 [错误消息] 开始应用错误样式');
        // 使用setTimeout确保DOM完全渲染后再应用样式到所有子元素
        setTimeout(() => {
            const messageContentEl = bubble.querySelector('.message-content');
            if (messageContentEl) {
                // 使用setProperty方法强制应用错误样式（优先级最高，使用淡红色）
                messageContentEl.style.setProperty('background', 'rgba(255, 200, 200, 0.1)', 'important');
                messageContentEl.style.setProperty('color', '#dc2626', 'important');
                messageContentEl.style.setProperty('border', '1px solid rgba(255, 150, 150, 0.2)', 'important');
                
                const computedStyle = window.getComputedStyle(messageContentEl);
                console.log('🎨 [错误消息] 样式已应用');
                console.log('   - 背景色:', computedStyle.backgroundColor);
                console.log('   - 文字颜色:', computedStyle.color);
                console.log('   - 边框:', computedStyle.border);
                
                // 确保所有文本元素也是红色（排除图标）
                const textElements = messageContentEl.querySelectorAll('p, span, div, strong, li');
                console.log('   - 文本元素数量:', textElements.length);
                textElements.forEach(el => {
                    if (!el.classList.contains('avatar-img') && el.tagName.toLowerCase() !== 'img') {
                        el.style.setProperty('color', '#dc2626', 'important');
                    }
                });
            } else {
                console.error('❌ [错误消息] 未找到message-content元素！');
            }
        }, 100);
    }
    
    // 触发淡入动画
    // requestAnimationFrame 确保在浏览器下一次重绘前执行
    requestAnimationFrame(() => {
        // 设置CSS过渡效果：所有属性在0.3秒内平滑变化
        bubble.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        // 将透明度设置为1（完全可见）
        bubble.style.opacity = '1';
        // 恢复到原始位置和大小（无偏移，100%大小）
        bubble.style.transform = 'translateY(0) scale(1)';
        
        // 控制台输出：显示消息的最终状态
        setTimeout(() => {
            const rect = bubble.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(bubble);
            console.log('✅ 消息气泡已显示');
            console.log('   - 位置:', `top: ${rect.top.toFixed(0)}px, left: ${rect.left.toFixed(0)}px`);
            console.log('   - 大小:', `width: ${rect.width.toFixed(0)}px, height: ${rect.height.toFixed(0)}px`);
            console.log('   - 可见性:', `opacity: ${computedStyle.opacity}, display: ${computedStyle.display}`);
            console.log('   - 是否在DOM中:', bubble.parentNode ? '✅ 是' : '❌ 否');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        }, 350); // 等待动画完成
    });
    
    // 延迟100毫秒后滚动到底部，确保消息已完全渲染
    setTimeout(scrollToBottom, 100);
}

/**
 * 显示加载指示器
 * 当AI正在处理请求时，动态创建一个新的加载指示器气泡，显示在用户消息之后
 */
function showLoadingIndicator() {
    // 显示处理中logo
    if (elements.processingLogoContainer) {
        elements.processingLogoContainer.classList.add('show');
    }
    
    // 如果已经存在加载指示器，先移除
    const existingIndicator = elements.chatArea.querySelector('.loading-indicator.show');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    // 创建新的加载指示器气泡
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'loading-indicator show';
    loadingBubble.innerHTML = `
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <span class="loading-text">灵辑正在努力中</span>
    `;
    
    // 将加载指示器添加到聊天区域的最后（用户消息之后）
    elements.chatArea.appendChild(loadingBubble);
    
    // 滚动到底部，让用户看到加载提示
    setTimeout(() => {
        scrollToBottom();
    }, 50);
}

/**
 * 隐藏加载指示器
 * 当AI处理完成时，隐藏加载动画
 */
function hideLoadingIndicator(animate = true) {
    // 隐藏处理中logo
    if (elements.processingLogoContainer) {
        elements.processingLogoContainer.classList.remove('show');
    }
    
    // 查找所有显示的加载指示器
    const loadingIndicators = elements.chatArea.querySelectorAll('.loading-indicator.show');
    
    loadingIndicators.forEach(indicator => {
        // 如果需要动画效果（破碎动画）
        if (animate) {
            // 添加破碎动画类
            indicator.classList.add('breaking');
            // 移除show类
            indicator.classList.remove('show');
            
            // 动画完成后完全移除
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.remove();
                }
            }, 500); // 动画持续时间
        } else {
            // 直接移除（无动画）
            indicator.remove();
        }
    });
}

/**
 * 更新当前文档标题
 * 在界面上显示当前正在操作的文档名称
 * @param {string} title - 要显示的文档标题
 */
function updateActiveDocTitle(title) {
    // 更新应用状态中的当前文档名称
    AppState.currentDocument = title;
    // 更新界面上的文档标题显示（左侧当前文档区域）
    // 限制显示长度为10个字符
    if (elements.activeDocTitle) {
        const displayTitle = title.length > 10 ? title.substring(0, 10) + '...' : title;
        elements.activeDocTitle.textContent = displayTitle;
        // 添加title属性，鼠标悬停时显示完整标题
        elements.activeDocTitle.setAttribute('title', title);
    }
}

/**
 * 更新文档列表
 * 在侧边栏中显示所有文档的列表
 * @param {Array<string>} documents - 文档名称数组
 */
function updateDocumentList(documents) {
    // 更新应用状态中的文档列表
    AppState.documents = documents || [];
    // 清空文档列表容器，准备重新填充
    elements.docList.innerHTML = '';
    
    // 如果没有文档
    if (!documents || documents.length === 0) {
        // 创建一个"暂无文档"的提示项
        const emptyItem = document.createElement('li');
        // 设置列表项的CSS类名
        emptyItem.className = 'doc-list-item';
        // 设置提示文本
        emptyItem.textContent = '暂无文档';
        // 将提示项添加到列表中
        elements.docList.appendChild(emptyItem);
        // 提前返回，不执行后面的代码
        return;
    }
    
    // 遍历文档数组，为每个文档创建一个列表项
    documents.forEach((doc, index) => {
        // 创建列表项元素
        const item = document.createElement('li');
        // 设置列表项的CSS类名
        item.className = 'doc-list-item';
        // 如果这个文档是当前活跃文档
        if (doc === AppState.currentDocument) {
            // 添加'active'类，用于高亮显示当前文档
            item.classList.add('active');
        }
        
        // 创建文档名称的span元素
        const docName = document.createElement('span');
        // 设置文档名称的CSS类名
        docName.className = 'doc-name';
        // 限制文档名称长度（10个字符以内）
        const displayName = doc.length > 10 ? doc.substring(0, 10) + '...' : doc;
        docName.textContent = displayName;
        // 将文档名称添加到列表项中
        item.appendChild(docName);
        
        // 为列表项添加点击事件监听器
        item.addEventListener('click', () => {
            // 当点击文档时，切换到该文档
            switchDocument(doc);
            // 切换文档后关闭侧边栏
            closeSidebar();
        });
        
        // 将列表项添加到文档列表中
        elements.docList.appendChild(item);
    });
    
    // 在所有文档的最后添加"新建文档"按钮
    const createDocItem = document.createElement('li');
    createDocItem.className = 'doc-list-item create-doc-item';
    
    const createDocBtn = document.createElement('button');
    createDocBtn.className = 'create-doc-btn';
    createDocBtn.innerHTML = '<span class="create-icon">➕</span><span class="create-text">新建文档</span>';
    createDocBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // 防止触发父元素事件
        showCreateDocumentDialog();
    });
    
    createDocItem.appendChild(createDocBtn);
    elements.docList.appendChild(createDocItem);
}

/**
 * 显示新建文档对话框
 * 提示用户输入文档名称，然后创建新文档
 */
async function showCreateDocumentDialog() {
    const docName = prompt("请输入新文档的名称 (最多10个字符):");
    if (docName === null) { // 用户点击了取消
        return;
    }

    const trimmedDocName = docName.trim();

    if (!trimmedDocName) {
        alert("文档名称不能为空！");
        return;
    }

    if (trimmedDocName.length > 10) {
        alert("文档名称不能超过10个字符！");
        return;
    }

    // 检查文档是否已存在
    if (AppState.documents.includes(trimmedDocName)) {
        alert(`文档 "${trimmedDocName}" 已存在，请使用其他名称。`);
        return;
    }

    try {
        // 发送创建文档的请求到后端
        const response = await sendMessageToBackend(`创建文档 ${trimmedDocName}`);
        console.log('创建文档响应:', response);
        
        if (response.response_type === 'TEXT' && (response.content.includes('成功创建') || response.content.includes('✅'))) {
            // 等待一小段时间，确保后端数据已保存到D1数据库
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // 刷新文档列表
            const documents = await fetchDocumentList();
            console.log('获取到的文档列表:', documents);
            
            // 更新文档列表显示
            updateDocumentList(documents);
            
            // 切换到新创建的文档
            switchDocument(trimmedDocName);
            
            // 显示成功消息（不显示alert，改为在聊天区域显示）
            addMessageToChat('ai', `✅ 文档 "${trimmedDocName}" 创建成功！`);
        } else {
            alert(`创建文档失败：${response.content || '未知错误'}`);
        }
    } catch (error) {
        console.error('创建文档失败:', error);
        alert(`创建文档时发生错误：${error.message}`);
    }
}

/**
 * 切换文档
 * 切换到指定的文档，并更新界面显示
 * @param {string} docName - 要切换到的文档名称
 */
function switchDocument(docName) {
    // 更新当前文档标题
    updateActiveDocTitle(docName);
    // 可以在这里发送切换文档的指令到后端（当前版本只是前端切换）
    // 显示切换成功的提示消息
    addMessageToChat('ai', `已切换到文档：${docName}`);
    // 更新文档列表，重新高亮当前文档
    updateDocumentList(AppState.documents);
}

/**
 * 打开文档列表侧边栏
 * 通过切换文档按钮触发
 */
function openSidebar() {
    // 给侧边栏添加'open'类，触发CSS动画显示侧边栏
    elements.sidebar.classList.add('open');
    // 显示侧边栏遮罩层（半透明背景）
    elements.sidebarOverlay.classList.add('show');
    // 禁止页面滚动，防止背景内容滚动
    document.body.style.overflow = 'hidden';
}

/**
 * 显示查看文档弹窗（完整查看当前文档）
 */
async function showViewDocumentModal() {
    if (!elements.viewDocumentModal || !elements.viewDocumentTitle || !elements.viewDocumentText) {
        return;
    }
    
    const currentDoc = AppState.currentDocument || '试用文档';
    console.log('[查看文档] 当前选中的文档:', currentDoc);
    console.log('[查看文档] AppState.currentDocument:', AppState.currentDocument);
    
    elements.viewDocumentTitle.textContent = currentDoc;
    elements.viewDocumentText.textContent = '正在加载文档内容...';
    
    // 显示弹窗
    elements.viewDocumentModal.classList.remove('hidden');
    
    try {
        // 通过发送"查看所有笔记"获取所有文档，然后显示当前文档的全部内容
        console.log('[试用模式] 获取文档内容，当前文档:', currentDoc);
        const response = await sendMessageToBackend('查看所有笔记');
        console.log('[试用模式] API响应:', response);
        
        if (response.response_type === 'ALL_DOCUMENTS' && response.documents) {
            const documentKeys = Object.keys(response.documents);
            console.log('[试用模式] 文档列表:', documentKeys);
            console.log('[试用模式] 查找文档:', currentDoc);
            
            // 获取当前文档的内容
            let docContent = response.documents[currentDoc];
            
            // 关键修复：如果直接匹配失败，尝试不区分大小写匹配
            if (!docContent) {
                console.log('[试用模式] 直接匹配失败，尝试不区分大小写匹配');
                for (const key in response.documents) {
                    if (key.toLowerCase() === currentDoc.toLowerCase()) {
                        console.log('[试用模式] 找到匹配的文档（不区分大小写）:', key);
                        docContent = response.documents[key];
                        // 更新标题为实际找到的文档名
                        elements.viewDocumentTitle.textContent = key;
                        break;
                    }
                }
            }
            
            // 如果仍然找不到，尝试精确匹配（去除空格）
            if (!docContent) {
                console.log('[试用模式] 不区分大小写匹配失败，尝试去除空格匹配');
                const currentDocTrimmed = currentDoc.trim();
                for (const key in response.documents) {
                    if (key.trim() === currentDocTrimmed) {
                        console.log('[试用模式] 找到匹配的文档（去除空格）:', key);
                        docContent = response.documents[key];
                        elements.viewDocumentTitle.textContent = key;
                        break;
                    }
                }
            }
            
            console.log('[试用模式] 当前文档内容:', docContent ? (Array.isArray(docContent) ? docContent.length + '行' : '非数组') : '不存在');
            
            // 关键修复：如果当前文档不存在，不要fallback到默认文档，而是显示错误信息
            if (!docContent) {
                console.warn('[试用模式] 文档不存在:', currentDoc);
                console.warn('[试用模式] 可用的文档列表:', documentKeys);
                elements.viewDocumentText.textContent = `文档 "${currentDoc}" 不存在或为空。\n\n可用的文档：${documentKeys.join(', ')}`;
                return;
            }
            
                // 将文档内容数组转换为字符串，保留换行
                const content = Array.isArray(docContent) ? docContent.join('\n') : docContent;
                console.log('[试用模式] 显示文档内容，长度:', content.length);
                elements.viewDocumentText.textContent = content;
        } else if (response.response_type === 'DOCUMENT') {
            // 如果返回的是文档内容
            const content = response.content || '';
            elements.viewDocumentText.textContent = content;
        } else if (response.response_type === 'TEXT' && response.content) {
            // 如果返回的是文本，也显示
            elements.viewDocumentText.textContent = response.content;
        } else {
            elements.viewDocumentText.textContent = '无法获取文档内容，请稍后重试。';
        }
    } catch (error) {
        console.error('获取文档内容失败:', error);
        elements.viewDocumentText.textContent = `获取文档内容时发生错误：${error.message}`;
    }
}

/**
 * 隐藏查看文档弹窗
 */
function hideViewDocumentModal() {
    if (elements.viewDocumentModal) {
        elements.viewDocumentModal.classList.add('hidden');
    }
}

/**
 * 关闭侧边栏
 * 隐藏文档列表侧边栏
 */
function closeSidebar() {
    // 移除'open'类，触发CSS动画隐藏侧边栏
    elements.sidebar.classList.remove('open');
    // 隐藏侧边栏遮罩层
    elements.sidebarOverlay.classList.remove('show');
    // 恢复页面滚动
    document.body.style.overflow = '';
}

/**
 * 显示确认模态框
 * 当用户执行危险操作（如清空文档）时，弹出确认对话框
 * @param {string} message - 要显示的确认消息
 * @returns {Promise<boolean>} - 返回一个Promise，resolve时返回用户的选择（true=确认，false=取消）
 */
function showConfirmationModal(message) {
    // 返回一个Promise，用于异步处理用户的选择
    return new Promise((resolve) => {
        // 转义HTML特殊字符的辅助函数
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        // 设置模态框中显示的确认消息文本
        // 将换行符转换为HTML，支持多行显示和空行
        // 保留空行，将换行符转换为 <br> 标签
        const formattedMessage = message
            .split('\n')
            .map(line => {
                // 如果是空行，保留一个 <br> 标签
                if (line.trim() === '') {
                    return '<br>';
                }
                // 转义HTML特殊字符，防止XSS攻击
                return escapeHtml(line);
            })
            .join('<br>');
        elements.modalText.innerHTML = formattedMessage;
        // 显示模态框（添加'show'类）
        elements.confirmationModal.classList.add('show');
        
        // 定义确认按钮的点击处理函数
        const handleConfirm = () => {
            // 隐藏模态框
            elements.confirmationModal.classList.remove('show');
            // 移除事件监听器，防止重复触发
            elements.confirmYesBtn.removeEventListener('click', handleConfirm);
            elements.confirmNoBtn.removeEventListener('click', handleCancel);
            // 返回true表示用户确认了操作
            resolve(true);
        };
        
        // 定义取消按钮的点击处理函数
        const handleCancel = () => {
            // 隐藏模态框
            elements.confirmationModal.classList.remove('show');
            // 移除事件监听器
            elements.confirmYesBtn.removeEventListener('click', handleConfirm);
            elements.confirmNoBtn.removeEventListener('click', handleCancel);
            // 返回false表示用户取消了操作
            resolve(false);
        };
        
        // 为确认按钮添加点击事件监听器
        elements.confirmYesBtn.addEventListener('click', handleConfirm);
        // 为取消按钮添加点击事件监听器
        elements.confirmNoBtn.addEventListener('click', handleCancel);
    });
}

/**
 * 处理文档匹配确认
 * 当文档类型与内容类型不匹配时，显示确认对话框
 * @param {Object} response - 后端返回的响应对象，包含匹配检查信息
 */
async function handleMatchConfirmation(response) {
    return new Promise((resolve) => {
        console.log('[文档匹配确认] 开始显示确认对话框');
        console.log('[文档匹配确认] 响应内容:', response);
        
        // 存储原始内容，以便在新建文档后提示用户
        // 从 intent_info 中获取 content，如果没有则从 content_to_process 获取
        const originalContent = response.intent_info?.content || response.intent_info?.content_to_process || '';
        const suggestedDocName = response.suggested_doc_title || '新文档';
        
        console.log('[文档匹配确认] 原始内容:', originalContent);
        console.log('[文档匹配确认] 建议的文档名:', suggestedDocName);
        
        // 设置确认消息（支持换行和分段）
        if (elements.matchConfirmationMessage) {
            const message = response.match_warning_message || response.content || '是否确认添加此内容？';
            // 将换行符转换为 <br>，并添加适当的样式
            // 使用 <div> 来创建段落，而不是简单的 <br>
            const formattedMessage = message
                .split('\n\n')  // 按双换行符分段
                .map(paragraph => {
                    // 检查是否是警告或建议段落
                    if (paragraph.startsWith('⚠️')) {
                        return `<div class="match-warning-title">${paragraph.replace(/\n/g, '<br>')}</div>`;
                    } else if (paragraph.startsWith('💡')) {
                        return `<div class="match-suggestion">${paragraph.replace(/\n/g, '<br>')}</div>`;
                    } else {
                        return `<div class="match-content">${paragraph.replace(/\n/g, '<br>')}</div>`;
                    }
                })
                .join('<div class="match-spacer"></div>');  // 段落之间添加间距
            
            elements.matchConfirmationMessage.innerHTML = formattedMessage;
            console.log('[文档匹配确认] 消息已设置:', message);
        } else {
            console.error('[文档匹配确认] 错误: matchConfirmationMessage 元素未找到');
        }
        
        // 显示确认对话框
        if (elements.matchConfirmationModal) {
            elements.matchConfirmationModal.classList.remove('hidden');
            elements.matchConfirmationModal.classList.add('show');
            console.log('[文档匹配确认] 弹窗已显示，类名:', elements.matchConfirmationModal.className);
            
            // 检查按钮是否存在
            console.log('[文档匹配确认] 确定加入按钮:', elements.matchConfirmYesBtn);
            console.log('[文档匹配确认] 新建文档按钮:', elements.matchConfirmNewDocBtn);
            console.log('[文档匹配确认] 取消按钮:', elements.matchConfirmCancelBtn);
            
            // 确保所有按钮都可见（强制显示）
            if (elements.matchConfirmYesBtn) {
                elements.matchConfirmYesBtn.style.display = 'block';
                elements.matchConfirmYesBtn.style.visibility = 'visible';
                elements.matchConfirmYesBtn.style.opacity = '1';
                console.log('[文档匹配确认] 确定加入按钮 - 已强制显示');
            } else {
                console.error('[文档匹配确认] 错误: matchConfirmYesBtn 元素未找到');
            }
            if (elements.matchConfirmNewDocBtn) {
                elements.matchConfirmNewDocBtn.style.display = 'block';
                elements.matchConfirmNewDocBtn.style.visibility = 'visible';
                elements.matchConfirmNewDocBtn.style.opacity = '1';
                console.log('[文档匹配确认] 新建文档按钮 - 已强制显示');
            } else {
                console.error('[文档匹配确认] 错误: matchConfirmNewDocBtn 元素未找到');
            }
            if (elements.matchConfirmCancelBtn) {
                elements.matchConfirmCancelBtn.style.display = 'block';
                elements.matchConfirmCancelBtn.style.visibility = 'visible';
                elements.matchConfirmCancelBtn.style.opacity = '1';
                console.log('[文档匹配确认] 取消按钮 - 已强制显示');
            } else {
                console.error('[文档匹配确认] 错误: matchConfirmCancelBtn 元素未找到');
            }
        } else {
            console.error('[文档匹配确认] 错误: matchConfirmationModal 元素未找到');
        }
        
        // 确认添加按钮
        const handleConfirmYes = async () => {
            if (elements.matchConfirmationModal) {
                elements.matchConfirmationModal.classList.remove('show');
                elements.matchConfirmationModal.classList.add('hidden');
            }
            
            // 移除事件监听器
            if (elements.matchConfirmYesBtn) {
                elements.matchConfirmYesBtn.removeEventListener('click', handleConfirmYes);
            }
            if (elements.matchConfirmNewDocBtn) {
                elements.matchConfirmNewDocBtn.removeEventListener('click', handleConfirmNewDoc);
            }
            if (elements.matchConfirmCancelBtn) {
                elements.matchConfirmCancelBtn.removeEventListener('click', handleCancel);
            }
            
            // 发送确认消息到后端
            try {
                AppState.isLoading = true;
                showLoadingIndicator();
                
                // 发送"确认"消息，包含原始内容
                const confirmResponse = await sendMessageToBackend('确认');
                
                hideLoadingIndicator(true);
                await new Promise(r => setTimeout(r, 300));
                AppState.isLoading = false;
                
                // 处理确认后的响应
                await handleBackendResponse(confirmResponse);
            } catch (error) {
                hideLoadingIndicator(false);
                AppState.isLoading = false;
                addMessageToChat('ai', `确认操作时发生错误：${error.message}`, 'text', true);
            }
            
            resolve(true);
        };
        
        // 新建文档按钮
        const handleConfirmNewDoc = async () => {
            console.log('[文档匹配确认] 点击了"新建文档"按钮');
            
            // 先关闭文档匹配确认弹窗
            if (elements.matchConfirmationModal) {
                elements.matchConfirmationModal.classList.remove('show');
                elements.matchConfirmationModal.classList.add('hidden');
                console.log('[文档匹配确认] 已关闭文档匹配确认弹窗');
            }
            
            // 移除事件监听器
            if (elements.matchConfirmYesBtn) {
                elements.matchConfirmYesBtn.removeEventListener('click', handleConfirmYes);
            }
            if (elements.matchConfirmNewDocBtn) {
                elements.matchConfirmNewDocBtn.removeEventListener('click', handleConfirmNewDoc);
            }
            if (elements.matchConfirmCancelBtn) {
                elements.matchConfirmCancelBtn.removeEventListener('click', handleCancel);
            }
            
            // 等待一小段时间，确保弹窗关闭动画完成
            await new Promise(resolve => setTimeout(resolve, 200));
            
            // 显示新建文档对话框，使用建议的文档名称作为默认值
            const docName = prompt(`请输入新文档的名称:\n(建议: ${suggestedDocName})`, suggestedDocName);
            if (docName === null) { // 用户点击了取消
                resolve(false);
                return;
            }

            const trimmedDocName = docName.trim();
            if (!trimmedDocName) {
                alert("文档名称不能为空！");
                resolve(false);
                return;
            }

            if (trimmedDocName.length > 10) {
                alert("文档名称不能超过10个字符！");
                resolve(false);
                return;
            }

            try {
                AppState.isLoading = true;
                showLoadingIndicator();
                
                // 发送创建文档的请求到后端
                const createResponse = await sendMessageToBackend(`创建文档 ${trimmedDocName}`);
                console.log('创建文档响应:', createResponse);
                
                hideLoadingIndicator(true);
                await new Promise(r => setTimeout(r, 300));
                AppState.isLoading = false;
                
                if (createResponse.response_type === 'TEXT' && (createResponse.content.includes('成功创建') || createResponse.content.includes('✅'))) {
                    // 等待一小段时间，确保后端数据已保存
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    // 刷新文档列表
                    const documents = await fetchDocumentList();
                    updateDocumentList(documents);
                    
                    // 切换到新创建的文档
                    switchDocument(trimmedDocName);
                    
                    // 显示提示消息，引导用户输入之前的内容
                    if (originalContent) {
                        addMessageToChat('ai', `✅ 文档「${trimmedDocName}」已创建。\n\n📝 新文档为空，内容已自动填充到输入框，您可以直接发送或修改后发送。`, 'text', false);
                        // 将原始内容填充到输入框，方便用户直接发送
                        if (elements.userInput) {
                            elements.userInput.value = originalContent;
                            elements.userInput.focus();
                            // 选中所有文本，方便用户直接替换或发送
                            elements.userInput.select();
                        }
                    } else {
                        addMessageToChat('ai', `✅ 文档「${trimmedDocName}」已创建。`);
                    }
                } else {
                    addMessageToChat('ai', `❌ 创建文档失败：${createResponse.content || '未知错误'}`, 'text', true);
                }
            } catch (error) {
                hideLoadingIndicator(false);
                AppState.isLoading = false;
                console.error('创建文档失败:', error);
                addMessageToChat('ai', `创建文档时发生错误：${error.message}`, 'text', true);
            }
            
            resolve(false);
        };
        
        // 取消按钮
        const handleCancel = () => {
            if (elements.matchConfirmationModal) {
                elements.matchConfirmationModal.classList.remove('show');
                elements.matchConfirmationModal.classList.add('hidden');
            }
            
            // 移除事件监听器
            if (elements.matchConfirmYesBtn) {
                elements.matchConfirmYesBtn.removeEventListener('click', handleConfirmYes);
            }
            if (elements.matchConfirmNewDocBtn) {
                elements.matchConfirmNewDocBtn.removeEventListener('click', handleConfirmNewDoc);
            }
            if (elements.matchConfirmCancelBtn) {
                elements.matchConfirmCancelBtn.removeEventListener('click', handleCancel);
            }
            
            addMessageToChat('ai', '操作已取消。');
            resolve(false);
        };
        
        // 绑定事件监听器
        if (elements.matchConfirmYesBtn) {
            elements.matchConfirmYesBtn.addEventListener('click', handleConfirmYes);
        }
        if (elements.matchConfirmNewDocBtn) {
            elements.matchConfirmNewDocBtn.addEventListener('click', handleConfirmNewDoc);
        }
        if (elements.matchConfirmCancelBtn) {
            elements.matchConfirmCancelBtn.addEventListener('click', handleCancel);
        }
    });
}

// ============================================
// API通信函数
// ============================================

/**
 * 发送消息到后端
 * 将用户的输入发送到后端API，获取AI的回复
 * @param {string} text - 用户输入的文本
 * @returns {Promise<Object>} - 返回一个Promise，resolve时返回后端返回的响应数据
 */
async function sendMessageToBackend(text) {
    // 拼接完整的API URL：基础URL + 接口路径
    const url = API_CONFIG.baseURL + API_CONFIG.endpoints.chat;
    
    // 使用try-catch捕获可能的错误
    try {
        // 使用fetch API发送HTTP POST请求到后端
        const response = await fetch(url, {
            method: 'POST',  // 使用POST方法
            headers: {
                'Content-Type': 'application/json',  // 设置请求头，告诉服务器发送的是JSON数据
            },
            body: JSON.stringify({  // 将请求数据转换为JSON字符串
                session_id: AppState.sessionId,  // 发送会话ID，用于区分不同用户
                text: text  // 发送用户输入的文本
            })
        });
        
        // 检查响应状态，如果不是200-299之间的状态码，说明请求失败
        if (!response.ok) {
            // 尝试获取错误详情
            let errorDetail = `HTTP error! status: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorDetail = errorData.detail;
                } else if (errorData.message) {
                    errorDetail = errorData.message;
                } else if (errorData.content) {
                    errorDetail = errorData.content;
                }
            } catch (e) {
                // 如果无法解析JSON，使用状态码
                const text = await response.text().catch(() => '');
                if (text) {
                    errorDetail = text.substring(0, 200); // 限制长度
                }
            }
            // 抛出错误，包含详细错误信息
            const error = new Error(errorDetail);
            error.status = response.status;
            throw error;
        }
        
        // 将响应体解析为JSON对象
        const data = await response.json();
        // 返回解析后的数据
        return data;
    } catch (error) {
        // 如果发生错误，在控制台输出错误信息
        console.error('API请求失败:', error);
        // 重新抛出错误，让调用者处理
        throw error;
    }
}

/**
 * 获取文档列表
 * 从后端API获取所有文档的名称列表
 * @returns {Promise<Array<string>>} - 返回一个Promise，resolve时返回文档名称数组
 */
async function fetchDocumentList() {
    // 拼接完整的API URL，添加session_id参数
    const url = new URL(API_CONFIG.baseURL + API_CONFIG.endpoints.documents);
    
    // 检查是否为试用模式
    // 默认为试用模式，除非明确设置为 'false'（即用户已登录）
    const storedMode = localStorage.getItem('is_trial_mode');
    const isTrialMode = storedMode !== 'false';
    
    console.log('[获取文档列表] 模式检查:', {
        storedMode: storedMode,
        isTrialMode: isTrialMode,
        sessionId: AppState.sessionId,
        trialSessionId: localStorage.getItem('trial_session_id')
    });
    
    // 试用模式必须使用trial_session_id
    if (isTrialMode) {
        const trialSessionId = localStorage.getItem('trial_session_id') || AppState.sessionId;
        if (trialSessionId) {
            url.searchParams.set('session_id', trialSessionId);
        }
        url.searchParams.set('doc_type', 'trial');
        url.searchParams.set('is_trial', 'true');
        console.log('[获取文档列表] 启用试用模式，session_id:', trialSessionId);
    } else {
        if (AppState.sessionId) {
            url.searchParams.set('session_id', AppState.sessionId);
        }
        url.searchParams.set('doc_type', 'dev');
        url.searchParams.set('is_trial', 'false');
        console.log('[获取文档列表] 启用开发者模式，session_id:', AppState.sessionId);
    }
    
    // 使用try-catch捕获可能的错误
    try {
        // 使用fetch API发送HTTP GET请求
        const response = await fetch(url.toString(), {
            method: 'GET',  // 使用GET方法
            headers: {
                'Content-Type': 'application/json',  // 设置请求头
            }
        });
        
        // 检查响应状态
        if (!response.ok) {
            // 如果请求失败，抛出错误
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 解析响应为JSON对象
        const data = await response.json();
        console.log('[获取文档列表] API响应:', data);
        
        // 返回文档数组，如果data.documents不存在则返回空数组
        let documents = data.documents || [];
        console.log('[获取文档列表] 解析后的文档列表:', documents);
        
        // 如果文档列表为空，根据模式返回默认文档
        if (documents.length === 0) {
            const storedMode = localStorage.getItem('is_trial_mode');
            const isTrialMode = storedMode !== 'false';
            
            if (isTrialMode) {
                documents = ["通信原理笔记", "PM问答笔记", "试用文档"];
                console.log('[获取文档列表] 文档列表为空，使用试用模式默认文档:', documents);
            } else {
                documents = ["介绍文档", "更新记录日志"];
                console.log('[获取文档列表] 文档列表为空，使用开发者模式默认文档:', documents);
            }
        }
        
        // 更新AppState中的文档列表
        AppState.documents = documents;
        
        console.log('[获取文档列表] 最终返回的文档列表:', documents);
        return documents;
    } catch (error) {
        // 如果发生错误，在控制台输出错误信息
        console.error('获取文档列表失败:', error);
        // 即使出错，也返回默认列表（试用模式）
        return ['试用文档'];
    }
}

// ============================================
// 核心业务逻辑
// ============================================

/**
 * 处理用户发送的消息
 * 这是处理用户输入的核心函数，负责发送消息、显示加载状态、处理响应等
 */
async function handleSendMessage() {
    console.log('[发送消息] 函数被调用');
    
    // 获取用户输入框中的文本，并去除首尾空白字符
    const text = elements.userInput ? elements.userInput.value.trim() : '';
    console.log('[发送消息] 输入文本:', text);
    
    // 如果输入为空
    if (!text) {
        console.log('[发送消息] 输入为空，不发送');
        // 添加视觉反馈：输入框轻微震动动画
        if (elements.userInput) {
            elements.userInput.style.animation = 'shake 0.3s';
            // 300毫秒后移除动画，恢复原状
            setTimeout(() => {
                elements.userInput.style.animation = '';
            }, 300);
        }
        // 提前返回，不处理空消息
        return;
    }
    
    // 如果正在处理中（防止重复提交）
    if (AppState.isLoading) {
        console.log('[发送消息] 正在处理中，忽略新消息');
        // 忽略新消息，直接返回
        return;
    }
    
    console.log('[发送消息] 开始处理消息');
    
    // 禁用发送按钮，防止重复点击
    elements.sendBtn.disabled = true;
    
    // 清空输入框
    elements.userInput.value = '';
    // 自动调整输入框高度（因为内容被清空，高度会恢复）
    autoResizeTextarea(elements.userInput);
    
    // 在聊天区域显示用户发送的消息
    addMessageToChat('user', text);
    
    // 设置加载状态为true
    AppState.isLoading = true;
    // 显示加载指示器（"AI正在思考..."）
    showLoadingIndicator();
    
    // 更新连接状态为加载中（加速旋转）
    updateConnectionStatus('loading');
    
    // 清空之前的反馈信息
    clearAIFeedback();
    // 添加初始反馈（显示用户输入）
    addAIFeedback(`[用户输入] ${text.substring(0, 50)}${text.length > 50 ? '...' : ''}`);
    
    // 使用try-catch处理可能的错误
    try {
        // 记录开始时间（用于计算响应时间）
        const startTime = performance.now();
        
        // 发送消息到后端，等待响应
        console.log('📤 发送消息到后端:', text.substring(0, 50) + (text.length > 50 ? '...' : ''));
        addAIFeedback('[系统] 正在调用意图识别器...');
        
        const response = await sendMessageToBackend(text);
        
        // 计算响应时间
        const endTime = performance.now();
        const elapsedTime = ((endTime - startTime) / 1000).toFixed(2); // 转换为秒，保留两位小数
        console.log(`⏱️ 响应时间: ${elapsedTime}秒`);
        addAIFeedback(`⏱️ [响应时间] ${elapsedTime}秒`);
        
        console.log('✅ 收到后端响应:', response);
        console.log('✅ 响应中的意图信息:', response.intent_info);
        console.log('✅ 响应中的工具调用:', response.tools_used);
        
        // 显示意图识别调试信息（模拟后端日志格式）
        if (response.intent_info) {
            console.log('[意图识别] 原始intent_data:', {
                intent: response.intent_info.intent,
                original_intent: response.intent_info.original_intent,
                doc_title: response.intent_info.doc_title,
                position: response.intent_info.position,
                content_length: response.intent_info.content_length,
                message_style: response.intent_info.message_style
            });
            console.log('[意图识别] 处理后的intent:', response.intent_info.intent || response.intent_info.original_intent || 'UNKNOWN');
            
            // 如果是GREETING意图，显示特殊日志
            const intent = response.intent_info.intent || response.intent_info.original_intent;
            if (intent === 'GREETING') {
                console.log('[意图识别] ✅ 检测到GREETING意图！');
                console.log('[GREETING处理] 进入GREETING意图处理分支');
                console.log('[GREETING处理] 内容:', response.content ? response.content.substring(0, 50) + '...' : 'None');
                console.log('[GREETING处理] intent_info:', response.intent_info);
                console.log('[GREETING处理] tools_used:', response.tools_used);
            }
        } else {
            console.log('[意图识别] ⚠️ 响应中未包含intent_info');
        }
        
        // 先隐藏加载指示器（在显示回复之前，使用破碎动画）
        hideLoadingIndicator(true);
        
        // 等待动画完成后再显示回复（确保动画效果可见）
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // 更新连接状态为已连接（恢复正常旋转）
        updateConnectionStatus('connected');
        
        // 处理后端返回的响应（这里会调用 addAIFeedbackFromResponse 显示详细信息）
        await handleBackendResponse(response);
        
        // 设置加载状态为false
        AppState.isLoading = false;
        // 重新启用发送按钮
        elements.sendBtn.disabled = false;
        
    } catch (error) {
        // 如果发生错误，隐藏加载指示器（不使用动画，直接隐藏）
        hideLoadingIndicator(false);
        // 设置加载状态为false
        AppState.isLoading = false;
        // 重新启用发送按钮
        elements.sendBtn.disabled = false;
        
        // 根据错误类型提供更友好的提示信息
        let errorMessage = '';
        // 检查是否是网络连接错误
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            // 如果是网络错误，提供详细的解决方案
            errorMessage = `❌ 无法连接到后端服务器\n\n` +
                         `可能的原因：\n` +
                         `1. 后端API服务器未启动\n` +
                         `2. 后端服务器地址配置不正确\n\n` +
                         `解决方案：\n` +
                         `1. 请先启动后端服务器：\n` +
                         `   - Windows: 运行 start_api_server.bat\n` +
                         `   - 或执行: python api_server.py\n\n` +
                         `2. 确认后端服务器运行在: ${API_CONFIG.baseURL}\n\n` +
                         `3. 如果后端运行在不同地址，请修改 app.js 中的 API_CONFIG.baseURL`;
        } else if (error.status === 500 || error.message.includes('HTTP error! status: 500')) {
            // 如果是500错误，尝试显示真实的错误原因
            // 如果错误消息不是通用的HTTP错误消息，使用它
            if (error.message && !error.message.startsWith('HTTP error! status:')) {
                errorMessage = `❌ 服务器错误：${error.message}\n\n` +
                             `这可能是后端代码的问题。请检查后端日志获取详细信息。`;
            } else {
                // 如果是通用的HTTP错误，提供更详细的提示
                errorMessage = `❌ 服务器内部错误（500）\n\n` +
                             `可能的原因：\n` +
                             `1. 后端代码执行出错\n` +
                             `2. 数据库连接失败\n` +
                             `3. LLM API调用失败\n\n` +
                             `请检查后端控制台的错误日志，或联系技术支持。`;
            };
        } else {
            // 如果是其他错误，显示通用错误信息
            errorMessage = `抱歉，发生了错误：${error.message}\n\n请检查后端服务是否正常运行。`;
        }
        
        // 添加错误反馈
        addAIFeedback(`[错误] ${error.message}`);
        
        // 更新连接状态为已连接（恢复正常旋转）
        updateConnectionStatus('connected');
        
        // 在聊天区域显示错误消息（使用error样式）
        addMessageToChat('ai', errorMessage, 'text', true);
        // 在控制台输出详细错误信息，方便调试
        console.error('处理消息时出错:', error);
    }
}

/**
 * 处理后端响应
 * 根据后端返回的响应类型，执行不同的操作
 * @param {Object} response - 后端返回的响应对象，包含response_type、content等字段
 */
async function handleBackendResponse(response) {
    // 检查响应是否有效
    if (!response) {
        console.error('[handleBackendResponse] 响应对象为空');
        return;
    }
    
    // 从响应对象中解构出需要的字段
    const { response_type, content, new_session_id, dev_mode_enabled, edit_mode_enabled, message_style } = response;
    
    // 控制台输出：显示后端响应的详细信息
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📥 收到后端响应');
    console.log('响应类型:', response_type);
    console.log('响应内容:', content ? content.substring(0, 100) + (content.length > 100 ? '...' : '') : '(空)');
    console.log('消息样式:', message_style || 'normal');
    console.log('是否开发者模式:', dev_mode_enabled);
    console.log('是否编辑模式:', edit_mode_enabled);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    // 演示模式：不保存 session_id，但显示在界面上
    // 即使后端返回了 new_session_id，也不保存
    // 下次刷新时会创建新的 session
    if (new_session_id) {
        // 更新界面显示（但不保存到 AppState）
        updateSessionIdDisplay(new_session_id);
    }
    // if (new_session_id) {
    //     AppState.sessionId = new_session_id;
    // }   
    // 更新开发者模式状态（仅用于状态跟踪，不再自动跳转）
    if (dev_mode_enabled !== undefined) {
        AppState.devModeEnabled = dev_mode_enabled;
    }
    
    // 检查是否是重复内容警告（优先处理）
    if (response.intent_info && (response.intent_info.intent === 'DUPLICATE_CONTENT' || response.intent_info.original_intent === 'DUPLICATE_CONTENT')) {
        console.log('[去重检测] 检测到重复内容，显示警告消息');
        // 显示警告消息
        const warningMessage = content || '⚠️ 检测到重复内容，不进行添加';
        addMessageToChat('ai', warningMessage, 'text', false, true); // false = 不是错误，true = 是警告
        addAIFeedback('[系统] 检测到重复内容，已阻止添加');
        return;
    }
    
    // 检查是否需要总结文档（优先处理）
    if (response.system_action_required === 'SUMMARIZE_DOCUMENT') {
        console.log('[总结功能] 检测到总结请求');
        const targetDoc = response.target_document || AppState.currentDocument;
        console.log('[总结功能] 目标文档:', targetDoc);
        
        // 显示加载提示
        addMessageToChat('ai', `📝 正在生成「${targetDoc}」的总结...`, 'text');
        addAIFeedback(`[系统] 开始总结文档: ${targetDoc}`);
        
        // 调用后端 API 获取总结
        try {
            const summaryResponse = await fetch(API_CONFIG.baseURL + API_CONFIG.endpoints.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: `请总结文档「${targetDoc}」的内容`,
                    session_id: AppState.sessionId,
                    current_document: targetDoc
                })
            });
            
            if (summaryResponse.ok) {
                const summaryData = await summaryResponse.json();
                if (summaryData.content) {
                    // 显示总结结果
                    addMessageToChat('ai', summaryData.content, 'text');
                    addAIFeedback(`[系统] 总结完成`);
                } else {
                    addMessageToChat('ai', '⚠️ 无法生成总结，请稍后再试。', 'text', false, true);
                }
            } else {
                addMessageToChat('ai', '⚠️ 总结请求失败，请稍后再试。', 'text', false, true);
            }
        } catch (error) {
            console.error('[总结功能] 错误:', error);
            addMessageToChat('ai', '⚠️ 总结请求失败，请检查网络连接。', 'text', false, true);
        }
        return;
    }
    
    // 根据响应类型执行不同的操作
    switch (response_type) {
        case 'DEV_MODE_REQUIRED':
            // 如果需要开发者模式，显示提示（通常使用错误样式）
            const devModeIsError = (message_style === 'error' || message_style === undefined);
            addMessageToChat('ai', content, 'text', devModeIsError);
            addAIFeedbackFromResponse(response);
            // 可以在这里添加一个提示，引导用户输入开发者模式代码
            break;
        case 'EDIT_MODE_REQUIRED':
            // 如果需要修改权限，显示提示（使用错误样式，红色）
            // 后端应该返回 message_style="error"，如果没有则默认使用错误样式
            const editModeIsError = (message_style === 'error' || message_style === undefined || message_style === null);
            addMessageToChat('ai', content, 'text', editModeIsError, false);
            addAIFeedbackFromResponse(response);
            break;
        case 'CREATE_NEW_DOCUMENT_CONFIRMATION':
            // 需要确认是否创建新文档
            const suggestedTitle = response.suggested_doc_title || '新文档';
            const createDocConfirmed = await showConfirmationModal(content);
            if (createDocConfirmed) {
                // 用户确认，发送确认消息
                await sendMessageToBackend('确认');
            } else {
                // 用户取消，发送取消消息
                await sendMessageToBackend('取消');
            }
            break;
        case 'TEXT':
            // 如果是普通文本回复，只根据后端返回的message_style决定是否使用错误样式
            // 不再依赖内容关键词判断，因为正常消息也可能包含"抱歉"等词
            const isError = message_style === 'error';
            const isWarning = message_style === 'warning';
            
            if (isError) {
                console.log('⚠️ [TEXT响应] 后端指定使用错误样式显示');
            } else if (isWarning) {
                console.log('⚠️ [TEXT响应] 后端指定使用警告样式显示');
            } else {
                console.log('✅ [TEXT响应] 使用正常样式显示');
            }
            addMessageToChat('ai', content, 'text', isError, isWarning);
            addAIFeedbackFromResponse(response);
            // 跳出switch语句
            break;
            
        case 'CONFIRMATION':
            // 检查是否是文档匹配确认
            console.log('[CONFIRMATION响应] match_confirmation_needed:', response.match_confirmation_needed);
            console.log('[CONFIRMATION响应] match_confirmation_needed 类型:', typeof response.match_confirmation_needed);
            console.log('[CONFIRMATION响应] match_confirmation_needed 值:', response.match_confirmation_needed);
            console.log('[CONFIRMATION响应] 完整响应:', JSON.stringify(response, null, 2));
            
            // 检查 match_confirmation_needed 字段（支持多种可能的字段名）
            const needsMatchConfirmation = response.match_confirmation_needed === true || 
                                          response.match_confirmation_needed === 'true' ||
                                          response.matchConfirmationNeeded === true ||
                                          response.matchConfirmationNeeded === 'true';
            
            console.log('[CONFIRMATION响应] needsMatchConfirmation:', needsMatchConfirmation);
            
            if (needsMatchConfirmation) {
                // 文档匹配确认
                console.log('[CONFIRMATION响应] 调用 handleMatchConfirmation');
                await handleMatchConfirmation(response);
            } else {
                // 普通确认操作（如清空文档）
                console.log('[CONFIRMATION响应] 使用普通确认模态框');
            const confirmed = await showConfirmationModal(content);
            // 如果用户确认了
            if (confirmed) {
                // 设置加载状态
                AppState.isLoading = true;
                // 显示加载指示器
                showLoadingIndicator();
                // 使用try-catch处理可能的错误
                try {
                    // 发送"确认"消息到后端
                    const confirmResponse = await sendMessageToBackend('确认');
                    // 隐藏加载指示器（使用破碎动画）
                    hideLoadingIndicator(true);
                    // 等待动画完成
                    await new Promise(resolve => setTimeout(resolve, 300));
                    // 设置加载状态为false
                    AppState.isLoading = false;
                    // 递归处理确认后的响应
                    await handleBackendResponse(confirmResponse);
                } catch (error) {
                    // 如果确认操作失败，隐藏加载指示器（不使用动画）
                    hideLoadingIndicator(false);
                    // 设置加载状态为false
                    AppState.isLoading = false;
                    // 显示错误消息
                    addMessageToChat('ai', `确认操作时发生错误：${error.message}`, 'text', true);
                }
            } else {
                // 如果用户取消了操作
                addMessageToChat('ai', '操作已取消。');
                }
            }
            // 跳出switch语句
            break;
            
        case 'DOCUMENT':
            // 如果是文档内容，以文档卡片形式展示
            addMessageToChat('ai', content, 'document');
            addAIFeedbackFromResponse(response);
            // 跳出switch语句
            break;
            
        case 'UNKNOWN':
            // 如果是无法识别的指令，根据message_style决定使用哪种样式
            // 注意：问候消息应该通过 GREETING 意图处理，不应该进入这个分支
            const unknownIsWarning = message_style === 'warning';
            const unknownIsError = (message_style === 'error' || (message_style === undefined && !unknownIsWarning));
            
            if (unknownIsWarning) {
                console.log('⚠️ [UNKNOWN响应] 三次无法理解，将使用警告样式显示（黄色气泡）');
            } else {
                console.log('⚠️ [UNKNOWN响应] 收到无法识别的指令，将使用错误样式显示');
            }
            addMessageToChat('ai', content || '抱歉，我无法理解您的指令。', 'text', unknownIsError, unknownIsWarning);
            addAIFeedbackFromResponse(response);
            break;
            
        default:
            // 如果是未知类型，作为普通文本处理
            // 如果content为空，显示默认消息
            addMessageToChat('ai', content || '收到未知类型的响应。');
    }
    
    // 无论响应类型是什么，都刷新文档列表
    // 因为操作可能会改变文档列表（如创建新文档）
    const documents = await fetchDocumentList();
    // 更新界面上的文档列表
    updateDocumentList(documents);
}

// ============================================
// 事件绑定
// ============================================

/**
 * 初始化所有事件监听器
 * 为页面上的所有交互元素绑定事件处理函数
 */
// 标记是否已经绑定过事件，避免重复绑定
let eventListenersBound = false;

// 将标记暴露到全局作用域，允许外部重置
window.eventListenersBound = false;

function initEventListeners() {
    console.log('[初始化] 开始绑定事件监听器');
    
    // 同步全局标记
    if (window.eventListenersBound !== undefined) {
        eventListenersBound = window.eventListenersBound;
    }
    
    // 如果已经绑定过，直接返回，避免重复绑定
    if (eventListenersBound) {
        console.log('[初始化] 事件监听器已经绑定过，跳过重复绑定');
        return;
    }
    
    // 确保发送按钮是启用状态
    if (elements.sendBtn) {
        elements.sendBtn.disabled = false;
        console.log('[初始化] 发送按钮已启用');
    } else {
        console.error('[初始化] 发送按钮元素不存在！');
    }
    
    // 清空输入框内容（防止刷新后内容残留）
    if (elements.userInput) {
        elements.userInput.value = '';
        console.log('[初始化] 输入框已清空');
    } else {
        console.error('[初始化] 输入框元素不存在！');
    }
    
    // 发送按钮点击事件：当用户点击发送按钮时
    if (elements.sendBtn) {
        // 先移除可能存在的旧事件监听器（避免重复绑定）
        const newSendBtn = elements.sendBtn.cloneNode(true);
        elements.sendBtn.parentNode.replaceChild(newSendBtn, elements.sendBtn);
        elements.sendBtn = newSendBtn;
        
        elements.sendBtn.addEventListener('click', (e) => {
            console.log('[发送按钮] 点击事件触发');
            e.preventDefault();
            e.stopPropagation();
            handleSendMessage();
        });
        console.log('[初始化] 发送按钮事件已绑定，按钮ID:', elements.sendBtn.id);
    } else {
        console.error('[初始化] 发送按钮元素不存在！');
    }
    
    // 输入框回车事件：当用户在输入框中按下键盘时
    if (elements.userInput) {
        elements.userInput.addEventListener('keydown', (event) => {
            // 如果按下的是Enter键
            if (event.key === 'Enter' || event.keyCode === 13) {
                // 如果按住Ctrl键或Cmd键（Mac），允许换行（不阻止默认行为）
                if (event.ctrlKey || event.metaKey) {
                    // Ctrl+Enter 或 Cmd+Enter：换行，不阻止默认行为
                    console.log('[输入框] Ctrl+Enter：换行');
                    return; // 允许默认行为（换行）
                }
                // Enter键（无Ctrl）：发送消息
                console.log('[输入框] Enter：发送消息，阻止默认行为');
                // 阻止默认行为（默认是换行）
                event.preventDefault();
                event.stopPropagation();
                // 触发发送消息
                handleSendMessage();
            }
        });
        console.log('[初始化] 输入框事件已绑定');
    }
    
    // 输入框内容变化事件：当用户输入或删除文本时
    if (elements.userInput) {
        elements.userInput.addEventListener('input', () => {
            // 自动调整输入框高度，适应内容
            autoResizeTextarea(elements.userInput);
        });
    }
    
    // 输入框获得焦点事件：当用户点击输入框时
    if (elements.userInput) {
        elements.userInput.addEventListener('focus', () => {
            // 给输入框的父容器添加边框颜色，提供视觉反馈
            if (elements.userInput.parentElement) {
                elements.userInput.parentElement.style.borderColor = 'var(--primary-color)';
            }
        });
    }
    
    // 输入框失去焦点事件：当用户点击其他地方时
    if (elements.userInput) {
        elements.userInput.addEventListener('blur', () => {
            // 移除边框颜色，恢复默认样式
            if (elements.userInput.parentElement) {
                elements.userInput.parentElement.style.borderColor = '';
            }
        });
    }
    
    // 切换文档按钮点击事件：当用户点击切换文档按钮时
    if (elements.switchDocBtn) {
        // 先移除可能存在的旧事件监听器
        const newSwitchBtn = elements.switchDocBtn.cloneNode(true);
        elements.switchDocBtn.parentNode.replaceChild(newSwitchBtn, elements.switchDocBtn);
        elements.switchDocBtn = newSwitchBtn;
        
        elements.switchDocBtn.addEventListener('click', (e) => {
            console.log('[切换文档按钮] 点击事件触发');
            e.preventDefault();
            e.stopPropagation();
            openSidebar();
        });
        console.log('[初始化] 切换文档按钮事件已绑定');
    } else {
        console.warn('[初始化] 切换文档按钮元素不存在');
    }
    
    // 查看文档按钮点击事件：当用户点击查看文档按钮时，弹出模态框显示当前文档的全部内容
    if (elements.viewDocBtn) {
        // 先移除可能存在的旧事件监听器
        const newViewBtn = elements.viewDocBtn.cloneNode(true);
        elements.viewDocBtn.parentNode.replaceChild(newViewBtn, elements.viewDocBtn);
        elements.viewDocBtn = newViewBtn;
        
        elements.viewDocBtn.addEventListener('click', (e) => {
            console.log('[查看文档按钮] 点击事件触发');
            e.preventDefault();
            e.stopPropagation();
            showViewDocumentModal();
        });
        console.log('[初始化] 查看文档按钮事件已绑定');
    } else {
        console.warn('[初始化] 查看文档按钮元素不存在');
    }
    
    // 关闭查看文档弹窗按钮点击事件
    if (elements.closeViewDocumentBtn) {
        elements.closeViewDocumentBtn.addEventListener('click', hideViewDocumentModal);
    }
    
    // 点击弹窗遮罩层关闭弹窗
    if (elements.viewDocumentModal) {
        elements.viewDocumentModal.addEventListener('click', (e) => {
            if (e.target === elements.viewDocumentModal) {
                hideViewDocumentModal();
            }
        });
    }
    
    // 登录按钮点击事件：当用户点击登录按钮时
    if (elements.loginBtn) {
        elements.loginBtn.addEventListener('click', () => {
            // 调用登录处理函数（如果存在）
            if (typeof handleLogin === 'function') {
                handleLogin();
            } else {
                // 如果没有登录处理函数，可以显示登录模态框
                // 或者执行其他登录逻辑
                console.log('登录按钮被点击');
            }
        });
    }
    
    // 应用端下载按钮悬停事件：显示/隐藏提示框
    if (elements.downloadAppBtn && elements.downloadAppTooltip) {
        const downloadAppContainer = elements.downloadAppBtn.closest('.download-app-container-header');
        if (downloadAppContainer) {
            downloadAppContainer.addEventListener('mouseenter', () => {
                elements.downloadAppTooltip.classList.remove('hidden');
            });
            downloadAppContainer.addEventListener('mouseleave', () => {
                elements.downloadAppTooltip.classList.add('hidden');
            });
        }
    }
    
    // 面试模式按钮悬停事件：显示/隐藏提示框
    // 旧的面试模式按钮已移除，事件处理已移到对话模式下拉菜单中
    
    // 语音输入按钮悬停提示
    if (elements.voiceBtnContainer && elements.voiceBtnTooltip) {
        const updateTooltipPosition = () => {
            if (elements.voiceBtnContainer && elements.voiceBtnTooltip) {
                const rect = elements.voiceBtnContainer.getBoundingClientRect();
                // 计算提示框位置：在按钮上方居中
                const left = rect.left + rect.width / 2; // 按钮中心点
                const bottom = window.innerHeight - rect.top + 10; // 按钮顶部上方10px
                elements.voiceBtnTooltip.style.left = `${left}px`;
                elements.voiceBtnTooltip.style.bottom = `${bottom}px`;
            }
        };
        
        elements.voiceBtnContainer.addEventListener('mouseenter', () => {
            updateTooltipPosition();
            elements.voiceBtnTooltip.classList.remove('hidden');
        });
        elements.voiceBtnContainer.addEventListener('mouseleave', () => {
            elements.voiceBtnTooltip.classList.add('hidden');
        });
        
        // 窗口大小改变时更新位置
        window.addEventListener('resize', updateTooltipPosition);
        // 滚动时更新位置
        window.addEventListener('scroll', updateTooltipPosition, true);
    }
    
    // 附件上传按钮提示框（在图标上方弹出，使用CSS定位，不需要JavaScript计算位置）
    if (elements.attachmentBtn && elements.attachmentBtnTooltip) {
        elements.attachmentBtn.addEventListener('mouseenter', () => {
            elements.attachmentBtnTooltip.classList.remove('hidden');
        });
        elements.attachmentBtn.addEventListener('mouseleave', () => {
            elements.attachmentBtnTooltip.classList.add('hidden');
        });
    }
    
    // 对话模式下拉菜单
    if (elements.dialogueModeBtn && elements.dialogueModeDropdown) {
        console.log('对话模式按钮和下拉菜单已找到，绑定事件监听器');
        
        // 先移除可能存在的旧事件监听器（避免重复绑定）
        const newDialogueBtn = elements.dialogueModeBtn.cloneNode(true);
        elements.dialogueModeBtn.parentNode.replaceChild(newDialogueBtn, elements.dialogueModeBtn);
        elements.dialogueModeBtn = newDialogueBtn;
        
        elements.dialogueModeBtn.addEventListener('click', (e) => {
            console.log('对话模式按钮被点击');
            e.stopPropagation();
            e.preventDefault();
            const hasHidden = elements.dialogueModeDropdown.classList.contains('hidden');
            console.log('当前hidden状态:', hasHidden);
            
            // 切换显示/隐藏状态
            if (hasHidden) {
                // 显示弹窗
                elements.dialogueModeDropdown.classList.remove('hidden');
                console.log('显示弹窗');
            } else {
                // 隐藏弹窗
                elements.dialogueModeDropdown.classList.add('hidden');
                console.log('隐藏弹窗');
            }
        });
        
        // 点击外部关闭下拉菜单（使用事件委托，避免重复绑定）
        if (!window.dialogueModeClickHandler) {
            window.dialogueModeClickHandler = (e) => {
                if (elements.dialogueModeBtn && elements.dialogueModeDropdown) {
                    if (!elements.dialogueModeBtn.contains(e.target) && 
                        !elements.dialogueModeDropdown.contains(e.target)) {
                        elements.dialogueModeDropdown.classList.add('hidden');
                        // 清除内联样式
                        elements.dialogueModeDropdown.style.position = '';
                        elements.dialogueModeDropdown.style.top = '';
                        elements.dialogueModeDropdown.style.left = '';
                        elements.dialogueModeDropdown.style.bottom = '';
                        elements.dialogueModeDropdown.style.transform = '';
                    }
                }
            };
            document.addEventListener('click', window.dialogueModeClickHandler);
        }
        
        // 模式切换
        if (elements.normalModeItem) {
            elements.normalModeItem.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡，避免触发外部点击关闭
                console.log('对话模式被点击');
                // 切换到对话模式
                elements.dialogueModeDropdown.classList.add('hidden');
                // 清除内联样式
                elements.dialogueModeDropdown.style.position = '';
                elements.dialogueModeDropdown.style.top = '';
                elements.dialogueModeDropdown.style.left = '';
                elements.dialogueModeDropdown.style.bottom = '';
                elements.dialogueModeDropdown.style.transform = '';
                // 更新按钮文本
                const modeText = elements.dialogueModeBtn.querySelector('.mode-text');
                if (modeText) {
                    modeText.textContent = '对话模式';
                    console.log('按钮文本已更新为: 对话模式');
                } else {
                    console.error('找不到按钮文本元素');
            }
        });
    }
    
        if (elements.interviewModeItem) {
            // 面试模式不允许切换，点击时显示介绍弹窗
            elements.interviewModeItem.addEventListener('click', (e) => {
                e.stopPropagation(); // 阻止事件冒泡
                console.log('面试模式被点击（开发中，显示介绍弹窗）');
                
                // 显示面试模式介绍弹窗
                if (elements.interviewModeInfoPanel) {
                    showInterviewModeInfoPanel();
                }
            });
        }
        
        // 面试模式介绍弹窗关闭按钮
        if (elements.interviewModeInfoClose) {
            elements.interviewModeInfoClose.addEventListener('click', (e) => {
                e.stopPropagation();
                hideInterviewModeInfoPanel();
            });
        }
    }
    
    // 模型选型按钮提示框
    if (elements.modelSelectorBtn && elements.modelSelectorTooltip) {
        elements.modelSelectorBtn.addEventListener('mouseenter', () => {
            elements.modelSelectorTooltip.classList.remove('hidden');
        });
        elements.modelSelectorBtn.addEventListener('mouseleave', () => {
            elements.modelSelectorTooltip.classList.add('hidden');
        });
    }
    
    // 笔记共享按钮提示框
    if (elements.shareNoteBtn && elements.shareNoteTooltip) {
        elements.shareNoteBtn.addEventListener('mouseenter', () => {
            elements.shareNoteTooltip.classList.remove('hidden');
        });
        elements.shareNoteBtn.addEventListener('mouseleave', () => {
            elements.shareNoteTooltip.classList.add('hidden');
        });
    }
    
    // 笔记共享按钮点击事件
    if (elements.shareNoteBtn && elements.shareNoteModal) {
        elements.shareNoteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showShareNoteModal();
        });
    }
    
    // 关闭笔记共享弹窗
    if (elements.closeShareNoteModal) {
        elements.closeShareNoteModal.addEventListener('click', (e) => {
            e.stopPropagation();
            hideShareNoteModal();
        });
    }
    
    // 点击弹窗外部关闭
    if (elements.shareNoteModal) {
        elements.shareNoteModal.addEventListener('click', (e) => {
            if (e.target === elements.shareNoteModal) {
                hideShareNoteModal();
            }
        });
    }
    
    // 复制分享链接
    if (elements.copyShareLinkBtn && elements.shareNoteLink) {
        elements.copyShareLinkBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                await navigator.clipboard.writeText(elements.shareNoteLink.value);
                // 临时改变按钮文本
                const originalText = elements.copyShareLinkBtn.textContent;
                elements.copyShareLinkBtn.textContent = '✅ 已复制';
                setTimeout(() => {
                    elements.copyShareLinkBtn.textContent = originalText;
                }, 2000);
            } catch (err) {
                console.error('复制失败:', err);
                // 降级方案：选中文本
                elements.shareNoteLink.select();
                elements.shareNoteLink.setSelectionRange(0, 99999);
                try {
                    document.execCommand('copy');
                    const originalText = elements.copyShareLinkBtn.textContent;
                    elements.copyShareLinkBtn.textContent = '✅ 已复制';
                    setTimeout(() => {
                        elements.copyShareLinkBtn.textContent = originalText;
                    }, 2000);
                } catch (err2) {
                    console.error('复制失败:', err2);
                    alert('复制失败，请手动复制链接');
                }
            }
        });
    }
    
    // 设置按钮（原登录按钮功能）
    if (elements.settingsBtn) {
        elements.settingsBtn.addEventListener('click', () => {
            // 触发原登录按钮的功能
            if (elements.loginBtn) {
                elements.loginBtn.click();
            }
        });
    }
    
    // 左侧侧边栏更新通知按钮
    if (elements.updateNotificationBtnLeft) {
        elements.updateNotificationBtnLeft.addEventListener('click', (e) => {
            e.stopPropagation();
            // 直接切换更新通知面板
            toggleUpdateNotificationPanel();
        });
        
        // 同步通知徽章
        if (elements.notificationBadge) {
            const badgeLeft = document.getElementById('notification-badge-left');
            if (badgeLeft && elements.notificationBadge.textContent) {
                badgeLeft.textContent = elements.notificationBadge.textContent;
                badgeLeft.style.display = elements.notificationBadge.style.display;
            }
        }
    }
    
    // 点击外部关闭更新通知面板
    document.addEventListener('click', (e) => {
        if (elements.updateNotificationPanel && 
            !elements.updateNotificationPanel.contains(e.target) &&
            !elements.updateNotificationBtnLeft.contains(e.target) &&
            !elements.updateNotificationBtn?.contains(e.target)) {
            hideUpdateNotificationPanel();
            }
        });
    
    // 左侧侧边栏开发者模式按钮
    if (elements.devModeBtnLeft) {
        elements.devModeBtnLeft.addEventListener('click', () => {
            // 跳转到开发者模式页面
            window.location.href = 'dev-mode.html';
        });
    }
    
    // 开发者模式按钮点击事件：当用户点击开发者模式按钮时
    if (elements.devModeBtn) {
        elements.devModeBtn.addEventListener('click', () => {
            // 跳转到开发者模式页面
            window.location.href = 'dev-mode.html';
        });
    }
    
    // AI反馈面板切换事件
    if (elements.aiFeedbackHeader) {
        elements.aiFeedbackHeader.addEventListener('click', (e) => {
            // 如果点击的是切换按钮，阻止事件冒泡（切换按钮有自己的事件处理）
            if (e.target.closest('.ai-feedback-toggle')) {
                e.stopPropagation();
                return;
            }
            // 点击头部其他区域也切换
            if (elements.aiFeedbackPanel) {
                elements.aiFeedbackPanel.classList.toggle('collapsed');
                console.log('[AI反馈] 面板状态:', elements.aiFeedbackPanel.classList.contains('collapsed') ? '收起' : '展开');
                // 更新箭头图标方向
                updateAIFeedbackToggleIcon();
            }
        });
    }
    
    // 也可以直接点击箭头按钮切换
    if (elements.aiFeedbackToggle) {
        elements.aiFeedbackToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            if (elements.aiFeedbackPanel) {
                elements.aiFeedbackPanel.classList.toggle('collapsed');
                console.log('[AI反馈] 切换按钮点击，面板状态:', elements.aiFeedbackPanel.classList.contains('collapsed') ? '收起' : '展开');
                // 更新箭头图标方向
                updateAIFeedbackToggleIcon();
            }
        });
    }
    
    // 标准对话示例面板切换事件
    // 整个 header 区域都可以点击来切换展开/收起状态
    if (elements.exampleHeader) {
        // 检查是否已经绑定过事件（防止重复绑定）
        if (elements.exampleHeader.dataset.listenerBound === 'true') {
            console.log('[示例面板] 事件监听器已绑定，跳过重复绑定');
        } else {
            // 使用防抖机制，防止重复触发
            let isToggling = false;
            let toggleTimeout = null;
            
            const handleHeaderClick = (e) => {
                // 如果点击的是复制按钮，不处理（让复制按钮的事件处理）
            if (e.target.closest('.example-item-copy')) {
                    return;
            }
                
                // 阻止事件冒泡和默认行为
                e.stopPropagation();
                e.preventDefault();
                e.stopImmediatePropagation();
                
                // 防止重复触发
                if (isToggling) {
                    console.log('[示例面板] 正在切换中，忽略重复点击');
                    return;
                }
                
                // 清除之前的定时器
                if (toggleTimeout) {
                    clearTimeout(toggleTimeout);
                }
                
                // 其他所有区域（包括切换按钮和标题）都可以点击切换
                console.log('[示例面板] 头部被点击');
                if (elements.examplePanel) {
                    isToggling = true;
                    
                const wasCollapsed = elements.examplePanel.classList.contains('collapsed');
                elements.examplePanel.classList.toggle('collapsed');
                const isNowCollapsed = elements.examplePanel.classList.contains('collapsed');
                console.log('[示例面板] 头部点击，状态变化:', wasCollapsed ? '收起' : '展开', '->', isNowCollapsed ? '收起' : '展开');
                console.log('[示例面板] 面板类名:', elements.examplePanel.className);
                updateExampleToggleIcon();
                    
                    // 500ms 后允许再次切换
                    toggleTimeout = setTimeout(() => {
                        isToggling = false;
                        toggleTimeout = null;
                    }, 500);
            } else {
                console.error('[示例面板] examplePanel 元素不存在');
                    isToggling = false;
    }
            };
            
            elements.exampleHeader.addEventListener('click', handleHeaderClick, true); // 使用捕获阶段，确保先处理
            elements.exampleHeader.dataset.listenerBound = 'true'; // 标记已绑定
            console.log('[示例面板] 事件监听器已绑定');
        }
            } else {
        console.warn('[示例面板] exampleHeader 元素不存在，无法绑定事件');
    }
    
    // 说明书按钮点击事件：显示/隐藏说明书面板
    if (elements.manualBtn) {
        elements.manualBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleManualPanel();
        });
    }
    
    // 关闭说明书按钮点击事件
    if (elements.closeManualBtn) {
        elements.closeManualBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            hideManualPanel();
        });
    }
    
    // 更新通知按钮点击事件：显示/隐藏更新通知面板
    if (elements.updateNotificationBtn) {
        elements.updateNotificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleUpdateNotificationPanel();
        });
    }
    
    // 关闭更新通知按钮点击事件
    if (elements.closeNotificationBtn) {
        elements.closeNotificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            hideUpdateNotificationPanel();
        });
    }
    
    // 意见反馈按钮点击事件
    if (elements.feedbackBtn) {
        elements.feedbackBtn.addEventListener('click', () => {
            showFeedbackModal();
        });
    }
    
    // 关闭意见反馈弹窗按钮
    if (elements.closeFeedbackModal) {
        elements.closeFeedbackModal.addEventListener('click', () => {
            hideFeedbackModal();
        });
    }
    
    // 意见反馈弹窗背景点击关闭
    if (elements.feedbackModal) {
        elements.feedbackModal.addEventListener('click', (e) => {
            if (e.target === elements.feedbackModal) {
                hideFeedbackModal();
            }
        });
    }
    
    // 意见反馈取消按钮
    if (elements.feedbackCancelBtn) {
        elements.feedbackCancelBtn.addEventListener('click', () => {
            hideFeedbackModal();
        });
    }
    
    // 意见反馈提交按钮
    if (elements.feedbackSubmitBtn) {
        elements.feedbackSubmitBtn.addEventListener('click', () => {
            submitFeedback();
        });
    }
    
    // 星级评分点击事件
    if (elements.starRating) {
        const stars = elements.starRating.querySelectorAll('.star');
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                setRating(index + 1);
            });
            star.addEventListener('mouseenter', () => {
                highlightStars(index + 1);
            });
        });
        elements.starRating.addEventListener('mouseleave', () => {
            const currentRating = elements.starRating.dataset.rating || 0;
            highlightStars(parseInt(currentRating));
        });
    }
    
    // 关闭意见反馈成功提示
    if (elements.feedbackSuccessClose) {
        elements.feedbackSuccessClose.addEventListener('click', () => {
            hideFeedbackSuccessPanel();
        });
    }
    
    // 移除自动关闭逻辑，让用户自行关闭
    // 点击页面其他地方时不再自动关闭更新通知面板
    // document.addEventListener('click', (e) => {
    //     if (elements.updateNotificationPanel && 
    //         !elements.updateNotificationPanel.contains(e.target) && 
    //         !elements.updateNotificationBtn.contains(e.target)) {
    //         hideUpdateNotificationPanel();
    //     }
    // });
    
    // 关闭侧边栏按钮点击事件：当用户点击关闭按钮时
    if (elements.closeSidebarBtn) {
        elements.closeSidebarBtn.addEventListener('click', closeSidebar);
    }
    
    // 侧边栏遮罩层点击事件：当用户点击遮罩层时
    if (elements.sidebarOverlay) {
        elements.sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // 标记已绑定
    eventListenersBound = true;
    window.eventListenersBound = true;
    console.log('[初始化] 所有事件监听器绑定完成');
}

// ============================================
// 面试模式介绍弹窗管理
// ============================================

// 面试模式介绍弹窗的自动关闭定时器
let interviewModeInfoPanelTimer = null;

/**
 * 显示面试模式介绍弹窗
 */
function showInterviewModeInfoPanel() {
    if (!elements.interviewModeInfoPanel) return;
    
    // 清除之前的定时器（如果存在）
    if (interviewModeInfoPanelTimer) {
        clearTimeout(interviewModeInfoPanelTimer);
        interviewModeInfoPanelTimer = null;
    }
    
    // 显示弹窗
    elements.interviewModeInfoPanel.classList.remove('hidden');
    elements.interviewModeInfoPanel.classList.remove('fading');
    
    // 5秒后自动关闭
    interviewModeInfoPanelTimer = setTimeout(() => {
        hideInterviewModeInfoPanel();
    }, 5000);
}

/**
 * 隐藏面试模式介绍弹窗
 */
function hideInterviewModeInfoPanel() {
    if (!elements.interviewModeInfoPanel) return;
    
    // 清除定时器
    if (interviewModeInfoPanelTimer) {
        clearTimeout(interviewModeInfoPanelTimer);
        interviewModeInfoPanelTimer = null;
    }
    
    // 添加淡出动画
    elements.interviewModeInfoPanel.classList.add('fading');
    
    // 等待淡出动画完成后隐藏
    setTimeout(() => {
        if (elements.interviewModeInfoPanel) {
            elements.interviewModeInfoPanel.classList.add('hidden');
        }
    }, 500); // 等待淡出动画完成
}

// 将函数暴露到全局作用域，以便在其他地方调用
window.showInterviewModeInfoPanel = showInterviewModeInfoPanel;
window.hideInterviewModeInfoPanel = hideInterviewModeInfoPanel;

// ============================================
// 笔记共享功能
// ============================================

/**
 * 显示笔记共享弹窗
 */
function showShareNoteModal() {
    if (!elements.shareNoteModal) return;
    elements.shareNoteModal.classList.remove('hidden');
}

/**
 * 隐藏笔记共享弹窗
 */
function hideShareNoteModal() {
    if (!elements.shareNoteModal) return;
    elements.shareNoteModal.classList.add('hidden');
}

// 将函数暴露到全局作用域
window.showShareNoteModal = showShareNoteModal;
window.hideShareNoteModal = hideShareNoteModal;

// ============================================
// 更新通知功能
// ============================================

/**
 * 解析更新日志，提取最近的三个重大更新
 * @returns {Array} 更新项数组，每个项包含日期、标题和内容
 */
function parseUpdateLog() {
    // 更新日志内容（从更新日志中提取的关键更新）
    const updates = [
        {
            date: '2025年12月26日',
            title: '🎨 界面全面重新设计',
            content: '全面重新设计了底部输入区域，采用浮动框设计；添加左侧功能侧边栏（更新通知、设置、开发者模式、知识库广场）；新增笔记共享功能；优化面试模式介绍弹窗逻辑；更新输入框占位符文本为"灵动笔记，记录灵感..."。'
        },
        {
            date: '2025年12月26日',
            title: '📤 笔记共享功能上线',
            content: '在底部输入框左上角添加笔记共享按钮，点击后在右下角显示分享弹窗，包含二维码和分享链接，支持一键复制链接功能。'
        },
        {
            date: '2025年12月22日',
            title: '📄 查看文档内容修复',
            content: '修复试用/开发模式查看文档只返回"默认文档"的问题：ALL_DOCUMENTS 接口补齐 PM问答笔记、试用文档、介绍文档、更新记录日志，缺失时自动回填真实内容。'
        }
    ];
    
    // 返回最近的三个更新（倒序）
    return updates.slice(-3).reverse();
}

/**
 * 显示更新通知面板
 */
function showUpdateNotificationPanel() {
    if (elements.updateNotificationPanel && elements.updateNotificationBtnLeft) {
        // 获取按钮的位置
        const btnRect = elements.updateNotificationBtnLeft.getBoundingClientRect();
        // 设置面板位置：在按钮右侧，底部对齐
        elements.updateNotificationPanel.style.left = `${btnRect.right + 12}px`;
        elements.updateNotificationPanel.style.bottom = `${window.innerHeight - btnRect.bottom}px`;
        
        elements.updateNotificationPanel.classList.remove('hidden');
        // 使用setTimeout确保DOM更新后再添加show类
        setTimeout(() => {
            elements.updateNotificationPanel.classList.add('show');
        }, 10);
    }
}

/**
 * 隐藏更新通知面板
 */
function hideUpdateNotificationPanel() {
    if (elements.updateNotificationPanel) {
        elements.updateNotificationPanel.classList.remove('show');
        setTimeout(() => {
            elements.updateNotificationPanel.classList.add('hidden');
        }, 300); // 等待动画完成
    }
}

/**
 * 切换更新通知面板显示状态
 */
function toggleUpdateNotificationPanel() {
    if (elements.updateNotificationPanel) {
        if (elements.updateNotificationPanel.classList.contains('hidden') || 
            !elements.updateNotificationPanel.classList.contains('show')) {
            showUpdateNotificationPanel();
        } else {
            hideUpdateNotificationPanel();
        }
    }
}

/**
 * 显示说明书面板
 */
function showManualPanel() {
    if (elements.manualPanel && elements.manualContent) {
        // 如果内容还未加载，先加载
        if (!elements.manualContent.dataset.loaded) {
            loadManualContent();
        }
        elements.manualPanel.classList.remove('hidden');
        setTimeout(() => {
            elements.manualPanel.classList.add('show');
        }, 10);
    }
}

/**
 * 隐藏说明书面板
 */
function hideManualPanel() {
    if (elements.manualPanel) {
        elements.manualPanel.classList.remove('show');
        setTimeout(() => {
            elements.manualPanel.classList.add('hidden');
        }, 300);
    }
}

/**
 * 切换说明书面板显示状态
 */
function toggleManualPanel() {
    if (elements.manualPanel) {
        if (elements.manualPanel.classList.contains('hidden') || 
            !elements.manualPanel.classList.contains('show')) {
            showManualPanel();
        } else {
            hideManualPanel();
        }
    }
}

/**
 * 加载说明书内容
 * 从后端API获取SYSTEM_PROMPT_COMPLETE.md内容并转换为HTML
 */
async function loadManualContent() {
    if (!elements.manualContent) return;
    
    // 显示加载中状态
    elements.manualContent.innerHTML = `
        <div style="padding: 20px; text-align: center; color: var(--text-secondary);">
            <p>📖 正在加载说明书...</p>
        </div>
    `;
    
    try {
        // 通过后端API获取说明书内容
        const response = await fetch(`${API_CONFIG.baseURL}/api/get-manual`);
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status}`);
        }
        
        const data = await response.json();
        const markdownText = data.content || '';
        
        // 简单的Markdown到HTML转换
        const htmlContent = convertMarkdownToHTML(markdownText);
        
        elements.manualContent.innerHTML = htmlContent;
        elements.manualContent.dataset.loaded = 'true';
    } catch (error) {
        console.error('[说明书] 加载失败:', error);
        elements.manualContent.innerHTML = `
            <div style="padding: 20px; text-align: center; color: var(--text-secondary);">
                <p>⚠️ 无法加载说明书内容</p>
                <p style="font-size: 12px; margin-top: 10px;">${error.message}</p>
                <p style="font-size: 12px; margin-top: 10px;">请检查后端服务是否正常运行</p>
            </div>
        `;
        elements.manualContent.dataset.loaded = 'true';
    }
}

/**
 * 简单的Markdown到HTML转换函数
 */
function convertMarkdownToHTML(markdown) {
    let html = markdown;
    
    // 转义HTML特殊字符（但保留代码块）
    const codeBlockRegex = /```[\s\S]*?```/g;
    const codeBlocks = [];
    html = html.replace(codeBlockRegex, (match) => {
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push(match);
        return placeholder;
    });
    
    // 转义HTML
    html = html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 恢复代码块
    codeBlocks.forEach((block, index) => {
        html = html.replace(`__CODE_BLOCK_${index}__`, block);
    });
    
    // 标题
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // 粗体
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 斜体
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 代码块
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // 行内代码
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 列表
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>');
    
    // 包装列表项
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // 段落（将连续的非列表、非标题行包装为段落）
    const lines = html.split('\n');
    let result = [];
    let currentParagraph = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) {
            if (currentParagraph.length > 0) {
                result.push('<p>' + currentParagraph.join(' ') + '</p>');
                currentParagraph = [];
            }
            continue;
        }
        
        if (line.startsWith('<h') || line.startsWith('<ul') || line.startsWith('<li') || 
            line.startsWith('<pre') || line.startsWith('</ul') || line.startsWith('</pre')) {
            if (currentParagraph.length > 0) {
                result.push('<p>' + currentParagraph.join(' ') + '</p>');
                currentParagraph = [];
            }
            result.push(line);
        } else {
            currentParagraph.push(line);
        }
    }
    
    if (currentParagraph.length > 0) {
        result.push('<p>' + currentParagraph.join(' ') + '</p>');
    }
    
    html = result.join('\n');
    
    // 链接
    html = html.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // 水平线
    html = html.replace(/^---$/gim, '<hr>');
    
    return html;
}

/**
 * 初始化更新通知
 * 解析更新日志并显示在通知面板中
 */
function initUpdateNotification() {
    if (!elements.updateList) return;
    
    const updates = parseUpdateLog();
    
    // 清空现有内容
    elements.updateList.innerHTML = '';
    
    // 如果没有更新，显示提示
    if (updates.length === 0) {
        elements.updateList.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">暂无更新记录</div>';
        return;
    }
    
    // 显示最近的三个重大更新
    updates.forEach((update, index) => {
        const updateItem = document.createElement('div');
        updateItem.className = 'update-item';
        updateItem.innerHTML = `
            <div class="update-date">📅 ${update.date}</div>
            <div class="update-title">${update.title}</div>
            <div class="update-content">${update.content}</div>
        `;
        elements.updateList.appendChild(updateItem);
    });
    
    // 显示通知徽章（如果有新更新）
    if (updates.length > 0 && elements.notificationBadge) {
        elements.notificationBadge.classList.add('show');
        // 同步到左侧侧边栏的徽章
        const badgeLeft = document.getElementById('notification-badge-left');
        if (badgeLeft) {
            badgeLeft.textContent = elements.notificationBadge.textContent;
            badgeLeft.style.display = elements.notificationBadge.style.display;
            badgeLeft.classList.add('show');
        }
    }
}

// ============================================
// 应用初始化
// ============================================

/**
 * 初始化应用
 * 在页面加载完成后，初始化应用的所有功能
 */
async function initApp() {
    // 在控制台输出初始化信息，方便调试
    console.log('正在初始化灵辑应用...');
    
    // 首先初始化DOM元素引用
    initElements();
    
    // 初始化会话ID（如果还没有的话）
    initSession();
    
    // 绑定所有事件监听器，让页面可以响应用户操作
    initEventListeners();
    
    // 初始化更新通知
    initUpdateNotification();
    
    // 初始化AI反馈面板（显示初始提示）
    if (elements.aiFeedbackList) {
        addAIFeedback('灵辑已就绪，等待您的指令...');
    }
    
    // 尝试加载文档列表
    try {
        // 从后端获取文档列表
        const documents = await fetchDocumentList();
        console.log('[初始化] 获取到的文档列表:', documents);
        
        // 更新界面上的文档列表显示
        updateDocumentList(documents);
        
        // 根据模式设置默认文档
        // 试用模式：默认显示"试用文档"
        // 开发者模式：默认显示"介绍文档"
        if (documents && documents.length > 0) {
            // 检查是否是试用模式（通过检查是否有"试用文档"）
            const trialDoc = documents.find(doc => doc === '试用文档');
            if (trialDoc) {
                // 试用模式：默认显示"试用文档"
                console.log('[初始化] 试用模式，设置默认文档为: 试用文档');
                AppState.currentDocument = '试用文档';
                updateActiveDocTitle('试用文档');
            } else {
                // 开发者模式：优先显示"介绍文档"
                const introDoc = documents.find(doc => doc === '介绍文档');
                if (introDoc) {
                    console.log('[初始化] 开发者模式，设置默认文档为: 介绍文档');
                    AppState.currentDocument = '介绍文档';
                    updateActiveDocTitle('介绍文档');
                } else {
                    // 如果没有介绍文档，使用第一个文档
                    console.log('[初始化] 使用第一个文档:', documents[0]);
                    AppState.currentDocument = documents[0];
                    updateActiveDocTitle(documents[0]);
                }
            }
        } else {
            console.warn('[初始化] 文档列表为空，使用默认文档');
            // 如果文档列表为空，根据模式设置默认文档
            const storedMode = localStorage.getItem('is_trial_mode');
            const isTrialMode = storedMode !== 'false';
            
            if (isTrialMode) {
                AppState.currentDocument = '试用文档';
                updateActiveDocTitle('试用文档');
            } else {
                AppState.currentDocument = '介绍文档';
                updateActiveDocTitle('介绍文档');
            }
        }
    } catch (error) {
        // 如果加载失败，在控制台输出警告，但不阻止应用运行
        console.error('[初始化] 无法加载文档列表:', error);
        // 设置默认文档
        const storedMode = localStorage.getItem('is_trial_mode');
        const isTrialMode = storedMode !== 'false';
        
        if (isTrialMode) {
            AppState.currentDocument = '试用文档';
            updateActiveDocTitle('试用文档');
        } else {
            AppState.currentDocument = '介绍文档';
            updateActiveDocTitle('介绍文档');
        }
    }
    
    // 检查并显示试用状态气泡
    updateTrialStatusBubble();
    
    // 初始化AI反馈面板
    initAIFeedbackPanel();
    
    // 初始化标准对话示例面板
    initExamplePanel();
    
    // 初始化连接状态指示器
    updateConnectionStatus('connected');
    
    // 添加页面关闭事件监听器，清空试用数据
    initPageUnloadHandler();
    
    // 在控制台输出初始化完成信息
    console.log('应用初始化完成！');
}

/**
 * 初始化页面关闭事件处理器
 * 在关闭网页时清空试用模式的数据
 */
function initPageUnloadHandler() {
    // 检查是否为试用模式
    const storedMode = localStorage.getItem('is_trial_mode');
    const isTrialMode = storedMode !== 'false';
    
    if (!isTrialMode) {
        // 如果不是试用模式，不需要清空数据
        return;
    }
    
    // 使用 beforeunload 事件（在页面卸载前触发）
    window.addEventListener('beforeunload', async (event) => {
        // 获取会话ID
        const sessionId = AppState.sessionId || localStorage.getItem('trial_session_id');
        
        if (!sessionId) {
            return;
        }
        
        // 使用 sendBeacon API 发送请求（即使页面关闭也能发送）
        try {
            const url = `${API_CONFIG.baseURL}/api/clear-trial-data`;
            const data = JSON.stringify({ session_id: sessionId });
            
            // sendBeacon 是异步的，但浏览器会保证请求发送完成
            navigator.sendBeacon(url, data);
        } catch (error) {
            console.error('清空试用数据失败:', error);
        }
    });
    
    // 也使用 visibilitychange 事件作为备用（当页面隐藏时）
    document.addEventListener('visibilitychange', async () => {
        if (document.visibilityState === 'hidden') {
            const sessionId = AppState.sessionId || localStorage.getItem('trial_session_id');
            
            if (!sessionId) {
                return;
            }
            
            try {
                const url = `${API_CONFIG.baseURL}/api/clear-trial-data`;
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ session_id: sessionId }),
                    keepalive: true  // 确保请求在页面关闭后也能完成
                });
                
                if (response.ok) {
                    console.log('试用数据已清空');
                }
            } catch (error) {
                console.error('清空试用数据失败:', error);
            }
        }
    });
}

// ============================================
// 连接状态指示器管理
// ============================================

/**
 * 更新连接状态指示器
 * @param {string} status - 连接状态：'connected'（已连接）、'loading'（加载中）、'disconnected'（断开连接）
 */
function updateConnectionStatus(status) {
    if (!elements.connectionStatusIndicator) {
        return;
    }
    
    // 移除所有状态类
    elements.connectionStatusIndicator.classList.remove('loading', 'connected', 'disconnected');
    
    // 根据状态添加相应的类并更新文字
    switch (status) {
        case 'loading':
            elements.connectionStatusIndicator.classList.add('loading');
            if (elements.connectionStatusText) {
                elements.connectionStatusText.textContent = '处理中...';
            }
            break;
        case 'connected':
            elements.connectionStatusIndicator.classList.add('connected');
            if (elements.connectionStatusText) {
                elements.connectionStatusText.textContent = '已连接';
            }
            break;
        case 'disconnected':
            elements.connectionStatusIndicator.classList.add('disconnected');
            if (elements.connectionStatusText) {
                elements.connectionStatusText.textContent = '未连接';
            }
            break;
        default:
            elements.connectionStatusIndicator.classList.add('connected');
            if (elements.connectionStatusText) {
                elements.connectionStatusText.textContent = '已连接';
            }
    }
}

// ============================================
// AI反馈面板管理
// ============================================

/**
 * 初始化AI反馈面板
 */
function initAIFeedbackPanel() {
    try {
        // 默认展开状态（不添加collapsed类）
        if (elements.aiFeedbackPanel) {
            // 确保面板是展开状态（移除collapsed类）
            elements.aiFeedbackPanel.classList.remove('collapsed');
            // 更新箭头图标方向
            updateAIFeedbackToggleIcon();
        }
        // 清空反馈列表
        if (elements.aiFeedbackList) {
            elements.aiFeedbackList.innerHTML = '';
        }
        // 更新时间显示
        updateAIFeedbackTime();
    } catch (error) {
        console.error('[AI反馈] 初始化面板时出错:', error);
        // 不抛出错误，避免中断脚本执行
    }
}

/**
 * 更新AI反馈面板切换按钮的图标方向
 */
function updateAIFeedbackToggleIcon() {
    try {
        if (elements.aiFeedbackPanel && elements.aiFeedbackToggle) {
            const toggleIcon = elements.aiFeedbackToggle.querySelector('.toggle-icon');
            if (toggleIcon) {
                // 确保图标存在
                if (!toggleIcon.textContent) {
                    toggleIcon.textContent = '▼';
                }
                // CSS已经通过 .collapsed 类控制旋转
                // 展开状态：三角形朝下 ▼ (rotate(0deg))
                // 收起状态：三角形朝右 ▶ (rotate(-90deg))
                const isCollapsed = elements.aiFeedbackPanel.classList.contains('collapsed');
                console.log('[AI反馈] 更新图标方向，面板状态:', isCollapsed ? '收起（朝右）' : '展开（朝下）');
                
                // 强制触发重绘，确保CSS transform生效
                toggleIcon.style.display = 'none';
                toggleIcon.offsetHeight; // 触发重排
                toggleIcon.style.display = 'inline-block';
            } else {
                console.warn('[AI反馈] toggle-icon 元素不存在！');
            }
        } else {
            console.warn('[AI反馈] 面板或切换按钮元素不存在！');
        }
    } catch (error) {
        console.error('[AI反馈] 更新图标时出错:', error);
        // 不抛出错误，避免中断脚本执行
    }
}

/**
 * 更新AI反馈时间显示
 */
function updateAIFeedbackTime() {
    if (elements.aiFeedbackTime) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        elements.aiFeedbackTime.textContent = timeStr;
    }
}

/**
 * 更新示例面板切换图标方向
 */
function updateExampleToggleIcon() {
    if (elements.examplePanel && elements.exampleToggle) {
        const toggleIcon = elements.exampleToggle.querySelector('.toggle-icon');
        if (toggleIcon) {
            const isCollapsed = elements.examplePanel.classList.contains('collapsed');
            // 收起状态：三角形朝右 ▶
            // 展开状态：三角形朝下 ▼
            toggleIcon.textContent = isCollapsed ? '▶' : '▼';
            console.log('[示例面板] 更新图标，状态:', isCollapsed ? '收起' : '展开', '类名:', elements.examplePanel.className);
        } else {
            console.warn('[示例面板] toggle-icon 元素不存在');
        }
    } else {
        console.warn('[示例面板] 面板或切换按钮元素不存在');
    }
}

/**
 * 初始化标准对话示例面板
 */
function initExamplePanel() {
    if (!elements.exampleList) return;
    
    // 示例内容（按难度排列，简单的在前面）
    const examples = [
        // 简单：基础问候和询问
        "你好",
        "你能做什么",
        "删除笔记",
        // 较难：复杂内容添加
        "这道数学题：求解方程 x² + 5x + 6 = 0，使用因式分解法",
    ];
    
    // 清空现有内容
    elements.exampleList.innerHTML = '';
    
    // 创建示例项
    examples.forEach((text, index) => {
        const exampleItem = document.createElement('div');
        exampleItem.className = 'example-item';
        exampleItem.innerHTML = `
            <span class="example-item-number">${index + 1}</span>
            <span class="example-item-text">${text}</span>
            <button class="example-item-copy" data-text="${text.replace(/"/g, '&quot;')}" aria-label="复制">
                📋
            </button>
        `;
        
        // 添加复制功能
        const copyBtn = exampleItem.querySelector('.example-item-copy');
        if (copyBtn) {
            copyBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const textToCopy = copyBtn.getAttribute('data-text');
                try {
                    await navigator.clipboard.writeText(textToCopy);
                    // 临时改变按钮文本显示复制成功
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '✓';
                    copyBtn.style.color = '#10b981';
                    setTimeout(() => {
                        copyBtn.textContent = originalText;
                        copyBtn.style.color = '#6366f1';
                    }, 1000);
                } catch (err) {
                    console.error('复制失败:', err);
                    // 降级方案：使用传统方法
                    const textArea = document.createElement('textarea');
                    textArea.value = textToCopy;
                    textArea.style.position = 'fixed';
                    textArea.style.opacity = '0';
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        const originalText = copyBtn.textContent;
                        copyBtn.textContent = '✓';
                        copyBtn.style.color = '#10b981';
                        setTimeout(() => {
                            copyBtn.textContent = originalText;
                            copyBtn.style.color = '#6366f1';
                        }, 1000);
                    } catch (err2) {
                        console.error('降级复制也失败:', err2);
                    }
                    document.body.removeChild(textArea);
                }
            });
        }
        
        elements.exampleList.appendChild(exampleItem);
    });
    
    // 默认收缩状态（无论是试用模式还是开发者模式）
    if (elements.examplePanel) {
    // 检查是否在试用模式（通过检查localStorage或试用模式标识）
    const storedMode = localStorage.getItem('is_trial_mode');
    const isTrialMode = storedMode !== 'false' ||
                       (document.getElementById('trial-mode-indicator') && 
                        !document.getElementById('trial-mode-indicator').classList.contains('hidden'));
        console.log('[示例面板] 初始化，试用模式:', isTrialMode, '当前类名:', elements.examplePanel.className);
        // 默认状态为收缩（无论是试用模式还是开发者模式）
            elements.examplePanel.classList.add('collapsed');
        console.log('[示例面板] 默认设置为收缩状态，类名:', elements.examplePanel.className);
        updateExampleToggleIcon();
    } else {
        console.error('[示例面板] examplePanel 元素不存在，无法初始化');
    }
}

/**
 * 添加AI反馈信息
 * @param {string} message - 反馈消息内容
 */
function addAIFeedback(message) {
    try {
        if (!elements.aiFeedbackList) {
            console.warn('[AI反馈] aiFeedbackList 元素不存在');
            return;
        }
        
        if (!message) {
            console.warn('[AI反馈] 反馈消息为空');
            return;
        }
        
        console.log('[AI反馈] 添加反馈:', message);
        
        // 创建反馈项
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'ai-feedback-item';
        feedbackItem.textContent = String(message);
        
        // 添加到列表底部（最新的在下方）
        elements.aiFeedbackList.appendChild(feedbackItem);
        
        // 自动滚动到底部，确保最新消息可见
        const feedbackContent = elements.aiFeedbackList.parentElement;
        if (feedbackContent) {
            feedbackContent.scrollTop = feedbackContent.scrollHeight;
        }
        
        // 更新时间
        updateAIFeedbackTime();
        
        // 限制反馈项数量（最多显示5条，删除最旧的）
        // 增加数量以确保详细的意图识别和工具调用信息能够显示
        const items = elements.aiFeedbackList.querySelectorAll('.ai-feedback-item');
        if (items.length > 5) {
            items[0].remove(); // 删除最旧的第一条
        }
        
        // 确保面板是展开的（默认状态）
        if (elements.aiFeedbackPanel && elements.aiFeedbackPanel.classList.contains('collapsed')) {
            // 如果面板是收起的，不自动展开（保持用户的选择）
        }
    } catch (error) {
        console.error('[AI反馈] 添加反馈时出错:', error);
        // 不抛出错误，避免中断脚本执行
    }
}

// 将后端响应转换为详细的"智能体判断"反馈
function addAIFeedbackFromResponse(response) {
    try {
        if (!response) {
            console.warn('[AI反馈] 响应对象为空，跳过反馈');
            return;
        }
        
        const { response_type, content, intent_info, tools_used } = response;
        const doc = AppState.currentDocument || '试用文档';
        
        console.log('[AI反馈] 响应数据:', { response_type, intent_info, tools_used });
        console.log('[AI反馈] intent_info详情:', JSON.stringify(intent_info, null, 2));
        console.log('[AI反馈] intent_info.intent:', intent_info?.intent);
        console.log('[AI反馈] intent_info.original_intent:', intent_info?.original_intent);
        
        // 构建反馈消息
        // 优先使用 intent_info.intent，否则使用 response_type
        // 注意：intent_info.intent 是后端处理后的意图（如 GREETING），而 intent_info.original_intent 是LLM返回的原始意图
        const typeLabel = (intent_info && (intent_info.intent || intent_info.original_intent)) || response_type || 'UNKNOWN';
        let msg = `[判定] ${typeLabel}`;
        
        // 添加意图识别信息
        if (intent_info) {
            // 文档标题
            if (intent_info.doc_title) {
                msg += ` | 文档: ${intent_info.doc_title}`;
            } else {
                // 如果没有文档标题，使用当前文档作为fallback
                msg += ` | 文档: ${doc}`;
            }
            
            // 位置信息
            if (intent_info.position) {
                const pos = intent_info.position === 'start' ? '开头' : 
                           intent_info.position === 'end' ? '结尾' : 
                           intent_info.position;
                msg += ` | 位置: ${pos}`;
            }
            
            // 内容长度
            if (intent_info.content_length !== undefined && intent_info.content_length > 0) {
                msg += ` | 内容长度: ${intent_info.content_length}字符`;
            }
        } else {
            // 如果没有意图信息，使用文档信息作为fallback
            msg += ` | 文档: ${doc}`;
        }
        
        // 添加工具调用信息
        if (tools_used && tools_used.length > 0) {
            const toolsStr = tools_used.join(', ');
            msg += ` | 工具: ${toolsStr}`;
        }
        
        // 添加内容预览（如果有）
        if (content) {
            const preview = String(content).replace(/\s+/g, ' ').slice(0, 30);
            if (preview) {
                msg += ` | 预览: ${preview}...`;
            }
        }
        
        console.log('[AI反馈] 生成的详细反馈消息:', msg);
        addAIFeedback(msg);
    } catch (error) {
        console.error('[AI反馈] 添加反馈时出错:', error);
        // 不抛出错误，避免中断脚本执行
    }
}

/**
 * 清空AI反馈信息
 */
function clearAIFeedback() {
    if (elements.aiFeedbackList) {
        elements.aiFeedbackList.innerHTML = '';
    }
    updateAIFeedbackTime();
}

// ============================================
// 试用状态气泡管理
// ============================================

/**
 * 更新试用状态面板的显示（3秒后自动消失）
 */
function updateTrialStatusBubble() {
    const trialPanel = document.getElementById('trial-status-panel');
    const trialIndicator = document.getElementById('trial-mode-indicator');
    const trialCloseBtn = document.getElementById('trial-status-close');
    
    // 检查是否为试用模式
    const storedMode = localStorage.getItem('is_trial_mode');
    const isTrialMode = storedMode !== 'false';
    
    if (isTrialMode) {
        // 显示左侧试用状态面板（3秒后自动消失）
        if (trialPanel) {
            trialPanel.classList.remove('hidden');
            trialPanel.classList.remove('fading');
            
            // 绑定关闭按钮事件（如果还没有绑定）
            if (trialCloseBtn && !trialCloseBtn.hasAttribute('data-listener-attached')) {
                trialCloseBtn.setAttribute('data-listener-attached', 'true');
                trialCloseBtn.addEventListener('click', () => {
                    if (trialPanel) {
                        trialPanel.classList.add('fading');
                        setTimeout(() => {
                            if (trialPanel) {
                                trialPanel.classList.add('hidden');
                            }
                        }, 500); // 等待淡出动画完成
                    }
                });
            }
            
            // 3秒后自动消失
            setTimeout(() => {
                if (trialPanel && !trialPanel.classList.contains('hidden')) {
                    trialPanel.classList.add('fading');
                    setTimeout(() => {
                        if (trialPanel) {
                            trialPanel.classList.add('hidden');
                        }
                    }, 500); // 等待淡出动画完成
                }
            }, 3000); // 3秒后开始淡出
        }
        // 显示右侧试用模式标识（固定显示）
        if (trialIndicator) {
            trialIndicator.classList.remove('hidden');
        }
    } else {
        // 隐藏试用状态面板
        if (trialPanel) {
            trialPanel.classList.add('hidden');
            trialPanel.classList.remove('fading');
        }
        // 隐藏右侧试用模式标识
        if (trialIndicator) {
            trialIndicator.classList.add('hidden');
        }
    }
}

// ============================================
// 启动应用
// ============================================

// 当DOM加载完成后初始化应用
// 检查文档的加载状态
console.log('[app.js] 脚本开始执行，readyState:', document.readyState);

// 确保在 DOM 完全加载后再初始化
function startApp() {
    console.log('[app.js] 准备初始化应用...');
    try {
        initApp();
    } catch (error) {
        console.error('[app.js] 初始化应用时出错:', error);
        console.error('错误堆栈:', error.stack);
    }
}

// ============================================
// 意见反馈功能
// ============================================

let currentRating = 0;

/**
 * 显示意见反馈弹窗
 */
function showFeedbackModal() {
    if (elements.feedbackModal) {
        elements.feedbackModal.classList.remove('hidden');
        // 重置表单
        currentRating = 0;
    }
}

/**
 * 隐藏意见反馈弹窗
 */
function hideFeedbackModal() {
    if (elements.feedbackModal) {
        elements.feedbackModal.classList.add('hidden');
        // 重置表单
        resetFeedbackForm();
    }
}

/**
 * 设置评分
 */
function setRating(rating) {
    currentRating = rating;
    if (elements.starRating) {
        elements.starRating.dataset.rating = rating;
        highlightStars(rating);
        updateRatingText(rating);
    }
}

/**
 * 高亮星星
 */
function highlightStars(rating) {
    if (elements.starRating) {
        const stars = elements.starRating.querySelectorAll('.star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
}

/**
 * 更新评分文本
 */
function updateRatingText(rating) {
    if (elements.ratingText) {
        const texts = {
            1: '非常不满意',
            2: '不满意',
            3: '一般',
            4: '满意',
            5: '非常满意'
        };
        elements.ratingText.textContent = texts[rating] || '请选择评分';
    }
}

/**
 * 重置反馈表单
 */
function resetFeedbackForm() {
    currentRating = 0;
    if (elements.starRating) {
        elements.starRating.dataset.rating = 0;
        highlightStars(0);
        updateRatingText(0);
    }
    if (elements.feedbackTextarea) {
        elements.feedbackTextarea.value = '';
    }
}

/**
 * 提交意见反馈
 */
function submitFeedback() {
    const rating = currentRating;
    const text = elements.feedbackTextarea ? elements.feedbackTextarea.value.trim() : '';
    
    // 直接关闭反馈弹窗，不进行验证
    hideFeedbackModal();
    
    // 显示成功提示
    showFeedbackSuccessPanel();
    
    // 这里不需要实际存储功能，只是显示提示
    console.log('[意见反馈] 评分:', rating, '意见:', text);
}

/**
 * 显示意见反馈成功提示
 */
function showFeedbackSuccessPanel() {
    if (elements.feedbackSuccessPanel) {
        elements.feedbackSuccessPanel.classList.remove('hidden');
        elements.feedbackSuccessPanel.classList.remove('fading');
        
        // 3秒后自动消失
        setTimeout(() => {
            hideFeedbackSuccessPanel();
        }, 3000);
    }
}

/**
 * 隐藏意见反馈成功提示
 */
function hideFeedbackSuccessPanel() {
    if (elements.feedbackSuccessPanel) {
        elements.feedbackSuccessPanel.classList.add('fading');
        setTimeout(() => {
            elements.feedbackSuccessPanel.classList.add('hidden');
            elements.feedbackSuccessPanel.classList.remove('fading');
        }, 500);
    }
}

/**
 * 更新 Session ID 显示
 * @param {string} sessionId - 会话 ID
 */
function updateSessionIdDisplay(sessionId) {
    const sessionIdValueElement = document.getElementById('session-id-value');
    if (sessionIdValueElement && sessionId) {
        // 只显示 session_id 的前 8 位
        const shortSessionId = sessionId.substring(0, 12);
        sessionIdValueElement.textContent = shortSessionId;
        console.log(`[Session] 更新界面显示: ${shortSessionId}`);
    }
}

if (document.readyState === 'loading') {
    // 如果文档还在加载中，等待DOMContentLoaded事件
    // DOMContentLoaded事件在HTML文档完全加载和解析后触发
    console.log('[app.js] 等待 DOMContentLoaded 事件...');
    document.addEventListener('DOMContentLoaded', startApp);
} else {
    // 如果文档已经加载完成，延迟一点时间确保所有脚本都已加载
    console.log('[app.js] DOM 已加载，延迟初始化...');
    setTimeout(startApp, 100);
}
