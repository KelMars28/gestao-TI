// Menu mobile toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');

mobileMenuBtn.addEventListener('click', function() {
    this.classList.toggle('active');
    mobileMenu.classList.toggle('show');
});

// Mobile dropdown toggle
const mobileDropdownToggle = document.querySelector('.mobile-dropdown-toggle');

if (mobileDropdownToggle) {
    mobileDropdownToggle.addEventListener('click', function(e) {
        e.preventDefault();
        const dropdownContent = document.querySelector('.mobile-dropdown-content');
        dropdownContent.classList.toggle('show');
    });
}

// Fechar menu mobile ao clicar em um link
const mobileLinks = document.querySelectorAll('.mobile-menu a');
mobileLinks.forEach(link => {
    link.addEventListener('click', function() {
        mobileMenu.classList.remove('show');
        mobileMenuBtn.classList.remove('active');
        
        // Fechar dropdown se estiver aberto
        const dropdownContent = document.querySelector('.mobile-dropdown-content');
        if (dropdownContent && dropdownContent.classList.contains('show')) {
            dropdownContent.classList.remove('show');
        }
    });
});

// Adicionar classe ativa ao link atual baseado na rolagem
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.menu a, .mobile-menu a');
    
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        
        if (pageYOffset >= sectionTop - sectionHeight / 3) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Fechar menu ao redimensionar para desktop
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        mobileMenu.classList.remove('show');
        mobileMenuBtn.classList.remove('active');
        
        // Fechar dropdown mobile
        const dropdownContent = document.querySelector('.mobile-dropdown-content');
        if (dropdownContent && dropdownContent.classList.contains('show')) {
            dropdownContent.classList.remove('show');
        }
    }
});

// Prevenir comportamento padrão dos links de dropdown
const dropdownLinks = document.querySelectorAll('.dropdown > a, .mobile-dropdown > a');
dropdownLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            e.preventDefault();
        }
    });
});

// ... (mantenha todo o seu código anterior aqui) ...

// --- Lógica de Proteção de Alterações ---

let formAlterado = false;

// Função para monitorar mudanças nos campos
// Ela roda automaticamente quando o DOM é carregado
document.addEventListener('DOMContentLoaded', function() {
    const formEdicao = document.getElementById('formEdicao');
    if (formEdicao) {
        formEdicao.addEventListener('input', () => {
            formAlterado = true;
        });
    }
});

// Função chamada pelo botão Sair no HTML
function confirmarSaida() {
    if (formAlterado) {
        return confirm("Você tem alterações não salvas! Se sair agora, perderá o que mudou. Deseja sair assim mesmo?");
    }
    return true; // Se não mudou nada, sai direto
}