export class LeftMenu {
  constructor() {
    this.createMenu();
    this.addCss("leftMenu");
    this.currentNegativeStyleIndex = 0;
  }

  createMenu() {
    const leftContent = document.querySelector("#left-content");

    const menuContainer = document.createElement("div");
    menuContainer.id = "leftMenuContainer";

    // Título do menu
    const title = document.createElement("h3");
    title.textContent = "Classificar";
    title.id = "leftMenuTitle";
    menuContainer.appendChild(title);

    // Filtros de classificação
    const filters = [
      { name: "Preço", key: "price" },
      { name: "Popularidade", key: "popularity" },
      { name: "Relevância", key: "relevance" },
      { name: "Novidades", key: "new" }
    ];

    const filterContainer = document.createElement("div");
    filterContainer.id = "filterContainer";

    filters.forEach((filter) => {
      const filterButton = document.createElement("button");
      filterButton.textContent = `Classificar por: ${filter.name}`;
      filterButton.className = "filterButton";
      filterContainer.appendChild(filterButton);

      filterButton.addEventListener("click", () => {
        const customEvent = new CustomEvent("filterBy", { detail: filter.key });
        document.dispatchEvent(customEvent);
      });
    });

    menuContainer.appendChild(filterContainer);
    leftContent.appendChild(menuContainer);
  }

  updateEmotionResult(emotion) {
    const menuContainer = document.querySelector("#leftMenuContainer");
    const title = document.querySelector("#leftMenuTitle");
    const filterContainer = document.querySelector("#filterContainer");
    const buttons = document.querySelectorAll(".filterButton");

    const negativeStyles = [
      {
        container: { display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "15px", backgroundColor: "#FFCDD2", borderRadius: "10px", boxShadow: "0 4px 8px rgba(244, 67, 54, 0.3)", padding: "10px", transition: "all 0.5s ease-in-out" },
        title: { fontSize: "20px", color: "#FF1744", letterSpacing: "1px", transition: "all 0.5s ease-in-out" },
        button: { backgroundColor: "#FFEBEE", color: "#FF1744", borderRadius: "5px", transition: "all 0.5s ease-in-out" }
      },
      {
        container: { display: "flex", flexDirection: "column", alignItems: "center", gap: "10px", backgroundColor: "#F8BBD0", borderRadius: "15px", boxShadow: "0 6px 10px rgba(233, 30, 99, 0.3)", padding: "15px", transition: "all 0.5s ease-in-out" },
        title: { fontSize: "22px", color: "#E91E63", letterSpacing: "1.5px", transition: "all 0.5s ease-in-out" },
        button: { backgroundColor: "#FCE4EC", color: "#E91E63", borderRadius: "10px", transition: "all 0.5s ease-in-out" }
      },
      {
        container: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "20px", backgroundColor: "#E1BEE7", borderRadius: "20px", boxShadow: "0 8px 12px rgba(156, 39, 176, 0.3)", padding: "12px", transition: "all 0.5s ease-in-out" },
        title: { fontSize: "24px", color: "#9C27B0", letterSpacing: "2px", transition: "all 0.5s ease-in-out" },
        button: { backgroundColor: "#EDE7F6", color: "#9C27B0", borderRadius: "8px", transition: "all 0.5s ease-in-out" }
      },
      {
        container: { display: "flex", flexWrap: "wrap", justifyContent: "space-evenly", gap: "12px", backgroundColor: "#BBDEFB", borderRadius: "25px", boxShadow: "0 10px 14px rgba(33, 150, 243, 0.3)", padding: "18px", transition: "all 0.5s ease-in-out" },
        title: { fontSize: "26px", color: "#2196F3", letterSpacing: "2.5px", transition: "all 0.5s ease-in-out" },
        button: { backgroundColor: "#E3F2FD", color: "#2196F3", borderRadius: "12px", transition: "all 0.5s ease-in-out" }
      }
    ];

    if (emotion === "Positivo") {
      
    } else {
      const style = negativeStyles[this.currentNegativeStyleIndex];

      Object.assign(menuContainer.style, style.container);
      Object.assign(title.style, style.title);

      buttons.forEach((button) => {
        Object.assign(button.style, style.button);
      });

      this.currentNegativeStyleIndex = (this.currentNegativeStyleIndex + 1) % negativeStyles.length;
    }
  }

  addCss(nomeCss) {
    const folhaDeEstilo = document.createElement("link");
    folhaDeEstilo.rel = "stylesheet";
    folhaDeEstilo.href = `./components/leftMenu/css/${nomeCss}.css`;
    document.head.appendChild(folhaDeEstilo);
  }
}