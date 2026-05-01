// Exemplo: Alerta simples ao adicionar ao carrinho
document.addEventListener('DOMContentLoaded', () => {
    const buyButton = document.querySelector('.btn-add-cart');
    
    if (buyButton) {
        buyButton.addEventListener('click', () => {
            // Verifica se um tamanho foi selecionado antes de enviar
            const sizes = document.getElementsByName('size');
            let selected = false;
            for (const size of sizes) {
                if (size.checked) {
                    selected = true;
                    break;
                }
            }
            
            if (!selected) {
                alert("Por favor, selecione um tamanho antes de comprar!");
            }
        });
    }
});