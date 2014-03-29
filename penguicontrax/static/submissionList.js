(function (ptrax) {

    ptrax.model.Submissions = can.Model.extend({
        'findAll': "/api/submissions?state=0,1,2"
    }, {});

    ptrax.SubmissionList = can.Control.extend({
        defaults : {
            submissions : [],
            submissionsTpl : "",
            userLinkTpl : "",
            userTextTpl : ""
        }
    },{

        init: function () {
            console.debug('init', this.options);

            //register child views
            can.view.registerView('user_link', ptrax.util.tplDecode(this.options.userLinkTpl));
            can.view.registerView('user_text', ptrax.util.tplDecode(this.options.userTextTpl));

            var renderer = can.view.mustache(ptrax.util.tplDecode(this.options.submissionsTpl));

            var fragment = renderer({
                submissions : this.options.submissions,
                user : ptrax.user
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
                    return this.attr('rsvped_by').length;
                },
                user_rsvp: function () {
                    return this.attr('rsvped_by').indexOf(ptrax.user.name) > 0 ? 'user-rsvp' : '';
                }
            });

            this.element.html(fragment);
        }

    });

})(window.ptrax);
