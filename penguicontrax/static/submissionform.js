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

  $('#resources, #players, #furniture, #otherfacility, #setupandrepeat, #othertime, .pp, #pptype, #pluralpptype').hide();

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
      $('#furniture').show('slow');
    else
      $('#furniture').hide('slow');
    if (otherfacilityshow)
      $('#otherfacility').show('slow');
    else
      $('#otherfacility').hide('slow');
    if (playersshow)
      $('#players').show('slow');
    else
      $('#players').hide('slow');
    if (ppshow)
      $('#pp').show('slow');
    else
      $('#pp').hide('slow');
    if (pptypeshow)
      $('#pptype').show('slow');
    else
      $('#pptype').hide('slow');
    if (resourcesshow)
      $('#resources').show('slow');
    else
      $('#resources').hide('slow');
    $('#pptype').text(pptypetext);
    $('#pluralpptype').text(pluralpptypetext);
  });

// Turn on time fields when a duration is selected.
  $('.timechange').first().each(function (index, elm) {
    console.log($(elm).val());
    update_time_options(parseInt($(elm).val()), true);
  });
  $('.timechange').change(function () {
    update_time_options(parseInt($(this).val()));
  });
  function update_time_options(timeval, firstShow) {
    var animation = 'slow';
    if (firstShow) {
      animation = null;
    }
    if (timeval == 0) {
      console.log("Hiding stuff");
      $("#setupandrepeat, #othertime").hide("slow");
    } else if (timeval == 5) {
      $("#setupandrepeat").hide("slow");
      $("#othertime").show("slow");
    } else {
      console.log("Showing stuff");
      $("#setupandrepeat, #othertime").show("slow");
    }
  }

// $('.timechange').change(function() {
//	if (parseInt($(this).val()) == 0) {
//		$("#setupandrepeat, #othertime").hide("slow");
//	} else if (parseInt($(this).val()) == 5){
//		$("#setupandrepeat").hide("slow");
//		$("#othertime").show("slow");
//	} else {
//		$("#setupandrepeat, #othertime").show("slow");
//	}
//});

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

// Turn the tag buttons on and off.

  $('.on').click(function () {
    console.log('Clicked an on');
    $($(this)).removeClass('on');
    $($(this)).addClass('off');
    $('#unusedtags').append($(this));
  });

  $('.off').click(function () {
    console.log('Clicked an off');
    $(this).removeClass('off');
    $(this).addClass('on');
    $('#selectedtags').append($(this));
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
    if ($("#facilityrequest").val("other facility requests")) {
      $("#facilityrequest").val("");
    }
    if ($("#timerequest").val("other time requests")) {
      $("#timerequest").val("");
    }
    facilitycomment = $("facilityrequest").val();
    timecomment = $("timerequest").val();
    $("#comments").val(facilitycomment + " " + timecomment);
  });
});
