const darkModeToggle = document.getElementById('darkModeToggle');

// 1. Ao carregar a página, verifica se o usuário já havia ativado o Modo Escuro antes
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
    if(darkModeToggle) darkModeToggle.checked = true;
}

// 2. Escuta o clique do botão switch liga/desliga
if (darkModeToggle) {
    darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark'); // Salva a escolha como escura
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light'); // Salva a escolha como clara
        }
    });
}