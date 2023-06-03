document.addEventListener('DOMContentLoaded', function() {
    var customSelects = document.querySelectorAll('.custom-select');
    
    customSelects.forEach(function(customSelect) {
      var select = customSelect.querySelector('select');
      var selectedItemsContainer = document.createElement('div');
      selectedItemsContainer.classList.add('selected-items');
      
      select.addEventListener('change', function() {
        renderSelectedItems();
      });
      
      function renderSelectedItems() {
        selectedItemsContainer.innerHTML = '';
        Array.from(select.selectedOptions).forEach(function(option) {
          var selectedItem = document.createElement('span');
          selectedItem.classList.add('selected-item');
          selectedItem.textContent = option.textContent;
          
          var removeItem = document.createElement('span');
          removeItem.classList.add('remove-item');
          removeItem.innerHTML = '&times;';
          removeItem.addEventListener('click', function() {
            option.selected = false;
            renderSelectedItems();
          });
          
          selectedItem.appendChild(removeItem);
          selectedItemsContainer.appendChild(selectedItem);
        });
      }
      
      customSelect.appendChild(selectedItemsContainer);
    });
  });
  