const canvas = document.getElementById('trading-canvas');
const ctx = canvas.getContext('2d');
const mouse = { x: -1000, y: -1000, active: false };
let candles = [], coins = [];
let coinImg = new Image();
coinImg.src = '/static/img/GoldCoin.png';

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    init();
}

class Candle {
    constructor(x) {
        this.x = x;
        this.y = Math.random() * canvas.height;
        this.w = 3 + Math.random() * 5;
        this.h = (Math.random() - 0.5) * 80;
        this.speed = 0.2 + Math.random() * 0.5;
        this.isGreen = Math.random() > 0.45;
    }

    draw() {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        const force = dist < 200 ? (200 - dist) / 200 : 0;
        
        const offsetX = force * (dx * 0.1);
        const offsetY = force * (dy * 0.15);
        
        const drawX = this.x - offsetX;
        const drawY = this.y - offsetY;
        
        const opacity = 0.05 + force * 0.15;
        const color = this.isGreen
            ? `rgba(180, 140, 20, ${opacity})`
            : `rgba(200, 100, 30, ${opacity})`;

        ctx.beginPath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.moveTo(drawX + this.w / 2, drawY - 15);
        ctx.lineTo(drawX + this.w / 2, drawY + this.h + 15);
        ctx.stroke();

        ctx.fillStyle = color;
        ctx.fillRect(drawX, drawY, this.w, this.h);
    }

    update() {
        this.x -= this.speed;
        if (this.x < -50) {
            this.x = canvas.width + 50;
            this.y = Math.random() * canvas.height;
        }
    }
}

class Coin {
    constructor(isInitial = true) {
        this.reset(isInitial);
    }

    reset(isInitial) {
        // If the page has just loaded, the elements are randomly distributed across the screen; 
        // if it's being reset during runtime, they enter from the right edge.
        this.x = isInitial ? Math.random() * canvas.width : canvas.width + 100;
        this.y = Math.random() * canvas.height;
        this.size = 20 + Math.random() * 20;
        this.speed = 0.5 + Math.random() * 1.2;
        this.opacity = 0.1 + Math.random() * 0.2;
        this.rotation = Math.random() * Math.PI * 2;
        this.spinSpeed = 0.02 + Math.random() * 0.05;
    }

    draw() {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        let drawX = this.x;
        let drawY = this.y;

        if (dist < 250) {
            const force = (250 - dist) / 250;
            drawX -= dx * force * 0.2;
            drawY -= dy * force * 0.2;
        }

        ctx.save();
        ctx.translate(drawX, drawY);
        ctx.rotate(this.rotation);
        ctx.globalAlpha = this.opacity;
        
        if (coinImg.complete) {
            ctx.drawImage(coinImg, -this.size / 2, -this.size / 2, this.size, this.size);
        }
        
        ctx.restore();
        ctx.globalAlpha = 1;
    }

    update() {
        this.x -= this.speed;
        this.rotation += this.spinSpeed;
        
        if (this.x < -100) {
            this.reset(false);
        }
    }
}

function init() {
    candles = [];
    coins = [];
    
    const candleCount = Math.floor(canvas.width / 40);
    for (let i = 0; i < candleCount; i++) {
        candles.push(new Candle(Math.random() * canvas.width));
    }
    
    for (let i = 0; i < 10; i++) {
        coins.push(new Coin(true));
    }
}

function drawGrid() {
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(180, 140, 20, 0.03)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 100) {
        ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height);
    }
    for (let y = 0; y < canvas.height; y += 100) {
        ctx.moveTo(0, y); ctx.lineTo(canvas.width, y);
    }
    ctx.stroke();
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    drawGrid();
    
    // Update and draw
    candles.forEach(c => {
        c.update();
        c.draw();
    });
    
    coins.forEach(c => {
        c.update();
        c.draw();
    });
    
    requestAnimationFrame(animate);
}

// Mouse interaction monitoring
window.addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.active = true;
});

window.addEventListener('mouseleave', () => {
    mouse.x = -1000;
    mouse.y = -1000;
    mouse.active = false;
});

window.addEventListener('resize', resize);

resize();
animate();