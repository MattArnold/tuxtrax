window.ptrax = window.ptrax || {};

(function (ptrax) {

  ptrax.TagFilter = can.Control.extend(
    {
      defaults: {
        tags: [],
        tplUrl: ""
      }
    },
    {
      init: function () {

        var tagList = [], view, data;

        can.each(this.options.tags, function (tag) {
          tagList.push({
            name: tag,
            excluded: false,
            included: true
          });
        });

        data = new can.Map({
          infoText: "",
          all: true,
          tags: tagList
        });

        view = can.view(this.options.tplUrl, data);

        this.options.viewModel = data;
        this.element.html(view);
        this.on();
        this.setInfoText();
      },

      //set the tag button state, updates the data object
      ".btn click": function (el) {
        var data = this.options.viewModel;
        var tag = el.data('tag');
        var tagList = data.tags;
        var all = data.attr('all');

        //look up the tag object
        var t = _.find(tagList, {name: tag});

        //user clicked a tag button
        if (t) {

          //if all is true, reset everything to false and just pick this one thing
          if (all) {
            data.attr('all', false);
          }

          can.batch.start();
          //exclude if included
          if (t.attr('included')) {
            //console.debug(t.name, 'included, set to excluded')
            t.attr('included', false);
            t.attr('excluded', true);
            //if there is nothing included, include everything that isn't explicitly excluded
            if (!_.any(tagList, "included")) {
              _.forEach(tagList, function (tag) {
                if (!tag.attr('excluded') && !(tag.attr('name') === t.attr('name'))) {
                  tag.attr('included', true);
                }
              });
            }
          } else if (t.attr('excluded')) {
            //console.debug(t.name, 'excluded, set to ignore')
            t.attr('excluded', false);
            t.attr('included', false);
          } else {
            //console.debug(t.name, 'neither included or excluded, set to included')
            //include if not excluded or included already
            t.attr('included', true);
          }

          //if nothing is now included or excluded, reselect all
          if (!_.any(tagList, "included") && !_.any(tagList, "excluded")) {
            data.attr('all', true);
          }

          //if everything is now included, reselect all
          if (_.all(tagList, "included")) {
            data.attr('all', true);
          }

          can.batch.stop();

        } else {
          //all
          data.attr('all', !all);
        }

        if (!data.attr('all')) {
          var included = _.pluck(_.filter(tagList, "included"), "name");
          var excluded = _.pluck(_.filter(tagList, "excluded"), "name");
          if(!_.isEmpty(included) || !_.isEmpty(excludded)){
            this.setInfoText(included, excluded);
          }
        }
      },

      "{viewModel} change": function (data, type, attr, action, newVal) {
        var tagList = data.tags;
        if (attr === "all") {
          can.batch.start();
          _.forEach(tagList, function (tagBtn) {
            //toggle all state
            tagBtn.attr('excluded', false);
            tagBtn.attr('included', newVal);
          });
          can.batch.stop();

          if(newVal){
            this.setInfoText();
          }else{
            this.setInfoText(null,null,true);
          }
        }
      },

      //handle taglist changes and update html in page
      "{viewModel.tags} change": function (tagsList, type, attr, action, newVal) {
        var data = this.options.viewModel;
        var prop = attr.split('.')[1];
        var idx = attr.split('.')[0];
        var tag = tagsList.attr(idx);

        //console.debug(prop, newVal, tag.name);

        //submissions that match the tag
        var submissions = $('.submission[data-tags~="' + tag.name + '"]');

        switch (prop) {
          case "included":
            if (newVal) {
              submissions.removeClass('hidden');
            } else {
              submissions.addClass('hidden');
            }
            break;
          case "excluded":
            if (newVal) {
              submissions.addClass('hidden');
            } else {
              submissions.removeClass('hidden');
            }
            break;
        }
      },

      setInfoText: function (included, excluded, noResults) {
        var $info = $('.submissions-list .info');
        var copy = "All submissions shown. Filter by tags using the widget on the left.";
        var includePrefix = " Showing ";
        var includeSuffix = ".";
        var excludePrefix = " Excluding ";
        var excludeSuffix = ".";

        function getTagString(arr) {
          var str = arr.join(',');
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

        console.debug('setInfo',arguments)
        if(noResults){
          copy = "Nothing to show."
        }else{
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

})(ptrax);