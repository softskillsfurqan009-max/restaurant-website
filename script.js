// ========== MENU DATA ==========
const menuItems = [
  { id:1, name:"Gold Label Wagyu Burger", category:"Burgers", price:18.99, img:"https://images.pexels.com/photos/1633578/pexels-photo-1633578.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Black truffle, wagyu beef, edible gold" },
  { id:2, name:"Crispy Zinger Deluxe", category:"Burgers", price:13.99, img:"https://images.pexels.com/photos/2983101/pexels-photo-2983101.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Spicy buttermilk chicken, signature sauce" },
  { id:3, name:"Elite Fried Chicken (10pc)", category:"Crispy Chicken", price:21.99, img:"https://images.pexels.com/photos/6065572/pexels-photo-6065572.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Secret recipe, double fried, crispy" },
  { id:4, name:"Truffle Mushroom Pizza", category:"Pizza", price:19.99, img:"https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Porcini, truffle oil, fresh mozzarella" },
  { id:5, name:"Parmesan Truffle Fries", category:"Fries", price:9.99, img:"https://images.pexels.com/photos/1583884/pexels-photo-1583884.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Fresh parmesan, rosemary, truffle oil" },
  { id:6, name:"Lamb Shawarma Plate", category:"Shawarma", price:15.99, img:"https://images.pexels.com/photos/6287764/pexels-photo-6287764.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Slow roasted lamb, tahini, pickles" },
  { id:7, name:"Wagyu Cheesesteak", category:"Sandwiches", price:17.99, img:"https://images.pexels.com/photos/1600711/pexels-photo-1600711.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Wagyu beef, provolone, caramelized onions" },
  { id:8, name:"Spicy Harissa Wrap", category:"Wraps", price:11.99, img:"https://images.pexels.com/photos/2673352/pexels-photo-2673352.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Grilled chicken, harissa sauce" },
  { id:9, name:"Lobster Hot Dog", category:"Hot Dogs", price:16.99, img:"https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Lobster tail, brioche bun, caviar aioli" },
  { id:10, name:"Gold Milkshake", category:"Drinks", price:10.99, img:"https://images.pexels.com/photos/1126359/pexels-photo-1126359.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Vanilla bean, caramel, edible gold" },
  { id:11, name:"Molten Lava Cake", category:"Desserts", price:11.99, img:"https://images.pexels.com/photos/3026804/pexels-photo-3026804.jpeg?auto=compress&cs=tinysrgb&w=400&h=260&fit=crop", desc:"Warm chocolate lava, vanilla gelato" }
];

// ========== CART FUNCTIONS ==========
let cart = JSON.parse(localStorage.getItem('eliteCart')) || [];

function updateCartUI() {
  const count = cart.reduce((a, i) => a + i.qty, 0);
  const cartCountEl = document.getElementById('cartCount');
  if (cartCountEl) cartCountEl.innerText = count;
  localStorage.setItem('eliteCart', JSON.stringify(cart));
  
  const container = document.getElementById('cartItemsList');
  if (container) {
    if (cart.length === 0) {
      container.innerHTML = "<p style='text-align:center; color:#666;'>Your cart is empty</p>";
    } else {
      container.innerHTML = cart.map(item => `
        <div style="display:flex; justify-content:space-between; margin-bottom:15px; border-bottom:1px solid rgba(212,175,55,0.2); padding:12px 0;">
          <div><strong style="color:#D4AF37;">${item.name}</strong><br>$${item.price}</div>
          <div><button class="qty-btn" data-id="${item.id}" data-delta="-1" style="background:#D4AF37; border:none; width:28px; border-radius:50%; cursor:pointer;">-</button> <span style="margin:0 10px;">${item.qty}</span> <button class="qty-btn" data-id="${item.id}" data-delta="1" style="background:#D4AF37; border:none; width:28px; border-radius:50%; cursor:pointer;">+</button></div>
          <div>$${(item.price * item.qty).toFixed(2)}</div>
        </div>`).join('');
      
      document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.onclick = () => {
          const id = parseInt(btn.dataset.id);
          const delta = parseInt(btn.dataset.delta);
          const idx = cart.findIndex(i => i.id === id);
          if (idx !== -1) {
            cart[idx].qty += delta;
            if (cart[idx].qty <= 0) cart.splice(idx, 1);
            updateCartUI();
          }
        };
      });
    }
    const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
    const cartTotalEl = document.getElementById('cartTotal');
    if (cartTotalEl) cartTotalEl.innerHTML = `Total: $${total.toFixed(2)}`;
  }
}

