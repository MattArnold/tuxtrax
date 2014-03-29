(function (ptrax) {

    ptrax.model.Submissions = can.Model.extend({
        'findAll': "/api/submissions?state=0,1,2"
    }, {});

    ptrax.SubmissionList = can.Control.extend({
        defaults: {
            submissions: [],
            submissionsTpl: "",
            userLinkTpl: "",
            userTextTpl: ""
        }
    }, {

        init: function () {
            //register child views
            can.view.registerView('user_link', ptrax.util.tplDecode(this.options.userLinkTpl));
            can.view.registerView('user_text', ptrax.util.tplDecode(this.options.userTextTpl));

            var renderer = can.view.mustache(ptrax.util.tplDecode(this.options.submissionsTpl));

            var fragment = renderer({
                submissions: this.options.submissions,
                user: ptrax.user
            }, {

                _followUpState: function () {
                    var state = ["submitted", "followed-up", "accepted", "rejected"];
                    return state[this.attr('followUpState')];
                },
                _duration: function () {
                    var suffix = this.attr('duration') > 1 ? ' hrs' : ' hr';
                    return this.attr('duration') + suffix;
                },
                num_rsvp: function () {
                    return ''+this['rsvped_by'].attr().length;
                },
                user_rsvp: function () {
                    var rsvps = this['rsvped_by'].attr();
                    return _.find(rsvps, {'id': ptrax.user.id }) ? 'fa-star' : 'fa-star-o';
                }
            });

            this.element.html(fragment);
        },

        ".toggle-user-rsvp click": function (el) {
            var submission = el.data('submission');
            var user_rsvp = _.findIndex(submission.attr('rsvped_by'),{'id': ptrax.user.id });
            var apiUrl = '/api/submission/' + submission.attr('id') + '/rsvp';

            if (!submission.attr('updating')) {
                submission.attr('updating', true);

                if (user_rsvp < 0) {
                    //add it
                    $.ajax({
                        url: apiUrl,
                        type: 'POST',
                        success: function () {
                            submission['rsvped_by'].push(ptrax.user);
                            submission.attr('updating', false);
                        }
                    });
                } else {
                    //if its is already there, take it out
                    $.ajax({
                        url: apiUrl,
                        type: 'DELETE',
                        success: function () {
                            //if its is already there, take it out
                            submission['rsvped_by'].splice(user_rsvp, 1);
                            submission.attr('updating', false);
                        }
                    });
                }
            }
        }

    });

})(window.ptrax);
