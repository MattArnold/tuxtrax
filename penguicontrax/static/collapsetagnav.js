    //Handle collapsing and expanding the tag navigation panel
$(document).ready(function () {
    $('#hidenav').click(function () {
        $('.tagsinput').css('display', 'none');
        $('#shownav').css('display', 'block');
        $('#report').removeClass('col-md-10');
        $('#report').addClass('col-md-12');
    });
    $('#shownavbtn').click(function () {
        $('.tagsinput').css('display', 'none');
        $('#shownav').css('display', 'block');
        $('#report').removeClass('col-md-12');
        $('#report').addClass('col-md-10');
    });
});