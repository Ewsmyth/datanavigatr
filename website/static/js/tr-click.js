$(document).ready(function() {
    $(".user-row").click(function() {
      var url = $(this).data("url");
      if (url) {
        window.location.href = url;
      }
    });
});