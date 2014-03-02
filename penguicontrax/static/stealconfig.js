steal.config({
  map: {
    "*": {
      'lodash/lodash.js': "lodash",
      'moment_lib/moment_lib.js': "moment_lib",
      'jquery/jquery.js': "jquery",
      "can/util/util.js": "can/util/jquery/jquery.js"
    }
  },
  paths: {
    "lodash" : "bower_components/lodash/dist/lodash.js",
    "moment_lib" : "bower_components/momentjs/moment.js",
    "jquery": "bower_components/jquery/dist/jquery.js"
  },
  shim: {
    jquery: {
      exports: "jQuery"
    },
    'moment_lib': {
      exports: "moment"
    },
    'lodash' : {
      exports :"_"
    }
  },
  ext: {
    js: "js",
    css: "css",
    less: "steal/less/less-node.js",
    coffee: "steal/coffee/coffee.js",
    ejs: "can/view/ejs/ejs.js",
    mustache: "can/view/mustache/mustache.js"
  },

  //config for less node proxy
  less : {
    //the path that the less middleware will proxy
    proxyPath : "/dev/piano-less-proxy",
    //app context (used to load the source map)
    appContext : "/piano"
  },

  fixtures: false,

  //version below should be replaced during build process with a revision or similar information to indicate build number
  version: 'development'
});
