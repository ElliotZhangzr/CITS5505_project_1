const marketData = {
    AAPL: [174, 176, 175, 179, 183, 181, 185, 188, 186, 191],
    TSLA: [198, 204, 201, 208, 214, 210, 216, 221, 219, 225],
    NVDA: [785, 792, 788, 801, 814, 809, 822, 834, 828, 841]
};

const holdings = {
    AAPL: { qty: 5, avg: 175 },
    TSLA: { qty: 2, avg: 203 },
    NVDA: { qty: 1, avg: 790 }
};

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

let activeSymbol = "AAPL";

function formatUsd(value) {
    return `$${value.toFixed(2)}`;
}

function getLastPrice(symbol) {
    const series = marketData[symbol];
    return series[series.length - 1];
}

function drawChart(symbol) {
    const series = marketData[symbol];
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
        const x = pad + (idx / (series.length - 1)) * (w - pad * 2);
        const y = h - pad - ((price - min) / (max - min)) * (h - pad * 2);
        return { x, y };
    });

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.slice(1).forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = "#0f658e";
    ctx.lineWidth = 2.5;
    ctx.stroke();

    ctx.lineTo(points[points.length - 1].x, h - pad);
    ctx.lineTo(points[0].x, h - pad);
    ctx.closePath();
    ctx.fillStyle = "rgba(15,101,142,0.14)";
    ctx.fill();

    const first = series[0];
    const last = series[series.length - 1];
    const change = ((last - first) / first) * 100;

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
    Object.entries(marketData).forEach(([symbol, series]) => {
        const first = series[0];
        const last = series[series.length - 1];
        const delta = ((last - first) / first) * 100;

        const item = document.createElement("li");
        item.innerHTML = `
            <span>${symbol}</span>
            <span>${formatUsd(last)}</span>
            <span class="delta ${delta >= 0 ? "up" : "down"}">${delta >= 0 ? "+" : ""}${delta.toFixed(2)}%</span>
        `;
        marketList.appendChild(item);
    });
}

function executeTrade(type) {
    const symbol = tradeSymbol.value;
    const qty = Number(tradeQty.value);

    if (!Number.isInteger(qty) || qty <= 0) {
        tradeMessage.textContent = "Quantity must be an integer greater than 0.";
        return;
    }

    const price = getLastPrice(symbol);
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

drawChart(activeSymbol);
renderHoldings();
renderMarketOverview();
initTabs();
