export class RightContent {
  constructor() {
    this.categories = ["Eletrônicos", "Vestuário", "Livros", "Esportes", "Casa"];
    this.products = this.generateRandomProducts(20);
    this.filteredProducts = [...this.products];
    this.createContent();
    this.setupListeners();
    this.currentNegativeStyleIndex = 0;
  }

  generateRandomProducts(quantity) {
    const randomProducts = [];
    for (let i = 0; i < quantity; i++) {
      const category = this.categories[Math.floor(Math.random() * this.categories.length)];
      const price = (Math.random() * 100).toFixed(2);
      const popularity = Math.floor(Math.random() * 100);
      const name = `Produto ${i + 1}`;
      randomProducts.push({ name, category, price, popularity });
    }
    return randomProducts;
  }

  createContent() {
    const rightContent = document.querySelector("#right-content");

    // Container principal
    const contentWrapper = document.createElement("div");
    contentWrapper.id = "rightContentWrapper";
    rightContent.appendChild(contentWrapper);

    // Mantendo o carrossel original
    const carousel = document.createElement("div");
    carousel.id = "carouselContainer";

    this.promoImages = ["promo1.jpg", "promo2.jpg", "promo3.jpg"];
    this.currentIndex = 0;

    this.promoImages.forEach((image, index) => {
      const img = document.createElement("img");
      img.src = `./components/rightContent/images/${image}`;
      img.alt = `Promoção ${index + 1}`;
      img.className = index === 0 ? "active" : "";
      carousel.appendChild(img);
    });

    contentWrapper.appendChild(carousel);

    // Container dos produtos
    const productContainer = document.createElement("div");
    productContainer.id = "productContainer";
    contentWrapper.appendChild(productContainer);

    // Lista de produtos com scroll ativo quando necessário
    this.productList = document.createElement("div");
    this.productList.id = "productList";
    productContainer.appendChild(this.productList);

    this.updateProductList();
    this.addCss("rightContent");

    this.startCarousel();
  }

  startCarousel() {
    const carouselImages = document.querySelectorAll("#carouselContainer img");
    setInterval(() => {
      carouselImages.forEach((img) => img.classList.remove("active"));
      this.currentIndex = (this.currentIndex + 1) % this.promoImages.length;
      carouselImages[this.currentIndex].classList.add("active");
    }, 3000);
  }

  setupListeners() {
    document.addEventListener("filterCategory", (event) => {
      const category = event.detail;
      this.filteredProducts = this.products.filter((product) => product.category === category);
      this.updateProductList();
    });

    document.addEventListener("filterBy", (event) => {
      const key = event.detail;
      this.filteredProducts.sort((a, b) => a[key] - b[key]);
      this.updateProductList();
    });

    document.addEventListener("searchQuery", (event) => {
      const query = event.detail;
      this.filteredProducts = this.products.filter((product) => product.name.toLowerCase().includes(query));
      this.updateProductList();
    });
  }

  updateProductList() {
    this.productList.innerHTML = "";

    this.filteredProducts.forEach((product) => {
      const productItem = document.createElement("div");
      productItem.className = "productItem";
      productItem.innerHTML = `
        <div class="productBox">
          <h3>${product.name}</h3>
          <p>Categoria: ${product.category}</p>
          <p>Preço: R$${product.price}</p>
          <p>Popularidade: ${product.popularity}</p>
        </div>
      `;
      this.productList.appendChild(productItem);
    });
  }

  updateEmotionResult(emotion) {
    const contentWrapper = document.getElementById("rightContentWrapper");
    const carouselContainer = document.getElementById("carouselContainer");
    const productContainer = document.getElementById("productContainer");
    const productItems = document.querySelectorAll(".productBox");

    const negativeStyles = [
      {
        container: { backgroundColor: "#FFCDD2", transition: "all 0.5s ease-in-out" },
        carousel: { boxShadow: "0 4px 8px rgba(244, 67, 54, 0.3)" },
        productContainer: { overflowY: "auto", maxHeight: "400px", backgroundColor: "#FFEBEE" },
        productItem: { borderRadius: "8px", boxShadow: "0 4px 6px rgba(244, 67, 54, 0.3)" }
      }
    ];

    if (emotion === "Positivo") {
      contentWrapper.style.backgroundColor = "#E8F5E9";
    } else {
      const style = negativeStyles[this.currentNegativeStyleIndex];

      Object.assign(contentWrapper.style, style.container);
      Object.assign(carouselContainer.style, style.carousel);
      Object.assign(productContainer.style, style.productContainer);
      productItems.forEach((item) => Object.assign(item.style, style.productItem));

      this.currentNegativeStyleIndex = (this.currentNegativeStyleIndex + 1) % negativeStyles.length;
    }
  }

  addCss(nomeCss) {
    const folhaDeEstilo = document.createElement("link");
    folhaDeEstilo.rel = "stylesheet";
    folhaDeEstilo.href = `./components/rightContent/css/${nomeCss}.css`;
    document.head.appendChild(folhaDeEstilo);
  }
}