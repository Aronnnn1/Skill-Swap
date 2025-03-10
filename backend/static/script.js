function openForm(formId) {
    document.getElementById(formId).style.display = 'flex';
}

function closeForm(formId) {
    document.getElementById(formId).style.display = 'none';
}

// Limit teacher subjects to 3 selections
function selectSubject(button) {
    const selectedButtons = document.querySelectorAll('.subject-btn.selected');
    
    // If the subject is already selected, deselect it
    if (button.classList.contains('selected')) {
        button.classList.remove('selected');
    } else {
        // If less than 3 subjects are selected, add this one
        if (selectedButtons.length < 3) {
            button.classList.add('selected');
        } else {
            alert("You can select up to 3 subjects only.");
        }
    }
}