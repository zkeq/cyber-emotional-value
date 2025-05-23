/**
 * WebSocket connection manager utility
 * Handles connection, reconnection, and message processing
 */
class WebSocketManager {
    constructor(options = {}) {
        this.url = options.url;
        this.onMessage = options.onMessage || (() => {});
        this.onError = options.onError || (() => {});
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
    }

    async connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnect();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.onMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.onDisconnect(event);
                
                // Attempt to reconnect if not closed intentionally
                if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => this.reconnect(), this.reconnectDelay);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.onError(error);
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.onError(error);
        }
    }

    async reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        await this.connect();
    }

    send(data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }
}

