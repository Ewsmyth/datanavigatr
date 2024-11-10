document.addEventListener('DOMContentLoaded', function() {
    // Select all mission-toggle elements
    const toggles = document.querySelectorAll('.mission-toggle');
  
    // Add click event to toggle the visibility of the queries
    toggles.forEach(toggle => {
      toggle.addEventListener('click', function() {
        const missionId = this.getAttribute('data-mission-id');
        const queryList = document.getElementById(missionId);
  
        // Toggle the visibility of the query list
        if (queryList.style.display === 'none') {
          queryList.style.display = 'block';
        } else {
          queryList.style.display = 'none';
        }
      });
    });
  });
  