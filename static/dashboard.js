const chart = document.getElementById("stockChart");
const ctx = chart.getContext("2d");
const currentPriceEl = document.getElementById("currentPrice");
const priceChangeEl = document.getElementById("priceChange");
const holdingBody = document.getElementById("holdingBody");
const totalValueEl = document.getElementById("totalValue");
const totalAssetsEl = document.getElementById("totalAssets");
const realizedProfitEl = document.getElementById("realizedProfit");
const unrealizedProfitEl = document.getElementById("unrealizedProfit");
const totalProfitEl = document.getElementById("totalProfit");
const accountCashEl = document.getElementById("accountCash");
const marketList = document.getElementById("marketList");
const tradeMessage = document.getElementById("tradeMessage");
const tradeSymbol = document.getElementById("tradeSymbol");
const tradeQty = document.getElementById("tradeQty");

const stockState = {
    stocks: [],
    marketData: {}
};

const portfolioState = {
    cash: 0,
    stockValue: 0,
    totalAssets: 0,
    realizedProfit: 0,
    unrealizedProfit: 0,
    totalProfit: 0,
    holdings: []
};

let activeSymbol = "AAPL";

function formatUsd(value) {
    return `$${value.toFixed(2)}`;
}

function getLastPrice(symbol) {
    const series = stockState.marketData[symbol];
    if (!series || series.length === 0) {
        return null;
    }
    return series[series.length - 1];
}

function getSymbols() {
    return Object.keys(stockState.marketData).filter((symbol) => {
        const series = stockState.marketData[symbol];
        return series && series.length > 0;
    });
}

function getChangePercent(symbol) {
    const series = stockState.marketData[symbol];
    if (!series || series.length < 2) {
        return 0;
    }

    const first = series[0];
    const last = series[series.length - 1];
    return ((last - first) / first) * 100;
}

function getStockId(symbol) {
    const stock = stockState.stocks.find((item) => item.symbol === symbol);
    if (stock) {
        return stock.id;
    }

    const selectedOption = tradeSymbol.options[tradeSymbol.selectedIndex];
    return selectedOption ? selectedOption.dataset.stockId : null;
}

function setPortfolio(data) {
    portfolioState.cash = data.cash;
    portfolioState.stockValue = data.stockValue;
    portfolioState.totalAssets = data.totalAssets;
    portfolioState.realizedProfit = data.realizedProfit;
    portfolioState.unrealizedProfit = data.unrealizedProfit;
    portfolioState.totalProfit = data.totalProfit;
    portfolioState.holdings = data.holdings;
}

function recalculatePortfolioFromPrices() {
    let stockValue = 0;
    let unrealizedProfit = 0;

    portfolioState.holdings = portfolioState.holdings.map((position) => {
        const currentPrice = getLastPrice(position.symbol) ?? position.currentPrice;
        const marketValue = currentPrice * position.quantity;
        const holdingProfit = (currentPrice - position.averageCost) * position.quantity;

        stockValue += marketValue;
        unrealizedProfit += holdingProfit;

        return {
            ...position,
            currentPrice,
            marketValue,
            unrealizedProfit: holdingProfit
        };
    });

    portfolioState.stockValue = stockValue;
    portfolioState.unrealizedProfit = unrealizedProfit;
    portfolioState.totalAssets = portfolioState.cash + stockValue;
    portfolioState.totalProfit = portfolioState.realizedProfit + unrealizedProfit;
}

function appendLatestPrices(latestPrices, maxPoints = 400) {
    Object.entries(latestPrices).forEach(([symbol, price]) => {
        if (!stockState.marketData[symbol]) {
            stockState.marketData[symbol] = [];
        }

        const currentPrice = getLastPrice(symbol);

        if (currentPrice === price) {
            return;
        }

        stockState.marketData[symbol].push(price);

        if (stockState.marketData[symbol].length > maxPoints) {
            stockState.marketData[symbol].shift();
        }
    });
}

function drawChart(symbol) {
    const series = stockState.marketData[symbol];
    if (!series || series.length === 0) {
        ctx.clearRect(0, 0, chart.width, chart.height);
        currentPriceEl.textContent = "$0.00";
        priceChangeEl.textContent = "0.00%";
        priceChangeEl.className = "down";
        return;
    }

    const w = chart.width;
    const h = chart.height;
    const pad = 24;
    const min = Math.min(...series) - 3;
    const max = Math.max(...series) + 3;

    ctx.clearRect(0, 0, w, h);

    ctx.strokeStyle = "rgba(20,53,67,0.16)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i += 1) {
        const y = pad + ((h - pad * 2) / 4) * i;
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(w - pad, y);
        ctx.stroke();
    }

    const points = series.map((price, idx) => {
        const x = series.length === 1
            ? w / 2
            : pad + (idx / (series.length - 1)) * (w - pad * 2);
        const y = h - pad - ((price - min) / (max - min)) * (h - pad * 2);
        return { x, y };
    });

    const last = series[series.length - 1];
    const change = getChangePercent(symbol);

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.slice(1).forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.lineTo(points[points.length - 1].x, h - pad);
    ctx.lineTo(points[0].x, h - pad);
    ctx.closePath();
    ctx.fillStyle = "rgba(20, 53, 67, 0.06)";
    ctx.fill();

    for (let i = 1; i < points.length; i += 1) {
        ctx.beginPath();
        ctx.moveTo(points[i - 1].x, points[i - 1].y);
        ctx.lineTo(points[i].x, points[i].y);
        ctx.strokeStyle = series[i] >= series[i - 1] ? "#16a34a" : "#dc2626";
        ctx.lineWidth = 2.5;
        ctx.stroke();
    }

    currentPriceEl.textContent = `${symbol} ${formatUsd(last)}`;
    priceChangeEl.textContent = `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`;
    priceChangeEl.className = change >= 0 ? "up" : "down";
}

