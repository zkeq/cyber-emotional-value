/**
 * Statistics footer component
 * Displays elapsed time and token consumption
 */
class StatsFooter {
    constructor(options = {}) {
        this.container = options.container;
        this.elapsedSeconds = options.elapsedSeconds || 0;
        this.totalTokens = options.totalTokens || 0;
        
        this.render();
    }

    render() {
        this.container.innerHTML = `
            <div class="stats-footer bg-white/80 backdrop-blur-sm border-t border-white/50 p-4">
                <div class="max-w-4xl mx-auto">
                    <div class="flex justify-center items-center gap-8 text-sm text-gray-600">
                        <div class="flex items-center gap-2">
                            <span class="text-xl">⏰</span>
                            <span>已沉浸</span>
                            <span id="elapsed-time" class="font-semibold text-praise-coral">
                                ${this.formatTime(this.elapsedSeconds)}
                            </span>
                        </div>
                        
                        <div class="flex items-center gap-2">
                            <span class="text-xl">✨</span>
                            <span>已收获</span>
                            <span id="total-tokens" class="font-semibold text-praise-blue">
                                ${this.totalTokens.toLocaleString()}
                            </span>
                            <span>情绪能量</span>
                        </div>

                        <div class="flex items-center gap-2">
                            <span class="text-xl">💝</span>
                            <span class="text-praise-green font-medium">
                                持续为你输送爱意中...
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    updateStats(elapsedSeconds, totalTokens) {
        this.elapsedSeconds = elapsedSeconds;
        this.totalTokens = totalTokens;

        const elapsedTimeElement = document.getElementById('elapsed-time');
        const totalTokensElement = document.getElementById('total-tokens');

        if (elapsedTimeElement) {
            elapsedTimeElement.textContent = this.formatTime(elapsedSeconds);
            this.addUpdateAnimation(elapsedTimeElement);
        }

        if (totalTokensElement) {
            totalTokensElement.textContent = totalTokens.toLocaleString();
            this.addUpdateAnimation(totalTokensElement);
        }
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        if (minutes === 0) {
            return `${remainingSeconds} 秒`;
        } else {
            return `${minutes} 分 ${remainingSeconds} 秒`;
        }
    }

    addUpdateAnimation(element) {
        element.style.transform = 'scale(1.1)';
        element.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
}

