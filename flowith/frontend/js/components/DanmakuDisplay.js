/**
 * Danmaku display component
 * Handles the animation and rendering of praise messages
 */
class DanmakuDisplay {
    constructor(options = {}) {
        this.container = options.container;
        this.tracks = 8; // Number of horizontal tracks
        this.trackHeight = 60; // Height of each track in pixels
        this.activeMessages = new Map(); // Track active danmaku messages
        this.colors = [
            'text-praise-coral',
            'text-praise-pink', 
            'text-praise-blue',
            'text-praise-green',
            'text-praise-purple',
            'text-yellow-600',
            'text-indigo-500',
            'text-rose-500'
        ];
        this.trackAvailability = new Array(this.tracks).fill(0); // Timestamp when each track becomes available
        
        this.init();
    }

    init() {
        if (!this.container) {
            console.error("DanmakuDisplay: Container element not provided or not found.");
            return;
        }
        this.container.innerHTML = `
            <div class="danmaku-area relative w-full h-full pointer-events-none">
                <!-- Danmaku messages will be inserted here -->
            </div>
        `;
        
        this.danmakuArea = this.container.querySelector('.danmaku-area');
        if (!this.danmakuArea) {
             console.error("DanmakuDisplay: Failed to create danmaku-area.");
             return;
        }
        
        // Set height based on tracks, ensure it's at least a minimum height
        const calculatedHeight = this.tracks * this.trackHeight;
        this.danmakuArea.style.height = `${Math.max(calculatedHeight, 400)}px`; // Ensure min height of 400px
    }

    addPraise(message) {
        if (!this.danmakuArea) {
            console.warn("DanmakuDisplay: danmakuArea not initialized. Cannot add praise.");
            return;
        }
        if (!message || typeof message.text !== 'string' || !message.id) {
            console.warn('DanmakuDisplay: Invalid message object received.', message);
            return;
        }

        // Find an available track
        const trackIndex = this.findAvailableTrack();
        
        // Create danmaku element
        const danmakuElement = this.createDanmakuElement(message, trackIndex);
        
        // Add to DOM
        this.danmakuArea.appendChild(danmakuElement);
        
        // Track the active message
        this.activeMessages.set(message.id, {
            element: danmakuElement,
            track: trackIndex,
            startTime: Date.now()
        });

        // Mark track as occupied for a short duration to prevent immediate reuse by very fast messages
        // The actual visual occupancy is determined by the animation duration.
        // This helps in staggering messages if many arrive almost simultaneously.
        this.trackAvailability[trackIndex] = Date.now() + 500; // Minimum 0.5s gap for track re-selection

        // Remove element after animation (animation duration + buffer)
        const animationDuration = this.calculateAnimationDuration(message.text);
        setTimeout(() => {
            this.removeDanmaku(message.id);
        }, animationDuration + 2000); // Add 2s buffer
    }

    findAvailableTrack() {
        const now = Date.now();
        
        // Try to find a completely free track first
        for (let i = 0; i < this.tracks; i++) {
            if (this.trackAvailability[i] <= now) {
                return i;
            }
        }
        
        // If all tracks are "busy" (recently used), pick the one that became available earliest
        let earliestTime = this.trackAvailability[0];
        let earliestTrack = 0;
        for (let i = 1; i < this.tracks; i++) {
            if (this.trackAvailability[i] < earliestTime) {
                earliestTime = this.trackAvailability[i];
                earliestTrack = i;
            }
        }
        return earliestTrack;
    }

    calculateAnimationDuration(text) {
        // Calculate duration based on text length and screen width
        // This aims for a comfortable reading speed.
        const averageCharWidth = 16; // Approximate average width of a character in pixels at typical font size
        const textWidth = text.length * averageCharWidth;
        const screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        
        const totalDistanceToTravel = screenWidth + textWidth; // Element starts at 100vw, travels its own width past 0
        
        // Speed: pixels per second. Adjust for desired danmaku speed.
        // Slower speed (e.g., 75px/s) means longer duration. Faster (e.g., 150px/s) means shorter.
        const speed = 100; // pixels per second 
        
        let durationSeconds = totalDistanceToTravel / speed;
        
        // Ensure a minimum and maximum duration for very short/long texts or screen sizes
        durationSeconds = Math.max(8, Math.min(durationSeconds, 20)); // e.g., min 8s, max 20s
        
        return durationSeconds * 1000; // Convert to milliseconds
    }

    createDanmakuElement(message, trackIndex) {
        const element = document.createElement('div');
        const color = this.colors[Math.floor(Math.random() * this.colors.length)];
        const fontSize = 14 + Math.floor(Math.random() * 8); // 14-21px
        // Ensure topPosition doesn't cause overflow if trackHeight is small or many tracks
        const topPosition = (trackIndex * this.trackHeight) + Math.floor(Math.random() * (this.trackHeight - fontSize - 5)); // Add vertical randomness within track
        
        element.className = `danmaku-item absolute whitespace-nowrap font-medium ${color} pointer-events-none`;
        element.style.top = `${Math.max(0, topPosition)}px`; // Ensure top is not negative
        element.style.fontSize = `${fontSize}px`;
        element.style.lineHeight = '1.4'; // Consistent line height
        element.style.textShadow = '1px 1px 3px rgba(0, 0, 0, 0.2), 0 0 1px rgba(255,255,255,0.7)'; // Enhanced text shadow
        element.style.zIndex = `${Math.floor(Math.random() * 10) + 1}`; // Random z-index for overlap effect
        
        // The animation itself will start with transform: translateX(100vw)
        // So no initial 'left' or 'right' positioning beyond normal flow is strictly needed here.
        // element.style.left = '100vw'; // Or rely on keyframe 0%
        
        element.textContent = message.text;
        element.setAttribute('data-message-id', message.id);
        
        // Add animation using the keyframes defined in CSS/Tailwind config
        const durationMs = this.calculateAnimationDuration(message.text);
        element.style.animation = `danmaku ${durationMs / 1000}s linear forwards`;
        
        return element;
    }

    removeDanmaku(messageId) {
        const messageData = this.activeMessages.get(messageId);
        if (messageData && messageData.element && messageData.element.parentNode) {
            messageData.element.remove();
        }
        this.activeMessages.delete(messageId);
    }

    destroy() {
        // Clear all active messages and remove their elements from DOM
        this.activeMessages.forEach((messageData) => {
            if (messageData.element && messageData.element.parentNode) {
                messageData.element.remove();
            }
        });
        this.activeMessages.clear();
        if (this.danmakuArea && this.danmakuArea.parentNode) {
            this.danmakuArea.innerHTML = ''; // Clear the area
        }
        console.log("DanmakuDisplay destroyed.");
    }
}
