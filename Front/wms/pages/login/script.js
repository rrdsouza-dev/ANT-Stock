const formulario = document.getElementById('loginForm');
const mensagem = document.getElementById('mensagem');

formulario.addEventListener('submit', function(evento) {
    evento.preventDefault(); // Evita que a página recarregue ao enviar

    const email = document.getElementById('email').value;
    const senha = document.getElementById('password').value;

    // Exemplo básico de validação no navegador
    if (email === "usuario@exemplo.com" && senha === "123456") {
        mensagem.style.color = "green";
        mensagem.textContent = "Login realizado com sucesso!";
        
        // Exemplo de redirecionamento:
        // window.location.href = "pagina-inicial.html";
    } else {
        mensagem.style.color = "red";
        mensagem.textContent = "E-mail ou senha incorretos!";
    }
});
