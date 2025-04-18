// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize cosmic background animations
    createCosmicBackground();
    
    // Apply fade-in animations to elements with the 'fade-in' class
    document.querySelectorAll('.fade-in').forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('visible');
        }, 100 * index);
    });

    // Add hover effects to navigation links
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.color = 'var(--star-yellow)';
        });
        link.addEventListener('mouseleave', () => {
            link.style.color = 'var(--cosmic-white)';
        });
    });

    // Add subtle animation to buttons on hover
    const buttons = document.querySelectorAll('.cosmic-btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 6px 25px rgba(126, 34, 206, 0.6)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = button.classList.contains('primary') 
                ? '0 4px 20px rgba(126, 34, 206, 0.4)'
                : 'none';
        });
    });

    // Add click animation to buttons
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 100);
        });
    });
});

// Function to create cosmic background elements (shooting stars, space dust)
function createCosmicBackground() {
    const universe = document.querySelector('.universe-background');
    if (!universe) return;

    // Create shooting stars
    for (let i = 0; i < 50; i++) {
        const star = document.createElement('div');
        star.className = 'shooting-star';
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDuration = `${Math.random() * 3 + 1}s`;
        star.style.animationDelay = `${Math.random() * 5}s`;
        universe.appendChild(star);
    }

    // Create space dust particles
    for (let i = 0; i < 100; i++) {
        const dust = document.createElement('div');
        dust.className = 'space-dust';
        dust.style.left = `${Math.random() * 100}%`;
        dust.style.top = `${Math.random() * 100}%`;
        dust.style.width = `${Math.random() * 2 + 1}px`;
        dust.style.height = dust.style.width;
        dust.style.opacity = Math.random() * 0.5 + 0.2;
        dust.style.animation = `twinkle-star ${Math.random() * 5 + 2}s infinite alternate`;
        universe.appendChild(dust);
    }
}

// Function to initialize planet animations on the homepage
function initializePlanetAnimations() {
    const planets = document.querySelectorAll('.planet');
    planets.forEach(planet => {
        // Add a subtle rotation animation
        planet.style.animation = 'rotate-planet 60s linear infinite';
    });
}

// Call planet animations for specific pages
if (document.querySelector('.cosmic-hero')) {
    initializePlanetAnimations();
}

// Add smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add date range validation
document.addEventListener('DOMContentLoaded', function() {
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');
    const taskForm = document.querySelector('.cosmic-form');

    // Set minimum date as today
    const today = new Date().toISOString().split('T')[0];
    startDate.min = today;
    endDate.min = today;

    // Update end date minimum when start date changes
    startDate.addEventListener('change', function() {
        endDate.min = this.value;
        if (endDate.value && endDate.value < this.value) {
            endDate.value = this.value;
        }
    });

    // Form validation
    taskForm.addEventListener('submit', function(e) {
        const start = new Date(startDate.value);
        const end = new Date(endDate.value);

        if (end < start) {
            e.preventDefault();
            alert('End date cannot be before start date');
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Edit task functionality
    const editModal = document.getElementById('edit-task-modal');
    const editButtons = document.querySelectorAll('.edit-task-btn');
    const editCloseBtn = editModal.querySelector('.close-modal');
    
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const taskCard = this.closest('.task-card');
            
            // Populate edit form
            document.getElementById('edit_task_id').value = taskId;
            document.getElementById('edit_title').value = taskCard.querySelector('h4').textContent;
            document.getElementById('edit_description').value = taskCard.querySelector('p').textContent;
            
            const tags = Array.from(taskCard.querySelectorAll('.tag'))
                .map(tag => tag.textContent)
                .join(', ');
            document.getElementById('edit_tags').value = tags;
            
            // Show modal
            editModal.style.display = 'block';
        });
    });
    
    // Close edit modal
    editCloseBtn.addEventListener('click', function() {
        editModal.style.display = 'none';
    });
    
    // Close on outside click
    window.addEventListener('click', function(event) {
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    });
});