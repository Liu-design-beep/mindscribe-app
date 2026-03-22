/**
 * 登录/试用选择逻辑
 */

// ================================
// 试用密码验证状态（纯内存变量，刷新页面自动重置）
// ================================
window.trialVerified = false; // 本次会话是否已通过密码验证

// 检查是否已经选择过
function checkUserChoice() {
    // 临时禁用检查，强制显示弹窗（用于调试）
    // const choice = localStorage.getItem('user_choice');
    // const sessionId = localStorage.getItem('trial_session_id');
    
    // 调试：输出检查结果
    // console.log('检查用户选择:', { choice, sessionId });
    
    // 临时注释掉，强制显示弹窗
    // if (choice === 'trial' && sessionId) {
    //     // 已经选择试用，直接进入应用
    //     hideModal();
    //     showTrialWarning();
    //     return true;
    // } else if (choice === 'login') {
    //     // 已经选择登录，隐藏模态框
    //     hideModal();
    //     return true;
    // }
    // 如果没有选择，返回 false，显示弹窗
    return false;
}

// 显示模态框
function showModal() {
    const modal = document.getElementById('login-trial-modal');
    if (modal) {
        modal.classList.remove('hidden');
        // 使用 cssText 确保优先级最高，包含居中属性
        modal.style.cssText = 'position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important; visibility: visible !important; opacity: 1 !important; z-index: 10000 !important;';
    }
}

// 隐藏模态框
function hideModal() {
    const modal = document.getElementById('login-trial-modal');
    if (modal) {
        // 强制隐藏：使用 !important 覆盖所有内联样式
        modal.style.cssText = 'display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;';
        modal.classList.add('hidden');
        console.log('[隐藏模态框] 模态框已强制隐藏');
    }
}

// 进入试用模式（点击试用按钮时调用）
function enterTrialMode() {
    // 隐藏登录/试用选择弹窗
    hideModal();
    
    // 直接进入应用界面，密码验证推迟到第一次输入时
    // 重置验证状态（确保每次进入都需要重新验证）
    window.trialVerified = false;
    
    // 显示应用界面（如果应用被隐藏）
    const appContainer = document.querySelector('.app-container') || document.body;
    if (appContainer.style) {
        appContainer.style.display = '';
    }
    
    // 延迟一点时间，确保模态框完全隐藏后再初始化
    setTimeout(() => {
        console.log('[试用模式] 开始初始化试用模式...');
        
        // 验证模态框是否真的隐藏了
        const modal = document.getElementById('login-trial-modal');
        if (modal) {
            const computedStyle = window.getComputedStyle(modal);
            console.log('[试用模式] 模态框状态:', {
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                opacity: computedStyle.opacity,
                pointerEvents: computedStyle.pointerEvents,
                hasHiddenClass: modal.classList.contains('hidden')
            });
            
            // 如果模态框仍然可见，强制隐藏
            if (computedStyle.display !== 'none' || computedStyle.visibility !== 'hidden') {
                console.warn('[试用模式] 模态框仍然可见，强制隐藏');
                modal.style.cssText = 'display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;';
            }
        }
        
        // 重新初始化DOM元素引用（确保元素引用是最新的）
        if (typeof initElements === 'function') {
            initElements();
            console.log('[试用模式] DOM元素引用已重新初始化');
        } else {
            console.warn('[试用模式] initElements 函数不存在');
        }
        
        // 重新初始化会话（确保试用模式的sessionId正确）
        if (typeof initSession === 'function') {
            initSession();
            console.log('[试用模式] 会话已重新初始化');
        } else {
            console.warn('[试用模式] initSession 函数不存在');
        }
        
        // 强制重新绑定事件监听器（即使已经绑定过）
        // 因为可能在模态框显示时，某些元素还没有准备好
        if (typeof initEventListeners === 'function') {
            // 临时重置标记，允许重新绑定
            if (window.eventListenersBound !== undefined) {
                window.eventListenersBound = false;
                console.log('[试用模式] 重置事件监听器标记，准备重新绑定');
            }
            initEventListeners();
            console.log('[试用模式] 事件监听器已重新绑定');
        } else {
            console.error('[试用模式] initEventListeners 函数不存在！');
        }
        
        // 验证按钮元素是否存在
        const sendBtn = document.getElementById('send-btn');
        const switchDocBtn = document.getElementById('switch-doc-btn');
        const viewDocBtn = document.getElementById('view-doc-btn');
        console.log('[试用模式] 按钮元素检查:', {
            sendBtn: sendBtn ? '存在' : '不存在',
            switchDocBtn: switchDocBtn ? '存在' : '不存在',
            viewDocBtn: viewDocBtn ? '存在' : '不存在'
        });
        
        // 测试按钮是否可点击
        if (sendBtn) {
            const btnStyle = window.getComputedStyle(sendBtn);
            console.log('[试用模式] 发送按钮状态:', {
                display: btnStyle.display,
                visibility: btnStyle.visibility,
                pointerEvents: btnStyle.pointerEvents,
                disabled: sendBtn.disabled,
                zIndex: btnStyle.zIndex
            });
        }
        
        // 更新试用状态气泡
        if (typeof updateTrialStatusBubble === 'function') {
            updateTrialStatusBubble();
        }
        
        // 刷新文档列表
        if (typeof fetchDocumentList === 'function' && typeof updateDocumentList === 'function') {
            fetchDocumentList().then(documents => {
                updateDocumentList(documents);
            }).catch(err => {
                console.error('刷新文档列表失败:', err);
            });
        }
        
        console.log('[试用模式] 试用模式初始化完成');
    }, 200); // 增加延迟时间，确保模态框完全隐藏
}

