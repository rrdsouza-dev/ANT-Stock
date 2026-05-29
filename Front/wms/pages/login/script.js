const formulario = document.getElementById('loginForm');
const mensagem = document.getElementById('mensagem');

formulario.addEventListener('submit', function (evento) {
    evento.preventDefault(); // Evita que a página recarregue ao enviar

    const email = document.getElementById('email').value;
    const senha = document.getElementById('password').value;

    // Exemplo básico de validação no navegador
    if (email === "usuario@exemplo.com" && senha === "123456") {
        mensagem.style.color = "green";
        mensagem.textContent = "Login realizado com sucesso!";

        // Exemplo de redirecionamento:
        window.location.href = "/Front/wms/pages/home/index.html";
    } else {
        mensagem.style.color = "red";
        mensagem.textContent = "E-mail ou senha incorretos!";
    }
});

function login(){
    location.reload();
}

let contas = []
let divConta = document.getElementById('newAccount')

function createAccount() {
    divConta.innerHTML = `
    <div>
        <h2>criar uma nova conta</h2>
                <form id="loginForm">
                    <div class="input-group">
                        <label for="text">Nome de usúario</label>
                        <input type="text" id="nameUser" required>
                    </div>
                    <div class="input-group">
                        <label for="email">E-mail</label>
                        <input type="email" id="email" required>
                    </div>
                    <div class="input-group">
                        <label for="password">Senha</label>
                        <input type="password" id="password" required>
                    </div>
                    <button type="submit">Entrar</button>
                    <button onClick="login()">Login</button>
                    <p id="mensagem"></p>
    </div>
    `

}

