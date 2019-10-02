$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
// Add the classes to the toolip when it is created
  $('[data-toggle="tooltip"]').on('inserted.bs.tooltip',function () {
    var thisClass = $(this).attr("class");
    $('.tooltip-inner').addClass(thisClass);
    $('.arrow').addClass(thisClass + "-arrow");
    });
});