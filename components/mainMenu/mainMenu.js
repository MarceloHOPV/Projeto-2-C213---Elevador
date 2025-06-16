export class MainMenu {
  constructor() {
    this.createMenu();
    this.addCss("mainMenu");
    this.menuOpen = false;
    this.currentNegativeStyleIndex = 0;
  }

  createMenu() {
    const container = document.querySelector("#top-content");
    const wrapper = document.createElement("div");
    wrapper.id = "menuWrapper";

    // Barra superior com título e botão
    const topBar = document.createElement("div");
    topBar.id = "topBar";

    const siteTitle = document.createElement("h1");
    siteTitle.textContent = "Meu Site";
    siteTitle.id = "siteTitle";
    topBar.appendChild(siteTitle);

    wrapper.appendChild(topBar);

    // Menu lateral
    const menuContainer = document.createElement("div");
    menuContainer.id = "menuContainer";
    menuContainer.classList.add("closed");
    wrapper.appendChild(menuContainer);

    // Botão de abrir/fechar
    const toggleButton = document.createElement("button");
    toggleButton.textContent = "☰ Menu";
    toggleButton.id = "menuToggle";
    toggleButton.addEventListener("click", () => this.toggleMenu());
    menuContainer.appendChild(toggleButton);

    // Container dos itens do menu
    const menuContent = document.createElement("div");
    menuContent.id = "menuContent";
    menuContainer.appendChild(menuContent);

    // Título do menu
    const title = document.createElement("h2");
    title.textContent = "Explore Categorias";
    title.id = "menuTitle";
    menuContent.appendChild(title);

    // Container dos cartões de categorias
    const cardContainer = document.createElement("div");
    cardContainer.id = "cardContainer";

    const categories = [
      { name: "Eletrônicos", icon: "💻" },
      { name: "Vestuário", icon: "👗" },
      { name: "Livros", icon: "📚" },
      { name: "Esportes", icon: "⚽" },
      { name: "Casa", icon: "🏠" },
    ];

    categories.forEach((category) => {
      const card = document.createElement("div");
      card.className = "categoryCard";

      const icon = document.createElement("span");
      icon.className = "categoryIcon";
      icon.textContent = category.icon;
      card.appendChild(icon);

      const categoryName = document.createElement("p");
      categoryName.className = "categoryName";
      categoryName.textContent = category.name;
      card.appendChild(categoryName);

      // **Adiciona evento de filtragem**
      card.addEventListener("click", () => {
        const customEvent = new CustomEvent("filterCategory", { detail: category.name });
        document.dispatchEvent(customEvent);
      });

      cardContainer.appendChild(card);
    });

    menuContent.appendChild(cardContainer);
    container.appendChild(wrapper);
  }

  toggleMenu() {
    const menuContainer = document.getElementById("menuContainer");
    const menuContent = document.getElementById("menuContent");
    this.menuOpen = !this.menuOpen;

    if (this.menuOpen) {
      menuContainer.classList.remove("closed");
      menuContainer.classList.add("open");
      menuContent.style.display = "block";
    } else {
      menuContainer.classList.remove("open");
      menuContainer.classList.add("closed");
      menuContent.style.display = "none";
    }
  }

  updateEmotionResult(emotion) {
    const cardContainer = document.getElementById("cardContainer");
    const title = document.getElementById("menuTitle");
    const cards = document.querySelectorAll(".categoryCard");

    const negativeStyles = [
      { container: { display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "15px", backgroundColor: "#FFCDD2", borderRadius: "10px", transition: "all 0.5s ease-in-out" }, title: { fontSize: "20px", color: "#FF1744", transition: "all 0.5s ease-in-out" }, card: { backgroundColor: "#FFEBEE", borderRadius: "5px", transition: "all 0.5s ease-in-out" }},
      { container: { display: "flex", flexDirection: "column", alignItems: "center", backgroundColor: "#F8BBD0", borderRadius: "15px", transition: "all 0.5s ease-in-out" }, title: { fontSize: "22px", color: "#E91E63", transition: "all 0.5s ease-in-out" }, card: { backgroundColor: "#FCE4EC", borderRadius: "10px", transition: "all 0.5s ease-in-out" }},
      { container: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "20px", backgroundColor: "#E1BEE7", borderRadius: "20px", transition: "all 0.5s ease-in-out" }, title: { fontSize: "24px", color: "#9C27B0", transition: "all 0.5s ease-in-out" }, card: { backgroundColor: "#EDE7F6", borderRadius: "10px", transition: "all 0.5s ease-in-out" }},
      { container: { display: "flex", flexWrap: "wrap", justifyContent: "space-evenly", backgroundColor: "#BBDEFB", borderRadius: "25px", transition: "all 0.5s ease-in-out" }, title: { fontSize: "26px", color: "#2196F3", transition: "all 0.5s ease-in-out" }, card: { backgroundColor: "#E3F2FD", borderRadius: "15px", transition: "all 0.5s ease-in-out" }}
    ];

    if (emotion !== "Positivo") {
      const style = negativeStyles[this.currentNegativeStyleIndex];
      Object.assign(cardContainer.style, style.container);
      Object.assign(title.style, style.title);

      cards.forEach((card) => {
        Object.assign(card.style, style.card);
      });

      this.currentNegativeStyleIndex = (this.currentNegativeStyleIndex + 1) % negativeStyles.length;
    }
  }

  addCss(nomeCss) {
    const folhaDeEstilo = document.createElement("link");
    folhaDeEstilo.rel = "stylesheet";
    folhaDeEstilo.href = `./components/mainMenu/css/${nomeCss}.css`;
    document.head.appendChild(folhaDeEstilo);
  }
}