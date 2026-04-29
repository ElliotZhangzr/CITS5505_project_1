const holdings = {};

const chart = document.getElementById("stockChart");
const ctx = chart.getContext("2d");
const currentPriceEl = document.getElementById("currentPrice");
const priceChangeEl = document.getElementById("priceChange");
const holdingBody = document.getElementById("holdingBody");
const totalValueEl = document.getElementById("totalValue");
const marketList = document.getElementById("marketList");
const tradeMessage = document.getElementById("tradeMessage");
const tradeSymbol = document.getElementById("tradeSymbol");
const tradeQty = document.getElementById("tradeQty");

const stockState = {
    stocks: [],
    marketData: {}
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
    let total = 0;

    Object.keys(holdings).forEach((symbol) => {
        const position = holdings[symbol];
        const market = getLastPrice(symbol);
        if (market === null) {
            return;
        }

        const value = market * position.qty;
        total += value;

        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${symbol}</td>
            <td>${position.qty}</td>
            <td>${formatUsd(position.avg)}</td>
            <td>${formatUsd(value)}</td>
        `;
        holdingBody.appendChild(row);
    });

    totalValueEl.textContent = formatUsd(total);
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
        tradeSymbol.appendChild(option);
    });

    activeSymbol = symbols[0] || activeSymbol;
}

function executeTrade(type) {
    const symbol = tradeSymbol.value;
    const qty = Number(tradeQty.value);
    const price = getLastPrice(symbol);

    if (price === null) {
        tradeMessage.textContent = "No stock data available.";
        return;
    }

    if (!Number.isInteger(qty) || qty <= 0) {
        tradeMessage.textContent = "Quantity must be an integer greater than 0.";
        return;
    }

    const position = holdings[symbol] || { qty: 0, avg: price };

    if (type === "buy") {
        const totalCost = position.avg * position.qty + price * qty;
        const totalQty = position.qty + qty;
        position.qty = totalQty;
        position.avg = totalCost / totalQty;
        holdings[symbol] = position;
        tradeMessage.textContent = `Bought ${qty} shares of ${symbol} at ${formatUsd(price)}.`;
    } else {
        if (qty > position.qty) {
            tradeMessage.textContent = `Sell failed: insufficient ${symbol} holdings.`;
            return;
        }
        position.qty -= qty;
        if (position.qty === 0) {
            delete holdings[symbol];
        } else {
            holdings[symbol] = position;
        }
        tradeMessage.textContent = `Sold ${qty} shares of ${symbol} at ${formatUsd(price)}.`;
    }

    renderHoldings();
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
        stockState.stocks = data.stocks;
        stockState.marketData = data.marketData;
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
