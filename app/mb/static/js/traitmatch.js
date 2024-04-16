// Javascript for the trait match tool

// Function to retrieve CSRF token from cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const referenceCitation = urlParams.get('reference_citation');
    
    if (referenceCitation) {
      document.getElementById('id_reference__citation').value = referenceCitation;
      document.getElementById('Find').submit();
    }
}

$(document).ready(function() {
    // Event listeners
    $("button[id^='editButton_']").click(handleEditButtonClick);
    $("table").on("click", "td.source-attribute-name .editable", handleEditableClick);
    $("button[id^='matchButton_']").click(handleMatchButtonClick);
    $("table").on("keypress", "td.source-attribute-name input.edit-input", handleEnterKeyPress);

    // Functions
    function handleEditButtonClick(event) {
      var sourceAttributeId = $(this).attr("id").split("_")[1];
      var $editableSpan = $(this).closest("tr").find("td.source-attribute-name .editable");
      var $input = $editableSpan.find("input.edit-input");
      var originalValue = $input.closest("td").find(".editable").data("original-value");

      if ($input.length) {
        var newValue = $input.val();
        
        getMatch(newValue, sourceAttributeId);
        $input.closest("td").find(".editable").text(originalValue); 

      } else {
        activateEditableField($editableSpan);
      }
    }

    function activateEditableField($editableSpan) {
      var currentValue = $editableSpan.text();
      $editableSpan.html("<input type='text' class='edit-input' value='" + currentValue + "'>");
      var $input = $editableSpan.find("input.edit-input");
      $input.focus();

      $input.on("blur", function() {
        var $input = $(this);
        setTimeout(function() {
          if (!$input.is(":focus")) { 
            handleEditInputBlur.call($input);
          }
        },200);
      });
    }
    

    function handleEditInputBlur() {
      var $input = $(this);
      var newValue = $input.val();
      var sourceAttributeId = $input.closest("td").find(".editable").data("source-attribute-id");
      var originalValue = $input.closest("td").find(".editable").data("original-value");
  
      getMatch(newValue, sourceAttributeId);
      $input.closest("td").find(".editable").text(originalValue);
    }

    function handleEditableClick() {
      if (!$(this).find("input").length) {
        activateEditableField($(this));
      }
    }

    function handleEnterKeyPress(event) {
      if (event.which === 13) {
        $(this).blur();
      }
    }

    function getMatch(sourceAttributeName, sourceAttributeId) {
      var csrftoken = getCookie('csrftoken');

      $.ajax({
        url: newMatchEndpointUrl,
        method: 'POST',
        data: {
          source_attribute_name: sourceAttributeName,
          csrfmiddlewaretoken: csrftoken,
        },
        success: function (data) {
          if (data.match) {
            var selectedMasterAttributeId = data.match.id;
            var $dropdown = $(
              "span.editable[data-source-attribute-id='" +
                sourceAttributeId +
                "']"
            ).closest('tr').find("select[name='master_attribute']");
            $dropdown.val(selectedMasterAttributeId);
          } else {
            console.log('No match found for current name');
          }
        },
        error: function (xhr, status, error) {
          console.error('Error fetching match:', error);
        },
      });
    }

    function handleMatchButtonClick() {
      var sourceAttributeId = $(this).attr("id").split("_")[1];
      var selectedMasterAttributeId = $(this).closest("tr").find("select[name='master_attribute']").val();
      matchAttributes(sourceAttributeId, selectedMasterAttributeId);
    }

    function matchAttributes(sourceAttributeId, selectedMasterAttributeId) {
      var csrftoken = getCookie('csrftoken');

      $.ajax({
        url: matchOperationEndpointUrl,
        method: "POST",
        data: {
          source_attribute_id: sourceAttributeId,
          selected_master_attribute_id: selectedMasterAttributeId,
          csrfmiddlewaretoken: csrftoken
        },
        success: function(data) {
          if (data.success) {
            showMessage("success", "Match successful!");
            location.reload();
          } else {
            showMessage("error", "Match failed: " + data.error);
          }
        },
        error: function(xhr, status, error) {
          showMessage("error", "An error occurred while matching.");
        }
      });
    }

    function showMessage(type, message) {
      var className = (type === "error") ? "error-message" : "success-message";
      $("#message-container").html("<p class='" + className + "'>" + message + "</p>");
      setTimeout(function() {
        $("#message-container").empty();
      }, 4000);
    }
});
