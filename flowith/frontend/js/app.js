/**
 * Main application controller
 * Manages the overall application state and component rendering
 */
class App {
    constructor() {
        this.currentView = 'initial'; // 'initial' or 'main'
        this.userDemand = '';
        this.appElement = document.getElementById('app');
        
        this.init();
    }

    init() {
        this.renderCurrentView();
    }

    renderCurrentView() {
        if (this.currentView === 'initial') {
            this.renderInitialPage();
        } else if (this.currentView === 'main') {
            this.renderMainPage();
        }
    }

    renderInitialPage() {
        const initialPage = new InitialPage({
            onSubmit: (demand) => this.handleDemandSubmit(demand)
        });
        initialPage.render(this.appElement);
    }

    renderMainPage() {
        const mainPage = new MainPage({
            userDemand: this.userDemand
        });
        mainPage.render(this.appElement);
    }

    handleDemandSubmit(demand) {
        this.userDemand = demand;
        this.currentView = 'main';
        this.renderCurrentView();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new App();
});

