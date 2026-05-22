function login() {
    let userInputElement = document.getElementById('user');
    let username = userInputElement.value; // Pega o texto digitado

    if (username.trim() !== "") {
        // Salva o nome no navegador
        localStorage.setItem('usuarioLogado', username);
        
        // Redireciona para a página do painel (ajuste o caminho se necessário)
        window.location.href = "index.html"; 
    } else {
        alert("Por favor, digite um email/usuário.");
    }
}

// Executa assim que a página carrega
window.onload = function() {
    let nomeUserElement = document.getElementById('nomeUser');
    
    // Recupera o nome salvo
    let usuarioSalvo = localStorage.getItem('usuarioLogado');

    if (usuarioSalvo) {
        nomeUserElement.innerHTML = `Olá, ${usuarioSalvo}`;
    } else {
        // Caso o usuário acesse a página sem fazer login antes
        nomeUserElement.innerHTML = `Olá, Visitante`;
    }
}