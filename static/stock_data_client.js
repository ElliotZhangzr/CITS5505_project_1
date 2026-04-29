const StockDataClient = {
    async loadStockData(limit = 400) {
        const response = await fetch(`/api/stocks?limit=${limit}`);

        if (!response.ok) {
            throw new Error("Failed to load stock data.");
        }

        return response.json();
    },

    async loadLatestPrices() {
        const response = await fetch("/api/stocks/latest");

        if (!response.ok) {
            throw new Error("Failed to load latest stock prices.");
        }

        return response.json();
    }
};
