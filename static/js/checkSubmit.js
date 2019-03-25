$(function() {
    $('#submit').attr('disabled', 'disabled');
  
    $('#check').click(function() {
      if ( $(this).prop('checked') == false ) {
        $('#submit').attr('disabled', 'disabled');
      } else {
        $('#submit').removeAttr('disabled');
      }
    });
  });