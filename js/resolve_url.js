// resolve_url.js
const TinyURL = require('tinyurl');
const urlToResolve = process.argv[2]; // Get URL from command-line argument

TinyURL.resolve(urlToResolve).then(
  function(res) {
    console.log(res); // Print the full URL
  },
  function(err) {
    console.error(err);
    process.exit(1); // Exit with an error code
  }
);
