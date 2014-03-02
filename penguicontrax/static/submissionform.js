// Animate event-type tabs when clicked,
// to show which one is currently in use.

$('input[id="typelist"]:checked').parent().click(function() {
	console.log('Clicked checked.');
	$("#noroomtype").prop('checked');
	$('.roomtab').animate({fontSize: '1em'});	
});

$('input[name="typelist"]:not(input[name="typelist"]:checked)').click(function() {
	console.log('Clicked unchecked.');
	$(this).animate({fontSize: '1.2em'});
	$('.roomtab').not(this).animate({fontSize: '.8em'});
});

// Turn on and off appropriate fields for different event-type tabs.

var pluralized = false;

$(document).ready(function() {
	$('#resources, #players, #furniture, #otherfacility, #setupandrepeat, #othertime, .pp, #pptype, #pluralpptype').hide();
	$('.typelist:checked').first().each(function(index, elm) {
		update_type_options($(elm).val(), true);
	});
	$('.typelist').change(function() {
		update_type_options($(this).val());
	});
});

function update_type_options(type, firstShow) {
	if (pluralized == false) {
		$('#pptype').show();
	};
	var animation = 'slow';
	if (firstShow) {
		animation = null;
	}
	switch (type) {
		case 'noroomtype':
			$('#players, #resources, #otherfacility, .pp').hide(animation);
			$('#pptype, #pluralpptype').text('');
			break;
		case 'talk':
			$('#players').hide(animation);
			$('#pptype').text("Speaker:");
			$('#pluralpptype').text("Panelists:");
			$('#resources, #otherfacility, .pp').show(animation);
			break;
		case 'workshop':
			$('#players').hide(animation);
			$('#pptype').text("Activity leader:");
			$('#pluralpptype').text("Activity leaders:");
			$('#resources, #furniture, #otherfacility, .pp').show(animation);
			break;
		case 'bof':
			$('#resources, #players, #furniture, #pptype, #pluralpp').hide(animation);
			$('#otherfacility').show(animation);
			break;
		case 'game':
			$('#resources, #players, #furniture').hide(animation);
			$('#pptype').text('Game master:');
			$('#pluralpptype').text('Game masters:');
			$('#players, #furniture, #otherfacility').show(animation);
			break;
		case 'onstage':
			$('#players, #furniture').hide(animation);
			$('#pptype').text('Performer:');
			$('#pluralpptype').text('Performers:');
			$('#resources, #otherfacility').show(animation);
			break;
		case 'roving':
			$('#resources, #players, #furniture').hide(animation);
			$('#pptype').text('Activity leader:');
			$('#pluralpptype').text("Activity leaders:");
			$('#otherfacility').show(animation);
			break;
	}
}


// Turn on time fields when a duration is selected.
$('.timechange').first().each(function(index, elm) {
	console.log($(elm).val());
	update_time_options(parseInt($(elm).val()), true);
});
$('.timechange').change(function() {
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
	} else if (timeval == 5){
		$("#setupandrepeat").hide("slow");
		$("#othertime").show("slow");
	} else {
		console.log("Showing stuff");
		$("#setupandrepeat, #othertime").show("slow");
	}
}

// blurb should have 700 characters max. title should have 80 characters max. person should have 24 characters max.
function countChar(thebox, limit) {
	var len = thebox.value.length;
	if (len >= limit) {
		thebox.value = thebox.value.substring(0, limit);
	} else {
		remaining = limit - len;
		$('#charnum').text(remaining + " characters remaining in " + thebox.name);
	}
};


// Limit the addition of new program participant fields.
var people = 0;
$("#newperson").click(function() {
	pluralized = true;
	$('#pptype').hide();
	$('#pluralpptype').show();
	if(people<8){
		$("#who").append('<input name="person' + people + '" type="text" size="24" onkeyup="countChar(this, 24)" class="pp" />');
		people = people + 1;
	}
})

// Turn the tag buttons on and off.

$('.on').click(function() {
	console.log('Clicked an on');
	$($(this)).removeClass('on');
	$($(this)).addClass('off');
	$('#unusedtags').append($(this));
});

$('.off').click(function() {
	console.log('Clicked an off');
	$(this).removeClass('off');
	$(this).addClass('on');
	$('#selectedtags').append($(this));
});

// Animate the track buttons when clicked.

$('input[name="tracklist"]:checked:enabled').parent().click(function() {
	console.log('Clicked checked.');
	$(this).animate({fontSize: '1em'});
	$('.track').not($(this)).animate({fontSize: '1em'});	
});

$('input[name="tracklist"]:not(:checked)').parent().click(function() {
	console.log('Clicked unchecked.');
	$(this).animate({fontSize: '1.2em'});
	$('.track').not($(this)).animate({fontSize: '.8em'});
});

$('#submitevent').click( function() {
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
