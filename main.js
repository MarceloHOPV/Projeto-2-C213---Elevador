import { MainMenu } from "./components/mainMenu/mainMenu.js";
import { RightContent } from "./components/rightContent/rightContent.js";
import { LeftMenu } from "./components/leftMenu/leftMenu.js";
import { Footer } from "./components/footer/footer.js";

let isCapturing = false; // Variável global para controle da captura

document.addEventListener('DOMContentLoaded', () => {
    const mainMenu = new MainMenu();
    const rightContent = new RightContent();
    const leftMenu = new LeftMenu();
    const footer = new Footer();

    const capturePhotos = (quantity, callback) => {
        if (isCapturing) {
            console.warn("Já existe uma captura de fotos em andamento. Aguarde o retorno da API.");
            return;
        }

        isCapturing = true; // Marca que a captura está ativa
        const photoBase64Array = [];

        navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                const videoElement = document.createElement('video');
                videoElement.srcObject = stream;
                videoElement.play();

                videoElement.onloadedmetadata = () => {
                    const canvas = document.createElement('canvas');
                    const context = canvas.getContext('2d');
                    let photoCount = 0;

                    const capturePhoto = () => {
                        if (photoCount < quantity) {
                            canvas.width = videoElement.videoWidth;
                            canvas.height = videoElement.videoHeight;
                            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

                            const photoBase64 = canvas.toDataURL('image/png').split(',')[1];
                            photoBase64Array.push(photoBase64);

                            photoCount++;
                            setTimeout(capturePhoto, 500);
                        } else {
                            stream.getTracks().forEach((track) => track.stop());

                            sendToAPI(photoBase64Array).then((data) => {
                                isCapturing = false; // Libera para nova captura
                                if (data) {
                                    console.log(`Resultado final da API: ${data.dominant_emotion}`);
                                    if (callback) callback(data.dominant_emotion);
                                }
                            }).catch(() => {
                                isCapturing = false; // Libera em caso de erro
                            });
                        }
                    };

                    capturePhoto();
                };
            })
            .catch((error) => {
                isCapturing = false; // Libera para nova captura em caso de erro
                console.error("Erro ao acessar a câmera:", error);
            });
    };

    const sendToAPI = (base64ImagesArray) => {
        const url = "http://127.0.0.1:5000/api/analyze_emotion";

        const payload = {
            images: base64ImagesArray,
            fileNamePrefix: `foto_${Date.now()}`
        };

        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.ok ? response.json() : null)
        .catch(error => {
            console.error("Erro ao enviar as imagens ou processar resposta:", error);
            return null;
        });
    };

    document.addEventListener('click', (event) => {
        const clickedElement = event.target;
        const parentSection = clickedElement.closest('section');

        if (parentSection) {
            const sectionId = parentSection.id;
            console.log(`Interagindo com: ${sectionId}`);

            capturePhotos(10, (finalEmotion) => {
                console.log(`Emoção na seção ${sectionId}: ${finalEmotion}`);

                document.getElementById('emotion-content').innerHTML = `
                    <p>Emoção detectada: ${finalEmotion}</p>
                `

                if (sectionId === 'top-content') {
                    mainMenu.updateEmotionResult(finalEmotion);
                } else if (sectionId === 'right-content') {
                    rightContent.updateEmotionResult(finalEmotion);
                } else if (sectionId === 'left-content') {
                    leftMenu.updateEmotionResult(finalEmotion);
                } else if (sectionId === 'bottom-content') {
                    footer.updateEmotionResult(finalEmotion);
                }
            });
        }
    });
});