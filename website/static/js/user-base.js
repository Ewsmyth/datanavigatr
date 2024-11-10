const sidebar = document.getElementById('sidebar');
const resizeHandle = document.getElementById('resize-handle');
const mainContent = document.getElementById('main-content');

let isResizing = false;

// When the mouse is pressed down on the resize handle
resizeHandle.addEventListener('mousedown', function (e) {
    isResizing = true;
    document.body.style.cursor = 'ew-resize';
});

// When the mouse moves
window.addEventListener('mousemove', function (e) {
    if (!isResizing) return;

    const newWidth = e.clientX;

    // Set the new width, with a minimum and maximum width
    if (newWidth > 70 && newWidth < 500) {
        sidebar.style.width = newWidth + 'px';
        mainContent.style.marginLeft = newWidth + 'px';
    }
});

// When the mouse is released
window.addEventListener('mouseup', function () {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = 'default';
    }
});