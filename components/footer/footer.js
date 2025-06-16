export class Footer {
    constructor() {
      this.createFooter();
    }
  
    createFooter() {
      const footer = document.querySelector("#bottom-content");
  
      const footerContainer = document.createElement("div");
      footerContainer.id = "footerContainer";
  
      // Informações de exemplo
      const infoSections = [
        "Sobre nós", 
        "Termos de Uso", 
        "Política de Privacidade",
        "Suporte ao Cliente"
      ];
  
      infoSections.forEach(section => {
        const info = document.createElement("p");
        info.textContent = section;
        footerContainer.appendChild(info);
      });
  
      footer.appendChild(footerContainer);
      this.addCss("footer");

    }

    addCss(nomeCss) {
        const folhaDeEstilo = document.createElement("link");
        folhaDeEstilo.rel = "stylesheet";
        // Ajuste o caminho conforme a estrutura do seu projeto
        folhaDeEstilo.href = `./components/footer/css/${nomeCss}.css`;
        document.head.appendChild(folhaDeEstilo);
      }

      updateEmotionResult(emotion) {
        const footer = document.querySelector("#footerContainer");
        if (emotion === "Positivo") {
            footer.style.backgroundColor = "#C8E6C9"; // Verde suave
            footer.style.display = "grid";
            footer.style.gridTemplateColumns = "repeat(2, 1fr)"; // Layout em 2 colunas
            footer.style.transition = "background-color 0.5s ease, grid-template-columns 0.5s ease";
        } else {
            footer.style.backgroundColor = "#FFCDD2"; // Vermelho suave
            footer.style.display = "grid";
            footer.style.gridTemplateColumns = "1fr"; // Layout em 1 coluna
            footer.style.transition = "background-color 0.5s ease, grid-template-columns 0.5s ease";
        }
    }
  }