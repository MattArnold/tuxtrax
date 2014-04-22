module.exports = function (grunt) {
    grunt.initConfig({
        less: {
            development: {
                options: {
                    paths: ["static"],
                    ieCompat: false,
                    sourceMap: true,
                    sourceMapFilename : "static/less.source.map",
                    sourceMapBasepath : "static",
                    sourceMapUrl : "/static/less.source.map",
                    sourceMapRootpath : "/static"
                },
                files: {
                    "static/ptrax.css": "static/ptrax.less"
                }
            },
            production : {
                options: {
                    paths: ["static"],
                    ieCompat: false,
                    sourceMap: false,
                    cssmin : true,
                    cleancss : true
                },
                files: {
                    "static/ptrax.css": "static/ptrax.less"
                }
            }
        },
        watch: {
            files: "static/**/*.less",
            tasks: ["less:development"],
            options: {
                atBegin: true
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
};