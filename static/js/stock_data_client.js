const StockDataClient = {
    // guards against file:// protocol where origin is "null"
    apiUrl(path) {
        if (!window.location.origin || window.location.origin === "null") {
            throw new Error("Please open the dashboard through the Flask server.");
        }

        return new URL(path, window.location.origin).toString();
    },

    // unified response parser: extracts error message from JSON or falls back to generic
    async parseResponse(response, fallbackMessage) {
        const text = await response.text();
        let data = {};

        if (text) {
            try {
                data = JSON.parse(text);
            } catch (error) {
                throw new Error(fallbackMessage);
            }
        }

        if (!response.ok) {
            throw new Error(data.error || fallbackMessage);
        }

        return data;
    },

    async loadStockData(limit = 400) {
        const response = await fetch(this.apiUrl(`/api/stocks?limit=${limit}`));
        return this.parseResponse(response, "Failed to load stock data.");
    },

    async loadLatestPrices() {
        const response = await fetch(this.apiUrl("/api/stocks/latest"));
        return this.parseResponse(response, "Failed to load latest stock prices.");
    },

    async loadPortfolio() {
        const response = await fetch(this.apiUrl("/api/portfolio"));
        return this.parseResponse(response, "Failed to load portfolio.");
    },

    async executeTrade(stockId, side, quantity) {
        // CSRF token read from <meta> injected by Jinja
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";
        const response = await fetch(this.apiUrl("/api/trades"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ stockId, side, quantity })
        });
        return this.parseResponse(response, "Trade failed.");
    }
};