function renderHoldings() {
    holdingBody.innerHTML = "";

    portfolioState.holdings.forEach((position) => {
        const row = document.createElement("tr");
        const profitClass = position.unrealizedProfit >= 0 ? "up" : "down";
        row.innerHTML = `
            <td>${position.symbol}</td>
            <td>${position.quantity}</td>
            <td>${formatUsd(position.averageCost)}</td>
            <td>${formatUsd(position.currentPrice)}</td>
            <td>${formatUsd(position.marketValue)}</td>
            <td class="${profitClass}">${formatUsd(position.unrealizedProfit)}</td>
        `;
        holdingBody.appendChild(row);
    });

    totalValueEl.textContent = formatUsd(portfolioState.stockValue);
    totalAssetsEl.textContent = formatUsd(portfolioState.totalAssets);
    realizedProfitEl.textContent = formatUsd(portfolioState.realizedProfit);
    unrealizedProfitEl.textContent = formatUsd(portfolioState.unrealizedProfit);
    totalProfitEl.textContent = formatUsd(portfolioState.totalProfit);
    accountCashEl.textContent = formatUsd(portfolioState.cash);
}

function renderMarketOverview() {
    marketList.innerHTML = "";
    getSymbols().forEach((symbol) => {
        const last = getLastPrice(symbol);
        const delta = getChangePercent(symbol);

        const item = document.createElement("li");
        item.innerHTML = `
            <span>${symbol}</span>
            <span>${formatUsd(last)}</span>
            <span class="delta ${delta >= 0 ? "up" : "down"}">${delta >= 0 ? "+" : ""}${delta.toFixed(2)}%</span>
        `;
        marketList.appendChild(item);
    });
}

function renderStockControls() {
    const stockTabs = document.querySelector(".stock-tabs");
    const symbols = getSymbols();

    stockTabs.innerHTML = "";
    tradeSymbol.innerHTML = "";

    symbols.forEach((symbol, index) => {
        const tab = document.createElement("button");
        tab.className = index === 0 ? "stock-tab active" : "stock-tab";
        tab.dataset.symbol = symbol;
        tab.textContent = symbol;
        stockTabs.appendChild(tab);

        const option = document.createElement("option");
        option.value = symbol;
        option.textContent = symbol;
        option.dataset.stockId = stockState.stocks.find((stock) => stock.symbol === symbol)?.id || "";
        tradeSymbol.appendChild(option);
    });

    activeSymbol = symbols[0] || activeSymbol;
}

async function executeTrade(type) {
    const symbol = tradeSymbol.value;
    const qty = Number(tradeQty.value);
    const stockId = getStockId(symbol);

    if (!Number.isInteger(qty) || qty <= 0) {
        tradeMessage.textContent = "Quantity must be an integer greater than 0.";
        return;
    }

    if (stockId === null) {
        tradeMessage.textContent = "No stock data available.";
        return;
    }

    try {
        const portfolio = await StockDataClient.executeTrade(stockId, type.toUpperCase(), qty);
        const latestData = await StockDataClient.loadLatestPrices();
        appendLatestPrices(latestData.latestPrices);
        setPortfolio(portfolio);
        recalculatePortfolioFromPrices();
        drawChart(activeSymbol);
        renderHoldings();
        renderMarketOverview();
        tradeMessage.textContent = `${type === "buy" ? "Bought" : "Sold"} ${qty} shares of ${symbol}.`;
    } catch (error) {
        tradeMessage.textContent = error.message;
    }
}

function initTabs() {
    const tabs = Array.from(document.querySelectorAll(".stock-tab"));
    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((btn) => btn.classList.remove("active"));
            tab.classList.add("active");
            activeSymbol = tab.dataset.symbol;
            drawChart(activeSymbol);
            tradeSymbol.value = activeSymbol;
        });
    });
}

document.getElementById("buyBtn").addEventListener("click", () => executeTrade("buy"));
document.getElementById("sellBtn").addEventListener("click", () => executeTrade("sell"));

async function initDashboard() {
    try {
        const data = await StockDataClient.loadStockData();
        const portfolio = await StockDataClient.loadPortfolio();
        stockState.stocks = data.stocks;
        stockState.marketData = data.marketData;
        setPortfolio(portfolio);
        recalculatePortfolioFromPrices();
        renderStockControls();

        if (getSymbols().length === 0) {
            drawChart(activeSymbol);
            renderHoldings();
            renderMarketOverview();
            tradeMessage.textContent = "No stock data available.";
            return;
        }

        drawChart(activeSymbol);
        renderHoldings();
        renderMarketOverview();
        initTabs();

        setInterval(async () => {
            try {
                const latestData = await StockDataClient.loadLatestPrices();
                appendLatestPrices(latestData.latestPrices);
                recalculatePortfolioFromPrices();
            } catch (error) {
                tradeMessage.textContent = error.message;
                return;
            }

            drawChart(activeSymbol);
            renderHoldings();
            renderMarketOverview();
        }, 2000);
    } catch (error) {
        tradeMessage.textContent = error.message;
    }
}

initDashboard();
