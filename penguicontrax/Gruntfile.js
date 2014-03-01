module.exports = function(grunt) {
  grunt.initConfig({
    less: {
      development: {
        options: {
          paths: ["static/ptrax.less"]
        },
        files: {
          "static/ptrax.css": "static/ptrax.less"
        }
      }
    },
    watch: {
      files: "static/ptrax.less",
      tasks: ["less"],
      options : {
        atBegin : true
      }
    }
  });
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');
};