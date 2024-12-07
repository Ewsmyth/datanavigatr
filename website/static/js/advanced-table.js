let pageSize = 100000;
let currentPage = 1;

// Pagination function
document.getElementById('page-size').addEventListener('change', function () {
    if (this.value === 'all') {
        pageSize = document.getElementById('dynamic-table').tBodies[0].rows.length;
    } else {
        pageSize = parseInt(this.value);
    }
    currentPage = 1;
    paginateTable();
});

function paginateTable() {
    const table = document.getElementById('dynamic-table').tBodies[0];
    const rows = Array.from(table.rows);

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;

    rows.forEach((row, index) => {
        row.style.display = index >= start && index < end ? '' : 'none';
    });
}

paginateTable();

function exportTableToZip() {
    console.log("Export function triggered.");

    const table = document.getElementById("dynamic-table");
    if (!table) {
        console.error("Table element not found!");
        return;
    }

    const headers = Array.from(table.querySelectorAll("thead th h4")).map(
        (header) => header.textContent.trim()
    );
    console.log("Extracted headers:", headers);

    const rows = Array.from(table.querySelectorAll("tbody tr")).map((row) => {
        const cells = row.querySelectorAll("td");
        const rowData = {};
        cells.forEach((cell, index) => {
            const header = headers[index];
            if (cell.querySelector("img")) {
                // Extract image filenames
                const filenames = Array.from(cell.querySelectorAll("img")).map((img) =>
                    img.src.split("/").pop()
                );
                rowData[header] = filenames;
                console.log(`Extracted filenames for header '${header}':`, filenames);
            } else {
                rowData[header] = cell.textContent.trim();
                console.log(`Extracted text for header '${header}':`, rowData[header]);
            }
        });
        return rowData;
    });

    console.log("Final table data to send:", { headers, rows });

    // Send data to the backend for ZIP file generation
    fetch("/export-zip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ headers, rows }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            console.log("Backend responded successfully.");
            return response.blob();
        })
        .then((blob) => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "export.zip";
            a.click();
            window.URL.revokeObjectURL(url);
            console.log("ZIP file download initiated.");
        })
        .catch((error) => {
            console.error("Error exporting table:", error);
        });
}

// Column resizing logic
const tableHead = document.getElementById('table-head');
let headers = Array.from(tableHead.querySelectorAll('th'));
const table = document.getElementById('dynamic-table');

// Resizing functionality
headers.forEach((header, index) => {
    const resizeHandle = document.createElement('div');
    resizeHandle.classList.add('resize-handle');
    header.appendChild(resizeHandle);

    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    resizeHandle.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.pageX;
        startWidth = header.offsetWidth;

        header.classList.add('resizing');
        document.body.classList.add('resizing');

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    });

    function onMouseMove(e) {
        if (!isResizing) return;

        const newWidth = startWidth + (e.pageX - startX);
        header.style.width = `${newWidth}px`;

        document.querySelectorAll(`#dynamic-table td:nth-child(${index + 1})`).forEach(cell => {
            cell.style.width = `${newWidth}px`;
        });

        const totalTableWidth = Array.from(headers).reduce((total, th) => total + th.offsetWidth, 0);
        table.style.width = `${totalTableWidth}px`;
    }

    function onMouseUp() {
        if (!isResizing) return;

        isResizing = false;
        header.classList.remove('resizing');
        document.body.classList.remove('resizing');

        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    }
});

// Column reordering logic
let draggedColumn = null;
let draggedIndex = -1;
let targetColumn = null;

headers.forEach((header) => {
    const h4Element = header.querySelector('h4');

    h4Element.addEventListener('mousedown', () => {
        draggedColumn = header;
        draggedIndex = Array.from(headers).indexOf(header);  // Update draggedIndex dynamically
        header.classList.add('dragging');

        document.addEventListener('mousemove', onColumnDrag);
        document.addEventListener('mouseup', onColumnDrop);
    });

    header.addEventListener('mouseenter', () => {
        if (draggedColumn && draggedColumn !== header) {
            header.classList.add('drag-over');
            targetColumn = header;
        }
    });

    header.addEventListener('mouseleave', () => {
        header.classList.remove('drag-over');
        targetColumn = null;
    });
});

function onColumnDrag(e) {
    e.preventDefault();
    if (!draggedColumn) return;
}

function onColumnDrop() {
    if (!draggedColumn || !targetColumn) return;

    const fromIndex = draggedIndex;
    const toIndex = Array.from(headers).indexOf(targetColumn);  // Update toIndex dynamically

    moveColumn(fromIndex, toIndex);

    draggedColumn.classList.remove('dragging');
    targetColumn.classList.remove('drag-over');

    draggedColumn = null;
    targetColumn = null;

    // Update the headers list after the column has been moved
    headers = Array.from(tableHead.querySelectorAll('th'));

    document.removeEventListener('mousemove', onColumnDrag);
    document.removeEventListener('mouseup', onColumnDrop);
}

// Function to move the columns in the table
function moveColumn(fromIndex, toIndex) {
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        const movingCell = cells[fromIndex];
        const referenceCell = cells[toIndex];

        if (fromIndex < toIndex) {
            referenceCell.parentNode.insertBefore(movingCell, referenceCell.nextSibling);
        } else {
            referenceCell.parentNode.insertBefore(movingCell, referenceCell);
        }
    });
}










document.addEventListener('DOMContentLoaded', function() {
    const columnNames = Array.from(document.querySelectorAll('#dynamic-table thead th h4')).map(th => th.textContent);

    document.querySelectorAll('#dynamic-table tbody tr').forEach(row => {
        row.addEventListener('click', function() {
            const rowData = Array.from(this.querySelectorAll('td h4')).map(cell => cell.innerHTML.trim());
            displayModal(rowData, columnNames);
        });
    });
});

function displayModal(rowData, columnNames) {
    const modal = document.getElementById('row-modal');
    const modalContent = document.getElementById('modal-data');

    // Create a table with two columns: one for column names and one for data
    let tableContent = '<table>';
    rowData.forEach((data, index) => {
        tableContent += `
            <tr>
                <td><strong>${columnNames[index]}</strong></td>
                <td>${escapeHTMLSelective(data)}</td>
            </tr>
        `;
    });
    tableContent += '</table>';

    // Populate the modal content with the table
    modalContent.innerHTML = tableContent;

    // Show the modal
    modal.style.display = 'block';
}

document.getElementById('close-modal').addEventListener('click', function() {
    const modal = document.getElementById('row-modal');
    modal.style.display = 'none';
});

window.onclick = function(event) {
    const modal = document.getElementById('row-modal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

// Selectively escape HTML, allowing <ReporterID> or similar tags to remain intact
function escapeHTMLSelective(unsafe) {
    return unsafe.replace(/<(?!\/?(ReporterID|ReporterUsrnm|ReporterChatID)\b)[^>]*>/g, match => {
        return match.replace(/&/g, "&amp;")
                    .replace(/</g, "&lt;")
                    .replace(/>/g, "&gt;");
    });
}
