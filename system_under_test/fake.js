var config = require('./serverParams.json');
const http = require(config.protocol);

const requestListener = function (req, res) {
  res.writeHead(config.responseCode, config.responseHeaders);
  res.end(config.responseMessage);
  console.log("got one")
}

const server = http.createServer(requestListener);
server.listen(config.port);