// 处理登录选项
function handleLogin() {
    // 保存选择
    localStorage.setItem('user_choice', 'login');
    
    // 设置非试用模式标志
    localStorage.setItem('is_trial_mode', 'false');
    // 清理试用相关数据，避免误判为试用模式
    localStorage.removeItem('trial_session_id');
    localStorage.removeItem('trial_documents');
    
    // 隐藏模态框
    hideModal();
    
    // 为确保入口状态刷新，重新加载页面（避免残留试用态）
    window.location.reload();
}

// 显示试用模式警告
function showTrialWarning() {
    // 创建警告提示
    const warning = document.createElement('div');
    warning.id = 'trial-warning-banner';
    warning.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 15px 20px;
        text-align: center;
        z-index: 9999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-weight: 500;
        font-size: 14px;
    `;
    warning.innerHTML = `
        ⚠️ 试用模式：退出网页会把记录全部删除，需要进行登录才具备云端存储功能
        <button id="close-warning" style="
            margin-left: 15px;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        ">知道了</button>
    `;
    
    document.body.appendChild(warning);
    
    // 关闭按钮
    const closeBtn = document.getElementById('close-warning');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            warning.style.display = 'none';
        });
    }
    
    // 5秒后自动隐藏（可选）
    setTimeout(() => {
        if (warning.parentNode) {
            warning.style.opacity = '0';
            warning.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                if (warning.parentNode) {
                    warning.style.display = 'none';
                }
            }, 500);
        }
    }, 10000);
}

// 页面卸载时清理试用数据
window.addEventListener('beforeunload', () => {
    const choice = localStorage.getItem('user_choice');
    if (choice === 'trial') {
        // 清除试用数据，确保下次刷新时重新显示弹窗
        localStorage.removeItem('user_choice');
        localStorage.removeItem('trial_session_id');
        localStorage.removeItem('trial_documents');
        localStorage.removeItem('is_trial_mode');
        // 注意：这里只是清除本地存储，实际的 D1 数据库清理需要在后端处理
    }
});

// 初始化
function initLoginModal() {
    console.log('初始化登录弹窗...');
    
    // 确保模态框可见
    const modal = document.getElementById('login-trial-modal');
    if (!modal) {
        console.error('找不到登录弹窗元素！');
        return;
    }
    
    console.log('找到弹窗元素:', modal);
    
    // 检查是否已经选择过
    if (checkUserChoice()) {
        console.log('用户已选择，不显示弹窗');
        hideModal();
        return;
    }
    
    console.log('显示登录弹窗');
    
    // 强制显示：移除隐藏类，设置样式（使用 !important 确保优先级）
    modal.classList.remove('hidden');
    modal.removeAttribute('style');
    modal.style.cssText = 'position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important; visibility: visible !important; opacity: 1 !important; z-index: 10000 !important;';
    
    // 显示模态框
    showModal();
    
    // 绑定事件
    const loginOption = document.getElementById('login-option');
    const trialOption = document.getElementById('trial-option');
    
    if (loginOption) {
        loginOption.addEventListener('click', handleLogin);
        console.log('已绑定登录按钮');
    } else {
        console.warn('找不到登录选项元素');
    }
    
    if (trialOption) {
        trialOption.addEventListener('click', enterTrialMode);
        console.log('已绑定试用按钮');
    } else {
        console.warn('找不到试用选项元素');
    }
    
    // 再次确认显示 - 多次尝试确保显示
    setTimeout(() => {
        if (modal) {
            modal.classList.remove('hidden');
            modal.style.cssText = 'display: flex !important; visibility: visible !important; opacity: 1 !important; z-index: 10000 !important;';
            const computedStyle = window.getComputedStyle(modal);
            console.log('再次确认弹窗显示状态:', {
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                opacity: computedStyle.opacity,
                zIndex: computedStyle.zIndex,
                classList: Array.from(modal.classList),
                hasHiddenClass: modal.classList.contains('hidden')
            });
            
            // 如果还是隐藏，强制移除 hidden 类
            if (computedStyle.display === 'none' || modal.classList.contains('hidden')) {
                console.warn('弹窗仍然隐藏，强制显示...');
                modal.classList.remove('hidden');
                modal.removeAttribute('class');
                modal.className = 'login-trial-modal';
                modal.style.cssText = 'position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important; visibility: visible !important; opacity: 1 !important; z-index: 10000 !important;';
            }
        }
    }, 200);
    
    // 第三次确认（延迟更久）
    setTimeout(() => {
        if (modal) {
            const computedStyle = window.getComputedStyle(modal);
            const rect = modal.getBoundingClientRect();
            const modalContent = modal.querySelector('.modal-content');
            const contentRect = modalContent ? modalContent.getBoundingClientRect() : null;
            
            if (computedStyle.display === 'none' || modal.classList.contains('hidden')) {
                console.error('弹窗仍然无法显示！最终状态:', {
                    display: computedStyle.display,
                    visibility: computedStyle.visibility,
                    classList: Array.from(modal.classList),
                    inlineStyle: modal.style.cssText
                });
            } else {
                console.log('✅ 弹窗已成功显示！');
                console.log('弹窗详细信息:', {
                    '弹窗位置': `top: ${rect.top}, left: ${rect.left}`,
                    '弹窗大小': `width: ${rect.width}, height: ${rect.height}`,
                    '弹窗可见性': `display: ${computedStyle.display}, visibility: ${computedStyle.visibility}, opacity: ${computedStyle.opacity}`,
                    '弹窗层级': `z-index: ${computedStyle.zIndex}`,
                    '内容区域': contentRect ? `width: ${contentRect.width}, height: ${contentRect.height}` : '未找到内容区域'
                });
                
                // 如果弹窗大小异常，给出提示
                if (rect.width === 0 || rect.height === 0) {
                    console.warn('⚠️ 警告：弹窗大小为0，可能被隐藏或未正确渲染！');
                }
                if (!modalContent) {
                    console.error('❌ 错误：找不到弹窗内容区域！');
                } else {
                    console.log('✅ 弹窗内容区域正常');
                }
            }
        }
    }, 500);
}

// 页面加载完成后初始化
// 立即执行一次，确保弹窗默认显示
(function() {
    // 等待DOM元素创建
    function ensureModalVisible() {
        const modal = document.getElementById('login-trial-modal');
        if (modal) {
            console.log('立即初始化：找到弹窗元素，移除 hidden 类');
            // 立即移除 hidden 类并设置显示样式，包含居中属性
            modal.classList.remove('hidden');
            modal.style.cssText = 'position: fixed !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important; visibility: visible !important; opacity: 1 !important; z-index: 10000 !important;';
        } else {
            // 如果元素还没创建，稍后再试
            setTimeout(ensureModalVisible, 10);
        }
    }
    ensureModalVisible();
})();

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM 加载完成，初始化登录弹窗');
        setTimeout(initLoginModal, 50);
    });
} else {
    // 如果 DOM 已经加载完成，延迟一点初始化确保元素已存在
    console.log('DOM 已加载，延迟初始化登录弹窗');
    setTimeout(initLoginModal, 100);
}

// 导出函数供其他脚本使用
window.enterTrialMode = enterTrialMode;
window.handleLogin = handleLogin;

// ================================
// 试用密码验证功能
// ================================

const TRIAL_PASSWORD = '123'; // 试用密码

// 显示密码验证弹窗
function showPasswordModal() {
    const passwordModal = document.getElementById('trial-password-modal');
    const passwordInput = document.getElementById('trial-password-input');
    const errorMsg = document.getElementById('trial-password-error');
    
    if (passwordModal) {
        passwordModal.classList.remove('hidden');
        console.log('[密码验证] 显示密码验证弹窗');
        
        // 清空输入框和错误提示
        if (passwordInput) {
            passwordInput.value = '';
            passwordInput.focus();
        }
        if (errorMsg) {
            errorMsg.classList.add('hidden');
        }
    }
}

// 隐藏密码验证弹窗
function hidePasswordModal() {
    const passwordModal = document.getElementById('trial-password-modal');
    if (passwordModal) {
        passwordModal.classList.add('hidden');
        console.log('[密码验证] 隐藏密码验证弹窗');
    }
}

// 验证密码
function verifyPassword() {
    const passwordInput = document.getElementById('trial-password-input');
    const errorMsg = document.getElementById('trial-password-error');
    
    if (!passwordInput) return;
    
    const inputPassword = passwordInput.value.trim();
    
    if (inputPassword === TRIAL_PASSWORD) {
        console.log('[密码验证] ✅ 密码正确');
        
        // 标记本次会话已通过验证（纯内存，刷新即重置）
        window.trialVerified = true;
        
        // 隐藏密码弹窗
        hidePasswordModal();
        
        // 检查是否有待发送的消息（用户在验证前就按了发送）
        setTimeout(() => {
            if (window._pendingSendAfterVerify) {
                window._pendingSendAfterVerify = false;
                console.log('[密码验证] 检测到待发送消息，自动继续发送');
                if (typeof handleSendMessage === 'function') {
                    handleSendMessage();
                }
            } else {
                // 没有待发内容，只需聚焦到输入框
                const userInput = document.getElementById('user-input');
                if (userInput) {
                    userInput.focus();
                    console.log('[密码验证] 已聚焦到输入框，用户可继续输入');
                }
            }
        }, 100);
        
    } else {
        console.log('[密码验证] ❌ 密码错误');
        
        // 显示错误提示
        if (errorMsg) {
            errorMsg.classList.remove('hidden');
        }
        
        // 清空输入框
        passwordInput.value = '';
        passwordInput.focus();
    }
}

// 开始试用模式（密码验证成功后调用）
function startTrialMode() {
    // 保存选择
    localStorage.setItem('user_choice', 'trial');
    
    // 每次进入试用模式时，生成新的会话ID（确保数据库重新开始）
    localStorage.removeItem('trial_session_id');
    const sessionId = 'trial_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('trial_session_id', sessionId);
    console.log('[试用模式] 生成新的会话ID:', sessionId);
    
    // 设置试用模式标志
    localStorage.setItem('is_trial_mode', 'true');
    
    // 显示应用界面（如果应用被隐藏）
    const appContainer = document.querySelector('.app-container') || document.body;
    if (appContainer.style) {
        appContainer.style.display = '';
    }
    
    // 延迟一点时间，确保模态框完全隐藏后再初始化
    setTimeout(() => {
        console.log('[试用模式] 开始初始化试用模式...');
        
        // 重新初始化DOM元素引用
        if (typeof initElements === 'function') {
            initElements();
            console.log('[试用模式] DOM元素引用已重新初始化');
        }
        
        // 重新初始化会话
        if (typeof initSession === 'function') {
            initSession();
            console.log('[试用模式] 会话已重新初始化');
        }
        
        // 强制重新绑定事件监听器
        if (typeof initEventListeners === 'function') {
            if (window.eventListenersBound !== undefined) {
                window.eventListenersBound = false;
            }
            initEventListeners();
            console.log('[试用模式] 事件监听器已重新绑定');
        }
        
        // 更新试用状态气泡
        if (typeof updateTrialStatusBubble === 'function') {
            updateTrialStatusBubble();
        }
        
        // 刷新文档列表
        if (typeof fetchDocumentList === 'function' && typeof updateDocumentList === 'function') {
            fetchDocumentList().then(documents => {
                updateDocumentList(documents);
            }).catch(err => {
                console.error('刷新文档列表失败:', err);
            });
        }
        
        console.log('[试用模式] 试用模式初始化完成');
        
        // 显示续写手机端笔记确认弹窗（右上角）
        showMobileNotePrompt();
    }, 200);
}

// 取消密码验证，用户留在应用界面（但不能输入）
function cancelPasswordVerification() {
    hidePasswordModal();
    // 不返回登录弹窗，用户留在应用界面可以浏览，但输入时会再次弹出密码框
    console.log('[密码验证] 取消验证，用户留在应用界面');
}

// 初始化密码验证弹窗事件
function initPasswordModal() {
    const submitBtn = document.getElementById('trial-password-submit');
    const cancelBtn = document.getElementById('trial-password-cancel');
    const passwordInput = document.getElementById('trial-password-input');
    
    if (submitBtn) {
        submitBtn.addEventListener('click', verifyPassword);
        console.log('[密码验证] 确认按钮事件已绑定');
    }
    
    if (cancelBtn) {
        cancelBtn.addEventListener('click', cancelPasswordVerification);
        console.log('[密码验证] 取消按钮事件已绑定');
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                verifyPassword();
            }
        });
        console.log('[密码验证] 输入框回车事件已绑定');
    }
}

// 在 DOM 加载完成后初始化密码弹窗
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPasswordModal);
} else {
    setTimeout(initPasswordModal, 100);
}

// ================================
// 续写手机端笔记确认弹窗
// ================================

/**
 * 显示续写手机端笔记确认卡片
 * 在试用模式激活后，左下角弹出，20秒后自动关闭
 */
function showMobileNotePrompt() {
    const card = document.getElementById('mobile-note-prompt');
    const countdownEl = document.getElementById('mobile-note-countdown');
    const progressBar = document.getElementById('mobile-progress-bar');
    const confirmBtn = document.getElementById('mobile-note-confirm-btn');
    const cancelBtn = document.getElementById('mobile-note-cancel-btn');

    if (!card) {
        console.warn('[\u7eed\u5199\u5f39\u7a97] \u627e\u4e0d\u5230\u5361\u7247\u5143\u7d20');
        return;
    }

    // 显示卡片
    card.classList.remove('hidden');
    card.classList.remove('fading');
    console.log('[\u7eed\u5199\u5f39\u7a97] \u5df2\u663e\u793a\u7eed\u5199\u624b\u673a\u7aef\u7b14\u8bb0\u5361\u7247');

    // 使用通用倒计时（如果 app.js 已加\u8f7d）
    if (typeof startNotifyCountdown === 'function') {
        startNotifyCountdown(card, countdownEl, progressBar, 20);
    } else {
        // fallback：简单倒计时
        let secondsLeft = 20;
        if (countdownEl) countdownEl.textContent = secondsLeft;
        const t = setInterval(() => {
            secondsLeft -= 1;
            if (countdownEl) countdownEl.textContent = secondsLeft;
            if (secondsLeft <= 0) {
                clearInterval(t);
                hideMobileNotePrompt();
            }
        }, 1000);
        card._countdownInterval = t;
    }

    // 绑定确定按鈕
    if (confirmBtn && !confirmBtn.hasAttribute('data-mobile-listener')) {
        confirmBtn.setAttribute('data-mobile-listener', 'true');
        confirmBtn.addEventListener('click', () => {
            console.log('[\u7eed\u5199\u5f39\u7a97] \u7528\u6237\u70b9\u51fb\u786e\u5b9a');
            hideMobileNotePrompt();
        });
    }

    // 绑定\u5173\u95ed\u6309\u9215
    if (cancelBtn && !cancelBtn.hasAttribute('data-mobile-listener')) {
        cancelBtn.setAttribute('data-mobile-listener', 'true');
        cancelBtn.addEventListener('click', () => {
            console.log('[\u7eed\u5199\u5f39\u7a97] \u7528\u6237\u70b9\u51fb\u5173\u95ed');
            hideMobileNotePrompt();
        });
    }
}

/**
 * \u9690\u85cf\u7eed\u5199\u624b\u673a\u7aef\u7b14\u8bb0\u5361\u7247
 */
function hideMobileNotePrompt() {
    const card = document.getElementById('mobile-note-prompt');
    if (!card) return;

    if (typeof dismissNotifyCard === 'function') {
        dismissNotifyCard(card);
    } else {
        // fallback
        if (card._countdownInterval) clearInterval(card._countdownInterval);
        card.classList.add('fading');
        setTimeout(() => {
            card.classList.add('hidden');
            card.classList.remove('fading');
        }, 450);
    }
    console.log('[\u7eed\u5199\u5f39\u7a97] \u5361\u7247\u5df2\u5173\u95ed');
}

// 暴露到全局作用域
window.showMobileNotePrompt = showMobileNotePrompt;
window.hideMobileNotePrompt = hideMobileNotePrompt;