function addToCart(item) {
  const existing = cart.find(i => i.id === item.id);
  if (existing) existing.qty++;
  else cart.push({ ...item, qty: 1 });
  updateCartUI();
  showToast(`✓ ${item.name} added to cart!`);
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (toast) {
    toast.innerText = msg;
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 2000);
  }
}

function initCart() {
  updateCartUI();
  
  document.getElementById('cartIcon')?.addEventListener('click', () => {
    document.getElementById('cartSidebar')?.classList.add('open');
  });
  
  document.getElementById('closeCartBtn')?.addEventListener('click', () => {
    document.getElementById('cartSidebar')?.classList.remove('open');
  });
  
  document.getElementById('checkoutBtn')?.addEventListener('click', () => {
    if (cart.length === 0) showToast("Cart is empty");
    else { showToast("🎉 Order confirmed! Thank you for choosing KRUNCH ELITE."); cart = []; updateCartUI(); document.getElementById('cartSidebar')?.classList.remove('open'); }
  });
  
  // Add to cart buttons for deals
  document.querySelectorAll('.deal-add').forEach(btn => {
    btn.onclick = () => {
      addToCart({ id: Date.now(), name: btn.dataset.name, price: parseFloat(btn.dataset.price), desc: "Deal", img: "" });
    };
  });
  
  // Add to cart buttons for menu items
  document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.onclick = () => {
      const item = menuItems.find(i => i.id == btn.dataset.id);
      if (item) addToCart(item);
    };
  });
}

// ========== FOOTER ==========
function loadFooter() {
  const footerHtml = `
    <div class="footer-content">
      <div class="footer-col">
        <h3><i class="fas fa-crown"></i> KRUNCH ELITE</h3>
        <p>The pinnacle of fast food luxury. Experience flavors that redefine excellence.</p>
        <div class="social-links" style="margin-top:1rem;">
          <a href="#"><i class="fab fa-instagram"></i></a>
          <a href="#"><i class="fab fa-twitter"></i></a>
          <a href="#"><i class="fab fa-facebook-f"></i></a>
          <a href="#"><i class="fab fa-tiktok"></i></a>
        </div>
      </div>
      <div class="footer-col">
        <h3>Quick Links</h3>
        <p><a href="index.html">🏠 Home</a></p>
        <p><a href="menu.html">🍔 Menu</a></p>
        <p><a href="gallery.html">📸 Gallery</a></p>
        <p><a href="reservation.html">📅 Reservation</a></p>
        <p><a href="contact.html">📞 Contact</a></p>
      </div>
      <div class="footer-col">
        <h3>Working Hours</h3>
        <p>Monday - Friday: 11AM - 2AM</p>
        <p>Saturday - Sunday: 10AM - 3AM</p>
        <p>Delivery: 24/7</p>
      </div>
      <div class="footer-col">
        <h3>Newsletter</h3>
        <p>Get exclusive offers & updates</p>
        <div class="newsletter-input">
          <input type="email" placeholder="Your email" id="newsEmail">
          <button onclick="showToast('Subscribed!')"><i class="fas fa-paper-plane"></i></button>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 2025 KRUNCH ELITE — Where Luxury Meets Flavor. All Rights Reserved.</p>
    </div>
  `;
  const footerElement = document.getElementById('footer');
  if (footerElement) footerElement.innerHTML = footerHtml;
}

