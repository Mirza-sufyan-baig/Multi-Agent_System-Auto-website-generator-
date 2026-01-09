// Update brand name
document.title = "Cozy Cup";

// Add event listeners to navigation links
const navLinks = document.querySelectorAll('nav a');
navLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = link.textContent.toLowerCase();
        const section = document.querySelector(`#${sectionId}`);
        section.scrollIntoView({ behavior: 'smooth' });
    });
});

// Add event listener to hero section button
const heroButton = document.querySelector('.hero-section button');
heroButton.addEventListener('click', () => {
    const storySection = document.querySelector('#story');
    storySection.scrollIntoView({ behavior: 'smooth' });
});

// Add event listener to story section button
const storyButton = document.querySelector('.story-section button');
storyButton.addEventListener('click', () => {
    const locationSection = document.querySelector('#location');
    locationSection.scrollIntoView({ behavior: 'smooth' });
});

// Add event listener to location section button
const locationButton = document.querySelector('.location-section button');
locationButton.addEventListener('click', () => {
    // Open Google Maps or provide directions
    alert('Directions will be provided here');
});

// Initialize icons
// No icons are used in this script, but it's good practice to include this line
// lucide.createIcons();