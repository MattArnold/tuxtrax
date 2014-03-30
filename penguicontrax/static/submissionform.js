$(document).ready(function () {


    //style checkboxes
    //$(':checkbox[class!="button-checkbox"]').checkbox();

    //display a message as people type into fields with max length set on them
    $('form textarea[maxlength],form input[maxlength]').on("input",function () {
        var el, len, grp, limit, remaining, charnum, title;

        len = this.value.length;
        el = $(this);
        grp = el.parents('.form-group');

        limit = el.attr('maxlength');
        title = el.attr('data-display-title') ? el.attr('data-display-title') : this.name;

        charnum = grp.find('.charnum');
        remaining = limit - len;

        if (!charnum.length) {
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

        if (limit == len) {
            charnum.text("Maximum length of " + limit + " reached for " + title);
        } else if ((limit - len) < 5) {
            grp.addClass('has-warning');
        }
    }).on('blur', function () {
        $(this).parents('.form-group').removeClass('has-warning').find('.charnum').remove();
    });


    function updateTypeOptions() {
        //
        // To ensure that the elements hidden or shown in each state,
        // we use flags mark them all hidden, then set those which are
        // not hidden, and then use the flags at the end of the function
        // to set every element.
        //
        var pluralized = false;
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
            pptypeshow = true;
        }

        switch ($(this).val()) {

            case 'noroomtype':
                break;
            case 'talk':
                pptypetext = "Speaker:";
                pluralpptypetext = "Panelists:";
                resourcesshow = true;
                otherfacilityshow = true;
                ppshow = true;
                break;
            case 'workshop':
                pptypetext = 'Activity leader:';
                pluralpptypetext = 'Activity leaders:"';
                resourcesshow = true;
                furnitureshow = true;
                otherfacilityshow = true;
                ppshow = true;
                break;
            case 'bof':
                otherfacilityshow = true;
                break;
            case 'game':
                pptypetext = 'Game master:';
                pluralpptypetext = 'Game masters:';
                playersshow = true;
                furnitureshow = true;
                otherfacilityshow = true;
                break;
            case 'onstage':
                $('#pptype').text('Performer:');
                pptypetext = 'Performer:';
                pluralpptypetext = 'Performers:';
                resourcesshow = true;
                otherfacilityshow = true;
                break;
            case 'roving':
                pptypetext = 'Activity leader:';
                pluralpptypetext = 'Activity leaders:';
                otherfacilityshow = true;
                break;
        }

        // now we have all of the values. set everything.
        if (furnitureshow)
            $('#furniture').removeClass('hidden');
        else
            $('#furniture').addClass('hidden');
        if (otherfacilityshow)
            $('#otherfacility').removeClass('hidden');
        else
            $('#otherfacility').addClass('hidden');
        if (playersshow)
            $('#players').removeClass('hidden');
        else
            $('#players').addClass('hidden');
        if (ppshow)
            $('#pp').removeClass('hidden');
        else
            $('#pp').addClass('hidden');
        if (pptypeshow)
            $('#pptype').removeClass('hidden');
        else
            $('#pptype').addClass('hidden');
        if (resourcesshow)
            $('#resources').removeClass('hidden');
        else
            $('#resources').addClass('hidden');
        $('#pptype').text(pptypetext);
        $('#pluralpptype').text(pluralpptypetext);
    }


    function update_time_options() {
        var timeval = $(this).val();
        if (timeval == 0) {
            $("#setupandrepeat, #othertime").addClass('hidden');
        } else if (timeval == 5) {
            $("#setupandrepeat").addClass('hidden');
            $("#othertime").removeClass('hidden');
        } else {
            $("#setupandrepeat, #othertime").removeClass('hidden');
        }
    }

    //set up delegated handler for event type and timechange
    $('form')
        .delegate('input[name=eventtype]', 'change',function handleTypeChange() {
            if (this.checked) {
                updateTypeOptions.call(this);
            }
        }).delegate('input[name=duration]', 'change', function handleTimeChange() {
            if (this.checked) {
                update_time_options.call(this);
            }
        });

    //run once to catch initial page state
    $("[name=eventtype]:checked").each(function () {
        updateTypeOptions.call(this);
    });


    $("[name=timechange]:checked").each(function () {
        update_time_options.call(this);
    });


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
    //TODO refactor this so it works
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

    $('#submitevent').click(function (ev) {
        var facilitycomment, timecomment;
        var $presenter = $('[name="presenter"]');

        ev.preventDefault();

        if(!$presenter.val().length){
            $presenter.val($('[name="submitter_name"]').val());
        }

        // Combine all the comment fields into one comment.
        facilitycomment = $("facilityrequest").val();
        timecomment = $("timerequest").val();
        $("#comments").val(facilitycomment + " | " + timecomment);

        $('form').submit();
    });
});