// ========== HOME PAGE FUNCTIONS ==========
function loadFeaturedProducts() {
  const featuredGrid = document.getElementById('featuredGrid');
  if (featuredGrid) {
    const featured = menuItems.slice(0, 3);
    featuredGrid.innerHTML = featured.map(i => `
      <div class="menu-item">
        <img src="${i.img}" class="menu-img">
        <div class="menu-info">
          <h3>${i.name}</h3>
          <p style="color:#B0B0B0;">${i.desc}</p>
          <span class="price-tag">$${i.price}</span>
          <button class="order-btn add-to-cart" data-id="${i.id}">Add to Cart</button>
        </div>
      </div>
    `).join('');
    
    // Re-attach cart events
    document.querySelectorAll('.add-to-cart').forEach(btn => {
      btn.onclick = () => {
        const item = menuItems.find(i => i.id == btn.dataset.id);
        if (item) addToCart(item);
      };
    });
  }
}

function initTypingAnimation() {
  const typedStrings = ["🔥 Flame-Grilled Perfection", "🍔 100% Wagyu Beef", "🍕 Artisan Italian Pizza", "🍟 Gourmet Truffle Fries", "🥤 Premium Milkshakes"];
  let typedIndex = 0;
  const typedOutput = document.getElementById('typedOutput');
  
  if (!typedOutput) return;
  
  function typeWriter() {
    let i = 0;
    let str = typedStrings[typedIndex % typedStrings.length];
    typedOutput.innerText = '';
    function type() {
      if (i < str.length) {
        typedOutput.innerText += str.charAt(i);
        i++;
        setTimeout(type, 70);
      } else {
        setTimeout(() => { typedIndex++; typeWriter(); }, 2000);
      }
    }
    type();
  }
  typeWriter();
}

