const openPopupButton = document.getElementById('open-popup-button');
const closePopupButton = document.getElementById('close-popup-button');
const signupPopup = document.getElementById('signup-popup');

openPopupButton.addEventListener('click', () => {
    signupPopup.style.display = 'block';
});

closePopupButton.addEventListener('click', () => {
    signupPopup.style.display = 'none';
});
