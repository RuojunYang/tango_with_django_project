/**
 * Review Management Scripts
 * Contains functionality for the review management pages
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Review management page loaded successfully');
  
  // Initialize any interactive elements
  initReviewFilters();
  initReviewExpandCollapse();
});

/**
 * Initialize review filtering functionality
 */
function initReviewFilters() {
  // Get filter elements if they exist
  const filterForm = document.querySelector('.filter-form');
  
  if (filterForm) {
    filterForm.addEventListener('submit', function(e) {
      // Add any custom validation or processing here if needed
      console.log('Filter form submitted');
    });
    
    // Reset filters button if present
    const resetButton = document.querySelector('.reset-filters');
    if (resetButton) {
      resetButton.addEventListener('click', function(e) {
        e.preventDefault();
        // Reset all filter inputs
        const inputs = filterForm.querySelectorAll('input, select');
        inputs.forEach(input => {
          if (input.type === 'text' || input.type === 'date' || input.tagName === 'SELECT') {
            input.value = '';
          }
        });
        filterForm.submit();
      });
    }
  }
}

/**
 * Initialize expand/collapse functionality for long reviews
 */
function initReviewExpandCollapse() {
  const reviewContents = document.querySelectorAll('.review-content');
  
  reviewContents.forEach(content => {
    // If content is longer than a certain length
    if (content.textContent.length > 200) {
      const originalText = content.textContent;
      const truncatedText = originalText.substring(0, 200) + '...';
      
      // Create a wrapper for the text and buttons
      const wrapper = document.createElement('div');
      const textElement = document.createElement('p');
      textElement.textContent = truncatedText;
      
      // Create the expand button
      const expandButton = document.createElement('button');
      expandButton.textContent = 'Read more';
      expandButton.className = 'expand-review';
      expandButton.addEventListener('click', function() {
        if (textElement.textContent.endsWith('...')) {
          textElement.textContent = originalText;
          expandButton.textContent = 'Show less';
        } else {
          textElement.textContent = truncatedText;
          expandButton.textContent = 'Read more';
        }
      });
      
      // Add elements to the wrapper and replace content
      wrapper.appendChild(textElement);
      wrapper.appendChild(expandButton);
      content.innerHTML = '';
      content.appendChild(wrapper);
    }
  });
} 