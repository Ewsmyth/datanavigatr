// Dropdown toggle functionality
const dropdownToggle = document.getElementById('dropdown-toggle');
const dropdownMenu = document.getElementById('dropdown-menu');

dropdownToggle.addEventListener('click', function () {
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
});

window.addEventListener('click', function (e) {
    if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
        dropdownMenu.style.display = 'none';
    }
});

// Popup logic for each dropdown item

const newQueryPopup = document.getElementById('new-query-popup');
const newQueryBtn = document.getElementById('new-query-btn');
const newQueryClose = document.getElementById('new-query-close');

newQueryBtn.addEventListener('click', function () {
    newQueryPopup.style.display = 'flex';
});

newQueryClose.addEventListener('click', function () {
    newQueryPopup.style.display = 'none';
});

const newMissionPopup = document.getElementById('new-mission-popup');
const newMissionBtn = document.getElementById('new-mission-btn');
const newMissionClose = document.getElementById('new-mission-close');

newMissionBtn.addEventListener('click', function () {
    newMissionPopup.style.display = 'flex';
});

newMissionClose.addEventListener('click', function () {
    newMissionPopup.style.display = 'none';
});

const settingsPopup = document.getElementById('settings-popup');
const settingsBtn = document.getElementById('settings-btn');
const settingsClose = document.getElementById('settings-close');

settingsBtn.addEventListener('click', function () {
    settingsPopup.style.display = 'flex';
});

settingsClose.addEventListener('click', function () {
    settingsPopup.style.display = 'none';
});

// Close the popup if clicked outside the popup content
window.addEventListener('click', function (e) {
    if (e.target === newQueryPopup) {
        newQueryPopup.style.display = 'none';
    }
    if (e.target === newMissionPopup) {
        newMissionPopup.style.display = 'none';
    }
    if (e.target === settingsPopup) {
        settingsPopup.style.display = 'none';
    }
});