// ========== MENU PAGE FUNCTIONS ==========
function loadFullMenu() {
  const menuContainer = document.getElementById('menuContainer');
  if (!menuContainer) return;
  
  const cats = ["Burgers", "Crispy Chicken", "Pizza", "Fries", "Shawarma", "Sandwiches", "Wraps", "Hot Dogs", "Drinks", "Desserts"];
  let html = '';
  
  cats.forEach(cat => {
    const items = menuItems.filter(i => i.category === cat);
    if (items.length) {
      html += `<h3 style="color:#D4AF37; font-size:1.8rem; margin:2rem 0 1rem;">${cat}</h3><div class="menu-grid">`;
      items.forEach(item => {
        html += `
          <div class="menu-item">
            <img src="${item.img}" class="menu-img" alt="${item.name}">
            <div class="menu-info">
              <h3>${item.name}</h3>
              <p style="color:#B0B0B0; font-size:0.9rem; margin:8px 0;">${item.desc}</p>
              <span class="price-tag">$${item.price}</span>
              <button class="order-btn add-to-cart" data-id="${item.id}">Add to Cart</button>
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }
  });
  
  menuContainer.innerHTML = html;
  
  // Re-attach cart events
  document.querySelectorAll('.add-to-cart').forEach(btn => {
    btn.onclick = () => {
      const item = menuItems.find(i => i.id == btn.dataset.id);
      if (item) addToCart(item);
    };
  });
}

// ========== GALLERY PAGE FUNCTIONS ==========
function loadGallery() {
  const galleryGrid = document.getElementById('galleryGrid');
  if (!galleryGrid) return;
  
  const galleryImgs = [
    "https://images.pexels.com/photos/2983101/pexels-photo-2983101.jpeg", "https://images.pexels.com/photos/825661/pexels-photo-825661.jpeg", "https://images.pexels.com/photos/1633578/pexels-photo-1633578.jpeg", "https://images.pexels.com/photos/6065572/pexels-photo-6065572.jpeg", "https://images.pexels.com/photos/1583884/pexels-photo-1583884.jpeg", "https://images.pexels.com/photos/1126359/pexels-photo-1126359.jpeg", "https://images.pexels.com/photos/6287764/pexels-photo-6287764.jpeg", "https://images.pexels.com/photos/1600711/pexels-photo-1600711.jpeg", "https://images.pexels.com/photos/2673352/pexels-photo-2673352.jpeg", "https://images.pexels.com/photos/3026804/pexels-photo-3026804.jpeg", "https://images.pexels.com/photos/1639562/pexels-photo-1639562.jpeg", "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg"
  ];
  
  let html = '';
  for (let i = 0; i < 40; i++) {
    let img = galleryImgs[i % galleryImgs.length] + `?auto=compress&cs=tinysrgb&w=350&h=450&fit=crop`;
    html += `<div class="masonry-item"><img src="${img}" class="gallery-img" data-src="${img}"></div>`;
  }
  galleryGrid.innerHTML = html;
  
  // Lightbox functionality
  document.querySelectorAll('.gallery-img').forEach(img => {
    img.onclick = () => {
      const lightbox = document.getElementById('lightbox');
      const lightboxImg = document.getElementById('lightboxImg');
      if (lightbox && lightboxImg) {
        lightboxImg.src = img.dataset.src || img.src;
        lightbox.style.visibility = 'visible';
      }
    };
  });
  
  const lightbox = document.getElementById('lightbox');
  const closeLightbox = document.querySelector('.close-lightbox');
  if (lightbox && closeLightbox) {
    lightbox.onclick = () => lightbox.style.visibility = 'hidden';
    closeLightbox.onclick = () => lightbox.style.visibility = 'hidden';
  }
}

// ========== RESERVATION PAGE FUNCTIONS ==========
function initReservationForm() {
  const form = document.getElementById('reservationForm');
  if (!form) return;
  
  form.onsubmit = (e) => {
    e.preventDefault();
    const name = document.getElementById('resName')?.value || '';
    const date = document.getElementById('resDate')?.value || '';
    const time = document.getElementById('resTime')?.value || '';
    const guests = document.getElementById('resGuests')?.value || '';
    
    const msgEl = document.getElementById('reserveMsg');
    if (msgEl) {
      msgEl.innerHTML = `✓ Thank you ${name}! Your table for ${guests} on ${date} at ${time} is confirmed. We'll contact you shortly.`;
      msgEl.style.color = '#D4AF37';
    }
    form.reset();
    showToast("Reservation confirmed!");
  };
}

// ========== CONTACT PAGE FUNCTIONS ==========
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  
  form.onsubmit = (e) => {
    e.preventDefault();
    const name = document.getElementById('contactName')?.value || '';
    showToast(`Thank you ${name}! Your message has been sent. We'll reply within 24 hours.`);
    form.reset();
  };
}

// ========== PARTICLE SYSTEM ==========
const canvas = document.getElementById('particleCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let particles = [];
  
  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  
  function createParticles() {
    particles = [];
    for(let i = 0; i < 80; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2 + 1,
        speedX: (Math.random() - 0.5) * 0.5,
        speedY: (Math.random() - 0.5) * 0.3,
        opacity: Math.random() * 0.5 + 0.2
      });
    }
  }
  
  function animateParticles() {
    if(!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.speedX;
      p.y += p.speedY;
      if(p.x < 0) p.x = canvas.width;
      if(p.x > canvas.width) p.x = 0;
      if(p.y < 0) p.y = canvas.height;
      if(p.y > canvas.height) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(212, 175, 55, ${p.opacity})`;
      ctx.fill();
    });
    requestAnimationFrame(animateParticles);
  }
  
  window.addEventListener('resize', () => { resizeCanvas(); createParticles(); });
  resizeCanvas();
  createParticles();
  animateParticles();
}

// ========== CUSTOM CURSOR ==========
const cursorDot = document.querySelector('.cursor-dot');
const cursorOutline = document.querySelector('.cursor-outline');

if (cursorDot && cursorOutline) {
  document.addEventListener('mousemove', (e) => {
    cursorDot.style.transform = `translate(${e.clientX - 3}px, ${e.clientY - 3}px)`;
    cursorOutline.style.transform = `translate(${e.clientX - 22}px, ${e.clientY - 22}px)`;
  });
}

// ========== NAVBAR SCROLL EFFECT ==========
window.addEventListener('scroll', () => {
  const navbar = document.getElementById('navbar');
  if (navbar) {
    if (window.scrollY > 50) navbar.classList.add('scrolled');
    else navbar.classList.remove('scrolled');
  }
});

// ========== LOADER ==========
window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if (loader) {
    setTimeout(() => loader.classList.add('hide'), 1500);
  }
});

// ========== HAMBURGER MENU ==========
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('mobile');
  });
}