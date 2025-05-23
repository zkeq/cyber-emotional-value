/**
 * Main page component
 * Manages the overall praise display experience
 */
class MainPage {
    constructor(options = {}) {
        this.userDemand = options.userDemand || '';
        this.startTime = Date.now();
        this.totalTokens = 0;
        this.elapsedSeconds = 0;
        this.wsManager = null;
        this.danmakuDisplay = null;
        this.statsFooter = null;
        this.timerInterval = null;
        this.useMockData = false; // Set to false to use actual WebSocket connection
    }

    render(container) {
        container.innerHTML = `
            <div class="min-h-screen flex flex-col animate-fade-in">
                <!-- Header -->
                <div class="relative z-10 p-4 text-center">
                    <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                        正在为你生成满满的爱意 💕
                    </h2>
                    <p class="text-gray-500">
                        "${this.userDemand || '普遍的快乐能量'}"
                    </p>
                </div>

                <!-- Danmaku Display Area -->
                <div id="danmaku-container" class="flex-1 relative overflow-hidden">
                    <!-- Danmaku will be rendered here by DanmakuDisplay component -->
                </div>

                <!-- Stats Footer -->
                <div id="stats-footer" class="relative z-10">
                    <!-- Stats will be rendered here by StatsFooter component -->
                </div>
            </div>
        `;

        this.initializeComponents();
        this.startTimer();
        this.connectWebSocket();
    }

    initializeComponents() {
        // Initialize danmaku display
        this.danmakuDisplay = new DanmakuDisplay({
            container: document.getElementById('danmaku-container')
        });

        // Initialize stats footer
        this.statsFooter = new StatsFooter({
            container: document.getElementById('stats-footer'),
            elapsedSeconds: this.elapsedSeconds,
            totalTokens: this.totalTokens
        });
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            this.elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);
            this.statsFooter.updateStats(this.elapsedSeconds, this.totalTokens);
        }, 1000);
    }

    async connectWebSocket() {
        if (this.useMockData) {
            // Fallback to mock data if needed for standalone testing
            console.warn("Using mock data stream as useMockData is true.");
            this.startMockDataStream();
        } else {
            // Real WebSocket connection
            this.wsManager = new WebSocketManager({
                url: 'wss:////emotional-value-api-flowith.onmicrosoft.cn/ws/praise', // Standard WebSocket URL
                onMessage: (messages) => this.handlePraiseMessages(messages),
                onError: (error) => this.handleWebSocketError(error),
                onConnect: () => {
                    console.log('MainPage: WebSocket Connected successfully.');
                    // Send the user's demand to the backend upon connection
                    if (this.userDemand && this.wsManager) {
                        this.wsManager.send({ demand: this.userDemand });
                        console.log('Sent user demand to WebSocket:', this.userDemand);
                    } else if (this.wsManager) {
                        // Send a generic demand if none was provided
                        this.wsManager.send({ demand: "需要一些鼓励和快乐" });
                         console.log('Sent generic demand to WebSocket.');
                    }
                },
                onDisconnect: (event) => {
                    console.log('MainPage: WebSocket Disconnected.', event.wasClean ? 'Cleanly.' : 'Unexpectedly.');
                    // Optionally, display a message to the user or attempt custom reconnection logic here
                }
            });
            
            try {
                await this.wsManager.connect();
            } catch (error) {
                console.error('MainPage: Failed to initiate WebSocket connection:', error);
                this.handleWebSocketError(error);
                // Fallback or error message display
            }
        }
    }

    async startMockDataStream() { // Kept for testing if backend is unavailable
        try {
            const response = await fetch('data/mockPraises.json');
            if (!response.ok) throw new Error(`Failed to load mockPraises.json: ${response.statusText}`);
            const mockData = await response.json();
            
            const generateMessage = () => {
                const praise = mockData.praises[Math.floor(Math.random() * mockData.praises.length)];
                return {
                    id: `mock_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    text: praise.text,
                    timestamp: new Date().toISOString(),
                    tokens: praise.tokens || Math.floor(Math.random() * 5) + 5 // fallback tokens
                };
            };

            setInterval(() => {
                const batchSize = 8 + Math.floor(Math.random() * 5); // 8-12 messages
                const messages = [];
                for (let i = 0; i < batchSize; i++) {
                    messages.push(generateMessage());
                }
                this.handlePraiseMessages(messages);
            }, 1000);

        } catch (error) {
            console.error('Failed to load or process mock data:', error);
            // Display an error or a message indicating mock data failure
        }
    }

    handlePraiseMessages(data) {
        let messagesArray = [];

        if (Array.isArray(data)) {
            messagesArray = data;
        } else if (typeof data === 'object' && data !== null && data.text) {
            // Handle case where backend might send a single message object
            messagesArray = [data];
            console.log('Received single message object, processing as array.');
        } else {
            console.warn('Received WebSocket message in unexpected format:', data);
            return; // Ignore if format is not recognized
        }

        messagesArray.forEach(message => {
            if (typeof message.text !== 'string' || message.text.trim() === '') {
                console.warn('Skipping message with invalid text:', message);
                return;
            }

            // Ensure each message has a unique ID for DanmakuDisplay
            if (!message.id) {
                message.id = `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                console.log('Generated fallback ID for message:', message.id);
            }
            
            // Ensure tokens are a number, default to a small value if not present
            message.tokens = Number(message.tokens) || (message.text.length / 2); // Estimate tokens if not provided

            this.danmakuDisplay.addPraise(message);
            this.totalTokens += message.tokens;
        });

        this.statsFooter.updateStats(this.elapsedSeconds, this.totalTokens);
    }

    handleWebSocketError(error) {
        console.error('WebSocket connection error:', error);
        this.statsFooter.container.querySelector('.stats-footer > div > div:last-child > span:last-child').textContent = "连接中断 💔 尝试刷新...";
        // Optionally, try to use mock data as a fallback if connection fails permanently
        // if (!this.useMockData && this.reconnectAttempts >= maxReconnectAttempts) {
        //     console.log("WebSocket failed, falling back to mock data.");
        //     this.useMockData = true; // prevent further connection attempts
        //     this.startMockDataStream();
        // }
    }

    destroy() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        if (this.wsManager) {
            this.wsManager.disconnect();
            this.wsManager = null;
        }
        if (this.danmakuDisplay) {
            this.danmakuDisplay.destroy();
            this.danmakuDisplay = null;
        }
        console.log('MainPage destroyed, resources cleaned up.');
    }
}
