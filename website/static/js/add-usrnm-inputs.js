// JavaScript to dynamically add more username input fields
document.getElementById('add-member-btn').addEventListener('click', function () {
    const memberInputsDiv = document.getElementById('member-inputs');

    // Create a new input element for a username
    const newInputDiv = document.createElement('div');
    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.name = 'mission-members';  // Corrected name for dynamic inputs
    newInput.placeholder = 'Enter a username';
    newInput.required = true;

    // Add the new input to the div
    newInputDiv.appendChild(newInput);
    memberInputsDiv.appendChild(newInputDiv);
});