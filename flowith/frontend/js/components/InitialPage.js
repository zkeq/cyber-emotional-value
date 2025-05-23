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

