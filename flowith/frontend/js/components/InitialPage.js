/**
 * Initial landing page component
 * Handles user input for emotional needs
 */
class InitialPage {
    constructor(options = {}) {
        this.onSubmit = options.onSubmit || (() => {});
        this.demand = '';
    }

    render(container) {
        container.innerHTML = `
            <div class="min-h-screen flex items-center justify-center p-6 animate-fade-in">
                <div class="max-w-lg w-full text-center">
                    <!-- Logo/Title -->
                    <div class="mb-8">
                        <h1 class="text-4xl font-bold text-gray-800 mb-2">
                            ✨ 夸夸网站 ✨
                        </h1>
                        <p class="text-gray-600 text-lg">
                            给你满满的情绪价值
                        </p>
                    </div>

                    <!-- Input form -->
                    <div class="bg-white/70 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-white/50">
                        <div class="mb-6">
                            <input 
                                type="text" 
                                id="demandInput"
                                placeholder="今天想要怎样的情绪价值?"
                                class="w-full px-6 py-4 text-lg rounded-2xl border-2 border-gray-200 focus:border-praise-pink focus:outline-none transition-all duration-300 bg-white/80"
                                maxlength="100"
                            >
                        </div>
                        
                        <!-- Example suggestions -->
                        <div class="mb-6">
                            <p class="text-sm text-gray-500 mb-3">比如可以说:</p>
                            <div class="flex flex-wrap gap-2 justify-center">
                                <button class="suggestion-btn px-3 py-1 bg-praise-pink/20 text-praise-coral rounded-full text-sm hover:bg-praise-pink/30 transition-colors">
                                    需要被鼓励
                                </button>
                                <button class="suggestion-btn px-3 py-1 bg-praise-blue/20 text-blue-600 rounded-full text-sm hover:bg-praise-blue/30 transition-colors">
                                    工作压力大
                                </button>
                                <button class="suggestion-btn px-3 py-1 bg-praise-yellow/20 text-yellow-700 rounded-full text-sm hover:bg-praise-yellow/30 transition-colors">
                                    想要被夸奖
                                </button>
                                <button class="suggestion-btn px-3 py-1 bg-praise-green/20 text-green-700 rounded-full text-sm hover:bg-praise-green/30 transition-colors">
                                    感到孤独
                                </button>
                            </div>
                        </div>

                        <button 
                            id="submitBtn"
                            class="w-full bg-gradient-to-r from-praise-pink to-praise-coral text-white py-4 rounded-2xl text-lg font-semibold hover:from-praise-coral hover:to-praise-pink transform hover:scale-[1.02] transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            🌈 开始夸我！
                        </button>
                    </div>

                    <!-- Footer note -->
                    <p class="mt-6 text-sm text-gray-400">
                        让温暖的话语治愈你的心 💝
                    </p>
                    
                    <!-- GitHub Link -->
                    <a 
                        href="https://github.com/zkeq/cyber-emotional-value" 
                        target="_blank"
                        class="mt-4 inline-flex items-center gap-2 text-gray-500 hover:text-praise-pink transition-colors"
                    >
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
                        </svg>
                        <span class="text-sm">喜欢这个项目？ - 欢迎 Star ⭐</span>
                    </a>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const input = document.getElementById('demandInput');
        const submitBtn = document.getElementById('submitBtn');
        const suggestionBtns = document.querySelectorAll('.suggestion-btn');

        // Handle input changes
        input.addEventListener('input', () => {
            this.demand = input.value.trim();
            this.updateSubmitButton();
        });

        // Handle enter key
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.demand) {
                this.handleSubmit();
            }
        });

        // Handle submit button click
        submitBtn.addEventListener('click', () => {
            this.handleSubmit();
        });

        // Handle suggestion button clicks
        suggestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                input.value = btn.textContent.trim();
                this.demand = input.value;
                this.updateSubmitButton();
                input.focus();
            });
        });

        // Focus input on load
        setTimeout(() => input.focus(), 300);
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        if (this.demand) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled:opacity-50', 'disabled:cursor-not-allowed');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.add('disabled:opacity-50', 'disabled:cursor-not-allowed');
        }
    }

    handleSubmit() {
        if (this.demand && this.onSubmit) {
            this.onSubmit(this.demand);
        }
    }
}

