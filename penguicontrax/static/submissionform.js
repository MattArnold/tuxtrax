// Animate event-type tabs when clicked,
// to show which one is currently in use.

$('input[id="typelist"]:checked').parent().click(function () {
  console.log('Clicked checked.');
  $("#noroomtype").prop('checked');
  $('.roomtab').animate({fontSize: '1em'});
});

$('input[name="typelist"]:not(input[name="typelist"]:checked)').click(function () {
  console.log('Clicked unchecked.');
  $(this).animate({fontSize: '1.2em'});
  $('.roomtab').not(this).animate({fontSize: '.8em'});
});

// Turn on and off appropriate fields for different event-type tabs.

var pluralized = false;

$(document).ready(function () {

    //style select lists
    $("select").selectpicker();

    //style checkboxes
    $(':checkbox[class!="button-checkbox"]').checkbox();

    
    $('form textarea[maxlength],form input[maxlength]').on( "input", function() {
        var el,len,grp,limit,remaining,charnum,title;

        len = this.value.length;
        el = $(this);
        grp = el.parents('.control-group');

        limit = el.attr('maxlength');
        title = el.attr('data-display-title') ? el.attr('data-display-title') : this.name;

        charnum = grp.find('.charnum');
        remaining = limit - len;

        if(!charnum.length){
            grp.append('<small class="charnum" style="display:none"></small>');
            //rerun to get the pointer
            charnum = grp.find('.charnum');
        }

        if (len > 0) {
            charnum.css('display', 'block');
        } else {
            charnum.css('display', 'none');
        }

        charnum.text(remaining + " more characters can fit in the " + title + ".");

        grp.removeClass('has-warning');

        if(limit == len){
            charnum.text("Maximum length of " + limit + " reached for " +  title);
        }else if((limit - len) < 5){
            grp.addClass('has-warning');
        }
    }).on('blur',function(){
        $(this).parents('.control-group').removeClass('has-warning').find('.charnum').remove();
    });


  $('#pptype, #pluralpptype').css('display', 'none');

  $('.typelist:checked').first().each(function (index, elm) {
    update_type_options($(elm).val(), true);
  });

  $('.typelist').change(function () {
    //
    // To ensure that the elements hidden or shown in each state,
    // we use flags mark them all hidden, then set those which are
    // not hidden, and then use the flags at the end of the function
    // to set every element.
    //
    var furnitureshow = false;
    var otherfacilityshow = false;
    var playersshow = false;
    var ppshow = false;
    var pptypeshow = false;
    var resourcesshow = false;

    var pluralpptypetext = '';
    var pptypetext = '';

    // overwrite only
    if (pluralized == false) {
      // $('#pptype').show();
      pptypeshow = true;
    }

    switch ($(this).val()) {

      case 'noroomtype':
        // $('#players, #resources, #otherfacility, .pp').hide('slow');
        // $('#pptype, #pluralpptype').text('');
        break;
      case 'talk':
        // $('#players').hide('slow');
        // $('#pptype').text("Speaker:");
        // $('#pluralpptype').text("Panelists:");
        // $('#resources, #otherfacility, .pp').show('slow');
        pptypetext = "Speaker:";
        pluralpptypetext = "Panelists:";
        resourcesshow = true;
        otherfacilityshow = true;
        ppshow = true;
        break;
      case 'workshop':
        // $('#players').hide('slow');
        // $('#pptype').text("Activity leader:");
        // $('#pluralpptype').text("Activity leaders:");
        // $('#resources, #furniture, #otherfacility, .pp').show('slow');
        pptypetext = 'Activity leader:';
        pluralpptypetext = 'Activity leaders:"';
        resourcesshow = true;
        furnitureshow = true;
        otherfacilityshow = true;
        ppshow = true;
        break;
      case 'bof':
        // $('#resources, #players, #furniture, #pptype, #pluralpp').hide('slow');
        // $('#otherfacility').show('slow');
        otherfacilityshow = true;
        break;
      case 'game':
        // $('#resources, #players, #furniture').hide('slow');
        // $('#pptype').text('Game master:');
        // $('#pluralpptype').text('Game masters:');
        // $('#players, #furniture, #otherfacility').show('slow');
        pptypetext = 'Game master:';
        pluralpptypetext = 'Game masters:';
        playersshow = true;
        furnitureshow = true;
        otherfacilityshow = true;
        break;
      case 'onstage':
        // $('#players, #furniture').hide('slow');
        // $('#pluralpptype').text('Performers:');
        // $('#resources, #otherfacility').show('slow');
        $('#pptype').text('Performer:');
        pptypetext = 'Performer:';
        pluralpptypetext = 'Performers:';
        resourcesshow = true;
        otherfacilityshow = true;
        break;
      case 'roving':
        // $('#resources, #players, #furniture').hide('slow');
        // $('#pptype').text('Activity leader:');
        // $('#pluralpptype').text("Activity leaders:");
        // $('#otherfacility').show('slow');
        pptypetext = 'Activity leader:';
        pluralpptypetext = 'Activity leaders:';
        otherfacilityshow = true;
        break;
    }

    // now we have all of the values. set everything.
    if (furnitureshow)
      $('#furniture').css('display', 'block');
    else
      $('#furniture').css('display', 'none');
    if (otherfacilityshow)
      $('#otherfacility').css('display', 'block');
    else
      $('#otherfacility').css('display', 'none');
    if (playersshow)
      $('#players').css('display', 'block');
    else
      $('#players').css('display', 'none');
    if (ppshow)
      $('#pp').css('display', 'block');
    else
      $('#pp').css('display', 'none');
    if (pptypeshow)
      $('#pptype').css('display', 'block');
    else
      $('#pptype').css('display', 'none');
    if (resourcesshow)
      $('#resources').css('display', 'block');
    else
      $('#resources').css('display', 'none');
    $('#pptype').text(pptypetext);
    $('#pluralpptype').text(pluralpptypetext);
  });

// Turn on time fields when a duration is selected.
  $("[name=timechange]:checked").each(function(){
      update_time_options(parseInt($(this).val(),10))
  });

  //add change handler to timechange radio field
  $("form [name=timechange]").change(function () {

       $("[name=timechange]:checked").each(function(){
          update_time_options(parseInt($(this).val(),10))
      });

  });

  function update_time_options(timeval) {
    if (timeval == 0) {
      $("#setupandrepeat, #othertime").addClass('hidden');
    } else if (timeval == 5) {
      $("#setupandrepeat").addClass('hidden');
      $("#othertime").removeClass('hidden');
    } else {
      $("#setupandrepeat, #othertime").removeClass('hidden');
    }
  }

  $('#moresetuplink').click(function () {
    if ($('#setupandrepeat:visible').length == 0) {
      $('#setupandrepeat').show();
      $('#othertime').show();
    } else {
      $('#setupandrepeat').hide();
      $('#othertime').hide();
    }
    return false;
  });

// Limit the addition of new program participant fields.

  var people = 0;
  $("#newperson").click(function () {
    pluralized = true;
    $('#pptype').hide();
    $('#pluralpptype').show();
    if (people < 8) {
      $("#who").append('<input name="person' + people + '" type="text" size="24" onkeyup="countChar(this, 24)" class="pp" />');
      people = people + 1;
    }
  });


// Animate the track buttons when clicked.

  $('input[name="tracklist"]:checked:enabled').parent().click(function () {
    console.log('Clicked checked.');
    $(this).animate({fontSize: '1em'});
    $('.track').not($(this)).animate({fontSize: '1em'});
  });

  $('input[name="tracklist"]:not(:checked)').parent().click(function () {
    console.log('Clicked unchecked.');
    $(this).animate({fontSize: '1.2em'});
    $('.track').not($(this)).animate({fontSize: '.8em'});
  });

  $('#submitevent').click(function () {
    // Turn the submitter field into firstname and lastname.
    names = $("#submitter").split(" ");
    firstname = names.shift();
    lastname = names.join();
    $("firstname").val(firstname);
    $("lastname").val(lastname);

    // Combine all the comment fields into one comment.
    if ($("#facilityrequest").val("Other room and furniture setup requests go here. If you selected 'More', we'll work out the specifics with you later.")) {
      $("#facilityrequest").val("");
    }
    if ($("#timerequest").val("Other time requests go here. If you selected 'More', we'll work out the specifics with you later.")) {
      $("#timerequest").val("");
    }
    facilitycomment = $("facilityrequest").val();
    timecomment = $("timerequest").val();
    $("#comments").val(facilitycomment + " | " + timecomment);
  });
});