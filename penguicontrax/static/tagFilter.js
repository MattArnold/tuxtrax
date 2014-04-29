(function (ptrax) {
    var INCLUDED = 1;
    var NEUTRAL = 0;
    var EXCLUDED = -1;

    function isIncluded(tag) {
        return tag.attr('state') === INCLUDED;
    }

    function isNeutral(tag) {
        return tag.attr('state') === NEUTRAL;
    }

    function isExcluded(tag) {
        return tag.attr('state') === EXCLUDED;
    }

    function getCookieOrRandom(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i].trim();
            if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
        }
        return Math.floor(Math.random() * 100000);
    }


    ptrax.TagFilter = can.Control.extend(
        {
            defaults: {
                tags: [],
                tplUrl: ""
            }
        },
        {
            init: function () {

                var tagList = [], tpl, renderer;

                this.options.viewModel = new can.Map({
                            infoText: "",
                            all: true,
                            tags: [],
                            tagsByName: {},
                            submissionsByTagName: {}
                        });

                $.get('/api/tags?ver=' + getCookieOrRandom('submission_ver'))

                    .done(can.proxy(function (tags) {

                        this.options.tags = new can.List(tags);

                        can.each(this.options.tags, function (tag) {
                            tagList.push({
                                name: tag.id,
                                state: INCLUDED,
                                desc : tag.desc
                            });
                        });

                        this.options.viewModel.attr({
                            tags: tagList,
                            tagsByName: _.zipObject(_.pluck(tagList, 'name'), tagList)
                        });

                        tpl = ptrax.util.tplDecode(this.options.tpl);
                        renderer = can.view.mustache(tpl);

                        this.element.html(renderer(this.options.viewModel, {
                            isIncluded: function (options) {
                                if (isIncluded(this)) {

                                    return options.fn(this)
                                }
                            },
                            isExcluded: function (options) {
                                if (isExcluded(this)) {
                                    return options.fn(this)
                                }
                            }
                        }));

                        this.on();
                        this.setInfoText();

                    }, this));


            },

            isSubmissionVisible: function (submission) {
                var data = this.options.viewModel;

                function isTagNameIncluded(tag) {
                    return isIncluded(data.tagsByName[tag.id]);
                }

                function isTagNameNeutral(tag) {
                    return isNeutral(data.tagsByName[tag.id]);
                }

                function isTagNameExcluded(tag) {
                    return isExcluded(data.tagsByName[tag.id]);
                }

                var visible = _.any(submission.tags, isTagNameIncluded)
                    && !_.any(submission.tags, isTagNameExcluded);
                return visible;
            },

            //submissions list has a new item
            addSubmission: function (submission) {
                var data = this.options.viewModel;
                // register this submission's tags in the map
                can.each(submission.attr('tags'), function (tag) {
                    if(!data.submissionsByTagName[tag.id]){
                        data.submissionsByTagName[tag.id] = [];
                    }
                    data.submissionsByTagName[tag.id].push(submission);
                });
                // set initial visible state on the submission
                var visible = this.isSubmissionVisible(submission);
                submission.attr('hidden', !visible);
            },

            "{submissions} add" : function(list,ev,newItems){
                var self = this;
                _.each(newItems,function(submission){
                   self.addSubmission(submission);
                });
            },

            //set the tag button state, updates the data object
            ".btn click": function (el) {
                var data = this.options.viewModel;
                var tagName = el.data('tag');
                var tagList = data.tags;
                var all = data.attr('all');

                //look up the tag object
                var t = data.tagsByName[tagName];

                //user clicked a tag button
                if (t) {

                    //if all is true, reset everything to false and just pick this one thing
                    if (all) {
                        data.attr('all', false);
                    }

                    can.batch.start();
                    //exclude if included
                    if (isIncluded(t)) {
                        //console.debug(t.name, 'included, set to excluded')
                        t.attr('state', EXCLUDED);
                        //if there is nothing included, include everything that isn't explicitly excluded
                        if (!_.any(tagList, isIncluded)) {
                            _.forEach(tagList, function (tag) {
                                if (!isExcluded(tag) && !(tag.attr('name') === t.attr('name'))) {
                                    tag.attr('state', INCLUDED);
                                }
                            });
                        }
                    } else if (isExcluded(t)) {
                        //console.debug(t.name, 'excluded, set to ignore')
                        t.attr('state', NEUTRAL);
                    } else {
                        //console.debug(t.name, 'neither included or excluded, set to included')
                        //include if not excluded or included already
                        t.attr('state', INCLUDED);
                    }

                    //if nothing is now included or excluded, reselect all
                    if (!_.any(tagList, isIncluded) && !_.any(tagList, isExcluded)) {
                        data.attr('all', true);
                    }

                    //if everything is now included, reselect all
                    if (_.all(tagList, isIncluded)) {
                        data.attr('all', true);
                    }

                    can.batch.stop();

                } else {
                    //all
                    data.attr('all', !all);
                }

                if (!data.attr('all')) {
                    var included = _.pluck(_.filter(tagList, isIncluded), "name");
                    var excluded = _.pluck(_.filter(tagList, isExcluded), "name");
                    if (!(_.isEmpty(included) && _.isEmpty(excluded))) {
                        this.setInfoText(included, excluded);
                    }
                }
            },

            "{viewModel} change": function (data, type, attr, action, newVal) {
                var tagList = data.tags;
                if (attr === "all") {
                    can.batch.start();
                    _.forEach(tagList, function (tag) {
                        //toggle all state
                        tag.attr('state', newVal ? INCLUDED : NEUTRAL);
                    });
                    can.batch.stop();

                    if (newVal) {
                        this.setInfoText();
                    } else {
                        this.setInfoText(null, null, true);
                    }
                }
            },

            //handle taglist changes and update html in page
            "{viewModel.tags} change": function (tagsList, type, attr, action, newVal) {
                var self = this;
                var data = this.options.viewModel;
                var idx = attr.split('.')[0];
                var tag = tagsList.attr(idx);

                //console.debug(prop, newVal, tag.name);

                //submissions that match the tag
                var submissions = data.submissionsByTagName[tag.name] || [];

                can.batch.start();

                can.each(submissions, function (submission) {
                    var visible = self.isSubmissionVisible(submission);
                    submission.attr('hidden', !visible);
                });

                can.batch.stop();
            },

            setInfoText: function (included, excluded, noResults) {
                var $info = $('.submissions-list .info');
                var copy = $info.data('default');
                var includePrefix = " Showing ";
                var includeSuffix = ".";
                var excludePrefix = " Excluding ";
                var excludeSuffix = ".";

                function getTagString(arr) {
                    var str = arr.join(', ');
                    str = str.replace(/,/, ", ");

                    if (arr.length > 1) {
                        if (arr.length == 2) {
                            str = str.replace(/,/, " and");
                        } else {
                            str = str.replace(/,(?=[^,]*$)/, ' and ');
                        }
                    }

                    return str;

                }

                if (noResults) {
                    copy = "Nothing to show."
                } else {
                    if (!_.isEmpty(included) || !_.isEmpty(excluded)) {
                        copy = "";
                        if (!_.isEmpty(included)) {

                            copy += includePrefix + getTagString(included) + includeSuffix;
                        }

                        if (!_.isEmpty(excluded)) {
                            copy += excludePrefix + getTagString(excluded) + excludeSuffix;
                        }
                    }
                }

                $info.text(copy);
            }
        });

})(window.ptrax);