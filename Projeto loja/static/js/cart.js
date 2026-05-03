document.addEventListener('DOMContentLoaded', () => {
    const buyButton = document.querySelector('.btn-add-cart');
    
    if (buyButton) {
        buyButton.addEventListener('click', () => {
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